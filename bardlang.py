import re
import math
from lark import Lark, Transformer, UnexpectedInput

# ==========================================
# 1. BARDLANG GRAMMAR SPECIFICATION
# ==========================================

bardlang_grammar = r"""
    start: instruction+

    ?instruction: assignment
                | reassignment
                | print_statement
                | if_else
                | if_only
                | if_elif_else
                | if_elif_only
                | while_statement
                | for_statement
                | repeat_statement
                | unless_statement
                | func_def
                | func_call_stmt
                | return_statement
                | list_assignment
                | list_append
                | list_remove
                | list_sort
                | list_reverse
                | input_statement
                | break_statement
                | continue_statement
                | try_statement
                | raise_statement
                | class_def
                | method_call_stmt

    # ── variable declarations ───────────────────────────────────────────
    assignment: "Enter" IDENTIFIER ", a amount of" int_expr "."
              | "Enter" IDENTIFIER ", a numerical of" float_expr "."
              | "Enter" IDENTIFIER ", a scroll of" expr "."
              | "Enter" IDENTIFIER ", a banner of" bool_expr "."
              | "Enter" IDENTIFIER ", a roster of" "[" arg_list? "]" "." -> roster_assignment

    reassignment:    IDENTIFIER "becomes" expr "."
                   | IDENTIFIER "." IDENTIFIER "becomes" expr "."        -> attr_reassign

    print_statement: "Speak" (string | expr) "."

    # ── input ────────────────────────────────────────────────────────────
    input_statement: "Hearken" IDENTIFIER ", a amount of" string "."    -> input_int
                   | "Hearken" IDENTIFIER ", a numerical of" string "." -> input_float
                   | "Hearken" IDENTIFIER ", a scroll of" string "."    -> input_str

    # ── control flow ─────────────────────────────────────────────────────
    if_only:       "Hark!" "shouldst" condition "," "then" ":" then_block "Thus endeth the choice."
    if_else:       "Hark!" "shouldst" condition "," "then" ":" then_block "Alas," "else" ":" else_block "Thus endeth the choice."
    if_elif_only:  "Hark!" "shouldst" condition "," "then" ":" then_block elif_block+ "Thus endeth the choice."
    if_elif_else:  "Hark!" "shouldst" condition "," "then" ":" then_block elif_block+ "Alas," "else" ":" else_block "Thus endeth the choice."

    then_block:  instruction+
    else_block:  instruction+
    elif_block:  "Ponder!" "shouldst" condition "," "then" ":" instruction+

    break_statement:    "Cease."
    continue_statement: "Persist."

    COMMA: ","

    while_statement:  "While" condition COMMA "prithee" ":" instruction+ "Thus endeth the while."
    for_statement:    "For every" IDENTIFIER "from" expr "to" expr ":" instruction+ "Thus endeth the for."
                  |   "For every" IDENTIFIER "from" expr "to" expr "by" expr ":" instruction+ "Thus endeth the for." -> for_step_statement
    repeat_statement: "Repeat" expr "times" ":" instruction+ "Thus endeth the repeat."
    unless_statement: "Unless" condition COMMA "lest" ":" instruction+ "Thus endeth the unless."

    # ── error handling ───────────────────────────────────────────────────
    try_statement:   "Attempt" ":" try_block catch_clause "Thus endeth the attempt."
    try_block:       instruction+
    catch_clause:    "Should tragedy strike" ":" catch_block
                  |  "Should tragedy strike as" IDENTIFIER ":" catch_block -> catch_as
    catch_block:     instruction+
    raise_statement: "Forsooth" string "."

    # ── functions ────────────────────────────────────────────────────────
    func_def:         "A tale of" IDENTIFIER "(" param_list? ")" ":" instruction+ "Thus endeth the tale."
    func_call_stmt:   "Invoke" IDENTIFIER "(" arg_list? ")" "."
    return_statement: "Return henceforth" expr "."

    # ── lists (statements) ───────────────────────────────────────────────
    list_assignment: "Behold" IDENTIFIER ", a roster of" "[" arg_list? "]" "."
    list_append:     "Add" expr "unto" IDENTIFIER "."
    list_remove:     "Remove" expr "from" IDENTIFIER "."
    list_sort:       "Arrange" IDENTIFIER "."
    list_reverse:    "Invert" IDENTIFIER "."

    # ── class system ─────────────────────────────────────────────────────
    class_def: "A chronicle of" IDENTIFIER ":" class_body "Thus endeth the chronicle."
             | "A chronicle of" IDENTIFIER "begets" IDENTIFIER ":" class_body "Thus endeth the chronicle." -> class_inherit

    class_body: class_member+
    class_member: method_def | attr_decl

    attr_decl:   "Inscribe" IDENTIFIER "as" expr "."

    method_def: "A tale of" IDENTIFIER "(" param_list? ")" ":" instruction+ "Thus endeth the tale."

    method_call_stmt: IDENTIFIER "." IDENTIFIER "(" arg_list? ")" "."

    # ── parameters / arguments ───────────────────────────────────────────
    param_list: IDENTIFIER ("," IDENTIFIER)*
    arg_list:   expr ("," expr)*

    # ── typed wrappers ────────────────────────────────────────────────────
    int_expr:   expr
    float_expr: expr
    bool_expr:  TRUE_KW  -> true_val
             |  FALSE_KW -> false_val

    # ── conditions ────────────────────────────────────────────────────────
    ?condition: expr                                -> bare_expr
              | expr "doth equal" expr             -> eq
              | expr "doth not equal" expr         -> neq
              | expr "is greater than" expr        -> gt
              | expr "is lesser than" expr         -> lt
              | expr "is no less than" expr        -> gte
              | expr "is no more than" expr        -> lte
              | expr "is naught"                   -> is_none
              | expr "is not naught"               -> is_not_none
              | expr "contains" expr               -> contains
              | expr "lacks" expr                  -> lacks
              | expr "scroll" expr "holds" expr    -> scroll_holds
              | condition "and also" condition     -> and_cond
              | condition "or perchance" condition -> or_cond
              | "not" condition                    -> not_cond

    # ── expressions ───────────────────────────────────────────────────────
    ?expr: or_expr
         | "cast" expr "to amount"                          -> cast_int
         | "cast" expr "to numerical"                       -> cast_float
         | "cast" expr "to scroll"                          -> cast_str
         | expr "or else" expr                              -> default_of
         | "uppercase of" expr                              -> str_upper
         | "lowercase of" expr                              -> str_lower
         | "trimmed of" expr                                -> str_strip
         | "length of" expr                                 -> length_of
         | "joined" expr "with" expr                        -> str_join
         | "absolute of" expr                               -> abs_of
         | "root of" expr                                   -> sqrt_of
         | "floor of" expr                                  -> floor_of
         | "ceiling of" expr                                -> ceil_of
         | "rounded of" expr                                -> round_of
         | expr "raised to" expr                            -> pow_of
         | "lesser between" expr "and" expr                 -> min_of
         | "greater between" expr "and" expr                -> max_of
         | "split" expr "by" expr                           -> str_split
         | "replace" expr "with" expr "in" expr             -> str_replace
         | "excerpt" expr "from" expr "to" expr             -> str_slice
         | "echo" expr "times" expr                         -> str_repeat
         | "tally of" expr                                  -> list_sum
         | "position of" expr "in" expr                     -> list_index_of
         | "tally occurrences of" expr "in" expr            -> list_count
         | "weave" expr "with" expr                         -> list_join
         | "Conjure" IDENTIFIER "(" arg_list? ")"           -> obj_create

    ?or_expr:  and_expr | or_expr "or" and_expr   -> bor
    ?and_expr: add_expr | and_expr "and" add_expr -> band
    ?add_expr: mul_expr
             | add_expr "plus" mul_expr           -> add
             | add_expr "minus" mul_expr          -> sub
    ?mul_expr: unary_expr
             | mul_expr "times" unary_expr        -> mul
             | mul_expr "divided by" unary_expr   -> div
             | mul_expr "modulo" unary_expr       -> mod
    ?unary_expr: factor | "nay" factor            -> neg
    ?factor: atom | func_call_expr

    ?atom: NUMBER        -> number
         | FLOAT         -> float_num
         | string        -> string_val
         | IDENTIFIER    -> var
         | TRUE_KW       -> true_val
         | FALSE_KW      -> false_val
         | NAUGHT_KW     -> none_val
         | "(" expr ")"
         | list_index
         | method_call_expr
         | attr_access

    list_index:     IDENTIFIER "[" expr "]"
    func_call_expr: IDENTIFIER "(" arg_list? ")"
    method_call_expr: IDENTIFIER "." IDENTIFIER "(" arg_list? ")"
    attr_access: IDENTIFIER "." IDENTIFIER
    string:         ESCAPED_STRING

    TRUE_KW.2:  "true"
    FALSE_KW.2: "false"
    NAUGHT_KW.2: "naught"

    %import common.ESCAPED_STRING
    %import common.INT   -> NUMBER
    %import common.FLOAT
    %import common.CNAME -> IDENTIFIER
    %import common.WS
    %ignore WS
"""

parser = Lark(bardlang_grammar, parser='earley', lexer='dynamic_complete', ambiguity='resolve')

INDENT = "    "


# ==========================================
# 2. BARD TO PYTHON COMPILER TRANSFORMER
# ==========================================
class BardToPython(Transformer):

    def _indent(self, lines):
        flat_lines = []
        for item in lines:
            flat_lines.extend(str(item).splitlines())
        return "\n".join(INDENT + l for l in flat_lines if l.strip())

    def _block(self, items):
        return [str(i) for i in items if str(i).strip()]

    def start(self, items):
        return "\n".join(str(i) for i in items if str(i).strip())

    # ── typed wrappers ────────────────────────────────────────────────────
    def int_expr(self, items):   return f"int({items[0]})"
    def float_expr(self, items): return f"float({items[0]})"

    # ── assignments ───────────────────────────────────────────────────────
    def assignment(self, items):
        return f"{items[0]} = {items[1]}"

    def roster_assignment(self, items):
        name  = str(items[0])
        elems = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name} = [{elems}]"

    def obj_assign(self, items):
        varname   = str(items[0])
        classname = str(items[1])
        args      = str(items[2]) if len(items) > 2 and items[2] is not None else ""
        return f"{varname} = {classname}({args})"

    def reassignment(self, items):
        return f"{items[0]} = {items[1]}"

    def attr_reassign(self, items):
        return f"{items[0]}.{items[1]} = {items[2]}"

    # ── output ────────────────────────────────────────────────────────────
    def print_statement(self, items):
        return f"print({items[0]})"

    # ── input ─────────────────────────────────────────────────────────────
    def input_int(self, items):
        return f"{items[0]} = int(input({items[1]}))"

    def input_float(self, items):
        return f"{items[0]} = float(input({items[1]}))"

    def input_str(self, items):
        return f"{items[0]} = input({items[1]})"

    # ── if / elif / else ──────────────────────────────────────────────────
    def then_block(self, items): return self._block(items)
    def else_block(self, items): return self._block(items)

    def elif_block(self, items):
        cond  = str(items[0])
        body  = self._block(items[1:])
        return f"elif {cond}:\n" + self._indent(body)

    def if_only(self, items):
        return f"if {items[0]}:\n" + self._indent(items[1])

    def if_else(self, items):
        code  = f"if {items[0]}:\n" + self._indent(items[1])
        code += f"\nelse:\n"        + self._indent(items[2])
        return code

    def if_elif_only(self, items):
        code = f"if {items[0]}:\n" + self._indent(items[1])
        for branch in items[2:]:
            code += f"\n{branch}"
        return code

    def if_elif_else(self, items):
        code = f"if {items[0]}:\n" + self._indent(items[1])
        for branch in items[2:-1]:
            code += f"\n{branch}"
        code += f"\nelse:\n" + self._indent(items[-1])
        return code

    # ── control flow ──────────────────────────────────────────────────────
    def break_statement(self, _):    return "break"
    def continue_statement(self, _): return "continue"

    # ── while / for ───────────────────────────────────────────────────────
    def while_statement(self, items):
        from lark import Token
        clean = [i for i in items if not (isinstance(i, Token) and i.type == "COMMA")]
        return f"while {clean[0]}:\n" + self._indent(self._block(clean[1:]))

    def for_statement(self, items):
        from lark import Token
        clean = [i for i in items if not (isinstance(i, Token) and i.type == "COMMA")]
        var, start, end = str(clean[0]), str(clean[1]), str(clean[2])
        return f"for {var} in range({start}, {end} + 1):\n" + self._indent(self._block(clean[3:]))

    def for_step_statement(self, items):
        var, start, end, step = str(items[0]), str(items[1]), str(items[2]), str(items[3])
        body = self._block(items[4:])
        return (
            f"for {var} in _bard_range({start}, {end}, {step}):\n"
            + self._indent(body)
        )

    def repeat_statement(self, items):
        times = str(items[0])
        body = self._block(items[1:])
        return f"for _bard_repeat in range(int({times})):\n" + self._indent(body)

    def unless_statement(self, items):
        from lark import Token
        items = [i for i in items if not (isinstance(i, Token) and i.type == "COMMA")]
        condition = str(items[0])
        body = self._block(items[1:])
        return f"if not ({condition}):\n" + self._indent(body)

    # ── error handling ────────────────────────────────────────────────────
    def try_block(self, items):   return self._block(items)
    def catch_block(self, items): return self._block(items)

    def catch_clause(self, items):
        return (None, items[0])

    def catch_as(self, items):
        return (str(items[0]), items[1])

    def try_statement(self, items):
        err_name, catch_body = items[1]
        if err_name:
            catch_body = [f"{err_name} = str(_bard_err)"] + catch_body
        code  = "try:\n"    + self._indent(items[0])
        code += "\nexcept Exception as _bard_err:\n" + self._indent(catch_body)
        return code

    def raise_statement(self, items):
        return f"raise Exception({items[0]})"

    # ── functions ─────────────────────────────────────────────────────────
    def func_def(self, items):
        name = str(items[0])
        if len(items) > 1 and isinstance(items[1], list):
            params = ", ".join(items[1])
            body   = self._block(items[2:])
        else:
            params = ""
            body   = self._block(items[1:])
        if not body:
            body = ["pass"]
        return f"def {name}({params}):\n" + self._indent(body)

    def param_list(self, items):  return [str(i) for i in items]

    def func_call_stmt(self, items):
        name = str(items[0])
        args = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        if name == "primal":
            # primal(self, ...) -> super().__init__(remaining args after self)
            arg_list = [a.strip() for a in args.split(",")]
            rest = ", ".join(arg_list[1:]) if len(arg_list) > 1 else ""
            return f"super().__init__({rest})"
        return f"{name}({args})"

    def func_call_expr(self, items):
        name = str(items[0])
        args = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name}({args})"

    def return_statement(self, items): return f"return {items[0]}"
    def arg_list(self, items): return ", ".join(str(i) for i in items)

    # ── lists (statements) ────────────────────────────────────────────────
    def list_assignment(self, items):
        name  = str(items[0])
        elems = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name} = [{elems}]"

    def list_append(self, items): return f"{items[1]}.append({items[0]})"
    def list_remove(self, items): return f"{items[1]}.remove({items[0]})"
    def list_index(self, items):  return f"{items[0]}[{items[1]}]"
    def list_sort(self, items):   return f"{items[0]}.sort()"
    def list_reverse(self, items):return f"{items[0]}.reverse()"

    # ── class system ──────────────────────────────────────────────────────
    def class_body(self, items):  return items
    def class_member(self, items):return items[0]

    def attr_decl(self, items):
        return f"{items[0]} = {items[1]}"

    def method_def(self, items):
        name = str(items[0])
        if len(items) > 1 and isinstance(items[1], list):
            raw_params = items[1]
            body       = self._block(items[2:])
        else:
            raw_params = []
            body       = self._block(items[1:])
        # always inject 'self' as first param if not already present
        if not raw_params or raw_params[0] != "self":
            raw_params = ["self"] + raw_params
        # map 'enact' -> '__init__', 'primal' -> super().__init__
        if name == "enact":
            name = "__init__"
        if not body:
            body = ["pass"]
        return f"def {name}({', '.join(raw_params)}):\n" + self._indent(body)

    def class_def(self, items):
        name    = str(items[0])
        members = items[1]
        body    = "\n".join(
            INDENT + line
            for m in members
            for line in str(m).splitlines()
            if line.strip()
        )
        if not body.strip():
            body = INDENT + "pass"
        return f"class {name}:\n{body}"

    def class_inherit(self, items):
        child   = str(items[0])
        parent  = str(items[1])
        members = items[2]
        body    = "\n".join(
            INDENT + line
            for m in members
            for line in str(m).splitlines()
            if line.strip()
        )
        if not body.strip():
            body = INDENT + "pass"
        return f"class {child}({parent}):\n{body}"

    def method_call_stmt(self, items):
        obj    = str(items[0])
        method = str(items[1])
        args   = str(items[2]) if len(items) > 2 and items[2] is not None else ""
        return f"{obj}.{method}({args})"

    def method_call_expr(self, items):
        obj    = str(items[0])
        method = str(items[1])
        args   = str(items[2]) if len(items) > 2 and items[2] is not None else ""
        return f"{obj}.{method}({args})"

    def attr_access(self, items):
        return f"{items[0]}.{items[1]}"

    def obj_create(self, items):
        classname = str(items[0])
        args      = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{classname}({args})"

    # ── conditions ────────────────────────────────────────────────────────
    def bare_expr(self, i):       return str(i[0])
    def eq(self, i):              return f"({i[0]} == {i[1]})"
    def neq(self, i):             return f"({i[0]} != {i[1]})"
    def gt(self, i):              return f"({i[0]} > {i[1]})"
    def lt(self, i):              return f"({i[0]} < {i[1]})"
    def gte(self, i):             return f"({i[0]} >= {i[1]})"
    def lte(self, i):             return f"({i[0]} <= {i[1]})"
    def is_none(self, i):         return f"({i[0]} is None)"
    def is_not_none(self, i):     return f"({i[0]} is not None)"
    def contains(self, i):        return f"({i[1]} in {i[0]})"
    def lacks(self, i):           return f"({i[1]} not in {i[0]})"
    def scroll_holds(self, i):    return f"({i[2]} in {i[1]})"
    def and_cond(self, i):        return f"({i[0]} and {i[1]})"
    def or_cond(self, i):         return f"({i[0]} or {i[1]})"
    def not_cond(self, i):        return f"(not {i[0]})"

    # ── arithmetic expressions ─────────────────────────────────────────────
    def add(self, i):        return f"({i[0]} + {i[1]})"
    def sub(self, i):        return f"({i[0]} - {i[1]})"
    def mul(self, i):        return f"({i[0]} * {i[1]})"
    def div(self, i):        return f"({i[0]} / {i[1]})"
    def mod(self, i):        return f"({i[0]} % {i[1]})"
    def neg(self, i):        return f"(-{i[0]})"
    def bor(self, i):        return f"({i[0]} | {i[1]})"
    def band(self, i):       return f"({i[0]} & {i[1]})"

    # ── type casts ────────────────────────────────────────────────────────
    def cast_int(self, i):   return f"int({i[0]})"
    def cast_float(self, i): return f"float({i[0]})"
    def cast_str(self, i):   return f"str({i[0]})"
    def default_of(self, i):
        return f"((lambda _bard_value: _bard_value if _bard_value is not None else {i[1]})({i[0]}))"

    # ── original string builtins ──────────────────────────────────────────
    def str_upper(self, i):  return f"({i[0]}).upper()"
    def str_lower(self, i):  return f"({i[0]}).lower()"
    def str_strip(self, i):  return f"({i[0]}).strip()"
    def length_of(self, i):  return f"len({i[0]})"
    def str_join(self, i):   return f"(str({i[0]}) + str({i[1]}))"

    # ── new math builtins ─────────────────────────────────────────────────
    def abs_of(self, i):     return f"abs({i[0]})"
    def sqrt_of(self, i):    return f"__import__('math').sqrt({i[0]})"
    def floor_of(self, i):   return f"__import__('math').floor({i[0]})"
    def ceil_of(self, i):    return f"__import__('math').ceil({i[0]})"
    def round_of(self, i):   return f"round({i[0]})"
    def pow_of(self, i):     return f"({i[0]} ** {i[1]})"
    def min_of(self, i):     return f"min({i[0]}, {i[1]})"
    def max_of(self, i):     return f"max({i[0]}, {i[1]})"

    # ── new string builtins ───────────────────────────────────────────────
    def str_split(self, i):   return f"({i[0]}).split({i[1]})"
    def str_replace(self, i): return f"({i[2]}).replace({i[0]}, {i[1]})"
    def str_slice(self, i):   return f"({i[0]})[int({i[1]}):int({i[2]})]"
    def str_repeat(self, i):  return f"({i[0]} * int({i[1]}))"

    # ── new roster / list builtins ────────────────────────────────────────
    def list_sum(self, i):      return f"sum({i[0]})"
    def list_index_of(self, i): return f"({i[1]}).index({i[0]})"
    def list_count(self, i):    return f"({i[1]}).count({i[0]})"
    def list_join(self, i):     return f"({i[1]}).join([str(_x) for _x in {i[0]}])"

    # ── atoms ─────────────────────────────────────────────────────────────
    def number(self, i):     return str(i[0])
    def float_num(self, i):  return str(i[0])
    def string_val(self, i): return str(i[0])
    def string(self, i):     return str(i[0])
    def var(self, i):        return str(i[0])
    def true_val(self, i):   return "True"
    def false_val(self, i):  return "False"
    def none_val(self, i):   return "None"


# ==========================================
# 3. INTERPRETER EXECUTION INTERFACE
# ==========================================

def _bard_range(start, end, step=1):
    start = int(start)
    end = int(end)
    step = int(step)
    if step == 0:
        raise ValueError("For every ... by cannot use a step of 0")
    stop = end + (1 if step > 0 else -1)
    return range(start, stop, step)


def compile_bard_code(source_code: str) -> str:
    source_code = re.sub(r'#[^\n]*', '', source_code)
    ast = parser.parse(source_code)
    return BardToPython().transform(ast)


def run_bard_code(source_code: str, verbose: bool = False):
    try:
        python_code = compile_bard_code(source_code)
        if verbose:
            print("=== Generated Python ===")
            print(python_code)
            print("========================\n")
        namespace = {"_bard_range": _bard_range}
        exec(python_code, namespace, namespace)
    except UnexpectedInput as e:
        print(f"A Syntax Tragedy Has Occurred near line {e.line}, column {e.column}:")
        print(e.get_context(source_code))
        raise
    except Exception as e:
        print(f"A Tragedy Has Occurred: {e}")
        raise


# ==========================================
# 4. Main — test suite covering all features
# ==========================================
if __name__ == "__main__":

    # ── Section I: original features (regression) ────────────────────────
    test_original = r"""
    # string methods
    Enter msg, a scroll of "  Hello World  ".
    Speak uppercase of trimmed of msg.
    Speak length of msg.

    # contains / lacks
    Enter nums, a roster of [1, 2, 3, 4, 5].
    Hark! shouldst nums contains 3 , then :
        Speak "3 is in the roster.".
    Thus endeth the choice.
    Hark! shouldst nums lacks 9 , then :
        Speak "9 is not in the roster.".
    Thus endeth the choice.

    # break / continue
    For every i from 1 to 10 :
        Hark! shouldst i doth equal 5 , then :
            Cease.
        Thus endeth the choice.
        Speak i.
    Thus endeth the for.

    For every j from 1 to 6 :
        Hark! shouldst j doth equal 3 , then :
            Persist.
        Thus endeth the choice.
        Speak j.
    Thus endeth the for.

    # cast
    Enter raw, a scroll of "42".
    Enter num, a amount of cast raw to amount.
    Speak num times 2.

    # try / catch / raise
    Attempt :
        Forsooth "deliberate tragedy".
    Should tragedy strike :
        Speak "Caught the tragedy safely.".
    Thus endeth the attempt.

    # joined strings
    Enter greeting, a scroll of "Hello".
    Enter target, a scroll of "Kharl".
    Speak joined greeting with joined ", " with target.
    """

    # ── Section II: ponder (elif) ─────────────────────────────────────────
    test_ponder = r"""
    Enter score, a amount of 72.

    Hark! shouldst score is no less than 90 , then :
        Speak "Excellent.".
    Ponder! shouldst score is no less than 75 , then :
        Speak "Passed.".
    Ponder! shouldst score is no less than 60 , then :
        Speak "Needs improvement.".
    Alas, else :
        Speak "Failed.".
    Thus endeth the choice.
    """

    # ── Section III: math builtins ────────────────────────────────────────
    test_math = r"""
    Enter x, a numerical of nay 9.7.
    Speak absolute of x.
    Speak root of 144.
    Speak floor of x.
    Speak ceiling of x.
    Speak rounded of x.
    Speak 2 raised to 10.
    Speak lesser between 4 and 9.
    Speak greater between 4 and 9.
    """

    # ── Section IV: string builtins ───────────────────────────────────────
    test_strings = r"""
    Enter sentence, a scroll of "the quick brown fox".
    Enter words, a roster of [].
    words becomes split sentence by " ".
    Speak words.
    Speak length of words.

    Enter w, a scroll of "hello".
    Speak replace "l" with "r" in w.
    Speak excerpt w from 1 to 3.
    Speak echo "ha" times 3.
    """

    # ── Section V: roster builtins ────────────────────────────────────────
    test_roster = r"""
    Enter scores, a roster of [5, 2, 9, 1, 7, 3].
    Arrange scores.
    Speak scores.

    Invert scores.
    Speak scores.

    Speak tally of scores.
    Speak position of 9 in scores.
    Speak tally occurrences of 3 in scores.

    Enter parts, a roster of ["alpha", "beta", "gamma"].
    Speak weave parts with " | ".
    """

    # ── Section VI: class system ──────────────────────────────────────────
    test_classes = r"""
    A chronicle of Animal :
        A tale of enact(self, name) :
            self.name becomes name.
        Thus endeth the tale.
        A tale of speak(self) :
            Speak "...".
        Thus endeth the tale.
    Thus endeth the chronicle.

    A chronicle of Dog begets Animal :
        A tale of enact(self, name) :
            Invoke primal(self, name).
        Thus endeth the tale.
        A tale of speak(self) :
            Speak "Woof!".
        Thus endeth the tale.
        A tale of fetch(self, item) :
            Speak joined "Fetching: " with item.
        Thus endeth the tale.
    Thus endeth the chronicle.

    Enter luna, a scroll of Conjure Animal("Luna").
    Enter buddy, a scroll of Conjure Dog("Buddy").
    luna.speak().
    buddy.speak().
    buddy.fetch("the scroll").
    """

    # Section VII: Bard-native conveniences
    test_bardic = r"""
    Enter missing, a scroll of naught or else "fallback".
    Speak missing.

    Repeat 3 times :
        Speak "chorus".
    Thus endeth the repeat.

    For every i from 5 to 1 by nay 2 :
        Speak i.
    Thus endeth the for.

    Enter ready, a banner of false.
    Unless ready , lest :
        Speak "not ready".
    Thus endeth the unless.

    Attempt :
        Forsooth "named tragedy".
    Should tragedy strike as sorrow :
        Speak joined "Caught: " with sorrow.
    Thus endeth the attempt.
    """

    print("=" * 50)
    print("SECTION I  — Original features")
    print("=" * 50)
    run_bard_code(test_original, verbose=False)

    print("\n" + "=" * 50)
    print("SECTION II — Ponder (elif)")
    print("=" * 50)
    run_bard_code(test_ponder, verbose=False)

    print("\n" + "=" * 50)
    print("SECTION III — Math builtins")
    print("=" * 50)
    run_bard_code(test_math, verbose=False)

    print("\n" + "=" * 50)
    print("SECTION IV — String builtins")
    print("=" * 50)
    run_bard_code(test_strings, verbose=False)

    print("\n" + "=" * 50)
    print("SECTION V  — Roster builtins")
    print("=" * 50)
    run_bard_code(test_roster, verbose=False)

    print("\n" + "=" * 50)
    print("SECTION VI — Class system")
    print("=" * 50)
    run_bard_code(test_classes, verbose=False)

    print("\n" + "=" * 50)
    print("SECTION VII - Bard-native conveniences")
    print("=" * 50)
    run_bard_code(test_bardic, verbose=False)
