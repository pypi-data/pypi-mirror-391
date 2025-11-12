from molad.helper import MoladHelper
from molad.helper import MoladDetails
from molad.helper import Molad
from molad.helper import RoshChodesh
import datetime
import pytest

molads = [
    (
        'Regular Year',
        datetime.datetime(2023, 2, 15),
        MoladDetails(
            molad=Molad(
                friendly="Monday, 12:40 pm and 11 chalakim",
                day="Monday",
                hours=12,
                minutes=40,
                chalakim=11,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Adar",
                days=["Tuesday", "Wednesday"],
                gdays=[datetime.date(2023, 2, 21), datetime.date(2023, 2, 22)],
                text="Tuesday & Wednesday",
            )
        )
    ),
    (
        'Leap Year Before Adar',
        datetime.datetime(2023, 11, 11),
        MoladDetails(
            molad=Molad(
                friendly="Monday, 7:17 am and 2 chalakim",
                day="Monday",
                hours=7,
                minutes=17,
                chalakim=2,
                am_or_pm="am"
            ),
            is_shabbos_mevorchim=True,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Kislev",
                days=["Tuesday"],
                gdays=[datetime.date(2023, 11, 14)],
                text="Tuesday",
            )
        )
    ),
    (
        'Leap Year After Adar',
        datetime.datetime(2024, 5, 6),
        MoladDetails(
            molad=Molad(
                friendly="Wednesday, 11:41 am and 8 chalakim",
                day="Wednesday",
                hours=11,
                minutes=41,
                chalakim=8,
                am_or_pm="am"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=False,
            rosh_chodesh=RoshChodesh(
                month="Iyar",
                days=["Wednesday", "Thursday"],
                gdays=[datetime.date(2024, 5, 8), datetime.date(2024, 5, 9)],
                text="Wednesday & Thursday",
            )
        )
    ),
    (
        'Leap Year During Shevat',
        datetime.datetime(2024, 2, 2),
        MoladDetails(
            molad=Molad(
                friendly="Friday, 9:29 pm and 5 chalakim",
                day="Friday",
                hours=9,
                minutes=29,
                chalakim=5,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Adar I",
                days=["Friday", "Shabbos"],
                gdays=[datetime.date(2024, 2, 9), datetime.date(2024, 2, 10)],
                text="Friday & Shabbos",
            )
        )
    ),
    (
        'Leap Year During Adar 1',
        datetime.datetime(2024, 3, 4),
        MoladDetails(
            molad=Molad(
                friendly="Sunday, 10:13 am and 6 chalakim",
                day="Sunday",
                hours=10,
                minutes=13,
                chalakim=6,
                am_or_pm="am"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Adar II",
                days=["Sunday", "Monday"],
                gdays=[datetime.date(2024, 3, 10), datetime.date(2024, 3, 11)],
                text="Sunday & Monday",
            )
        )
    ),
    (
        'Leap Year During Adar 2',
        datetime.datetime(2024, 4, 4),
        MoladDetails(
            molad=Molad(
                friendly="Monday, 10:57 pm and 7 chalakim",
                day="Monday",
                hours=10,
                minutes=57,
                chalakim=7,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Nissan",
                days=["Tuesday"],
                gdays=[datetime.date(2024, 4, 9)],
                text="Tuesday",
            )
        )
    ),
    (
        'Far Past Year',
        datetime.datetime(1823, 3, 7),
        MoladDetails(
            molad=Molad(
                friendly="Wednesday, 8:51 am and 4 chalakim",
                day="Wednesday",
                hours=8,
                minutes=51,
                chalakim=4,
                am_or_pm="am"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Nissan",
                days=["Thursday"],
                gdays=[datetime.date(1823, 3, 13)],
                text="Thursday",
            )
        )
    ),
    (
        'Far Future Year',
        datetime.datetime(2122, 12, 26),
        MoladDetails(
            molad=Molad(
                friendly="Monday, 7:29 pm and 4 chalakim",
                day="Monday",
                hours=7,
                minutes=29,
                chalakim=4,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=True,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Tevet",
                days=["Tuesday", "Wednesday"],
                gdays=[datetime.date(2122, 12, 29), datetime.date(2122, 12, 30)],
                text="Tuesday & Wednesday",
            )
        )
    ),
    (
    'Two Day Rosh Chodesh Friday and Shabbos - Shabbos Mevorchim - Friday Before Sunset',
        datetime.datetime(2023, 4, 14, 11),
        MoladDetails(
            molad=Molad(
                friendly="Thursday, 2:08 pm and 13 chalakim",
                day="Thursday",
                hours=2,
                minutes=8,
                chalakim=13,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Iyar",
                days=["Friday", "Shabbos"],
                gdays=[datetime.date(2023, 4, 21), datetime.date(2023, 4, 22)],
                text="Friday & Shabbos",
            )
        )
    ),
    (
    'Two Day Rosh Chodesh Friday and Shabbos - Shabbos Mevorchim - Friday After Sunset',
        datetime.datetime(2023, 4, 14, 23),
        MoladDetails(
            molad=Molad(
                friendly="Thursday, 2:08 pm and 13 chalakim",
                day="Thursday",
                hours=2,
                minutes=8,
                chalakim=13,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=True,
            is_upcoming_shabbos_mevorchim=True,
            rosh_chodesh=RoshChodesh(
                month="Iyar",
                days=["Friday", "Shabbos"],
                gdays=[datetime.date(2023, 4, 21), datetime.date(2023, 4, 22)],
                text="Friday & Shabbos",
            )
        )
    ),
    (
    'Two Day Rosh Chodesh Friday and Shabbos - Friday Before Sunset',
        datetime.datetime(2023, 4, 21, 11),
        MoladDetails(
            molad=Molad(
                friendly="Thursday, 2:08 pm and 13 chalakim",
                day="Thursday",
                hours=2,
                minutes=8,
                chalakim=13,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=False,
            rosh_chodesh=RoshChodesh(
                month="Iyar",
                days=["Friday", "Shabbos"],
                gdays=[datetime.date(2023, 4, 21), datetime.date(2023, 4, 22)],
                text="Friday & Shabbos",
            )
        )
    ),
    (
    'Two Day Rosh Chodesh Friday and Shabbos - Friday After Sunset',
        datetime.datetime(2023, 4, 21, 23),
        MoladDetails(
            molad=Molad(
                friendly="Thursday, 2:08 pm and 13 chalakim",
                day="Thursday",
                hours=2,
                minutes=8,
                chalakim=13,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=False,
            rosh_chodesh=RoshChodesh(
                month="Iyar",
                days=["Friday", "Shabbos"],
                gdays=[datetime.date(2023, 4, 21), datetime.date(2023, 4, 22)],
                text="Friday & Shabbos",
            )
        )
    ),
    (
        'Shabbos Leading into Yom Tov',
        datetime.datetime(2025, 4, 6),
        MoladDetails(
            molad=Molad(
                friendly="Sunday, 8:30 pm and 2 chalakim",
                day="Sunday",
                hours=8,
                minutes=30,
                chalakim=2,
                am_or_pm="pm"
            ),
            is_shabbos_mevorchim=False,
            is_upcoming_shabbos_mevorchim=False,
            rosh_chodesh=RoshChodesh(
                month="Iyar",
                days=["Monday", "Tuesday"],
                gdays=[datetime.date(2025, 4, 28), datetime.date(2025, 4, 29)],
                text="Monday & Tuesday",
            )
        )
    ),
]

@pytest.mark.parametrize('name,date,expected', molads)
def test_molad(name, date, expected):
    calculated = get_molad(date)

    assert calculated.molad.friendly == expected.molad.friendly
    assert calculated.molad.day == expected.molad.day
    assert calculated.molad.hours == expected.molad.hours
    assert calculated.molad.minutes == expected.molad.minutes
    assert calculated.molad.chalakim == expected.molad.chalakim
    assert calculated.molad.am_or_pm == expected.molad.am_or_pm
    assert calculated.is_shabbos_mevorchim == expected.is_shabbos_mevorchim
    assert calculated.is_upcoming_shabbos_mevorchim == expected.is_upcoming_shabbos_mevorchim
    assert calculated.rosh_chodesh.month == expected.rosh_chodesh.month
    assert calculated.rosh_chodesh.days == expected.rosh_chodesh.days
    assert calculated.rosh_chodesh.gdays == expected.rosh_chodesh.gdays
    assert calculated.rosh_chodesh.text == expected.rosh_chodesh.text

class Config:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.time_zone = 'Asia/Jerusalem'

def get_molad(d) -> MoladDetails:
    config = Config()
    mh = MoladHelper(config)   
    return mh.get_molad(d)
