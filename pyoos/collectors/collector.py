from pytz import timezone

class Collector(object):

    def __init__(self):
        self.utc = timezone('UTC')

    def get_start_time(self):
        """
            The start time to collect data from

            If the datetime object passed in has no tzinfo
            associated with it, it is assumed to be UTC.
        """
        try: 
            return self._start_time
        except:
            return None
    def set_start_time(self, time):

        if not time.tzinfo:
            time = time.replace(tzinfo=self.utc)
        self._start_time = time.astimezone(self.utc)
    start_time = property(get_start_time, set_start_time)

    def get_end_time(self):
        """
            The end time to collect data to

            If the datetime object passed in has no tzinfo
            associated with it, it is assumed to be UTC.
        """
        try: 
            return self._end_time
        except:
            return None
    def set_end_time(self, time):

        if not time.tzinfo:
            time = time.replace(tzinfo=self.utc)
        self._end_time = time.astimezone(self.utc)
    end_time = property(get_end_time, set_end_time)