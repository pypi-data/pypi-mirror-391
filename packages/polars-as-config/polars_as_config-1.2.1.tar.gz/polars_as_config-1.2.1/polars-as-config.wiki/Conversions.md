# Conversions

Convert between Python Polars code and JSON configuration format.

## Polars to JSON

Convert Python Polars code to JSON configuration.

```python
from polars_as_config.polars_to_json import PolarsToJson

converter = PolarsToJson()
python_code = """
df = polars.read_csv('data.csv')
df = df.with_columns(polars.col('x').add(1).alias('x_plus_1'))
"""
json_config = converter.polars_to_json(python_code)
```

**Output:**

```json
[
  {
    "operation": "read_csv",
    "args": ["data.csv"],
    "kwargs": {},
    "dataframe": "df"
  },
  {
    "operation": "with_columns",
    "args": [],
    "kwargs": {
      "x_plus_1": {
        "expr": "alias",
        "args": ["x_plus_1"],
        "kwargs": {},
        "on": {
          "expr": "add",
          "args": [1],
          "kwargs": {},
          "on": { "expr": "col", "args": ["x"], "kwargs": {} }
        }
      }
    },
    "dataframe": "df"
  }
]
```

> **Note:**  
> When converting Python Polars code to JSON configuration (and vice versa),
> each operation must be written on a separate line. This is because the
> converter evaluates the code line by line, with one operation per line.
> Chained or multiple operations on a single line are **not supported**—split
> them into individual lines for correct conversion.

For example, **do this**:

### Custom Functions

```python
converter = PolarsToJson(custom_functions={'my_func'})
# or auto-discover
converter = PolarsToJson(allow_function_discovery=True)
```

### From functions instead of strings

To be able to convert Polars from a function instead of raw code as a string, we
added `polars_function_to_json`, which takes a `Callable` with the same format
desired above. It converts the code to a string to do exactly the same as the
previous.

## JSON to Polars

Convert JSON configuration back to Python code.

```python
from polars_as_config.json_to_polars import JsonToPolars

converter = JsonToPolars()
steps = [
  {"operation": "read_csv", "args": ["data.csv"]},
  {"operation": "select", "kwargs": {"columns": ["x", "y"]}}
]

# Multi-line format
code = converter.json_to_polars(steps, format="dataframe")
print(code)
# df = polars.read_csv('data.csv')
# df = df.select(columns=['x', 'y'])

# Single-line format
code = converter.json_to_polars(steps, format="oneliner")
print(code)
# polars.read_csv('data.csv').select(columns=['x', 'y'])
```

## Supported Features

- **Basic operations**: All standard Polars operations
- **Nested expressions**: Complex chained operations like
  `col('x').str.contains('pattern')`
- **Multiple dataframes**: Handle operations across different dataframes
- **Lists and dicts**: Complex argument structures
- **Custom functions**: User-defined functions with validation
- **Mixed arguments**: Both positional and keyword arguments

For expression syntax, see
[Technical Features](Technical-Features#expression-format-overview).
