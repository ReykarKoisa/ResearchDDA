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
        if self.start_time is None:
            return 0
        if self.is_running():
            return (get_ticks() - self.start_time) / 1000  # Timer still running
        else:
            return (self.end_time - self.start_time) / 1000  # Timer stopped


    def is_running(self):
        return self.start_time is not None and self.end_time is None