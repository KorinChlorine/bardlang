# BardLang

BardLang is a Shakespearean-themed domain-specific programming language that transpiles to Python. It keeps the theatrical syntax, but adds Bard-native conveniences that are not just renamed Python: `Unless`, `Repeat`, inclusive stepped ranges, `or else` defaults, named tragedy catches, classes, inheritance, and built-in math/string/roster phrases.

```bard
A tale of greet(name):
    Speak joined "Hello, " with name.
Thus endeth the tale.

Hearken who, a scroll of "Enter your name: ".
Invoke greet(who).
```

## Requirements

- Python 3.8+
- [Lark](https://github.com/lark-parser/lark)

```bash
pip install lark
```

## Usage

```bash
python bard.py yourscript.bard
```

To see generated Python:

```python
from bardlang import run_bard_code

with open("yourscript.bard") as f:
    run_bard_code(f.read(), verbose=True)
```

## Complete Command Reference

This section lists every command and expression form currently accepted by the grammar in `bardlang.py`.

### Program Structure

| Command | Form |
|---|---|
| Comment | `# comment text` |
| Statement terminator | Most single-line commands end with `.` |
| Block terminator | Blocks use matching `Thus endeth ...` lines |

### Literals and Values

| BardLang | Meaning |
|---|---|
| `123` | integer literal |
| `3.14` | float literal |
| `"hello"` | string literal |
| `true` | boolean true |
| `false` | boolean false |
| `naught` | null / `None` |
| `[a, b, c]` | roster / list literal |
| `name` | variable reference |
| `(expr)` | grouped expression |

### Variable Commands

| Command | Form |
|---|---|
| Declare integer | `Enter name, a amount of expr.` |
| Declare float | `Enter name, a numerical of expr.` |
| Declare string/expression | `Enter name, a scroll of expr.` |
| Declare boolean | `Enter name, a banner of true.` or `Enter name, a banner of false.` |
| Declare roster | `Enter name, a roster of [expr, expr].` |
| Reassign variable | `name becomes expr.` |
| Reassign attribute | `object.field becomes expr.` |

Examples:

```bard
Enter count, a amount of 5.
Enter price, a numerical of 3.14.
Enter title, a scroll of naught or else "Untitled".
Enter ready, a banner of true.
Enter nums, a roster of [1, 2, 3].

count becomes count plus 1.
hero.health becomes hero.health minus 10.
```

### Input and Output Commands

| Command | Form |
|---|---|
| Print | `Speak expr.` |
| Read integer | `Hearken name, a amount of "Prompt: ".` |
| Read float | `Hearken name, a numerical of "Prompt: ".` |
| Read string | `Hearken name, a scroll of "Prompt: ".` |

### Choice Commands

| Command | Form |
|---|---|
| If | `Hark! shouldst condition , then : ... Thus endeth the choice.` |
| If / else | `Hark! shouldst condition , then : ... Alas, else : ... Thus endeth the choice.` |
| Else-if | `Ponder! shouldst condition , then : ...` inside a choice |
| Unless | `Unless condition , lest : ... Thus endeth the unless.` |

Example:

```bard
Hark! shouldst score is no less than 90 , then :
    Speak "Excellent.".
Ponder! shouldst score is no less than 60 , then :
    Speak "Passed.".
Alas, else :
    Speak "Failed.".
Thus endeth the choice.

Unless ready , lest :
    Speak "Not ready.".
Thus endeth the unless.
```

### Loop Commands

| Command | Form |
|---|---|
| While loop | `While condition , prithee : ... Thus endeth the while.` |
| Inclusive for loop | `For every name from start to end : ... Thus endeth the for.` |
| Inclusive stepped for loop | `For every name from start to end by step : ... Thus endeth the for.` |
| Repeat loop | `Repeat expr times : ... Thus endeth the repeat.` |
| Break | `Cease.` |
| Continue | `Persist.` |

Examples:

```bard
While running , prithee :
    running becomes false.
Thus endeth the while.

For every i from 1 to 5 :
    Speak i.
Thus endeth the for.

For every i from 10 to 2 by nay 2 :
    Speak i.
Thus endeth the for.

Repeat 3 times :
    Speak "chorus".
Thus endeth the repeat.
```

### Function Commands

| Command | Form |
|---|---|
| Define function | `A tale of name(param, param): ... Thus endeth the tale.` |
| Call function as statement | `Invoke name(arg, arg).` |
| Return value | `Return henceforth expr.` |
| Call function as expression | `name(arg, arg)` |

Example:

```bard
A tale of add(a, b):
    Return henceforth a plus b.
Thus endeth the tale.

Enter result, a amount of add(2, 3).
Invoke add(2, 3).
```

### Class Commands

| Command | Form |
|---|---|
| Define class | `A chronicle of Name : ... Thus endeth the chronicle.` |
| Define subclass | `A chronicle of Child begets Parent : ... Thus endeth the chronicle.` |
| Class/default attribute | `Inscribe field as expr.` |
| Define method | `A tale of method(self, arg): ... Thus endeth the tale.` |
| Constructor method | `A tale of enact(self, arg): ... Thus endeth the tale.` |
| Parent constructor call | `Invoke primal(self, arg).` |
| Create object | `Conjure ClassName(arg, arg)` |
| Method call statement | `object.method(arg, arg).` |
| Method call expression | `object.method(arg, arg)` |
| Attribute access | `object.field` |
| Attribute assignment | `object.field becomes expr.` |

Example:

```bard
A chronicle of Character :
    Inscribe health as 100.

    A tale of enact(self, name) :
        self.name becomes name.
    Thus endeth the tale.
Thus endeth the chronicle.

A chronicle of Paladin begets Character :
    A tale of enact(self, name) :
        Invoke primal(self, name).
    Thus endeth the tale.
Thus endeth the chronicle.

Enter hero, a scroll of Conjure Paladin("Galahad").
hero.health becomes hero.health minus 10.
```

`enact` compiles to `__init__`, and `Invoke primal(self, ...)` calls the parent initializer.

### Roster/List Commands

| Command | Form |
|---|---|
| Declare roster | `Enter name, a roster of [expr, expr].` |
| Alternate roster declaration | `Behold name, a roster of [expr, expr].` |
| Append item | `Add expr unto name.` |
| Remove item | `Remove expr from name.` |
| Sort roster in place | `Arrange name.` |
| Reverse roster in place | `Invert name.` |
| Index roster | `name[index]` |

Example:

```bard
Enter nums, a roster of [3, 1, 2].
Add 4 unto nums.
Remove 1 from nums.
Arrange nums.
Invert nums.
Speak nums[0].
```

### Error Handling Commands

| Command | Form |
|---|---|
| Try/catch | `Attempt : ... Should tragedy strike : ... Thus endeth the attempt.` |
| Try/catch with message | `Attempt : ... Should tragedy strike as name : ... Thus endeth the attempt.` |
| Raise error | `Forsooth "message".` |

Example:

```bard
Attempt :
    Forsooth "Something failed.".
Should tragedy strike as sorrow :
    Speak joined "Caught: " with sorrow.
Thus endeth the attempt.
```

### Condition Forms

| BardLang | Meaning |
|---|---|
| `expr` | truthy test |
| `x doth equal y` | `x == y` |
| `x doth not equal y` | `x != y` |
| `x is greater than y` | `x > y` |
| `x is lesser than y` | `x < y` |
| `x is no less than y` | `x >= y` |
| `x is no more than y` | `x <= y` |
| `x is naught` | `x is None` |
| `x is not naught` | `x is not None` |
| `x contains y` | `y in x` |
| `x lacks y` | `y not in x` |
| `x scroll y holds z` | `z in y` |
| `condition and also condition` | logical `and` |
| `condition or perchance condition` | logical `or` |
| `not condition` | logical `not` |

### Arithmetic and Boolean Expressions

| BardLang | Meaning |
|---|---|
| `a plus b` | addition |
| `a minus b` | subtraction |
| `a times b` | multiplication |
| `a divided by b` | division |
| `a modulo b` | modulo |
| `nay a` | numeric negation |
| `a or b` | bitwise/logical OR operator emitted as `a | b` |
| `a and b` | bitwise/logical AND operator emitted as `a & b` |

### Casting and Default Expressions

| BardLang | Meaning |
|---|---|
| `cast expr to amount` | `int(expr)` |
| `cast expr to numerical` | `float(expr)` |
| `cast expr to scroll` | `str(expr)` |
| `expr or else fallback` | use `fallback` only when `expr` is `naught` |

### String Expressions

| BardLang | Meaning |
|---|---|
| `uppercase of expr` | uppercase string |
| `lowercase of expr` | lowercase string |
| `trimmed of expr` | strip whitespace |
| `length of expr` | length |
| `joined a with b` | concatenate as strings |
| `split text by separator` | split string |
| `replace old with new in text` | replace substring |
| `excerpt text from start to end` | slice string/list |
| `echo text times count` | repeat string |

### Math Expressions

| BardLang | Meaning |
|---|---|
| `absolute of expr` | absolute value |
| `root of expr` | square root |
| `floor of expr` | floor |
| `ceiling of expr` | ceiling |
| `rounded of expr` | rounded value |
| `base raised to exp` | exponentiation |
| `lesser between a and b` | minimum |
| `greater between a and b` | maximum |

### Roster/List Expressions

| BardLang | Meaning |
|---|---|
| `length of roster` | length |
| `tally of roster` | sum |
| `position of item in roster` | index of item |
| `tally occurrences of item in roster` | count item |
| `weave roster with separator` | join roster items into string |
| `roster[index]` | item at index |

## Architecture

BardLang is a transpiled DSL:

```text
.bard source
  -> Lark Earley parser
  -> parse tree
  -> BardToPython transformer
  -> Python source
  -> exec() in an isolated namespace
```

Syntax errors now report Bard source line and column context before re-raising the parser error.

## Limitations

- No module/import system; all Bard code lives in one file
- No dictionary/map type yet
- No first-class functions or closures
- No Bard standard library for files, networking, or dates
- Runtime tracebacks still come from generated Python, though syntax errors point at Bard source
- Type declarations are runtime casts/conventions, not a full static type checker

## License

MIT
