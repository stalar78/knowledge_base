"""
Timestamp formatting utilities.
"""


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS string.

    Handles durations longer than 24 hours correctly.

    Args:
        seconds: Non-negative floating-point number.

    Returns:
        String in HH:MM:SS format, where HH can be > 23.

    Examples:
        >>> format_timestamp(0)
        '00:00:00'
        >>> format_timestamp(65)
        '00:01:05'
        >>> format_timestamp(3661)
        '01:01:01'
        >>> format_timestamp(100000)
        '27:46:40'
    """
    if seconds < 0:
        raise ValueError("seconds must be non-negative")
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

