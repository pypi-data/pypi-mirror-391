import datetime
import math
import hdate
from hdate import Location, Months, HebrewDate

class Molad:
    def __init__(self, day, hours, minutes, am_or_pm, chalakim, friendly):
        self.day = day
        self.hours = hours
        self.minutes = minutes
        self.am_or_pm = am_or_pm
        self.chalakim = chalakim
        self.friendly = friendly

class RoshChodesh:
    def __init__(self, month, text, days, gdays=None):
        self.month = month
        self.text = text
        self.days = days
        self.gdays = gdays

class MoladDetails:
    def __init__(self, molad: Molad, is_shabbos_mevorchim : bool, is_upcoming_shabbos_mevorchim : bool, rosh_chodesh: RoshChodesh):
        self.molad = molad
        self.is_shabbos_mevorchim = is_shabbos_mevorchim
        self.is_upcoming_shabbos_mevorchim = is_upcoming_shabbos_mevorchim
        self.rosh_chodesh = rosh_chodesh

class MoladHelper:
    # Month numbering: TISHREI=1, MARCHESHVAN=2, KISLEV=3, TEVET=4, SHVAT=5,
    #                  ADAR=6, ADAR_I=7, ADAR_II=8, NISAN=9, IYYAR=10, SIVAN=11, 
    #                  TAMMUZ=12, AV=13, ELUL=14

    config = None

    def __init__(self, config):
        self.config = config
    
    def _get_molad_month_index(self, hdate_month, is_leap):
        """Convert hdate month to molad calculation index (0-based from Tishrei).
        
        Molad calculations count months from Tishrei:
        Non-leap: Tishrei=0, Cheshvan=1, Kislev=2, Tevet=3, Shevat=4, Adar=5,
                  Nisan=6, Iyar=7, Sivan=8, Tammuz=9, Av=10, Elul=11
        Leap:     Tishrei=0, Cheshvan=1, Kislev=2, Tevet=3, Shevat=4, Adar I=5, Adar II=6,
                  Nisan=7, Iyar=8, Sivan=9, Tammuz=10, Av=11, Elul=12
        """
        if hdate_month <= 5:  # TISHREI(1) through SHVAT(5)
            return hdate_month - 1
        elif hdate_month == 6:  # ADAR (non-leap year)
            return 5
        elif hdate_month == 7:  # ADAR_I (leap year)
            return 5
        elif hdate_month == 8:  # ADAR_II (leap year)
            return 6
        else:  # NISAN(9) through ELUL(14)
            # In non-leap: NISAN=6, IYYAR=7, SIVAN=8, TAMMUZ=9, AV=10, ELUL=11
            # In leap: NISAN=7, IYYAR=8, SIVAN=9, TAMMUZ=10, AV=11, ELUL=12
            offset = 7 if is_leap else 6
            return hdate_month - 9 + offset

    def sumup(self, multipliers) -> Molad:
        shifts = [
            [2, 5, 204],  # starting point
            [2, 16, 595],  # 19-year cycle
            [4, 8, 876],  # regular year
            [5, 21, 589],  # leap year
            [1, 12, 793],  # month
        ]
        mults = []
        mults.append(multipliers)
        out00 = self.multiply_matrix(mults, shifts)  # --> 1x3 triplet
        out0 = out00[0]
        out1 = self.carry_and_reduce(out0)  # now need to reduce by carrying
        out2 = self.convert_to_english(out1)  # convert to English date/time
        return out2

    def multiply_matrix(self, matrix1, matrix2):
        res = [[0 for x in range(5)] for y in range(5)]

        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                for k in range(len(matrix2)):

                    # resulted matrix
                    res[i][j] += matrix1[i][k] * matrix2[k][j]

        return res

    def carry_and_reduce(
        self, out0
    ):  # carry properly triple for the molad calculations
        # 7 days/week, 24 hours/day, 1080 chalakim/hours/day
        # we don't have to worry about the weeks.
        xx = out0[2]
        yy = xx % 1080
        zz = math.floor(xx / 1080)
        # chalakim
        if yy < 0:
            yy = yy + 1080
            z = zz - 1
            # carry up

        out1 = [0, 0, 0]
        out1[2] = yy
        xx = out0[1] + zz
        yy = xx % 24
        zz = math.floor(xx / 24)
        # hours
        if yy < 0:
            yy = yy + 24
            zz = zz - 1

        out1[1] = yy
        xx = out0[0] + zz
        yy = (xx + 6) % 7 + 1
        zz = math.floor(xx / 7)
        # days removing weeks - keep Shabbos=7
        if yy < 0:
            yy = yy + 7
        out1[0] = yy
        return out1

    def convert_to_english(self, out1) -> Molad:  # convert triple to English time
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Shabbos",
        ]
        day = out1[0]
        hours = out1[1]
        # hours are measured from 6 pm of the day before
        chalakim = out1[2]
        # 1080/hour, 18/minute, 3+1/3 seconds
        hours = hours - 6
        if hours < 0:
            day = day - 1
            hours = hours + 24
            # evening of previous day

        daynm = days[day - 1]
        pm = "am"

        if hours >= 12:
            pm = "pm"
            hours = hours - 12

        minutes = math.floor(chalakim / 18)
        chalakim = chalakim % 18
        # left over
        leng = len(str(minutes))
        filler = "0" if (leng == 1) else ""
        # like the 0 in 3:01
        hours = 12 if (hours == 0) else hours

        friendly = (
            str(daynm)
            + ", "
            + str(hours)
            + ":"
            + str(filler)
            + str(minutes)
            + " "
            + str(pm)
            + " and "
            + str(chalakim)
            + " chalakim"
        )

        return Molad(
            day = daynm,
            hours = hours,
            minutes = minutes,
            am_or_pm = pm,
            chalakim =  chalakim,
            friendly = friendly,
        )

    def get_actual_molad(self, date) -> Molad:
        """Calculate the molad for the next month."""
        next_month_data = self.get_next_month(date)
        year = next_month_data["year"]
        month = next_month_data["month"]  # hdate month value

        guachadazat = [3, 6, 8, 11, 14, 17, 19]
        cycles = math.floor(year / 19)  # 19-year cycles
        yrs = year % 19  # leftover years
        isleap = yrs in guachadazat  # is this year a leap year?

        molad_month = self._get_molad_month_index(month, isleap)

        regular = 0
        leap = 0

        for ii in range(yrs - 1):  # for years _prior_ to this one
            if (ii + 1) in guachadazat:
                leap = leap + 1
            else:
                regular = regular + 1

        multipliers = [1, cycles, regular, leap, molad_month]

        return self.sumup(multipliers)

    def get_hebrew_date(self, date):
        """Convert Gregorian date to Hebrew date information."""
        h = HebrewDate.from_gdate(date)
        return {
            "year": h.year,
            "month": h.month.value,
            "day": h.day,
        }

    def get_next_month(self, date):
        """Get the next Hebrew month."""
        h = HebrewDate.from_gdate(date)
        year = h.year
        month = h.month.value
        
        if month == 14:  # ELUL -> TISHREI of next year
            month = 1
            year = year + 1
        elif month == 6:  # ADAR (non-leap year) -> NISAN
            month = 9
        elif month == 5:  # SHVAT
            # Check if THIS year is a leap year to determine next month
            is_leap = HebrewDate(year, 1, 1).is_leap_year()
            # In leap year: SHVAT -> ADAR_I
            # In non-leap: SHVAT -> ADAR
            month = 7 if is_leap else 6
        else:
            month = month + 1

        return {"year": year, "month": month}

    def get_gdate(self, hebrew_date_dict, day):
        """Convert Hebrew date to Gregorian date."""
        month = hebrew_date_dict["month"]
        year = hebrew_date_dict["year"]
        
        # Validate day is within month's range
        temp_date = HebrewDate(year, month, 1)
        max_days = temp_date.days_in_month(Months(month))
        actual_day = min(day, max_days)
        
        hebrew_date = HebrewDate(year, month, actual_day)
        return hebrew_date.to_gdate()

    def get_day_of_week(self, gdate):
        weekday = gdate.strftime("%A")

        if weekday == "Saturday":
            weekday = "Shabbos"

        return weekday

    def get_rosh_chodesh_days(self, date) -> RoshChodesh:
        """Calculate Rosh Chodesh days for the upcoming month."""
        this_month = self.get_hebrew_date(date)
        next_month = self.get_next_month(date)

        # Format month name for display
        next_month_name = self._format_month_name(next_month["month"])

        # no Rosh Chodesh Tishrei
        if next_month["month"] == 1:
            return RoshChodesh(
                month = next_month_name,
                text = "",
                days = [],
                gdays = [],
            )

        # Check if current month has 30 days (determines if Rosh Chodesh is 1 or 2 days)
        temp_date = HebrewDate(this_month["year"], this_month["month"], 1)
        days_in_current_month = temp_date.days_in_month(Months(this_month["month"]))
        
        gdate_second = self.get_gdate(next_month, 1)
        second = self.get_day_of_week(gdate_second)

        if days_in_current_month == 30:
            # Two-day Rosh Chodesh
            gdate_first = self.get_gdate(this_month, 30)
            first = self.get_day_of_week(gdate_first)
            return RoshChodesh(
                month=next_month_name,
                text=first + " & " + second,
                days=[first, second],
                gdays=[gdate_first, gdate_second],
            )
        else:
            # One-day Rosh Chodesh
            return RoshChodesh(
                month=next_month_name,
                text=second,
                days=[second],
                gdays=[gdate_second],
            )
    
    def _format_month_name(self, month_value):
        """Format month name from Months enum value for display."""
        month_enum = Months(month_value)
        month_name = month_enum.name.replace('_', ' ').title()
        
        # Apply special formatting rules
        month_name = month_name.replace(' Ii', ' II')
        
        # Handle specific month name conversions
        name_mapping = {
            'Marcheshvan': 'Cheshvan',
            'Shvat': 'Shevat',
            'Iyyar': 'Iyar',
            'Nisan': 'Nissan',
        }
        
        return name_mapping.get(month_name, month_name)

    def get_shabbos_mevorchim_english_date(self, date):
        this_month = self.get_hebrew_date(date)
        gdate = self.get_gdate(this_month, 30)

        idx = (gdate.weekday() + 1) % 7
        sat_date = gdate - datetime.timedelta(7+idx-6)

        return sat_date
    
    def get_shabbos_mevorchim_hebrew_day_of_month(self, date):
        gdate = self.get_shabbos_mevorchim_english_date(date)
        h = HebrewDate.from_gdate(gdate)
        return h.day
    
    def is_shabbos_mevorchim(self, date) -> bool:
        """Check if the given date/time is Shabbos Mevorchim."""
        loc = self.get_current_location()
        date_only = date.date() if isinstance(date, datetime.datetime) else date
        
        # Get Hebrew date and adjust for sunset
        h = HebrewDate.from_gdate(date_only)
        hd = h.day
        is_shabbat = hdate.HDateInfo(date=date_only, diaspora=loc.diaspora).is_shabbat
        
        z = hdate.Zmanim(date=date_only, location=loc)
        # Make date timezone-aware for comparison
        tz = loc.timezone
        date_aware = date.replace(tzinfo=tz) if date.tzinfo is None else date
        
        if date_aware > z.shkia.local:
            hd += 1
            # Check if tomorrow is Shabbat
            tomorrow = date_only + datetime.timedelta(days=1)
            is_shabbat = hdate.HDateInfo(date=tomorrow, diaspora=loc.diaspora).is_shabbat

        sm = self.get_shabbos_mevorchim_hebrew_day_of_month(date)
        
        return is_shabbat and hd == sm and h.month != Months.ELUL
    
    def is_upcoming_shabbos_mevorchim(self, date) -> bool:
        weekday_sunday_as_zero = (date.weekday() + 1) % 7
        upcoming_saturday =  date - datetime.timedelta(days=weekday_sunday_as_zero) + datetime.timedelta(days=6)
        upcoming_saturday_at_midnight = datetime.datetime.combine(upcoming_saturday, datetime.datetime.min.time())

        return self.is_shabbos_mevorchim(upcoming_saturday_at_midnight)

    def get_current_location(self) -> Location:
        return Location(
            latitude=self.config.latitude,
            longitude=self.config.longitude,
            timezone=self.config.time_zone,
            diaspora=True,
        )

    def get_molad(self, date) -> MoladDetails:
        molad = self.get_actual_molad(date)
        is_shabbos_mevorchim = self.is_shabbos_mevorchim(date)
        is_upcoming_shabbos_mevorchim = self.is_upcoming_shabbos_mevorchim(date)
        rosh_chodesh = self.get_rosh_chodesh_days(date)

        return MoladDetails(molad, is_shabbos_mevorchim, is_upcoming_shabbos_mevorchim, rosh_chodesh)