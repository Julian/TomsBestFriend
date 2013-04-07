from parsley import makeGrammar as make_grammar


__version__ = "0.1.0-dev"


toml_grammar = r"""
document = key_group*:groups -> document(groups)
key_group = header_line?:header value_line+:values ignore -> (header, values)
header_line = ignore '[' key_name ']' line_end
key_name = key_segment ("." key_segment)*
key_segment = (~('[' | ']' | '.') anything)+
value_line = ignore name:k ws "=" ws value:v line_end -> (k, v)
name = <(~space anything)+>
value = string | datetime | float | integer | boolean | array
array = (empty_array |
         string_array |
         datetime_array |
         float_array |
         integer_array |
         boolean_array |
         array_array)
string = '"' ('\\' escape_char | ~'"' anything)*:c '"' -> ''.join(c)
escape_char = '0' | 't' | 'n' | 'r' | '"' | '\\'
integer = ('-' | -> ''):sign digit1_9:first <digit*>:rest -> int(sign + first + rest)
float = integer:whole '.' <digit+>:frac -> whole + float("." + frac)
boolean = ('true' | 'false')
datetime = (digit1_9 digit digit digit):year '-'
            (digit digit):month '-'
            (digit digit):day 'T'
            (digit digit):hour ':'
            (digit digit):minute ':'
            (digit digit):second
            ('.' digit+)?:fraction
            'Z'
empty_array = '[' ws ']'
string_array = '[' ws string:head   :tail(ws ',' ws string:value)*   ws ']'
integer_array = '[' ws integer:head  :tail(ws ',' ws integer:value)*  ws ']'
float_array = '[' ws float:head    :tail(ws ',' ws float:value)*    ws ']'
boolean_array = '[' ws boolean:head  :tail(ws ',' ws boolean:value)*  ws ']'
datetime_array = '[' ws datetime:head :tail(ws ',' ws datetime:value)* ws ']'
array_array = '[' ws array:head    :tail(ws ',' ws array:value)*    ws ']'
line_end = ws comment? nl
ignore = (comment | space | nl)*
comment = '#' (~'\n' anything)*
ws = space*
space = ' ' | '\t'
nl = '\r\n' | '\r' | '\n'
digit1_9 = :x ?(x in '123456789') -> x
"""


def document(groups):
    doc = dict(groups)
    doc.update(doc.pop(None, {}))
    return doc


TOMLParser = make_grammar(toml_grammar, {"document" : document})
