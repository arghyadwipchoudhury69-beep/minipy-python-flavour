"""\
MathPy: a small math-focused, Python-flavoured language.

Built-in functions:
    say(a, b, ...)   -> print values
    ask(prompt)      -> read input (numbers are converted automatically)
    fact(n)          -> factorial of n
    isprime(n)       -> true if n is prime, otherwise false
    fibo(n)          -> n-th Fibonacci number (fibo(0)=0, fibo(1)=1)
    hcf(a, b)        -> highest common factor (GCD)
    root(x)          -> square root
    power(a, b)      -> a raised to the power b

Statements: assignment, +=, -=, *=, /=, if / elif / else, while, for ... in range(...),
break, continue.

Run: python mathpy.py example.mth
"""
import ast
import math
import sys
from pathlib import Path

MAX_STEPS = 1_000_000
MAX_FACT = 5000
MAX_FIBO = 100000
MAX_EXPONENT = 10000


class MathPyError(Exception):
    pass


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


def convert_input(text):
    """Turn typed text into an int or float when possible."""
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


def as_int(value, fname):
    if isinstance(value, bool):
        raise MathPyError(f"{fname}() needs a whole number")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    raise MathPyError(f"{fname}() needs a whole number")


def as_number(value, fname):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MathPyError(f"{fname}() needs a number")
    return value


def show(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


# ---------- the math built-ins ----------

def fn_fact(n):
    n = as_int(n, "fact")
    if n < 0:
        raise MathPyError("fact() needs a number that is 0 or more")
    if n > MAX_FACT:
        raise MathPyError(f"fact() is limited to {MAX_FACT}")
    return math.factorial(n)


def fn_isprime(n):
    n = as_int(n, "isprime")
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def fn_fibo(n):
    n = as_int(n, "fibo")
    if n < 0:
        raise MathPyError("fibo() needs a number that is 0 or more")
    if n > MAX_FIBO:
        raise MathPyError(f"fibo() is limited to {MAX_FIBO}")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fn_hcf(a, b):
    return math.gcd(as_int(a, "hcf"), as_int(b, "hcf"))


def fn_root(x):
    x = as_number(x, "root")
    if x < 0:
        raise MathPyError("root() cannot take a negative number")
    result = math.sqrt(x)
    return int(result) if result.is_integer() else result


def fn_power(a, b):
    a = as_number(a, "power")
    b = as_number(b, "power")
    if abs(b) > MAX_EXPONENT:
        raise MathPyError(f"power() exponent is limited to {MAX_EXPONENT}")
    return a ** b


MATH_FUNCTIONS = {
    "fact": (1, fn_fact),
    "isprime": (1, fn_isprime),
    "fibo": (1, fn_fibo),
    "hcf": (2, fn_hcf),
    "root": (1, fn_root),
    "power": (2, fn_power),
}


class Interpreter:
    def __init__(self):
        self.variables = {}
        self.steps = 0

    # ----- expressions -----
    def evaluate(self, node):
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            raise MathPyError(f"Unknown variable: {node.id}")

        if isinstance(node, ast.BinOp):
            return self.binary(node.op, self.evaluate(node.left), self.evaluate(node.right))

        if isinstance(node, ast.UnaryOp):
            value = self.evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.Not):
                return not value
            raise MathPyError("Unary operator not supported")

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for v in node.values:
                    result = self.evaluate(v)
                    if not result:
                        return result
                return result
            result = False
            for v in node.values:
                result = self.evaluate(v)
                if result:
                    return result
            return result

        if isinstance(node, ast.Compare):
            left = self.evaluate(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self.evaluate(comparator)
                if not self.compare(op, left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return self.call(node.func.id, [self.evaluate(a) for a in node.args])

        raise MathPyError("This MathPy expression is not supported")

    def binary(self, op, left, right):
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return fn_power(left, right)
        raise MathPyError("Operator not supported")

    def compare(self, op, a, b):
        if isinstance(op, ast.Eq):
            return a == b
        if isinstance(op, ast.NotEq):
            return a != b
        if isinstance(op, ast.Lt):
            return a < b
        if isinstance(op, ast.LtE):
            return a <= b
        if isinstance(op, ast.Gt):
            return a > b
        if isinstance(op, ast.GtE):
            return a >= b
        raise MathPyError("Comparison not supported")

    def call(self, name, args):
        if name == "say":
            print(" ".join(show(a) for a in args))
            return None
        if name == "ask":
            if len(args) != 1:
                raise MathPyError("ask() needs exactly 1 argument")
            return convert_input(input(str(args[0])))
        if name in MATH_FUNCTIONS:
            arity, func = MATH_FUNCTIONS[name]
            if len(args) != arity:
                raise MathPyError(f"{name}() needs exactly {arity} argument(s)")
            return func(*args)
        raise MathPyError(f"Unknown function: {name}")

    # ----- statements -----
    def tick(self):
        self.steps += 1
        if self.steps > MAX_STEPS:
            raise MathPyError("Program stopped: too many steps (possible infinite loop)")

    def run_block(self, statements):
        for statement in statements:
            self.run_statement(statement)

    def run_statement(self, st):
        self.tick()

        if isinstance(st, ast.Assign):
            if len(st.targets) != 1 or not isinstance(st.targets[0], ast.Name):
                raise MathPyError("Only simple variable assignments are supported")
            self.variables[st.targets[0].id] = self.evaluate(st.value)

        elif isinstance(st, ast.AugAssign):
            if not isinstance(st.target, ast.Name):
                raise MathPyError("Only simple variable assignments are supported")
            name = st.target.id
            if name not in self.variables:
                raise MathPyError(f"Unknown variable: {name}")
            self.variables[name] = self.binary(st.op, self.variables[name], self.evaluate(st.value))

        elif isinstance(st, ast.Expr):
            self.evaluate(st.value)

        elif isinstance(st, ast.If):
            if self.evaluate(st.test):
                self.run_block(st.body)
            else:
                self.run_block(st.orelse)

        elif isinstance(st, ast.While):
            while self.evaluate(st.test):
                self.tick()
                try:
                    self.run_block(st.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue

        elif isinstance(st, ast.For):
            if not (isinstance(st.target, ast.Name)
                    and isinstance(st.iter, ast.Call)
                    and isinstance(st.iter.func, ast.Name)
                    and st.iter.func.id == "range"
                    and 1 <= len(st.iter.args) <= 3):
                raise MathPyError("for loops must look like: for i in range(...):")
            bounds = [as_int(self.evaluate(a), "range") for a in st.iter.args]
            for value in range(*bounds):
                self.tick()
                self.variables[st.target.id] = value
                try:
                    self.run_block(st.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue

        elif isinstance(st, ast.Break):
            raise BreakSignal()

        elif isinstance(st, ast.Continue):
            raise ContinueSignal()

        elif isinstance(st, ast.Pass):
            pass

        else:
            raise MathPyError("This MathPy statement is not supported")


def run_file(filename):
    try:
        source = Path(filename).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=filename)
        Interpreter().run_block(tree.body)
    except (BreakSignal, ContinueSignal):
        print("MathPy error: break/continue used outside a loop")
        sys.exit(1)
    except SyntaxError as error:
        print(f"MathPy syntax error (line {error.lineno}): {error.msg}")
        sys.exit(1)
    except (MathPyError, OSError, TypeError, ZeroDivisionError, OverflowError, ValueError) as error:
        print(f"MathPy error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python mathpy.py <program.mth>")
        sys.exit(1)
    run_file(sys.argv[1])
