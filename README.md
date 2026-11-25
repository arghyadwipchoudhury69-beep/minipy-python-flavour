# MathPy – A Math-Focused Python-Flavoured Language

MathPy is a small educational programming language inspired by Python. Its interpreter is written in Python. It has built-in math functions, so programs can calculate factorials, primes, Fibonacci numbers and more with one short command.

## Built-in functions

| Function | What it does | Example | Result |
|---|---|---|---|
| `say(a, b, ...)` | Prints one or more values | `say("Hi", 5)` | `Hi 5` |
| `ask(prompt)` | Reads input (numbers are converted automatically) | `n = ask("n: ")` | |
| `fact(n)` | Factorial of n | `fact(5)` | `120` |
| `isprime(n)` | Checks whether n is prime | `isprime(7)` | `true` |
| `fibo(n)` | n-th Fibonacci number | `fibo(10)` | `55` |
| `hcf(a, b)` | Highest common factor (GCD) | `hcf(48, 18)` | `6` |
| `root(x)` | Square root | `root(81)` | `9` |
| `power(a, b)` | a raised to the power b | `power(2, 10)` | `1024` |

## Language features

- Variables: `x = 10`
- Operators: `+  -  *  /  //  %  **`
- Comparisons: `==  !=  <  <=  >  >=`
- Logic: `and`, `or`, `not`
- Shortcuts: `+=  -=  *=  /=`
- Decisions: `if` / `elif` / `else`
- Loops: `while` and `for i in range(...)`, with `break` and `continue`
- Comments starting with `#`
- Clear errors, such as `MathPy error: root() cannot take a negative number`
- A safety limit stops infinite loops after 1,000,000 steps

## How to run

1. Install Python 3.8 or later.
2. Save `mathpy.py` and your MathPy program (for example `example.mth`, copied from the section below) in the same folder.
3. Open a terminal or Command Prompt in that folder.
4. Run:

```bash
python mathpy.py example.mth
```

MathPy programs use the `.mth` extension.

## Example program (save as `example.mth`)

```python
n = ask("Enter a whole number: ")
say("Factorial of", n, "is", fact(n))
say("Is", n, "prime?", isprime(n))

for i in range(2, n + 1):
    if isprime(i):
        say(i)
```

## Sample output (input: 10)

```
Enter a whole number: Factorial of 10 is 3628800
Is 10 prime? false
2
3
5
7
```

## Files

| File | Description |
|---|---|
| `mathpy.py` | The interpreter |
| `README.md` | This file |

## Limitations

MathPy does not yet support user-defined functions, lists or strings methods. Loops use `range(...)` only.
