import re

LONG = 0
SHORT = 1

class Dax:
    def find(self, msg):
        dax_re = re.compile(r'^dax\s' +         # DAX at the beginning
                            '(short|long)\s*' + # Short or Long
                            '[0-9]{4,5}\s*' +   # Entry
                            'stop\s*' +         # Stop
                            '([0-9]{4,5}|([0-9]{1,2}\spk))', # Stop level (price or distance ['PK'])
                            re.IGNORECASE)
        if dax_re.findall(msg):
            return True
        else:
            return False

    def get_longshort(self, msg):
        long_re = re.compile(r'^dax\s*long\s', re.IGNORECASE)
        return LONG if long_re.findall(msg) else SHORT

    def get_stop(self, msg):
        stop_re = re.compile(r'stop\s*([0-9]{4,5}|([0-9]{1,2}\spk))', re.IGNORECASE)
        stop_re_std = re.compile(r'[0-9]{4,5}', re.IGNORECASE)
        stop_re_pk = re.compile(r'[0-9]{1,2}\spk', re.IGNORECASE)
        s1 = stop_re.search(msg).group()
        s2 = stop_re_std.search(s1)
        s3 = stop_re_pk.search(s1)
        if s2:
            return int(s2.group())
        elif s3:
            return int(s3.group()[:-len(' pk')])
        else:
            raise Exception('Stop not found in msg ' + msg)

    def get_start(self, msg):
        # Set trade start
        in_re = re.compile(r'\s[0-9]{4,5}\s', re.IGNORECASE)
        return int(in_re.search(msg).group()[1:-1])

    def find_tvk(self, msg):
        tvk_re = re.compile(r'(?:^|\s|$)(tvk|flat)(?:^|\s|$)', re.IGNORECASE)
        if tvk_re.findall(msg):
            return True
        else:
            return False

    def find_einstand(self, msg):
        einstand_re = re.compile(r'(?:^|\s|$)einstand(?:^|\s|$)', re.IGNORECASE)
        if einstand_re.findall(msg):
            return True
        else:
            return False

    def find_stop(self, msg):
        stop_re = re.compile(r'stop [0-9]{4,5}', re.IGNORECASE)
        stop = stop_re.search(msg)
        if stop:
            return int(stop.group[5:])
        else:
            return False

