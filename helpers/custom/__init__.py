import re


def matches_as_entities(pattern, text, type, **kwargs):
    return [dict(
        end_char=m.end(0),
        start_char=m.start(0),
        text=text[m.start(0):m.end(0)],
        type=type
    ) for m in re.finditer(pattern, text, **kwargs)]
