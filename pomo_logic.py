import datetime

class pomo():
    def __init__(self):
        self.active_timers = []

    def get_timer(self, name):
        if any(name in x for x in self.active_timers):
            for timer in self.active_timers:
                if name in timer:
                    return timer
    
    def timerset(self, name, time_length, timer_type):
        current_time = datetime.datetime.now()
        self.active_timers.append([name, current_time, "study"])

    def canceltimer(self, name):
        if any(name in x for x in self.active_timers):
            for timer in self.active_timers:
                if name in timer:
                    self.active_timers.remove(timer)
                    return True
        return False