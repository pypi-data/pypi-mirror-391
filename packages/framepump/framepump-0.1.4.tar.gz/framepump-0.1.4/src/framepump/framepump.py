import ffmpeg
import imageio.v2 as imageio
import imageio_ffmpeg
import more_itertools
import numpy as np
import simplepyutils as spu


def video_extents(filepath):
    """Returns the video (width, height) as a numpy array, without loading the pixel data."""

    with imageio.get_reader(filepath, 'ffmpeg') as reader:
        return np.asarray(reader.get_meta_data()['source_size'])


def get_writer(path, fps, crf=15, audio_path=None):
    spu.ensure_parent_dir_exists(path)
    return imageio.get_writer(
        path,
        codec='libx264',
        input_params=['-r', str(fps), '-thread_queue_size', '64'],
        output_params=['-crf', str(crf)],
        audio_path=audio_path,
        audio_codec='copy',
        macro_block_size=2,
    )


def get_reader(video_path, output_imshape=None):
    output_params = ['-map', '0:v:0']
    if output_imshape is not None:
        output_params += ['-vf', f'scale={output_imshape[1]}:{output_imshape[0]}']

    return imageio.get_reader(video_path, 'ffmpeg', output_params=output_params)


# This uses ffmpeg.bla functios directly, including scaing the video to a specific resolution
def iter_frames(
    video_path, output_imshape=None, dtype=np.uint8, use_gpu=False, constant_framerate=True
):
    orig_imshape = video_extents(video_path)[::-1]
    imshape = output_imshape if output_imshape is not None else orig_imshape
    if dtype not in (np.uint8, np.uint16):
        raise ValueError(f"Unsupported dtype: {dtype}")

    arrshape = [imshape[0], imshape[1], 3]
    numbytes = np.prod(arrshape) * np.dtype(dtype).itemsize

    vsync = '1' if constant_framerate else '0'

    if use_gpu:
        if output_imshape is not None:
            x = (
                ffmpeg.input(video_path, hwaccel='cuda', hwaccel_output_format='cuda', vsync=vsync)
                .filter('scale_cuda', output_imshape[1], output_imshape[0])
                .filter('hwdownload')
                .filter('format', 'nv12')
            )
        else:
            x = ffmpeg.input(video_path, hwaccel='cuda', vsync=vsync)
    else:
        x = ffmpeg.input(video_path, vsync=vsync)
        if output_imshape is not None:
            x = x.filter('scale', output_imshape[1], output_imshape[0])

    pix_fmt = 'rgb48' if dtype == np.uint16 else 'rgb24'
    x = x.output('pipe:', format='rawvideo', pix_fmt=pix_fmt)
    global_args = ['-loglevel', 'quiet', '-nostdin']
    x = x.global_args(*global_args)

    with x.run_async(pipe_stdout=True) as process:
        while True:
            placeholder = np.empty([numbytes], np.uint8)
            n_read = process.stdout.readinto(memoryview(placeholder))
            if n_read == 0:
                break
            if n_read != numbytes:
                raise ValueError("Failed to read the expected number of bytes")

            yield placeholder.view(dtype).reshape(arrshape)


def has_audio(video_path):
    probe = ffmpeg.probe(video_path)
    return any(stream['codec_type'] == 'audio' for stream in probe['streams'])


@more_itertools.consumer
def iter_video_write(video_path, fps, crf=15, audio_source_path=None):
    spu.ensure_parent_dir_exists(video_path)

    frame = yield
    if frame is None:
        return

    if frame.dtype not in (np.uint8, np.uint16):
        raise ValueError(f'Unsupported frame dtype: {frame.dtype}')

    pix_fmt = 'rgb24' if frame.dtype == np.uint8 else 'rgb48'

    video = ffmpeg.input(
        'pipe:',
        format='rawvideo',
        pix_fmt=pix_fmt,
        s=f'{frame.shape[1]}x{frame.shape[0]}',
        r=str(fps),
        thread_queue_size=64,
    ).video

    out_pix_fmt = 'yuv420p' if frame.dtype == np.uint8 else 'yuv420p10le'

    if audio_source_path is not None and has_audio(audio_source_path):
        audio = ffmpeg.input(audio_source_path).audio
        x = ffmpeg.output(
            audio,
            video,
            video_path,
            acodec='copy',
            vcodec='h264',
            crf=str(crf),
            pix_fmt=out_pix_fmt,
        )
    else:
        x = ffmpeg.output(video, video_path, vcodec='h264', crf=str(crf), pix_fmt=out_pix_fmt)

    x = x.global_args('-loglevel', 'quiet')
    x = x.overwrite_output()

    with x.run_async(pipe_stdin=True) as process:
        while frame is not None:
            process.stdin.write(memoryview(np.ascontiguousarray(frame.reshape(-1)).view(np.uint8)))
            frame = yield


# class VideoWriter:
#     def __init__(self, video_path, fps, crf=15, audio_source_path=None):
#         self.gen = iter_video_write(video_path, fps, crf, audio_source_path=None)
#
#     def append_data(self, frame):
#         self.gen.send(frame)
#
#     def close(self):
#         try:
#             self.gen.send(None)
#         except StopIteration:
#             pass
#
#     def __enter__(self):
#         return self
#
#     def __exit__(self, *args, **kwargs):
#         self.close()
#


def get_fps(video_path):
    try:
        probe = ffmpeg.probe(video_path, select_streams='v:0', show_entries='stream=r_frame_rate')
        frame_rate = probe['streams'][0]['r_frame_rate']
        numerator, denominator = map(int, frame_rate.split('/'))
        return numerator / denominator
    except (ffmpeg.Error, StopIteration, KeyError) as e:
        raise ValueError(f"Failed to retrieve FPS: {e}")


def get_duration(video_path):
    try:
        return float(ffmpeg.probe(video_path)['format']['duration'])
    except (ffmpeg.Error, KeyError) as e:
        raise ValueError(f"Failed to retrieve duration: {e}")


def num_frames(path, exact=False, absolutely_exact=False):
    if absolutely_exact:
        with get_reader(path) as reader:
            return more_itertools.ilen(reader)

    if exact:
        return imageio_ffmpeg.count_frames_and_secs(path)[0]

    # with get_reader(path) as reader:
    #     metadata = reader.get_meta_data()
    #     n = metadata['nframes']
    #     if isinstance(n, int):
    #         return n

    # probe = ffmpeg.probe(path, select_streams='v:0', show_entries='stream=nb_frames')
    # n = probe['streams'][0].get('nb_frames')
    # if n is not None:
    #     return int(n)

    return int(round(get_duration(path) * get_fps(path)))


def video_audio_mux(vidpath_audiosource, vidpath_imagesource, out_video_path):
    video = ffmpeg.input(vidpath_imagesource).video
    audio = ffmpeg.input(vidpath_audiosource).audio
    (
        ffmpeg.output(audio, video, out_video_path, vcodec='copy', acodec='copy')
        .overwrite_output()
        .run()
    )


def trim_video(input_path, output_path, start_time, end_time):
    (
        ffmpeg.input(input_path, ss=start_time, to=end_time)
        .output(output_path, vcodec='h264_nvenc', rc='vbr_hq', cq=20, acodec='copy')
        .overwrite_output()
        .run()
    )


class VideoFrames:
    def __init__(self, video_path, dtype=np.uint8, use_gpu=False, constant_framerate=True):
        self.path = video_path
        self.original_imshape = video_extents(video_path)[::-1]
        self.n_frames_total = num_frames(video_path, exact=False)
        self.original_fps = get_fps(video_path)
        self.resized_imshape = None
        self.slicable_slice = spu.SlicableForwardSlice()
        self.repeat_count = 1

        if dtype not in (np.uint8, np.uint16, np.float16, np.float32, np.float64):
            raise ValueError(f"Unsupported dtype: {dtype}")

        self.dtype = dtype
        self.use_gpu = use_gpu
        self.constant_framerate = constant_framerate

    def clone(self):
        result = VideoFrames.__new__(VideoFrames)
        result.path = self.path
        result.original_imshape = self.original_imshape
        result.n_frames_total = self.n_frames_total
        result.resized_imshape = self.resized_imshape
        result.slicable_slice = self.slicable_slice
        result.original_fps = self.original_fps
        result.repeat_count = self.repeat_count
        result.dtype = self.dtype
        result.use_gpu = self.use_gpu
        result.constant_framerate = self.constant_framerate
        return result

    def repeat_each_frame(self, n: int):
        if n < 1:
            raise ValueError("The repeat count must be at least 1.")
        result = self.clone()
        result.repeat_count *= n
        return result

    def _maybe_to_float(self, value):
        if self.dtype == np.uint8 or self.dtype == np.uint16:
            return value

        if value.dtype == np.uint16 and self.dtype == np.float16:
            x = value.clip(0, 65504).astype(np.float16)
            x /= 65504.0
            return x

        maxval = np.iinfo(value.dtype).max
        return value.astype(self.dtype) / maxval

    def __iter__(self):
        internal_dtype = np.uint8 if self.dtype == np.uint8 else np.uint16
        frames = iter_frames(
            self.path,
            output_imshape=self.resized_imshape,
            dtype=internal_dtype,
            use_gpu=self.use_gpu,
            constant_framerate=self.constant_framerate,
        )
        try:
            sliced_cast_frames = map(self._maybe_to_float, self.slicable_slice.apply(frames))
            if self.repeat_count == 1:
                yield from spu.repeat_n(sliced_cast_frames, self.repeat_count)
            else:
                yield from sliced_cast_frames
        finally:
            frames.close()

    def __getitem__(self, item):
        if isinstance(item, slice):
            if self.repeat_count != 1:
                raise NotImplementedError('Slicing a frame-repeated video is not supported yet.')
            result = self.clone()
            result.slicable_slice = self.slicable_slice[item]
            return result
        else:
            raise TypeError("Only slice objects are supported.")

    def __len__(self):
        return len(range(self.n_frames_total)[self.slicable_slice.to_slice()]) * self.repeat_count

    @property
    def imshape(self):
        return self.resized_imshape if self.resized_imshape is not None else self.original_imshape

    @property
    def fps(self):
        return self.original_fps / self.slicable_slice.step * self.repeat_count

    def resized(self, shape):
        result = self.clone()
        result.resized_imshape = shape
        return result
