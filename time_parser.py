import time_info
import datetime


class TimeParser:
    zone = None
    clock = ''
    hour = 0
    minute = 0

    weekday = None
    day = None
    month = None

    asap = False
    dt = None

    def __init__(self, raw: str):
        self.args = raw.lower().split()
        for i in range(len(self.args)):
            if 'am' in self.args[i] or 'pm' in self.args[i]:
                if ':' in self.args[i] or ':' in self.args[i - 1]:
                    break
                elif self.args[i][0].isdigit():
                    temp = ''
                    is_modified = False
                    for char in self.args[i]:
                        if is_modified or char.isdigit():
                            temp += char
                        else:
                            temp += ':00' + char
                            is_modified = True
                    self.args[i] = temp
                else:
                    self.args[i - 1] = self.args[i - 1] + ':00'
            if '!' in self.args[i]:
                break
        for i in range(len(self.args)):
            if self.clock != '' or not self.parse_clock(i):
                self.parse_date(self.args[i])
            if '!' in self.args[i]:
                break
        self.parse_finish()

    def get_time(self):
        if self.asap:
            return None
        else:
            return self.dt

    def parse_clock(self, index: int):
        raw = self.args[index]
        i = raw.find(':')
        if i < 1:
            military_time = ''
            for c in raw:
                if c.isdigit():
                    military_time += c
                elif military_time != '':
                    break
            if len(military_time) == 4 or len(military_time) == 3:
                h = int(military_time[:-2])
                m = int(military_time[-2:])
                if h < 24 and m < 60 and '202' not in military_time:
                    self.clock = raw
                    self.hour = h
                    self.minute = m
        elif raw[i - 1].isnumeric() and raw[i + 1:i + 2].isnumeric():
            self.clock = raw
            self.minute = int(raw[i + 1:i + 3])
            if i - 2 >= 0 and raw[i - 2].isnumeric():
                self.hour = int(raw[i - 2:i])
            else:
                self.hour = int(raw[i - 1])
        if self.clock == '':
            return False
        raw = ''
        alpha = ''
        num = ''
        for s in self.args[index:index + 3]:
            raw += s + ' '
        for c in raw:
            if self.zone is None:
                if c.isalpha():
                    alpha += c
                elif alpha == 'am' and self.hour == 12:
                    self.hour = 0
                    alpha = ''
                elif alpha == 'pm' and self.hour != 12:
                    self.hour += 12
                    alpha = ''
                elif alpha in time_info.zones:
                    self.zone = time_info.zones[alpha]
                    alpha = ''
                else:
                    alpha = ''
            if self.zone is not None:
                if c == '+' or c == '-':
                    alpha = c
                elif c.isdigit():
                    num += c
                elif num != '':
                    break
        if num != '':
            extra = int(num)
            if extra > 100:
                extra /= 100
            if 0 <= extra <= 24:
                if alpha == '-':
                    self.zone -= extra
                elif alpha == '+':
                    self.zone += extra
        return True

    def parse_date(self, raw: str):
        alphas = ['']
        nums = ['0']
        for c in raw:
            if (c == '+' or c == '-') and nums[0] == '0':
                return
            if c.isalpha():
                alphas[-1] += c
            elif alphas[-1] != '':
                alphas.append('')
            if c.isdigit():
                nums[-1] += c
            elif nums[-1] != '0':
                nums.append('0')
        for s in alphas:
            if self.weekday is None and s in time_info.weekdays:
                self.weekday = time_info.weekdays[s]
                break
            if self.month is None and s in time_info.months:
                self.month = time_info.months[s]
                break

        if self.day is None or self.month is None:
            for s in nums:
                n = int(s)
                if 13 <= n <= 31:
                    if self.month is None and self.day is not None \
                            and 1 <= self.day <= 12:
                        self.month = self.day
                        self.day = n
                    elif self.day is None:
                        self.day = n
                elif self.day is None and 1 <= n <= 31:
                    self.day = n
                elif self.month is None and 1 <= n <= 12:
                    self.month = n

    def parse_finish(self):
        if self.day is None and self.weekday is None and self.clock == '':
            self.asap = True
        if self.zone is None:
            self.zone = 0
        tz = datetime.timezone(datetime.timedelta(hours=self.zone))
        now = datetime.datetime.now(tz)
        if self.day is None:
            if self.weekday is None:
                self.day = now.day
            elif self.weekday == -1:
                self.day = (now + datetime.timedelta(days=1)).day
                self.month = (now + datetime.timedelta(days=1)).month
            else:
                days = (self.weekday - now.weekday()) % 7
                self.day = (now + datetime.timedelta(days=days)).day
                self.month = (now + datetime.timedelta(days=days)).month
        if self.month is None:
            self.month = now.month
        if self.clock == '':
            self.hour = now.hour
            self.minute = now.minute
        self.dt = datetime.datetime(
            year=now.year, month=self.month, day=self.day, hour=self.hour,
            minute=self.minute, tzinfo=tz)
        if (now - self.dt).days > 100:
            self.dt = self.dt.replace(year=self.dt.year + 1)

    def __str__(self):
        result = 'month: ' + str(self.month) + '\n'
        result += 'day: ' + str(self.day) + '\n'
        result += 'weekday: ' + str(self.weekday) + '\n'
        result += 'hour: ' + str(self.hour) + '\n'
        result += 'minute: ' + str(self.minute) + '\n'
        result += 'zone: ' + str(self.zone) + '\n'
        return result
