#!/usr/bin/env python3
# "Epic Addition Ritual" — comically overengineered adder
# No external libraries used.

# -------------------------
# Stage directions / flavor
# -------------------------
"""
This program accepts two numbers (integers or floats) from the user (or uses defaults)
and returns their sum. Under the hood it:
 - Performs tokenization of the numeric strings
 - Builds a tiny AST
 - Evaluates the AST via a stack machine
 - Wraps numbers with Descriptor magic
 - Uses a Metaclass to bless the Summoner class
 - Decorates functions with theatrical decorators
 - Passes values through generator pipelines and a coroutine
 - Finally computes the sum and displays it with pomp
Everything is verbose and intentionally ridiculous.
"""

# -------------------------
# Metaclass: Bless the Summoner
# -------------------------
class RitualMeta(type):
    def __new__(mcls, name, bases, namespace):
        # Insist the class has a ritual_signature method (for drama)
        if 'ritual_signature' not in namespace:
            def ritual_signature(self): return f"⟆ Ritual({self.__class__.__name__})"
            namespace['ritual_signature'] = ritual_signature
        cls = super().__new__(mcls, name, bases, namespace)
        return cls

# -------------------------
# Descriptor: wraps a numeric value with verbose access
# -------------------------
class OracleDescriptor:
    def __init__(self, initial=None, name="<oracle>"):
        self._name = name
        self._value = initial

    def __get__(self, instance, owner):
        # When accessed, announce and return
        if instance is None:
            return self
        print(f"[OracleDescriptor:{self._name}] Revealing value to {instance.__class__.__name__}")
        return self._value

    def __set__(self, instance, value):
        print(f"[OracleDescriptor:{self._name}] Accepting offering: {value!r}")
        # naive validation: only numbers or numeric strings allowed
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip()):
            self._value = value
        else:
            raise ValueError("Only numbers or non-empty numeric strings may be offered to the oracle.")

# -------------------------
# Tiny tokenizer / AST builder
# -------------------------
def tokenize_numeric_string(s: str):
    """Turn something like '-12.34' -> tokens ['-', '12.34'] (comically simple)"""
    s = s.strip()
    if not s:
        raise ValueError("Empty token stream — silence is not allowed in ritual.")
    # Recognize a leading sign
    if s[0] in '+-':
        return [s[0], s[1:]]
    return ['+', s]

def build_ast_from_tokens(tokens):
    """Return a tiny AST node representing a signed number."""
    sign, magnitude = tokens
    # Clean magnitude: ensure only one dot and digits
    if magnitude.count('.') > 1:
        raise ValueError("Too many decimal points; the cosmos is displeased.")
    # AST as a tuple (type, sign, magnitude)
    return ('NumberLiteral', 1 if sign == '+' else -1, magnitude)

# -------------------------
# Stack machine evaluator (dramatic)
# -------------------------
def evaluate_number_ast(ast):
    t, sign, magnitude = ast
    assert t == 'NumberLiteral'
    # split int and fraction for theatrical digit-by-digit checking
    if '.' in magnitude:
        int_part, frac_part = magnitude.split('.', 1)
    else:
        int_part, frac_part = magnitude, ''
    # Validate digits one-by-one (because we're extra)
    for ch in (int_part + frac_part):
        if ch and not ch.isdigit():
            raise ValueError(f"Invalid numeric glyph in offering: {ch!r}")
    # Reconstruct numeric value manually to avoid passing through float pitfalls in a boring way:
    # integer part:
    int_val = 0
    for d in int_part or '0':
        int_val = int_val * 10 + (ord(d) - ord('0'))
    # fraction:
    frac_val = 0.0
    power = 1.0
    for d in frac_part:
        power *= 10.0
        frac_val += (ord(d) - ord('0')) / power
    numeric = sign * (int_val + frac_val)
    return numeric

# -------------------------
# Decorative function wrappers (for pomp)
# -------------------------
def announce_stage(f):
    def wrapper(*args, **kwargs):
        print(f"\n=== Announcing: {f.__name__} ===")
        result = f(*args, **kwargs)
        print(f"=== Completed: {f.__name__} -> {result!r} ===\n")
        return result
    wrapper.__name__ = f.__name__
    return wrapper

def reluctant_cache(f):
    cache = {}
    def wrapper(*args):
        key = tuple(args)
        if key in cache:
            print("[reluctant_cache] We already endured this calculation; returning memory.")
            return cache[key]
        print("[reluctant_cache] This is novel; I will remember it for a while.")
        cache[key] = f(*args)
        return cache[key]
    wrapper.__name__ = f.__name__
    return wrapper

# -------------------------
# Coroutine: the Whispering Pipeline
# -------------------------
def whispering_pipe(final_sink):
    """A tiny coroutine that whispers values downstream."""
    print("[whispering_pipe] Spawning whisper coroutine.")
    value = None
    try:
        while True:
            value = (yield)
            print(f"[whispering_pipe] whisper... {value!r} ...to the sink")
            final_sink(value)
    except GeneratorExit:
        print("[whispering_pipe] The whispering ends.")

# -------------------------
# Summoner class: combines everything
# -------------------------
class Summoner(metaclass=RitualMeta):
    left_oracle = OracleDescriptor(name="left")
    right_oracle = OracleDescriptor(name="right")

    def __init__(self, left, right):
        # Accept raw offerings (numbers or strings)
        self.left_oracle = left
        self.right_oracle = right

    def _parse_offer(self, offering):
        """Parse an offer (string or number) into a numeric value using the theater pipeline."""
        # If already numeric, turn to string to follow the same dramatic path
        if isinstance(offering, (int, float)):
            s = str(offering)
        else:
            s = str(offering)
        # Tokenize -> AST -> Evaluate
        tokens = tokenize_numeric_string(s)
        ast = build_ast_from_tokens(tokens)
        num = evaluate_number_ast(ast)
        return num

    @announce_stage
    @reluctant_cache
    def awaken_and_sum(self):
        # Parse offerings
        left_val = self._parse_offer(self.left_oracle)
        right_val = self._parse_offer(self.right_oracle)

        # Now we pass both numbers through a whispering pipeline (generator + sink)
        results = []
        def sink(v): results.append(v)

        coroutine = whispering_pipe(sink)
        next(coroutine)  # prime it
        coroutine.send(left_val)
        coroutine.send(right_val)
        coroutine.close()

        # Very small stack-based bytecode we invented for addition:
        # bytecodes: PUSH <value>, ADD -> pops two, pushes sum
        stack = []
        def PUSH(v): stack.append(v)
        def ADD(): 
            b = stack.pop(); a = stack.pop()
            stack.append(a + b)

        # Push both whispered results in order and add
        PUSH(results[0])
        PUSH(results[1])
        ADD()

        final = stack.pop()

        # Wrap with a faux monadic result that insists on being pretty-printed
        class ResultEnvelope:
            def __init__(self, value):
                self._value = value
            def __repr__(self):
                return f"<SumResult value={self._value!r} — rendered with gratuitous flourish>"
            def value(self):
                return self._value

        return ResultEnvelope(final)

# -------------------------
# Utility: gentle input parsing with defaults
# -------------------------
def solicit_number(prompt, default=None):
    raw = input(f"{prompt} [{default}]: ").strip()
    if raw == '':
        return default
    return raw  # keep as string to flow through pipeline

# -------------------------
# Main ritual: interact with user or run demo
# -------------------------
def main():
    print("Welcome to the Epic Addition Ritual (no external libraries were harmed).")
    print("You may supply integer or decimal numbers. Examples: 42, -3.14, +7.0")
    try:
        a = solicit_number("Offer the LEFT number", default="3.14")
        b = solicit_number("Offer the RIGHT number", default="2.71")
    except (EOFError, KeyboardInterrupt):
        print("\nA hush falls. Using defaults 3.14 and 2.71.")
        a, b = "3.14", "2.71"

    summoner = Summoner(a, b)
    print(summoner.ritual_signature())  # courtesy from metaclass
    result_envelope = summoner.awaken_and_sum()

    # Final declaration
    print("Behold the final proclamation:")
    print(result_envelope)           # pretty repr
    print("Raw numeric value:", result_envelope.value())

if __name__ == "__main__":
    main()
