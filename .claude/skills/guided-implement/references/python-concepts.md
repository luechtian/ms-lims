# Python Concepts Index

Python 3.13 idioms likely to appear in this project's tasks. Compact by design — a place to decide whether a concept needs a deep dive, not a textbook.

## Modern syntax the constitution allows

- **Type hints everywhere.** Use `list[int]` / `dict[str, int]`, not `List[int]` / `Dict[str, int]` (PEP 585). Use `X | None` for optionals (PEP 604), not `Optional[X]`. Function signatures and class attributes should carry hints.
- **`match` / `case`** for structural matching. Fair game but often over-reached; a plain `if/elif` chain is fine for simple dispatch.
- **f-strings** with `=` for debug (`f"{value=}"`). Avoid `%` formatting and `.format()` unless there's a concrete reason (logging's deferred formatting is one).
- **walrus `:=`** sparingly — when it genuinely removes duplication, not to show off.
- **`enumerate` / `zip` / comprehensions** beat `range(len(...))` and manual loops. A junior red flag: indexing into a list by counter.

## Properties and descriptors

A `@property` turns a method into an attribute access — `person.full_name` not `person.full_name()`. Use for derived values (like a computed `full_name` from `first_name + last_name`). Don't use a property that does expensive I/O or has side effects; attribute access should be cheap and idempotent.

Descriptors are one layer deeper (`__get__`, `__set__`, `__delete__`) — relevant for understanding how Django's `Field` and `Manager` work under the hood, but you'll rarely write one yourself. Don't deep-dive unless the user asks.

## Dunder methods worth knowing

- **`__str__`** — human-readable representation. Shown in `{{ obj }}` templates and the Django admin list. Every model in this project has one.
- **`__repr__`** — unambiguous debug representation. Django auto-generates a decent one; override only when the default hides useful info.
- **`__eq__` / `__hash__`** — rarely needed on Django models (PK-based equality is provided). If you override one, understand why both must usually be overridden together.

## Data containers

- **`dataclass`** / **`@dataclass(slots=True, frozen=True)`** — lightweight value objects. Not a replacement for Django models (no persistence), but good for passing structured data between functions.
- **`NamedTuple`** — even lighter; immutable and tuple-unpackable. Preferred when you want the tuple semantics.
- **`TypedDict`** — type hints for dict-shaped inputs. Handy at API boundaries.

## Context managers

`with open(...)` is the usual example. Useful when you need guaranteed cleanup — file handles, DB transactions (`transaction.atomic()`), locks. Write one with `@contextlib.contextmanager` or the class-based `__enter__` / `__exit__` protocol.

Common beginner miss: `django.db.transaction.atomic()` as a block, not as a decorator, when you only want part of a view's work to be transactional.

## Iterators, generators, and laziness

- **Generator functions** (`yield`) produce values on demand; memory-friendly for large sequences.
- **`itertools`** is the standard library's iterator toolkit; `chain`, `groupby`, `islice` are worth knowing by name.
- **Django QuerySets are lazy** — no SQL runs until you iterate, slice, or call a terminal like `.count()`, `.first()`, `list(...)`. Teach this alongside manager methods.

## Exceptions

- **Raise specific, not generic.** `ValueError` is better than `Exception`; Django's `ValidationError` is better than `ValueError` in model code. Custom subclasses when the caller might want to catch only this class.
- **EAFP over LBYL.** "Easier to ask forgiveness than permission" — try the operation and handle the exception, don't pre-check every condition. Exceptions: when the happy path is rare, or when the precheck is much cheaper.
- **Never bare `except:`** — always name the exception class. A bare except swallows `KeyboardInterrupt` and makes debugging miserable.

## Imports

- Absolute imports across apps (`from parties.api import ...`), not relative (`from ..models import ...`). Relative imports within a single package are acceptable but the project's preference leans absolute.
- Group imports: stdlib, third-party, first-party (Django, this project), blank line between groups. Ruff enforces this automatically — `uv run ruff format .` will fix ordering.

## Testing patterns (pytest)

- **Arrange / Act / Assert** — three visual blocks separated by blank lines. A junior test that reads as one long blob of setup and assertions is hard to maintain.
- **One logical assertion per test.** Multiple `assert` lines are fine if they're aspects of the same claim; a test that verifies five unrelated things is five tests.
- **Fixtures over setUp.** `@pytest.fixture` is the pytest-native equivalent of `setUp`. Factories + fixtures beat hand-rolled object creation in every test.
- **Parametrize** for the same test across inputs. `@pytest.mark.parametrize("x,expected", [...])` collapses repetitive test variants.

## Style enforced by ruff

Don't hand-enforce — run `uv run ruff format .` and `uv run ruff check .`. But know what's being enforced so you can explain review findings:

- PEP 8 naming: `snake_case` for functions and variables, `PascalCase` for classes, `SCREAMING_SNAKE` for module-level constants.
- Line length: whatever ruff is configured to — don't fight the formatter.
- No unused imports, no `import *`.
- f-strings without placeholders flagged (convert to a plain string).

## Where to go deeper

- Official tutorial and library docs: <https://docs.python.org/3.13/>
- PEPs worth knowing by number: 8 (style), 20 (zen), 257 (docstrings), 484/526 (type hints), 585 (generic builtins), 604 (union syntax), 634–636 (match).
- Real Python (<https://realpython.com/>) for long-form walkthroughs.
