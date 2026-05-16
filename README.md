# BardLang

A Shakespearean-themed compiled domain-specific programming language that transpiles to Python. Write code in dramatic Early Modern English — declare variables with `Enter`, loop with `While`, define functions with `A tale of`, and handle errors with `Attempt`.

```
A tale of greet(name):
    Speak joined "Hello, " with name.
Thus endeth the tale.

Hearken who, a scroll of "Enter your name: ".
Invoke greet(who).
```

---

## Requirements

- Python 3.8+
- [Lark](https://github.com/lark-parser/lark) parser

```bash
pip install lark
```

---

## Usage

```bash
python bard.py yourscript.bard
```

To see the generated Python output:

```python
from shakespeare_lang import run_bard_code

with open("yourscript.bard") as f:
    run_bard_code(f.read(), verbose=True)
```

---

## Language Reference

### Variables

BardLang is statically typed at declaration. Every variable must declare its type.

| BardLang | Type | Example |
|---|---|---|
| `a amount of` | `int` | `Enter x, a amount of 5.` |
| `a numerical of` | `float` | `Enter x, a numerical of 3.14.` |
| `a scroll of` | `str` | `Enter x, a scroll of "hello".` |
| `a banner of` | `bool` | `Enter x, a banner of true.` |
| `a roster of` | `list` | `Enter x, a roster of [1, 2, 3].` |

Reassignment (any type):
```
x becomes 42.
```

---

### Input

```
Hearken x, a scroll of "Enter your name: ".
Hearken x, a amount of "Enter an integer: ".
Hearken x, a numerical of "Enter a decimal: ".
```

---

### Output

```
Speak "Hello, world!".
Speak x.
Speak joined "Value is: " with cast x to scroll.
```

---

### Operators

**Arithmetic**

| BardLang | Python |
|---|---|
| `a plus b` | `a + b` |
| `a minus b` | `a - b` |
| `a times b` | `a * b` |
| `a divided by b` | `a / b` |
| `a modulo b` | `a % b` |
| `nay a` | `-a` |

**Conditions**

| BardLang | Python |
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
| `not cond` | `not` |

---

### Control Flow

**If / else:**
```
Hark! shouldst x is greater than 0 , then :
    Speak "Positive.".
Alas, else :
    Speak "Non-positive.".
Thus endeth the choice.
```

**While loop:**
```
While running , prithee :
    Speak "Looping...".
    running becomes false.
Thus endeth the while.
```

**For loop:**
```
For every i from 1 to 5 :
    Speak i.
Thus endeth the for.
```

**Break and continue:**
```
Cease.     # break
Persist.   # continue
```

---

### Functions

```
A tale of add(a, b):
    Return henceforth a plus b.
Thus endeth the tale.

Enter result, a numerical of add(3.0, 4.0).
Speak result.
```

Standalone call (discards return value):
```
Invoke add(3.0, 4.0).
```

---

### Lists

```
Enter nums, a roster of [1, 2, 3].

Add 4 unto nums.
Remove 1 from nums.

Enter first, a amount of nums[0].
Enter size, a amount of length of nums.
```

---

### String Operations

All string operations are expressions and can be nested:

```
Enter msg, a scroll of "  Hello World  ".

Speak uppercase of msg.
Speak lowercase of msg.
Speak trimmed of msg.
Speak uppercase of trimmed of msg.
Speak length of msg.
Speak joined "Hello, " with "Kharl".
```

---

### Type Casting

```
Enter raw, a scroll of "42".
Enter num, a amount of cast raw to amount.
Enter dec, a numerical of cast num to numerical.
Enter str, a scroll of cast num to scroll.
```

---

### Error Handling

```
Attempt :
    Hearken x, a numerical of "Enter a number: ".
    Hark! shouldst x is lesser than 0 , then :
        Forsooth "Negative numbers not allowed.".
    Thus endeth the choice.
    Speak x.
Should tragedy strike :
    Speak "Invalid input caught.".
Thus endeth the attempt.
```

`Forsooth "message".` raises an exception.  
`Should tragedy strike` catches any exception — equivalent to `except Exception`.

---

### Comments

```
# This is a comment.
```

---

## Example Programs

### Hello World

```
Speak "Hello, world!".
```

### Factorial (recursive)

```
A tale of factorial(n):
    Hark! shouldst n doth equal 0 , then :
        Return henceforth 1.
    Thus endeth the choice.
    Enter prev, a amount of n minus 1.
    Enter sub, a amount of factorial(prev).
    Return henceforth n times sub.
Thus endeth the tale.

Speak factorial(10).
```

### FizzBuzz

```
For every i from 1 to 30 :
    Hark! shouldst i modulo 15 doth equal 0 , then :
        Speak "FizzBuzz".
    Alas, else :
        Hark! shouldst i modulo 3 doth equal 0 , then :
            Speak "Fizz".
        Alas, else :
            Hark! shouldst i modulo 5 doth equal 0 , then :
                Speak "Buzz".
            Alas, else :
                Speak i.
            Thus endeth the choice.
        Thus endeth the choice.
    Thus endeth the choice.
Thus endeth the for.
```

### Interactive Calculator

```
Hearken a, a numerical of "First number : ".
Hearken op, a scroll of "Operator (+,-,*,/): ".
Hearken b, a numerical of "Second number: ".

Hark! shouldst op doth equal "+" , then :
    Speak a plus b.
Alas, else :
    Hark! shouldst op doth equal "-" , then :
        Speak a minus b.
    Alas, else :
        Hark! shouldst op doth equal "*" , then :
            Speak a times b.
        Alas, else :
            Hark! shouldst op doth equal "/" , then :
                Hark! shouldst b doth equal 0.0 , then :
                    Speak "Cannot divide by zero.".
                Alas, else :
                    Speak a divided by b.
                Thus endeth the choice.
            Alas, else :
                Speak "Unknown operator.".
            Thus endeth the choice.
        Thus endeth the choice.
    Thus endeth the choice.
Thus endeth the choice.
```

---

## Project Structure

```
bardlang/
├── shakespeare_lang.py   # Grammar, compiler, and interpreter
├── bard.py               # CLI runner
├── calculator.bard       # Demo: matrix/factorial script
├── calculator_app.bard   # Demo: interactive calculator
└── README.md
```

---

## Architecture

BardLang is a **transpiled DSL**. Source code goes through three stages:

```
.bard source
     │
     ▼
  Lark Earley parser
  (shakespeare_grammar)
     │
     ▼
  Abstract Syntax Tree
     │
     ▼
  BardToPython transformer
     │
     ▼
  Python source string
     │
     ▼
  exec() in isolated namespace
```

The grammar uses Lark's `earley` parser with `dynamic_complete` lexer and `ambiguity='resolve'` to handle the natural-language keyword conflicts cleanly. `TRUE_KW` and `FALSE_KW` are given priority `.2` to prevent `true`/`false` from being lexed as variable names.

---

## Limitations

- No module/import system — all code must be in one `.bard` file
- No dictionary/map type
- No first-class functions or closures
- No standard library (file I/O, networking, etc.)
- Error messages reference generated Python line numbers, not `.bard` line numbers
- `Should tragedy strike` does not expose the exception message to BardLang code

---

## License

MIT
