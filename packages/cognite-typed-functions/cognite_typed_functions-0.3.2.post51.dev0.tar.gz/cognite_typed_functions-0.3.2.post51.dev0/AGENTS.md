# Agents Instructions

We are bulding an enterprise grade framework for building type-safe
Cognite Functions with automatic OpenAPI schema generation, request
validation, and comprehensive error handling. We strive for the highest
level of quality and professionalism.

The framework will be used by our customers to build their own Cognite
Functions. Thus the framework must be simple and easy to use. We need to
keep the code clean and robust as we cannot update the code of a
deployed function. The customer would need to update the function and
redeploy.

## Environment

- This repository uses `uv`.
- To run python, use `uv run python`.
- To run the tests, use `uv run pytest`.

## Python

- This library uses Python 3.10+.
- All code **MUST** be type-annotated and all code needs to type check using `pyright`.
- Always annotate variables that are assigned with an empty lists or dictionary.
- Using `Any` or `# type: ignore` is the last resort. All type ignores must be specific to the error code that is being ignored.
- Use `ParamSpec` for decorators.
- Use builtin generic types instead of importing e.g `Optional`, `Dict`, `List` from `typing`.
- Use `Sequence` instead of `list` if it is expected to be immutable to avoid shared mutable state and enable covariant behavior.
- Use `Mapping` instead of `dict` if it is expected to be immutable to avoid shared mutable state.
- All imports at the top of the file.
- All imports must be at the top of the file.
- Write all docstrings in Google style, use consise and professional language.

## Code Structure

- Keep the number of lines of code in a file to less than 500 lines.
- Prefer smaller simpler functions and composability over larger nested complex functions. Follow the OPEN/CLOSED principle.
- Avoid nested functions, use extraction and return-early patterns.
- Do not mix error-handling and domain logic in the same function. Don't compress logic with different concerns into a single function.
- Make sure we avoid entropy dumps, e.g modules with different unrelated utilities.
- Avoid premature abstractions. But do suggest creating better abstractions, patterns, and protocols when the structure emerges.
