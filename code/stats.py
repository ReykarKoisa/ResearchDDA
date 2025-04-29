


class Stats:
    def __init__(self):
        self.health= 0;
        self.deaths = 0;
        self.time = 0;

    def get_health(self):
        return self.health

    def get_deaths(self):
        return self.deaths
    
    def get_time(self):
        return self.time
    
    def set_health(self,x):
        self.health = x
    
    def increment_death(self):
        self.death += 1

    def set_time(self,x):
        self.time = x