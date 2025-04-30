from pygame.time import get_ticks

class EventTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = get_ticks()
        self.end_time = None

    def stop(self):
        if self.start_time is not None:
            self.end_time = get_ticks()

    def get_duration(self):
        if self.start_time is not None and self.end_time is not None:
            return (self.end_time - self.start_time) / 1000  # in seconds
        elif self.start_time is not None:
            return (get_ticks() - self.start_time) / 1000  # still running
        return 0

    def is_running(self):
        return self.start_time is not None and self.end_time is None