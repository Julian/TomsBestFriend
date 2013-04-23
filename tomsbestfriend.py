import datetime

from parsley import makeGrammar as make_grammar


__version__ = "0.1.0-dev"


class Duplicated(Exception):
    """
    A key group was duplicated, or contained a duplicate value.

    """

    @classmethod
    def in_group(cls, key, key_group=None):
        group_str = "the document" if key_group is None else repr(key_group)
        return cls("%r already appears in %s." % (key, group_str))


toml_grammar = r"""
document = key_group*:groups -> document(groups)
key_group = (header_line:header value_line*:values | (-> []):header value_line+:values) ignore -> header, values
header_line = ignore '[' key_name:name ']' line_end -> name
key_name = key_segment:first ('.' key_segment)*:rest -> [first] + rest
key_segment = <(~('[' | ']' | '.') anything)+>
value_line = ~header_line ignore name:k ws '=' ws value:v line_end -> (k, v)
name = <(~(space | '=' | nl) anything)+>
value = string | datetime | float | integer | boolean | array
array = '[' ignore elements:members ignore ']' -> members
elements = (value:first (ignore ',' ignore value)*:rest ','? -> [first] + rest) | -> []
string = '"' (escape_char | ~('"' | '\\') anything)*:c '"' -> ''.join(c).decode("utf-8")
escape_char = '\\' (('0' -> '\0')
                   |('b' -> '\b')
                   |('t' -> '\t')
                   |('n' -> '\n')
                   |('f' -> '\f')
                   |('r' -> '\r')
                   |('"' -> '"')
                   |('\\' -> '\\')
                   |('/' -> '/')
                   |escape_unichar)
escape_unichar = 'u' <hexdigit{4}>:hs -> unichr(int(hs, 16)).encode("utf-8")
integer = ('-' | -> ''):sign digit1_9:first <digit*>:rest -> int(sign + first + rest)
float = integer:whole '.' <digit+>:frac -> float(str(whole) + "." + frac)
boolean = ('true' | 'false')
datetime = (digit1_9:first digit{3}:rest -> "".join([first] + rest)):year '-'
            digit{2}:month '-'
            digit{2}:day 'T'
            digit{2}:hour ':'
            digit{2}:minute ':'
            digit{2}:second
            (('.' digit+) | -> 0):microsecond
            'Z' -> datetime(
                year=int("".join(year)),
                month=int("".join(month)),
                day=int("".join(day)),
                hour=int("".join(hour)),
                minute=int("".join(minute)),
                second=int("".join(second)),
            )
line_end = ws comment? nl
ignore = (comment | space | nl)*
comment = '#' (~'\n' anything)*
ws = space*
space = ' ' | '\t'
nl = '\r\n' | '\r' | '\n'
digit1_9 = :x ?(x in '123456789') -> x
hexdigit = :x ?(x in '0123456789abcdefABCDEF') -> x
"""


def document(groups):
    doc = dict()
    for header, values in sorted(groups):
        key_group, subgroup = doc, None

        if header:
            path, key = header[:-1], header[-1]
            for subgroup in path:
                key_group = key_group.setdefault(subgroup, {})

            if key in key_group:
                raise Duplicated.in_group(key, subgroup)

            key_group[key] = key_group = {}

        for key, value in values:
            if key in key_group:
                raise Duplicated.in_group(key, subgroup)
            key_group[key] = value

    return doc


TOMLParser = make_grammar(
    toml_grammar, {"document" : document, "datetime" : datetime.datetime},
)


def loads(toml):
    """
    Load some ``TOML`` from a string.

    """

    return TOMLParser(toml).document()
