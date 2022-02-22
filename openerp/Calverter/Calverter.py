#!/usr/bin/env python
# #   Calverter.py  (2007/07/01)
##
##   Copyright (C) 2007 Mehdi Bayazee (Bayazee@Gmail.com)
##   Edited by Saeed Rasooli <saeed.gnu@gmail.com> (ilius) at 2009
##
##   Iranian (Jalali) calendar: 
##           http://en.wikipedia.org/wiki/Iranian_calendar
##   Islamic (Hijri) calendar:
##           http://en.wikipedia.org/wiki/Islamic_calendar
##   Gregorian calendar:
##           http://en.wikipedia.org/wiki/Gregorian_calendar
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 3, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.


import math, os, sys, time
from datetime import datetime
from dateutil.relativedelta import relativedelta


def my_raise():
    i = sys.exc_info()
    print('line %s: %s: %s' % (i[2].tb_lineno, i[0].__name__, i[1]))


useDB = True

DATE_GREG = 0
DATE_JALALI = 1
DATE_HIJRI = 2
DATE_JD = 4

minMonthLen = {DATE_GREG: 29, DATE_JALALI: 29, DATE_HIJRI: 29}
maxMonthLen = {DATE_GREG: 31, DATE_JALALI: 31, DATE_HIJRI: 30}

J0000 = 1721424.5  # Julian date of Gregorian epoch: 0000-01-01
J1970 = 2440587.5  # Julian date at Unix epoch: 1970-01-01
JMJD = 2400000.5  # Epoch of Modified Julian Date system
J1900 = 2415020.5  # Epoch (day 1) of Excel 1900 date system (PC)
J1904 = 2416480.5  # Epoch (day 0) of Excel 1904 date system (Mac)

NormLeap = ("Normal year", "Leap year")

GREGORIAN_EPOCH = 1721425.5
GREGORIAN_WEEKDAYS = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

HIJRI_EPOCH = 1948439.5;
HIJRI_WEEKDAYS = ("al-ahad", "al-'ithnayn", "ath-thalatha'", "al-arbia`aa'", "al-khamis", "al-jumu`a", "as-sabt")

JALALI_EPOCH = 1948320.5;
JALALI_WEEKDAYS = ("Yekshanbeh", "Doshanbeh", "Seshhanbeh", "Chaharshanbeh", "Panjshanbeh", "Jomeh", "Shanbeh")

#hijriDbInitH = (1427,2,20) ; hijriDbInitJD = 2453815
#hijriDbInitDates = ((2006,3,21), (1385,1,1), (1427,2,20)) ## not important
#hijriDbInitH = (1427,2,1) ; hijriDbInitJD = 2453796
hijriDbInitH = (1426, 2, 1);
hijriDbInitJD = 2453441
hijriMonthLenY = {
    1426: (00, 29, 30, 29, 30, 30, 30, 30, 29, 30, 29, 29),
    1427: (30, 29, 29, 30, 29, 30, 30, 30, 30, 29, 29, 30),
    1428: (29, 30, 29, 29, 29, 30, 30, 29, 30, 30, 30, 29),
    1429: (30, 29, 30, 29, 29, 29, 30, 30, 29, 30, 30, 29),
    1430: (30, 30, 29, 29, 30, 29, 30, 29, 29, 30, 30, 29),
    1431: (30, 30, 29)}

hijriMonthLen = {}
hijriDbEndJD = hijriDbInitJD
for y in hijriMonthLenY.keys():
    lst = hijriMonthLenY[y]
    for m in range(len(lst)):
        ml = lst[m]
        if ml != 0:
            hijriMonthLen[y * 12 + m] = ml
            hijriDbEndJD += ml


class Calverter:
    def jwday(j):
        "JWDAY: Calculate day of week from Julian day"
        return int(math.floor((j + 1.5))) % 7

    def weekday_before(self, weekday, jd):
        """WEEKDAY_BEFORE: Return Julian date of given weekday (0 = Sunday)
                           in the seven days ending on jd."""
        return jd - self.jwday(jd - weekday)


    def search_weekday(self, weekday, jd, direction, offset):
        """SEARCH_WEEKDAY: Determine the Julian date for:

                               weekday      Day of week desired, 0 = Sunday
                               jd           Julian date to begin search
                               direction    1 = next weekday, -1 = last weekday
                               offset       Offset from jd to begin search"""

        return self.weekday_before(weekday, jd + (direction * offset))

    #  Utility weekday functions, just wrappers for search_weekday

    def nearest_weekday(self, weekday, jd):
        return self.search_weekday(weekday, jd, 1, 3)

    def next_weekday(self, weekday, jd):
        return self.search_weekday(weekday, jd, 1, 7)

    def next_or_current_weekday(self, weekday, jd):
        return self.search_weekday(weekday, jd, 1, 6)

    def previous_weekday(self, weekday, jd):
        return self.search_weekday(weekday, jd, -1, 1)

    def previous_or_current_weekday(self, weekday, jd):
        return self.search_weekday(weekday, jd, 1, 0)


    def TestSomething(self):
        pass

    def leap_gregorian(self, year):
        "LEAP_GREGORIAN: Is a given year in the Gregorian calendar a leap year ?"
        return ((year % 4) == 0) and (not (((year % 100) == 0) and ((year % 400) != 0)))

    def gregorian_to_jd(self, year, month, day):
        "GREGORIAN_TO_JD: Determine Julian day number from Gregorian calendar date"

        # Python <= 2.5
        if month <= 2:
            tm = 0
        elif self.leap_gregorian(year):
            tm = -1
        else:
            tm = -2

        # Python 2.5
        #tm = 0 if month <= 2 else (-1 if self.leap_gregorian(year) else -2)

        return (GREGORIAN_EPOCH - 1) + (365 * (year - 1)) + math.floor((year - 1) / 4) + (
        -math.floor((year - 1) / 100)) + \
               math.floor((year - 1) / 400) + math.floor((((367 * month) - 362) / 12) + tm + day)


    def jd_to_gregorian(self, jd):
        "JD_TO_GREGORIAN: Calculate Gregorian calendar date from Julian day"

        wjd = math.floor(jd - 0.5) + 0.5
        depoch = wjd - GREGORIAN_EPOCH
        quadricent = math.floor(depoch / 146097)
        dqc = depoch % 146097
        cent = math.floor(dqc / 36524)
        dcent = dqc % 36524
        quad = math.floor(dcent / 1461)
        dquad = dcent % 1461
        yindex = math.floor(dquad / 365)
        year = int((quadricent * 400) + (cent * 100) + (quad * 4) + yindex)
        if not ((cent == 4) or (yindex == 4)):
            year += 1

        yearday = wjd - self.gregorian_to_jd(year, 1, 1)

        # Python <= 2.5
        if wjd < self.gregorian_to_jd(year, 3, 1):
            leapadj = 0
        elif self.leap_gregorian(year):
            leapadj = 1
        else:
            leapadj = 2

        # Python 2.5
        # leapadj = 0 if wjd < self.gregorian_to_jd(year, 3, 1) else (1 if self.leap_gregorian(year) else 2)

        month = int(math.floor((((yearday + leapadj) * 12) + 373) / 367))
        day = int(wjd - self.gregorian_to_jd(year, month, 1)) + 1

        return year, month, day

    def n_weeks(self, weekday, jd, nthweek):

        j = 7 * nthweek
        if nthweek > 0:
            j += self.previous_weekday(weekday, jd)
        else:
            j += next_weekday(weekday, jd)
        return j

    def iso_to_julian(self, year, week, day):
        "ISO_TO_JULIAN: Return Julian day of given ISO year, week, and day"
        return day + self.n_weeks(0, self.gregorian_to_jd(year - 1, 12, 28), week)

    def jd_to_iso(self, jd):
        "JD_TO_ISO: Return array of ISO (year, week, day) for Julian day"
        year = self.jd_to_gregorian(jd - 3)[0]
        if jd >= self.iso_to_julian(year + 1, 1, 1):
            year += 1

        week = int(math.floor((jd - self.iso_to_julian(year, 1, 1)) / 7) + 1)
        day = self.jwday(jd)
        if day == 0:
            day = 7

        return year, week, day

    def iso_day_to_julian(self, year, day):
        "ISO_DAY_TO_JULIAN: Return Julian day of given ISO year, and day of year"
        return (day - 1) + self.gregorian_to_jd(year, 1, 1)

    def jd_to_iso_day(self, jd):
        "JD_TO_ISO_DAY: Return array of ISO (year, day_of_year) for Julian day"
        year = self.jd_to_gregorian(jd)[0]
        day = int(math.floor(jd - self.gregorian_to_jd(year, 1, 1))) + 1
        return year, day

    def pad(self, Str, howlong, padwith):
        "PAD: Pad a string to a given length with a given fill character. "
        s = str(Str)

        while s.length < howlong:
            s = padwith + s
        return s

    def leap_hijri(self, year):
        "LEAP_HIJRI: Is a given year a leap year in the Islamic calendar ?"
        return (((year * 11) + 14) % 30) < 11

    def hijri_to_jd(self, year, month, day):
        "HIJRI_TO_JD: Determine Julian day from Islamic date"
        return (day + \
                math.ceil(29.5 * (month - 1)) + \
                (year - 1) * 354 + \
                math.floor((3 + (11 * year)) / 30) + \
                HIJRI_EPOCH) - 1

    def jd_to_hijri(self, jd, useDB=useDB):
        "JD_TO_HIJRI: Calculate Islamic date from Julian day"
        if useDB:
            jd = int(jd)
            if hijriDbEndJD > jd >= hijriDbInitJD:
                # (yi, mi, di) = hijriDbInitH
                # ymi = yi*12 + mi
                (y, m, d) = hijriDbInitH
                ym = y * 12 + m - 1
                while jd > hijriDbInitJD:
                    monthLen = hijriMonthLen[ym]
                    if jd - monthLen > hijriDbInitJD:
                        ym += 1
                        jd -= monthLen
                    elif d + jd - hijriDbInitJD > monthLen:
                        ym += 1
                        d = d + jd - hijriDbInitJD - monthLen
                        jd = hijriDbInitJD
                    else:
                        d = d + jd - hijriDbInitJD
                        jd = hijriDbInitJD
                (y, m) = divmod(ym, 12)
                m += 1
                return (y, m, d)
        jd = math.floor(jd) + 0.5
        year = int(math.floor(((30 * (jd - HIJRI_EPOCH)) + 10646) / 10631))
        month = int(min(12, math.ceil((jd - (29 + self.hijri_to_jd(year, 1, 1))) / 29.5) + 1))
        day = int(jd - self.hijri_to_jd(year, month, 1)) + 1;
        return year, month, day

    def leap_jalali(self, year):
        "LEAP_jalali: Is a given year a leap year in the Jalali calendar ?"

        # Python <= 2.5
        if year > 0:
            rm = 474
        else:
            rm = 473

        # Python 2.5
        # return ((((((year - 474 if year > 0 else 473 ) % 2820) + 474) + 38) * 682) % 2816) < 682

        return ((((((year - rm) % 2820) + 474) + 38) * 682) % 2816) < 682

    def jalali_to_jd(self, year, month, day):
        "JALALI_TO_JD: Determine Julian day from Jalali date"
        # Python <= 2.5
        if year >= 0:
            rm = 474
        else:
            rm = 473
        epbase = year - (rm)

        # Python 2.5
        # epbase = year - 474 if year>=0 else 473
        epyear = 474 + (epbase % 2820)

        if month <= 7:
            mm = (month - 1) * 31
        else:
            mm = ((month - 1) * 30) + 6

        return day + mm + \
               math.floor(((epyear * 682) - 110) / 2816) + \
               (epyear - 1) * 365 + \
               math.floor(epbase / 2820) * 1029983 + \
               (JALALI_EPOCH - 1)

    def jd_to_jalali(self, jd):
        "JD_TO_JALALI: Calculate Jalali date from Julian day"

        jd = math.floor(jd) + 0.5
        depoch = jd - self.jalali_to_jd(475, 1, 1)
        cycle = math.floor(depoch / 1029983)
        cyear = depoch % 1029983
        if cyear == 1029982:
            ycycle = 2820
        else:
            aux1 = math.floor(cyear / 366)
            aux2 = cyear % 366
            ycycle = math.floor(((2134 * aux1) + (2816 * aux2) + 2815) / 1028522) + aux1 + 1

        year = int(ycycle + (2820 * cycle) + 474)
        if year <= 0:
            year -= 1

        yday = (jd - self.jalali_to_jd(year, 1, 1)) + 1
        if yday <= 186:
            month = int(math.ceil(yday / 31))
        else:
            month = int(math.ceil((yday - 6) / 30))

        day = int(jd - self.jalali_to_jd(year, month, 1)) + 1
        return year, month, day

    def jd_to(self, jd, target, hijriAlg=0, hijriUseDB=True):
        ## hijriAlg:  0:Calvertor,  1:idate,  2:idate_umm_alqura
        if target == DATE_GREG:
            date = self.jd_to_gregorian(jd)
        elif target == DATE_JALALI:
            date = self.jd_to_jalali(jd)
        elif target == DATE_HIJRI:
            if hijriAlg == 0:
                date = self.jd_to_hijri(jd, useDB=hijriUseDB)
            elif hijriAlg == 1:
                date = self.jd_to_hijri_idate(jd, umm_alqura=False)
            elif hijriAlg == 2:
                date = self.jd_to_hijri_idate(jd, umm_alqura=True)
            else:
                raise ValueError('invalid hijriAlg=%s passed to function jd_to' % hijriAlg)
        else:
            raise ValueError, 'invalid target date mode: %s' % target
        return date

    def to_jd(self, y, m, d, source):
        if source == DATE_GREG:
            jd = self.gregorian_to_jd(y, m, d)
        elif source == DATE_JALALI:
            jd = self.jalali_to_jd(y, m, d)
        elif source == DATE_HIJRI:
            jd = self.hijri_to_jd(y, m, d)
        else:
            raise ValueError, 'invalid source date mode: %s' % source
        return jd

    def convert(self, y, m, d, source=DATE_GREG, target=DATE_JALALI, *args, **kwargs):
        jd = self.to_jd(y, m, d, source)
        return self.jd_to(jd, target, *args, **kwargs)
        """
        if source==DATE_GREG:
          jd = self.gregorian_to_jd(y, m, d)
        elif source==DATE_JALALI:
          jd = self.jalali_to_jd(y, m, d)
        elif source==DATE_HIJRI:
          jd = self.hijri_to_jd(y, m, d)
        else:
          raise ValueError, 'invalid source date mode: %s'%source
        if target==DATE_GREG:
          date = self.jd_to_gregorian(jd)
        elif target==DATE_JALALI:
          date = self.jd_to_jalali(jd)
        elif target==DATE_HIJRI:
          date = self.jd_to_hijri(jd)
        else:
          raise ValueError, 'invalid target date mode: %s'%source
        return date
        """

    def jd_to_hijri_idate(self, jd, umm_alqura=False):
        (y, m, d) = self.jd_to_gregorian(jd)
        fixed = str(y).zfill(4) + str(m).zfill(2) + str(d).zfill(2)
        cmd = 'idate --gregorian %s' % fixed
        if umm_alqura:
            cmd += ' --umm_alqura'
        output = os.popen(cmd).read()
        try:
            (hd, hm, hy) = output.split('\n')[3].split(':')[1].split('/')
            hy = hy.split(' ')[0]
        except:
            my_raise()
            raise OSError('command "idate" not found')
        return (int(hy), int(hm), int(hd))

    def test_with_idate(self):
        jd_today = int(self.gregorian_to_jd(*time.localtime()[:3]))
        for jd in range(jd_today - 400, jd_today + 10):
            greg = self.jd_to_gregorian(jd)
            hijri = self.jd_to_hijri(jd)
            hijri2 = self.jd_to_hijri_idate(jd)
            if hijri != hijri2:
                print greg, hijri, hijri2

    def last_dayof_month_jalali(self, year, month):
        if (month > 0 and month < 7):
            return 31
        elif (month < 12):
            return 30
        elif (month == 12):
            if (self.leap_jalali(year)):
                return 30
            else:
                return 29
        raise ValueError('invalid month=%d passed to function last_dayof_month_jalali' % month)

    def first_last_dayof_month_jalali(self, gregoriandate, addmonth=1):
        jalalidate = self.jd_to_jalali(
            self.gregorian_to_jd(int(gregoriandate.strftime('%Y')), int(gregoriandate.strftime('%m')),
                                 int(gregoriandate.strftime('%d'))))
        firstdate = self.jd_to_gregorian(self.jalali_to_jd(jalalidate[0], jalalidate[1], 1))
        if (addmonth > 1):
            gregoriandate += relativedelta(months=addmonth - 1)
            jalalidate = self.jd_to_jalali(
                self.gregorian_to_jd(int(gregoriandate.strftime('%Y')), int(gregoriandate.strftime('%m')),
                                     int(gregoriandate.strftime('%d'))))
        lastdate = self.jd_to_gregorian(
            self.jalali_to_jd(jalalidate[0], jalalidate[1], self.last_dayof_month_jalali(jalalidate[0], jalalidate[1])))
        return [datetime(*firstdate[0:3]), datetime(*lastdate[0:3])]


    # ---------- developed by  Nahal ------------------------------

    def get_first_dayof_month_gregorian(self, gregoriandate):
        day = gregoriandate.day
        return gregoriandate + datetime(days=-day + 1)

    def get_first_dayof_month_jalali(self, gregoriandate):

        jalalidate =  self.get_persian_date(gregoriandate)
        year = jalalidate.split('/')[0]
        month = jalalidate.split('/')[1]
        persiandate = []
        persiandate.append(year)
        persiandate.append(month)
        persiandate.append(1)
        return  self.get_gregorian_date(persiandate)

    def get_last_dayof_month_jalali(self, gregoriandate):

        jalalidate = self.get_persian_date(gregoriandate)
        year = jalalidate.split('/')[0]
        month = jalalidate.split('/')[1]
        persiandate = []
        persiandate.append(year)
        persiandate.append(month)
        day = 30

        if month < '7':
            day = 31
        else:
            isleapyear = self.leap_jalali(year)
            if isleapyear:
                day = 29
            else :
                day = 30

        persiandate.append(day)
        return self.get_gregorian_date(persiandate)


    def get_persian_date(self   , gregoriandate ):
        if gregoriandate:
            if len(gregoriandate) > 10:
                gregoriandate = gregoriandate.split(" ")[0]
            year, month, day = gregoriandate.split("-")
            jd = self.to_jd(int(year), int(month), int(day), 0)
            jyear, jmonth, jday =  self.jd_to_jalali(jd)
            jdate = "%s/%s/%s" % (jyear, jmonth, jday)
            return jdate
        else:
            return None

    def get_gregorian_date(self , persiandate):
        if len(persiandate) == 1:
            date = persiandate[0]
            if type(date) is str:
                m = persiandate.match(r'^(\d{4})\D(\d{1,2})\D(\d{1,2})$', date)
                if m:
                    [year, month, day] = [int(m.group(1)), int(m.group(2)), int(m.group(3))]
                else:
                    raise Exception("Invalid Input String")
            elif type(date) is tuple:
                year, month, day = date
                year = int(year)
                month = int(month)
                day = int(day)
            else:
                raise Exception("Invalid Input Type")
        elif len(persiandate) == 3:
            year = int(persiandate[0])
            month = int(persiandate[1])
            day = int(persiandate[2])
        else:
            raise Exception("Invalid Input")

            # Check validity of date. TODO better check (leap years)
        if year < 1 or month < 1 or month > 12 or day < 1 or day > 31 or (month > 6 and day == 31):
            raise Exception("Incorrect Date")


        # Convert date
        d_4 = (year + 1) % 4
        if month < 7:
            doy_j = ((month - 1) * 31) + day
        else:
            doy_j = ((month - 7) * 30) + day + 186
        d_33 = int(((year - 55) % 132) * .0305)
        a = 287 if (d_33 != 3 and d_4 <= d_33) else 286
        if (d_33 == 1 or d_33 == 2) and (d_33 == d_4 or d_4 == 1):
            b = 78
        else:
            b = 80 if (d_33 == 3 and d_4 == 0) else 79
        if int((year - 19) / 63) == 20:
            a -= 1
            b += 1
        if doy_j <= a:
            gy = year + 621
            gd = doy_j + b
        else:
            gy = year + 622
            gd = doy_j - a
        for gm, v in enumerate([0, 31, 29 if (gy % 4 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]):
            if gd <= v:
                break
            gd -= v
        gregoriandate = "%s/%s/%s" % (gy, gm, gd)
        return gregoriandate



if __name__ == '__main__':
    c = Calverter()
    # c.test_with_idate()
    """
    print hijriDbInitDates
    print
    for i in (0,1,2):
      (y,m,d) = hijriDbInitDates[i]
      jd = c.to_jd(y, m, d, i)
      print jd, c.jd_to_hijri(jd)
    print
    for i in (0, 1, 2):
      print c.jd_to(hijriDbInitJD, i)

    jdi = hijriDbInitJD
    for jd in range(jdi, jdi+1000):
      date1 = c.jd_to_hijri(jd, useDB=False)
      date2 = c.jd_to_hijri(jd, useDB=True)
      if date1!=date2:
        print date1, date2
    """
    arg = sys.argv
    if len(arg) < 3:
        sys.exit(0)
    if arg[1] == '-j':
        mode = DATE_JALALI
    elif arg[1] == '-g':
        mode = DATE_GREG
    elif arg[1] in ('-h', '-i'):
        mode = DATE_HIJRI
    elif arg[1] == '-jd':
        mode = DATE_JD
    else:
        sys.exit(1)
    if mode == DATE_JD:
        jd = int(arg[2])
    else:
        sp = arg[2].split('/')
        y = int(sp[0])
        m = int(sp[1])
        d = int(sp[2])
        jd = c.to_jd(y, m, d, mode)
    print 'Julian Day: %s' % jd
    print 'Gregorian:  ' + ('%2d/%2d/%2d' % c.jd_to(jd, DATE_GREG)).replace(' ', '0')
    print 'Jalali:     ' + ('%2d/%2d/%2d' % c.jd_to(jd, DATE_JALALI)).replace(' ', '0')
    print 'Hijri:      ' + ('%2d/%2d/%2d' % c.jd_to(jd, DATE_HIJRI)).replace(' ', '0')



