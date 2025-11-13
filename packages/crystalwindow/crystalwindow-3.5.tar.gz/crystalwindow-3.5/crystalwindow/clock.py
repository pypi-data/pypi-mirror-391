import time

class Clock:
    def __init__(self):
        self.last_time = time.time()
        self.delta = 0
        self.fps = 60

    def tick(self, fps=60):
        now = time.time()
        self.delta = now - self.last_time
        self.last_time = now
        self.fps = fps
        time.sleep(max(0, (1 / fps) - self.delta))
        return self.delta

    def get_fps(self):
        return round(1 / self.delta, 2) if self.delta else 0
