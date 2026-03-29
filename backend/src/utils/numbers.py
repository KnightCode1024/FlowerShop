def get_percent(number, percent) -> float:
    return round(
        number - number * (percent / 100), 2
    )
