import os

import utime


def format_date(dt: int) -> str:
    """
    Converts a unix timestamp to a string like "1 Jan 12:34\"
    :param dt: the unix timestamp
    :return: the formatted string
    """
    dtup = utime.localtime(dt)
    formatted: str
    if dtup[1] == 1:
        formatted = "Jan"
    elif dtup[1] == 2:
        formatted = "Feb"
    elif dtup[1] == 3:
        formatted = "Mar"
    elif dtup[1] == 4:
        formatted = "Apr"
    elif dtup[1] == 5:
        formatted = "May"
    elif dtup[1] == 6:
        formatted = "Jun"
    elif dtup[1] == 7:
        formatted = "Jul"
    elif dtup[1] == 8:
        formatted = "Aug"
    elif dtup[1] == 9:
        formatted = "Sep"
    elif dtup[1] == 10:
        formatted = "Oct"
    elif dtup[1] == 11:
        formatted = "Nov"
    elif dtup[1] == 12:
        formatted = "Dec"
    else:
        formatted = "???"

    return f"{dtup[2]} {formatted} {dtup[3]:02d}:{dtup[4]:02d}"


def wrap_text(text: str, max_length: int) -> list[str]:
    """
    Wraps the given text to the given maximum width, respecting word boundaries.
    If a word is too long to fit on a line, it will be hyphenated.
    :param text: the text to wrap
    :param max_length: the maximum length in characters
    :return: list of wrapped lines
    """
    if max_length < 2:
        print(f"wrap_text: max_width too small, returning as-is")
        return [text]

    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        # Check if adding this word would exceed max_width
        test_line = word if not current_line else current_line + " " + word

        if len(test_line) <= max_length:
            current_line = test_line
        else:
            # Word doesn't fit on current line
            if current_line:
                # Save current line and start new one
                lines.append(current_line)
                current_line = ""

            # Handle word that's too long for a single line
            if len(word) > max_length:
                # Break word with hyphenation
                while len(word) > max_length:
                    # Reserve one character for hyphen
                    chunk_size = max_length - 1
                    chunk = word[:chunk_size] + "-"
                    lines.append(chunk)
                    word = word[chunk_size:]
                current_line = word
            else:
                current_line = word

    # Add any remaining text
    if current_line:
        lines.append(current_line)

    return lines if lines else [""]


def sentence_join(inputs: list[str]) -> str:
    """
    Joins the given list of strings into a sentence, using commas and an 'and' as appropriate
    :param inputs: the list of strings
    :return: the sentence
    """
    if len(inputs) == 0:
        return ""
    elif len(inputs) == 1:
        return inputs[0]
    elif len(inputs) == 2:
        return f"{inputs[0]} and {inputs[1]}"
    else:
        return f"{', '.join(inputs[:-1])}, and {inputs[-1]}"


def ensure_suffix(to_check: str, suffix: str) -> str:
    """
    Ensures that the input ends with the given suffix.
    :param to_check: the string to check
    :param suffix: the suffix
    :return: the suffixed string
    """
    if to_check[-1] == suffix:
        return to_check
    else:
        return to_check + suffix


def truncate_lines(lines: list[str], max_lines: int) -> list[str]:
    """
    Truncates the given list of lines to the given maximum number of lines.
    :param lines: the lines
    :param max_lines: the maximum number of lines
    :return: the truncated lines
    """
    if len(lines) <= max_lines:
        return lines
    else:
        lines = lines[0:max_lines]
        lines[-1] = lines[-1][0:-3].strip() + "..."
        return lines


def dir_exists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) != 0
    except OSError:
        return False


def file_exists(filename):
    try:
        return (os.stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False
