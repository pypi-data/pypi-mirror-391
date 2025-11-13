import queue
import threading
from dataclasses import dataclass

import framepump.framepump as framepump_


class VideoWriter:
    def __init__(self, video_path=None, fps=None, audio_source_path=None, queue_size=32):
        self.q = None
        self.thread = None
        self.active = False
        self.queue_size = queue_size

        if video_path is not None:
            if fps is not None:
                self.start_sequence(video_path, fps, audio_source_path=audio_source_path)
            else:
                raise ValueError("fps must be provided if video_path is provided")

    def start_sequence(self, video_path, fps, audio_source_path=None):
        if self.thread is None:
            self.q = queue.Queue(self.queue_size)
            self.thread = threading.Thread(target=main_video_writer, args=(self.q,), daemon=True)
            self.thread.start()

        self.q.put(StartSequence(video_path, fps, audio_source_path=audio_source_path))
        self.active = True

    def is_active(self):
        return self.active

    def append_data(self, frame):
        if not self.active:
            raise ValueError("start_sequence has to be called before appending data")
        self.q.put(AppendFrame(frame))

    def end_sequence(self):
        if not self.active:
            raise ValueError("start_sequence has to be called before ending the sequence")
        self.q.put(EndSequence())
        self.active = False

    def close(self):
        if self.thread is not None:
            self.q.put(Quit())
            self.q.join()
            self.thread.join()
        self.active = False

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()


def main_video_writer(q):
    writer = None
    while True:
        msg = q.get()

        if isinstance(msg, AppendFrame) and writer is not None:
            writer.send(msg.frame)
        elif isinstance(msg, StartSequence):
            if writer is not None:
                writer.close()

            writer = framepump_.iter_video_write(
                msg.video_path, fps=msg.fps, audio_source_path=msg.audio_source_path
            )
        elif isinstance(msg, (EndSequence, Quit)):
            if writer is not None:
                writer.close()
                writer = None

        q.task_done()

        if isinstance(msg, Quit):
            return


@dataclass
class StartSequence:
    video_path: any = None
    fps: any = 30
    audio_source_path: any = None


@dataclass
class AppendFrame:
    frame: any


class EndSequence:
    pass


class Quit:
    pass
