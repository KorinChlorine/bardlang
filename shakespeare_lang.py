import re
from lark import Lark, Transformer

shakespeare_grammar = r"""
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

    // Typed variable declarations
    // amount  = int
    // numerical   = float
    // scroll = string
    // banner = bool
    // roster = list
    assignment: "Enter" IDENTIFIER ", a amount of" int_expr "."
              | "Enter" IDENTIFIER ", a numerical of" float_expr "."
              | "Enter" IDENTIFIER ", a scroll of" string "."
              | "Enter" IDENTIFIER ", a banner of" bool_expr "."
              | "Enter" IDENTIFIER ", a roster of" "[" arg_list? "]" "."

    reassignment:    IDENTIFIER "becomes" expr "."
    print_statement: "Speak" (string | expr) "."

    if_only: "Hark!" "shouldst" condition "," "then" ":" then_block "Thus endeth the choice."
    if_else: "Hark!" "shouldst" condition "," "then" ":" then_block "Alas," "else" ":" else_block "Thus endeth the choice."
    then_block: instruction+
    else_block: instruction+

    while_statement:  "Whilst" condition "," "prithee" ":" instruction+ "Thus endeth the whilst."
    for_statement:    "For every" IDENTIFIER "from" expr "to" expr ":" instruction+ "Thus endeth the for."
    func_def:         "A tale of" IDENTIFIER "(" param_list? ")" ":" instruction+ "Thus endeth the tale."
    func_call_stmt:   "Invoke" IDENTIFIER "(" arg_list? ")" "."
    return_statement: "Return henceforth" expr "."

    list_assignment: "Behold" IDENTIFIER ", a roster of" "[" arg_list? "]" "."
    list_append:     "Add" expr "unto" IDENTIFIER "."
    list_remove:     "Remove" expr "from" IDENTIFIER "."

    param_list: IDENTIFIER ("," IDENTIFIER)*
    arg_list:   expr ("," expr)*

    // Typed expression wrappers
    int_expr:    expr
    float_expr:  expr
    bool_expr:   "true"  -> true_val
               | "false" -> false_val

    ?condition: expr "doth equal" expr            -> eq
              | expr "doth not equal" expr         -> neq
              | expr "is greater than" expr        -> gt
              | expr "is lesser than" expr         -> lt
              | expr "is no less than" expr        -> gte
              | expr "is no more than" expr        -> lte
              | condition "and also" condition     -> and_cond
              | condition "or perchance" condition -> or_cond
              | "not" condition                    -> not_cond

    ?expr: or_expr

    ?or_expr:  and_expr | or_expr "or" and_expr   -> bor
    ?and_expr: add_expr | and_expr "and" add_expr  -> band
    ?add_expr: mul_expr
             | add_expr "plus" mul_expr            -> add
             | add_expr "minus" mul_expr           -> sub
    ?mul_expr: unary_expr
             | mul_expr "times" unary_expr         -> mul
             | mul_expr "divided by" unary_expr    -> div
             | mul_expr "modulo" unary_expr        -> mod
    ?unary_expr: factor | "nay" factor             -> neg
    ?factor: atom | func_call_expr

    ?atom: NUMBER        -> number
         | FLOAT         -> float_num
         | string        -> string_val
         | IDENTIFIER    -> var
         | "true"        -> true_val
         | "false"       -> false_val
         | "naught"      -> none_val
         | "(" expr ")"
         | list_index

    list_index:     IDENTIFIER "[" expr "]"
    func_call_expr: "Invoke" IDENTIFIER "(" arg_list? ")"
    string:         ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.INT   -> NUMBER
    %import common.FLOAT
    %import common.CNAME -> IDENTIFIER
    %import common.WS
    %ignore WS
"""

parser = Lark(shakespeare_grammar, parser='earley', lexer='dynamic_complete', ambiguity='resolve')

INDENT = "    "


class BardToPython(Transformer):

    def _indent(self, lines):
        return "\n".join(INDENT + l for l in lines)

    def _block(self, items):
        return [str(i) for i in items if str(i).strip()]

    def start(self, items):
        return "\n".join(str(i) for i in items if str(i).strip())

    # ── typed wrappers ────────────────────────────────────────────────────────

    def int_expr(self, items):
        return f"int({items[0]})"

    def float_expr(self, items):
        return f"float({items[0]})"

    # ── assignments ───────────────────────────────────────────────────────────

    def assignment(self, items):
        name  = str(items[0])
        value = str(items[1])
        return f"{name} = {value}"

    def reassignment(self, items):
        return f"{items[0]} = {items[1]}"

    def print_statement(self, items):
        return f"print({items[0]})"

    # ── if / else ─────────────────────────────────────────────────────────────

    def then_block(self, items):
        return self._block(items)

    def else_block(self, items):
        return self._block(items)

    def if_only(self, items):
        cond = items[0]
        body = items[1]
        return f"if {cond}:\n" + self._indent(body)

    def if_else(self, items):
        cond      = items[0]
        then_body = items[1]
        else_body = items[2]
        code  = f"if {cond}:\n" + self._indent(then_body)
        code += f"\nelse:\n"    + self._indent(else_body)
        return code

    # ── while / for ───────────────────────────────────────────────────────────

    def while_statement(self, items):
        cond = items[0]
        body = self._block(items[1:])
        return f"while {cond}:\n" + self._indent(body)

    def for_statement(self, items):
        var, start, end = str(items[0]), str(items[1]), str(items[2])
        body = self._block(items[3:])
        return f"for {var} in range({start}, {end} + 1):\n" + self._indent(body)

    # ── functions ─────────────────────────────────────────────────────────────

    def func_def(self, items):
        name = str(items[0])
        if len(items) > 1 and isinstance(items[1], list) and all(isinstance(x, str) and '\n' not in x for x in items[1]):
            params = ", ".join(items[1])
            body   = self._block(items[2:])
        else:
            params = ""
            body   = self._block(items[1:])
        if not body:
            body = ["pass"]
        return f"def {name}({params}):\n" + self._indent(body)

    def param_list(self, items):
        return [str(i) for i in items]

    def func_call_stmt(self, items):
        name = str(items[0])
        args = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name}({args})"

    def func_call_expr(self, items):
        name = str(items[0])
        args = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name}({args})"

    def return_statement(self, items):
        return f"return {items[0]}"

    def arg_list(self, items):
        return ", ".join(str(i) for i in items)

    # ── lists ─────────────────────────────────────────────────────────────────

    def list_assignment(self, items):
        name  = str(items[0])
        elems = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name} = [{elems}]"

    def list_append(self, items):
        return f"{items[1]}.append({items[0]})"

    def list_remove(self, items):
        return f"{items[1]}.remove({items[0]})"

    def list_index(self, items):
        return f"{items[0]}[{items[1]}]"

    # ── conditions ────────────────────────────────────────────────────────────

    def eq(self, i):        return f"({i[0]} == {i[1]})"
    def neq(self, i):       return f"({i[0]} != {i[1]})"
    def gt(self, i):        return f"({i[0]} > {i[1]})"
    def lt(self, i):        return f"({i[0]} < {i[1]})"
    def gte(self, i):       return f"({i[0]} >= {i[1]})"
    def lte(self, i):       return f"({i[0]} <= {i[1]})"
    def and_cond(self, i):  return f"({i[0]} and {i[1]})"
    def or_cond(self, i):   return f"({i[0]} or {i[1]})"
    def not_cond(self, i):  return f"(not {i[0]})"

    # ── expressions ───────────────────────────────────────────────────────────

    def add(self, i):   return f"({i[0]} + {i[1]})"
    def sub(self, i):   return f"({i[0]} - {i[1]})"
    def mul(self, i):   return f"({i[0]} * {i[1]})"
    def div(self, i):   return f"({i[0]} / {i[1]})"
    def mod(self, i):   return f"({i[0]} % {i[1]})"
    def neg(self, i):   return f"(-{i[0]})"
    def bor(self, i):   return f"({i[0]} | {i[1]})"
    def band(self, i):  return f"({i[0]} & {i[1]})"

    # ── atoms ─────────────────────────────────────────────────────────────────

    def number(self, i):      return str(i[0])
    def float_num(self, i):   return str(i[0])
    def string_val(self, i):  return str(i[0])
    def string(self, i):      return str(i[0])
    def var(self, i):         return str(i[0])
    def true_val(self, i):    return "True"
    def false_val(self, i):   return "False"
    def none_val(self, i):    return "None"


# ── public API ────────────────────────────────────────────────────────────────

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
        exec(python_code, {})
    except Exception as e:
        print(f"A Tragedy Has Occurred: {e}")
        raise


# ── demo ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo = """
# int
Enter age, a knave of 25.

# float
Enter height, a dame of 5.9.

# string
Enter name, a scroll of "Hamlet".

# bool
Enter alive, a banner of true.

# list
Enter nums, a roster of [1, 2, 3].

Speak age.
Speak height.
Speak name.
Speak alive.
Speak nums.

# type coercion check
Enter x, a knave of 7.
Enter y, a dame of 3.
Enter result, a dame of x plus y.
Speak result.
"""
    run_bard_code(demo)