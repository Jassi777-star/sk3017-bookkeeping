from datetime import date, datetime


def parse_month(value):
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m")
    except ValueError:
        return None
    return date(parsed.year, parsed.month, 1)


def month_bounds(month_start):
    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(month_start.year, month_start.month + 1, 1)
    return month_start, next_month


def shift_month(month_start, offset):
    month_index = month_start.year * 12 + month_start.month - 1 + offset
    year, month_zero = divmod(month_index, 12)
    return date(year, month_zero + 1, 1)


def recent_months(end_month, count):
    return [shift_month(end_month, offset) for offset in range(1 - count, 1)]
