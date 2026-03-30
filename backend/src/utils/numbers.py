def get_percent(number, percent) -> float:
    return round(
        number - float(number) * (float(percent) / 100), 2
    )
