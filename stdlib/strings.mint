#mode light

fn capitalize(s):
    if s == "":
        return s
    return upper(substring(s, 0, 1)) + substring(s, 1)

fn lines(s):
    return split(s, "\n")

fn unlines(list):
    return join(list, "\n")

fn strip(s):
    return trim(s)

fn pad_left(s, len, char):
    result = s
    while len(result) < len:
        result = char + result
    return result

fn pad_right(s, len, char):
    result = s
    while len(result) < len:
        result = result + char
    return result

fn count(s, substr):
    result = 0
    i = 0
    while i <= len(s) - len(substr):
        if substring(s, i, i + len(substr)) == substr:
            result = result + 1
        i = i + 1
    return result
