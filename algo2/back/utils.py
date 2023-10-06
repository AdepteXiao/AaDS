def duration_from_seconds(seconds: float) -> str:
    """
    представление времени трека в виде мин:сек
    :param seconds: длительность трека в секундах
    :return: длительность в виде мин:сек
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours != 0:
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return f"{int(minutes):02}:{int(seconds):02}"


def duration_from_ms(ms):
    """
    представление длительности трека в виде мин:сек
    :param ms: милисекунды трека
    :return: длительность в виде мин:сек
    """
    return duration_from_seconds(ms / 1000)
