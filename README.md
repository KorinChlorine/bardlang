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

## Language Reference

### Variables

```bard
Enter count, a amount of 5.
Enter price, a numerical of 3.14.
Enter name, a scroll of "Galahad".
Enter ready, a banner of true.
Enter items, a roster of [1, 2, 3].

count becomes count plus 1.
```

`a amount of` and `a numerical of` cast through `int(...)` and `float(...)`. `a scroll of` now accepts expressions, so defaults and object creation can be used directly.

```bard
Enter title, a scroll of naught or else "Untitled".
```

### Input and Output

```bard
Hearken name, a scroll of "Name: ".
Hearken age, a amount of "Age: ".
Speak joined "Hello, " with name.
```

### Control Flow

```bard
Hark! shouldst score is no less than 90 , then :
    Speak "Excellent.".
Ponder! shouldst score is no less than 60 , then :
    Speak "Passed.".
Alas, else :
    Speak "Failed.".
Thus endeth the choice.
```

`Unless` is the inverse of `Hark!`, useful for guard-style code:

```bard
Unless ready , lest :
    Speak "Not ready.".
Thus endeth the unless.
```

Loops:

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

Use `Cease.` for `break` and `Persist.` for `continue`.

### Functions

```bard
A tale of add(a, b):
    Return henceforth a plus b.
Thus endeth the tale.

Enter result, a amount of add(2, 3).
Invoke add(2, 3).
```

### Classes

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
```

`enact` compiles to `__init__`, and `Invoke primal(self, ...)` calls the parent initializer.

### Lists

```bard
Enter nums, a roster of [3, 1, 2].
Add 4 unto nums.
Remove 1 from nums.
Arrange nums.
Invert nums.

Speak nums[0].
Speak length of nums.
Speak tally of nums.
Speak position of 3 in nums.
Speak tally occurrences of 2 in nums.
```

### Strings

```bard
Enter msg, a scroll of "  Hello World  ".

Speak uppercase of msg.
Speak lowercase of msg.
Speak trimmed of msg.
Speak joined "Hello, " with "Kharl".
Speak split msg by " ".
Speak replace "l" with "r" in msg.
Speak excerpt msg from 1 to 4.
Speak echo "ha" times 3.
```

### Math and Expressions

```bard
Speak absolute of nay 9.
Speak root of 144.
Speak floor of 3.9.
Speak ceiling of 3.1.
Speak rounded of 3.5.
Speak 2 raised to 10.
Speak lesser between 4 and 9.
Speak greater between 4 and 9.
```

Defaulting uses `or else` and only falls back for `naught`, not for falsey values like `0` or `false`:

```bard
Enter label, a scroll of naught or else "Unknown".
```

### Conditions

| BardLang | Python meaning |
|---|---|
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
| `cond and also cond` | `and` |
| `cond or perchance cond` | `or` |

### Error Handling

```bard
Attempt :
    Forsooth "Something failed.".
Should tragedy strike as sorrow :
    Speak joined "Caught: " with sorrow.
Thus endeth the attempt.
```

`Should tragedy strike` catches any exception. `Should tragedy strike as name` exposes the exception message as a BardLang variable.

### Comments

```bard
# This is a comment.
```

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
