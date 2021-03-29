import datetime

class pomo():
    def __init__(self):
        self.active_timers = []

    def get_timer(self, name):
        if any(name in x for x in self.active_timers):
            for timer in self.active_timers:
                if name in timer:
                    return timer
    
    def set_timer(self, name, time_length, timer_type):
        current_time = datetime.datetime.now()
        finish_time = current_time + datetime.timedelta(minutes=int(time_length))
        self.active_timers.append([name, finish_time, "study"])

    def time_left(self, name):
        user = self.get_timer(name)
        if user is not None:
            time = user[1] - datetime.datetime.now()
            return int(time.total_seconds() / 60)

    def cancel_timer(self, name):
        if any(name in x for x in self.active_timers):
            for timer in self.active_timers:
                if name in timer:
                    self.active_timers.remove(timer)
                    return True
        return False