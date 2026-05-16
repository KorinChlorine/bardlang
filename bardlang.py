import re
from lark import Lark, Transformer

# ==========================================
# 1. BARDLANG GRAMMAR SPECIFICATION
# ==========================================
#
# KEYWORD REFERENCE
# -----------------
# Variables:
#   Enter x, a amount of <int_expr>.          → int
#   Enter x, a numerical of <float_expr>.     → float
#   Enter x, a scroll of "...".               → string
#   Enter x, a banner of true/false.          → bool
#   Enter x, a roster of [...].               → list
#   x becomes <expr>.                         → reassign
#
# Input:
#   Hearken x, a amount of "prompt".          → int input
#   Hearken x, a numerical of "prompt".       → float input
#   Hearken x, a scroll of "prompt".          → string input
#
# Output:
#   Speak <expr>.                             → print
#   Speak "literal".                          → print string
#
# Control flow:
#   Hark! shouldst <cond> , then : ... Thus endeth the choice.
#   Hark! shouldst <cond> , then : ... Alas, else : ... Thus endeth the choice.
#   While <cond> , prithee : ... Thus endeth the while.
#   For every x from <expr> to <expr> : ... Thus endeth the for.
#   Cease.                                    → break
#   Persist.                                  → continue
#
# Functions:
#   A tale of name(params) : ... Thus endeth the tale.
#   Return henceforth <expr>.
#   Invoke name(args).                        → standalone call statement
#   name(args)                                → call in expression
#
# Lists:
#   Behold x, a roster of [...].              → list (alias)
#   Add <expr> unto <list>.                   → append
#   Remove <expr> from <list>.                → remove
#   x[i]                                      → index
#   x contains <expr>                         → in operator
#   x lacks <expr>                            → not in operator
#
# String / length expressions:
#   uppercase of <expr>                       → .upper()
#   lowercase of <expr>                       → .lower()
#   trimmed of <expr>                         → .strip()
#   length of <expr>                          → len()
#   joined <expr> with <expr>                 → str + str
#
# Type casting (expression form):
#   cast <expr> to amount                     → int()
#   cast <expr> to numerical                  → float()
#   cast <expr> to scroll                     → str()
#
# Error handling:
#   Attempt : ... Should tragedy strike : ... Thus endeth the attempt.
#   Forsooth "<msg>".                         → raise Exception
#
# Conditions:
#   x doth equal y          ==
#   x doth not equal y      !=
#   x is greater than y     >
#   x is lesser than y      <
#   x is no less than y     >=
#   x is no more than y     <=
#   x is naught             is None
#   x is not naught         is not None
#   x contains y            y in x
#   x lacks y               y not in x
#   <cond> and also <cond>  and
#   <cond> or perchance <cond>  or
#   not <cond>              not
#
# Math operators:
#   plus  minus  times  divided by  modulo
#   nay <expr>   → negation
# ==========================================

bardlang_grammar = r"""
    start: instruction+

    ?instruction: assignment
                | reassignment
                | print_statement
                | if_else
                | if_only
                | while_statement
                | for_statement
                | func_def
                | func_call_stmt
                | return_statement
                | list_assignment
                | list_append
                | list_remove
                | input_statement
                | break_statement
                | continue_statement
                | try_statement
                | raise_statement

    # variable declarations
    assignment: "Enter" IDENTIFIER ", a amount of" int_expr "."
              | "Enter" IDENTIFIER ", a numerical of" float_expr "."
              | "Enter" IDENTIFIER ", a scroll of" string "."
              | "Enter" IDENTIFIER ", a banner of" bool_expr "."
              | "Enter" IDENTIFIER ", a roster of" "[" arg_list? "]" "." -> roster_assignment

    reassignment:    IDENTIFIER "becomes" expr "."
    print_statement: "Speak" (string | expr) "."

    # input
    input_statement: "Hearken" IDENTIFIER ", a amount of" string "."    -> input_int
                   | "Hearken" IDENTIFIER ", a numerical of" string "." -> input_float
                   | "Hearken" IDENTIFIER ", a scroll of" string "."    -> input_str

    # control flow
    if_only: "Hark!" "shouldst" condition "," "then" ":" then_block "Thus endeth the choice."
    if_else: "Hark!" "shouldst" condition "," "then" ":" then_block "Alas," "else" ":" else_block "Thus endeth the choice."
    then_block: instruction+
    else_block: instruction+

    break_statement:    "Cease."
    continue_statement: "Persist."

    COMMA: ","

    while_statement: "While" condition COMMA "prithee" ":" instruction+ "Thus endeth the while."
    for_statement:   "For every" IDENTIFIER "from" expr "to" expr ":" instruction+ "Thus endeth the for."

    # error handling
    try_statement:   "Attempt" ":" try_block "Should tragedy strike" ":" catch_block "Thus endeth the attempt."
    try_block:       instruction+
    catch_block:     instruction+
    raise_statement: "Forsooth" string "."

    # functions
    func_def:         "A tale of" IDENTIFIER "(" param_list? ")" ":" instruction+ "Thus endeth the tale."
    func_call_stmt:   "Invoke" IDENTIFIER "(" arg_list? ")" "."
    return_statement: "Return henceforth" expr "."

    # lists
    list_assignment: "Behold" IDENTIFIER ", a roster of" "[" arg_list? "]" "."
    list_append:     "Add" expr "unto" IDENTIFIER "."
    list_remove:     "Remove" expr "from" IDENTIFIER "."

    param_list: IDENTIFIER ("," IDENTIFIER)*
    arg_list:   expr ("," expr)*

    # typed expression wrappers
    int_expr:   expr
    float_expr: expr
    bool_expr:  TRUE_KW  -> true_val
             |  FALSE_KW -> false_val

    # conditions
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
              | condition "and also" condition     -> and_cond
              | condition "or perchance" condition -> or_cond
              | "not" condition                    -> not_cond

    # expressions
    ?expr: or_expr
         | "cast" expr "to amount"                -> cast_int
         | "cast" expr "to numerical"             -> cast_float
         | "cast" expr "to scroll"                -> cast_str
         | "uppercase of" expr                    -> str_upper
         | "lowercase of" expr                    -> str_lower
         | "trimmed of" expr                      -> str_strip
         | "length of" expr                       -> length_of
         | "joined" expr "with" expr              -> str_join

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
         | "naught"      -> none_val
         | "(" expr ")"
         | list_index

    list_index:     IDENTIFIER "[" expr "]"
    func_call_expr: IDENTIFIER "(" arg_list? ")"
    string:         ESCAPED_STRING

    TRUE_KW.2:  "true"
    FALSE_KW.2: "false"

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

    # typed wrappers
    def int_expr(self, items):   return f"int({items[0]})"
    def float_expr(self, items): return f"float({items[0]})"

    # assignments
    def assignment(self, items):
        return f"{items[0]} = {items[1]}"

    def roster_assignment(self, items):
        name  = str(items[0])
        elems = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name} = [{elems}]"

    def reassignment(self, items):
        return f"{items[0]} = {items[1]}"

    # output
    def print_statement(self, items):
        return f"print({items[0]})"

    # input
    def input_int(self, items):
        return f"{items[0]} = int(input({items[1]}))"

    def input_float(self, items):
        return f"{items[0]} = float(input({items[1]}))"

    def input_str(self, items):
        return f"{items[0]} = input({items[1]})"

    # if/else
    def then_block(self, items): return self._block(items)
    def else_block(self, items): return self._block(items)

    def if_only(self, items):
        return f"if {items[0]}:\n" + self._indent(items[1])

    def if_else(self, items):
        code  = f"if {items[0]}:\n" + self._indent(items[1])
        code += f"\nelse:\n"        + self._indent(items[2])
        return code

    # control flow
    def break_statement(self, _):    return "break"
    def continue_statement(self, _): return "continue"

    # while / for
    def while_statement(self, items):
        from lark import Token
        clean = [i for i in items if not (isinstance(i, Token) and i.type == "COMMA")]
        return f"while {clean[0]}:\n" + self._indent(self._block(clean[1:]))

    def for_statement(self, items):
        from lark import Token
        clean = [i for i in items if not (isinstance(i, Token) and i.type == "COMMA")]
        var, start, end = str(clean[0]), str(clean[1]), str(clean[2])
        return f"for {var} in range({start}, {end} + 1):\n" + self._indent(self._block(clean[3:]))

    # error handling
    def try_block(self, items):   return self._block(items)
    def catch_block(self, items): return self._block(items)

    def try_statement(self, items):
        code  = "try:\n"    + self._indent(items[0])
        code += "\nexcept Exception as _bard_err:\n" + self._indent(items[1])
        return code

    def raise_statement(self, items):
        return f"raise Exception({items[0]})"

    # functions
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
        return f"{name}({args})"

    def func_call_expr(self, items):
        name = str(items[0])
        args = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name}({args})"

    def return_statement(self, items): return f"return {items[0]}"
    def arg_list(self, items): return ", ".join(str(i) for i in items)

    # lists
    def list_assignment(self, items):
        name  = str(items[0])
        elems = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name} = [{elems}]"

    def list_append(self, items): return f"{items[1]}.append({items[0]})"
    def list_remove(self, items): return f"{items[1]}.remove({items[0]})"
    def list_index(self, items):  return f"{items[0]}[{items[1]}]"

    # conditions
    def bare_expr(self, i):    return str(i[0])
    def eq(self, i):           return f"({i[0]} == {i[1]})"
    def neq(self, i):          return f"({i[0]} != {i[1]})"
    def gt(self, i):           return f"({i[0]} > {i[1]})"
    def lt(self, i):           return f"({i[0]} < {i[1]})"
    def gte(self, i):          return f"({i[0]} >= {i[1]})"
    def lte(self, i):          return f"({i[0]} <= {i[1]})"
    def is_none(self, i):      return f"({i[0]} is None)"
    def is_not_none(self, i):  return f"({i[0]} is not None)"
    def contains(self, i):     return f"({i[1]} in {i[0]})"
    def lacks(self, i):        return f"({i[1]} not in {i[0]})"
    def and_cond(self, i):     return f"({i[0]} and {i[1]})"
    def or_cond(self, i):      return f"({i[0]} or {i[1]})"
    def not_cond(self, i):     return f"(not {i[0]})"

    # expressions
    def add(self, i):        return f"({i[0]} + {i[1]})"
    def sub(self, i):        return f"({i[0]} - {i[1]})"
    def mul(self, i):        return f"({i[0]} * {i[1]})"
    def div(self, i):        return f"({i[0]} / {i[1]})"
    def mod(self, i):        return f"({i[0]} % {i[1]})"
    def neg(self, i):        return f"(-{i[0]})"
    def bor(self, i):        return f"({i[0]} | {i[1]})"
    def band(self, i):       return f"({i[0]} & {i[1]})"
    def cast_int(self, i):   return f"int({i[0]})"
    def cast_float(self, i): return f"float({i[0]})"
    def cast_str(self, i):   return f"str({i[0]})"
    def str_upper(self, i):  return f"({i[0]}).upper()"
    def str_lower(self, i):  return f"({i[0]}).lower()"
    def str_strip(self, i):  return f"({i[0]}).strip()"
    def length_of(self, i):  return f"len({i[0]})"
    def str_join(self, i):   return f"(str({i[0]}) + str({i[1]}))"

    # atoms
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
        namespace = {}
        exec(python_code, namespace, namespace)
    except Exception as e:
        print(f"A Tragedy Has Occurred: {e}")
        raise


# ==========================================
# 4. SELF-TEST (non-interactive)
# ==========================================
if __name__ == "__main__":
    test = r"""
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

    # break
    For every i from 1 to 10 :
        Hark! shouldst i doth equal 5 , then :
            Cease.
        Thus endeth the choice.
        Speak i.
    Thus endeth the for.

    # continue
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

    # try/catch + raise
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
    run_bard_code(test, verbose=True)