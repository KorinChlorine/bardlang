from lark import Lark, Transformer, v_args

shakespeare_grammar = r"""
    start: instruction+

    ?instruction: assignment
                | reassignment
                | print_statement
                | if_statement
                | while_statement
                | for_statement
                | func_def
                | func_call_stmt
                | return_statement
                | list_assignment
                | list_append
                | list_remove

    // Variable declaration
    assignment: "Enter" IDENTIFIER ", a knave of" expr "."

    // Reassignment
    reassignment: IDENTIFIER "becomes" expr "."

    // Print
    print_statement: "Speak" (string | expr) "."

    // If / Else
    if_statement: "Hark!" "shouldst" condition "," "then" ":" instruction+ ("Alas," "else" ":" instruction+)? "Thus endeth the choice."

    // While loop
    while_statement: "Whilst" condition "," "prithee" ":" instruction+ "Thus endeth the whilst."

    // For loop (iterate over a range)
    for_statement: "For every" IDENTIFIER "from" expr "to" expr ":" instruction+ "Thus endeth the for."

    // Function definition
    func_def: "A tale of" IDENTIFIER "(" param_list? ")" ":" instruction+ "Thus endeth the tale."

    // Function call as statement
    func_call_stmt: "Invoke" IDENTIFIER "(" arg_list? ")" "."

    // Return statement
    return_statement: "Return henceforth" expr "."

    // List operations
    list_assignment: "Behold" IDENTIFIER ", a roster of" "[" arg_list? "]" "."
    list_append:  "Add" expr "unto" IDENTIFIER "."
    list_remove:  "Remove" expr "from" IDENTIFIER "."

    // Parameters and arguments
    param_list: IDENTIFIER ("," IDENTIFIER)*
    arg_list: expr ("," expr)*

    // Conditions
    ?condition: expr "doth equal" expr           -> eq
              | expr "doth not equal" expr        -> neq
              | expr "is greater than" expr       -> gt
              | expr "is lesser than" expr        -> lt
              | expr "is no less than" expr       -> gte
              | expr "is no more than" expr       -> lte
              | condition "and also" condition    -> and_cond
              | condition "or perchance" condition -> or_cond
              | "not" condition                   -> not_cond

    // Expressions
    ?expr: or_expr

    ?or_expr: and_expr
            | or_expr "or" and_expr              -> bor

    ?and_expr: add_expr
             | and_expr "and" add_expr           -> band

    ?add_expr: mul_expr
             | add_expr "plus" mul_expr          -> add
             | add_expr "minus" mul_expr         -> sub

    ?mul_expr: unary_expr
             | mul_expr "times" unary_expr       -> mul
             | mul_expr "divided by" unary_expr  -> div
             | mul_expr "modulo" unary_expr      -> mod

    ?unary_expr: factor
               | "nay" factor                    -> neg

    ?factor: atom
           | func_call_expr

    ?atom: NUMBER                                -> number
         | FLOAT                                 -> float_num
         | string                                -> string_val
         | IDENTIFIER                            -> var
         | "true"                                -> true_val
         | "false"                               -> false_val
         | "naught"                              -> none_val
         | "(" expr ")"
         | list_index

    list_index: IDENTIFIER "[" expr "]"
    func_call_expr: "Invoke" IDENTIFIER "(" arg_list? ")"

    string: ESCAPED_STRING

    %import common.ESCAPED_STRING
    %import common.INT     -> NUMBER
    %import common.FLOAT
    %import common.CNAME   -> IDENTIFIER
    %import common.WS
    %ignore WS
"""

parser = Lark(shakespeare_grammar, parser='earley', lexer='dynamic_complete', ambiguity='resolve')


INDENT = "    "

class BardToPython(Transformer):

    # ── helpers ──────────────────────────────────────────────────────────────

    def _indent(self, lines):
        return "\n".join(INDENT + l for l in lines)

    def _block(self, items):
        return [str(i) for i in items]

    # ── top-level ─────────────────────────────────────────────────────────────

    def start(self, items):
        return "\n".join(str(i) for i in items if str(i).strip())

    # ── statements ───────────────────────────────────────────────────────────

    def assignment(self, items):
        return f"{items[0]} = {items[1]}"

    def reassignment(self, items):
        return f"{items[0]} = {items[1]}"

    def print_statement(self, items):
        return f"print({items[0]})"

    # ── if / else ────────────────────────────────────────────────────────────

    def if_statement(self, items):
        cond = items[0]
        # split on the sentinel None produced by the optional else branch
        try:
            else_idx = items.index("__else__")
            then_block = items[1:else_idx]
            else_block = items[else_idx + 1:]
        except ValueError:
            then_block = items[1:]
            else_block = []

        code = f"if {cond}:\n"
        code += self._indent(self._block(then_block))
        if else_block:
            code += f"\nelse:\n"
            code += self._indent(self._block(else_block))
        return code

    # lark puts the two instruction+ groups flat; we need a sentinel
    # We inject it via an alias trick in the grammar — but since lark
    # earley flattens rules, we rely on the "Alas," keyword position.
    # Instead, override the whole transform with a raw tree hook below.

    # ── while ────────────────────────────────────────────────────────────────

    def while_statement(self, items):
        cond = items[0]
        body = self._block(items[1:])
        return f"while {cond}:\n" + self._indent(body)

    # ── for ──────────────────────────────────────────────────────────────────

    def for_statement(self, items):
        var   = str(items[0])
        start = str(items[1])
        end   = str(items[2])
        body  = self._block(items[3:])
        return f"for {var} in range({start}, {end} + 1):\n" + self._indent(body)

    # ── functions ─────────────────────────────────────────────────────────────

    def func_def(self, items):
        name = str(items[0])
        # find param_list if present
        if items[1] is not None and isinstance(items[1], list):
            params = ", ".join(str(p) for p in items[1])
            body   = self._block(items[2:])
        else:
            params = ""
            body   = self._block(items[1:])
        body = [b for b in body if b]  # drop empty strings
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
        name = str(items[0])
        elems = str(items[1]) if len(items) > 1 and items[1] is not None else ""
        return f"{name} = [{elems}]"

    def list_append(self, items):
        val  = str(items[0])
        name = str(items[1])
        return f"{name}.append({val})"

    def list_remove(self, items):
        val  = str(items[0])
        name = str(items[1])
        return f"{name}.remove({val})"

    def list_index(self, items):
        return f"{items[0]}[{items[1]}]"

    # ── conditions ───────────────────────────────────────────────────────────

    def eq(self, items):       return f"({items[0]} == {items[1]})"
    def neq(self, items):      return f"({items[0]} != {items[1]})"
    def gt(self, items):       return f"({items[0]} > {items[1]})"
    def lt(self, items):       return f"({items[0]} < {items[1]})"
    def gte(self, items):      return f"({items[0]} >= {items[1]})"
    def lte(self, items):      return f"({items[0]} <= {items[1]})"
    def and_cond(self, items): return f"({items[0]} and {items[1]})"
    def or_cond(self, items):  return f"({items[0]} or {items[1]})"
    def not_cond(self, items): return f"(not {items[0]})"

    # ── expressions ──────────────────────────────────────────────────────────

    def add(self, items): return f"({items[0]} + {items[1]})"
    def sub(self, items): return f"({items[0]} - {items[1]})"
    def mul(self, items): return f"({items[0]} * {items[1]})"
    def div(self, items): return f"({items[0]} / {items[1]})"
    def mod(self, items): return f"({items[0]} % {items[1]})"
    def neg(self, items): return f"(-{items[0]})"
    def bor(self, items): return f"({items[0]} | {items[1]})"
    def band(self, items): return f"({items[0]} & {items[1]})"

    # ── atoms ────────────────────────────────────────────────────────────────

    def number(self, items):    return str(items[0])
    def float_num(self, items): return str(items[0])
    def string_val(self, items): return str(items[0])
    def string(self, items):    return str(items[0])
    def var(self, items):       return str(items[0])
    def true_val(self, items):  return "True"
    def false_val(self, items): return "False"
    def none_val(self, items):  return "None"


# ── runner ────────────────────────────────────────────────────────────────────

def run_bard_code(source_code: str, verbose: bool = True):
    # Strip comments before parsing
    import re
    source_code = re.sub(r'#[^\n]*', '', source_code)
    if verbose:
        print("╔══════════════════════════════════════╗")
        print("║   ACT I: THE BARD SPEAKS (PARSING)   ║")
        print("╚══════════════════════════════════════╝")
    try:
        ast = parser.parse(source_code)
        python_code = BardToPython().transform(ast)

        if verbose:
            print("Generated Python Code:")
            print("──────────────────────")
            print(python_code)
            print("──────────────────────\n")
            print("╔══════════════════════════════════════╗")
            print("║   ACT II: THE PERFORMANCE (OUTPUT)   ║")
            print("╚══════════════════════════════════════╝")

        exec(python_code, {})

    except Exception as e:
        print(f"\n⚡ A Tragedy Has Occurred: {e}")
        raise


# ══════════════════════════════════════════════════════════════════════════════
#  DEMO SCRIPTS
# ══════════════════════════════════════════════════════════════════════════════

demo_basic = """
# Basic variables and arithmetic
Enter Romeo, a knave of 42.
Enter Juliet, a knave of 8.
Enter sum, a knave of Romeo plus Juliet.
Speak "Sum of Romeo and Juliet:".
Speak sum.
Enter product, a knave of Romeo times Juliet.
Speak "Product:".
Speak product.
"""

demo_conditionals = """
# Conditionals
Enter age, a knave of 20.
Hark! shouldst age is greater than 17, then :
    Speak "Thou art of age, good fellow!".
Alas, else :
    Speak "Thou art yet a youth.".
Thus endeth the choice.
"""

demo_while = """
# While loop
Enter counter, a knave of 1.
Whilst counter is no more than 5, prithee :
    Speak counter.
    counter becomes counter plus 1.
Thus endeth the whilst.
"""

demo_for = """
# For loop
Speak "Counting from 1 to 5:".
For every i from 1 to 5:
    Speak i.
Thus endeth the for.
"""

demo_functions = """
# Functions
A tale of greet(name) :
    Speak "Hail,".
    Speak name.
Thus endeth the tale.

A tale of add(a, b) :
    Enter result, a knave of a plus b.
    Return henceforth result.
Thus endeth the tale.

Invoke greet("Hamlet").
Enter total, a knave of Invoke add(10, 32).
Speak total.
"""

demo_lists = """
# Lists
Behold heroes, a roster of [1, 2, 3].
Add 4 unto heroes.
Speak heroes[0].
Speak heroes[3].
"""

demo_full = """
# Full showcase
A tale of factorial(n) :
    Hark! shouldst n is lesser than 2, then :
        Return henceforth 1.
    Thus endeth the choice.
    Enter prev, a knave of n minus 1.
    Enter sub, a knave of Invoke factorial(prev).
    Return henceforth n times sub.
Thus endeth the tale.

For every x from 1 to 7:
    Enter f, a knave of Invoke factorial(x).
    Speak f.
Thus endeth the for.
"""

if __name__ == "__main__":
    demos = [
        ("Basic Variables & Arithmetic", demo_basic),
        ("Conditionals",                 demo_conditionals),
        ("While Loop",                   demo_while),
        ("For Loop",                     demo_for),
        ("Functions",                    demo_functions),
        ("Lists",                        demo_lists),
        ("Factorial (Recursion)",         demo_full),
    ]

    for title, code in demos:
        print(f"\n{'═'*50}")
        print(f"  SCENE: {title}")
        print(f"{'═'*50}")
        run_bard_code(code)
        print()