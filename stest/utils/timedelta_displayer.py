#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/23 16:02:25
'''
import datetime


class TimeDeltaDisplayer(datetime.timedelta):
    def human_readable(self, lang="cn"):

        if lang == "cn":
            mm, ss = divmod(self.seconds, 60)
            hh, mm = divmod(mm, 60)

            # s = "%d:%02d:%02d" % (hh, mm, ss)
            if ss > 9:
                s = "%02d" % ss
            else:
                s = "%d" % ss
            if mm > 0:
                mf = "%02d分" if mm > 9 else "%d分"
                s = (mf % mm) + s
            if hh > 0:
                s = ("%d小时" % hh) + s

            if self.days:
                s = ("%d 天, " % self.days) + s
            if self.microseconds:
                s = s + ".%06d" % self.microseconds
            s = s + "秒"
        else:
            s = str(self)
        return s
