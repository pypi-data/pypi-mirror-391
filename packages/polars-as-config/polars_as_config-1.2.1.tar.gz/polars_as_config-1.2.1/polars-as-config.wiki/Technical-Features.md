The core idea is to represent Polars operations and expressions in a JSON
structure. Each step in your data transformation pipeline is an object in the
`"steps"` array of the configuration JSON.

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": {
        "source": "path/to/your/data.csv"
      }
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "new_column": {
          "expr": "add",
          "on": {
            "expr": "col",
            "kwargs": {
              "name": "column_a"
            }
          },
          "kwargs": {
            "other": 10
          }
        }
      }
    },
    {
      "operation": "collect"
    }
  ]
}
```

In this example:

1.  We first load a CSV file using `scan_csv`.
2.  Then, we add a new column named `"new_column"` by adding `10` to
    `"column_a"`.
3.  Finally, we collect the lazy frame into a DataFrame.

This would be equivalent to:

```python
import polars as pl

df = pl.scan_csv("path/to/your/data.csv")
df = df.with_columns(
    new_column=pl.col("column_a").add(10)
)
df = df.collect()
```

## Steps and Operations

Each step is an operation and its arguments. A step defines the function to call
on a dataframe or the `polars` module.

Operations are very similar to how [Expressions](#expressions) are implemented,
but they are top-level.

### Dataframe Context

- If a step specifies `dataframe_in`, the operation is called on that dataframe
- If `dataframe_in` is omitted or `None`, the operation is called on the
  `polars` module
- The result is assigned to the dataframe specified by `dataframe_out` (or
  `None` if omitted)

```python
# Operation on the module
df = pl.scan_csv("file.csv")  # dataframe_in is None or omitted
# Operation on a dataframe
df = df.collect()  # dataframe_in specifies which dataframe
```

For detailed information about managing dataframes, see the
**[Dataframes](Dataframes)** page.

## Passing Arguments and Keyword Arguments

You can pass both positional arguments (`args`) and keyword arguments (`kwargs`)
to Polars operations and expressions.

### Args and Kwargs in Operations

```json
{
  "steps": [
    ... // other operations
    {
      "operation": "scan_csv",
      "args": ["tests/test_data/xy.csv"], // <-- args
      "kwargs": { "has_header": true }    // <-- kwargs
    }
  ]
}
```

is equivalent to:

```python
pl.scan_csv("tests/test_data/xy.csv", has_header=True)
```

## Expressions

Polars expressions can be directly embedded as values for arguments or keyword
arguments. See
[Polars expressions](https://docs.pola.rs/api/python/stable/reference/expressions/index.html)
for more info about expressions.

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": { "source": "tests/test_data/xy.csv" }
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "x_eq_y": {
          "expr": "eq",
          "on": { "expr": "col", "kwargs": { "name": "x" } },
          "kwargs": { "other": { "expr": "col", "kwargs": { "name": "y" } } }
        }
      }
    }
  ]
}
```

### Args and Kwargs in Expressions

Works the same as in operations (top-level function calls).

```json
{
  "operation": "with_columns",
  "kwargs": {
    "x_plus_y": {
      "expr": "add",
      "on": {
        "expr": "col",
        "args": ["x"]
      },
      "args": [
        {
          "expr": "col",
          "args": ["y"]
        }
      ]
    }
  }
}
```

is equivalent to:

```python
df = df.with_columns(x_plus_y=pl.col("x").add(pl.col("y")))
```

### Nested Expressions with "on"

Expressions can be chained or nested by using the `"on"` keyword. The expression
defined in `"on"` becomes the subject upon which the current expression
operates.

```json
{
  "operation": "with_columns",
  "kwargs": {
    "sliced_and_upper": {
      "expr": "str.to_uppercase",
      "on": {
        "expr": "str.slice",
        "on": { "expr": "col", "kwargs": { "name": "first" } },
        "kwargs": { "offset": 1, "length": 2 }
      }
    }
  }
}
```

The rule to get the expression nesting is simple. The most inner expression is
the first one you write in Polars, and any chained expressions move up in the
JSON tree, operating "on" the inner expression.

In this example:

1. We select the column `"first"`.
2. We apply `str.slice` (with `offset: 1`, `length: 2`) _on_ the `"first"`
   column.
3. We then apply `str.to_uppercase` _on_ the result of the `str.slice`
   operation.

It is equivalent to:

```python
df = df.with_columns(
    sliced_and_upper=pl.col(name="first")
        .str.slice(offset=1, length=2)
        .str.to_uppercase()
)
```

This allows for building complex, multi-step transformations for a single
column. A more complex example:

```json
{
  "variables": {
    "multiplier": 3
  },
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": { "source": "tests/test_data/xy.csv" }
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "complex_calc": {
          "expr": "add",
          "on": {
            "expr": "mul",
            "on": { "expr": "col", "args": ["x"] },
            "args": ["$multiplier"]
          },
          "args": [1]
        }
      }
    }
  ]
}
```

This calculates `(x * multiplier) + 1`, or:

```python
df = pl.scan_csv(source="tests/test_data/xy.csv")
df = df.with_columns(complex_calc=pl.col("x").mul(3).add(1))
```

## Variables and Escaping

Configurations can be parameterized using a `"variables"` section. Variables are
prefixed with `$` when used.

```json
{
  "variables": {
    "input_file": "tests/test_data/xy.csv",
    "add_amount": 5
  },
  "steps": [
    { "operation": "scan_csv", "kwargs": { "source": "$input_file" } },
    {
      "operation": "with_columns",
      "kwargs": {
        "x_plus_var": {
          "expr": "add",
          "on": { "expr": "col", "kwargs": { "name": "x" } },
          "kwargs": { "other": "$add_amount" }
        }
      }
    }
  ]
}
```

### Variable Escaping

If you need to use a literal string that starts with a dollar sign, you can
escape it by using two dollar signs (`$$`).

```json
{
  "variables": {
    "my_var": "should_not_be_used"
  },
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": { "source": "tests/test_data/string_join.csv" }
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "literal_dollar": {
          "expr": "lit",
          "kwargs": { "value": "$$my_var" }
        }
      }
    }
  ]
}
```

In the example above, the `literal_dollar` column will contain the string
`"$my_var"` rather than the value of the `my_var` variable.

You can mix escaped and unescaped variables:

```json
{
  "variables": {
    "actual_value": 42.0,
    "file_path": "tests/test_data/xy.csv"
  },
  "steps": [
    { "operation": "scan_csv", "kwargs": { "source": "$file_path" } },
    {
      "operation": "with_columns",
      "kwargs": {
        "escaped_text": {
          "expr": "lit",
          "kwargs": { "value": "$$actual_value" }
        },
        "real_value": {
          "expr": "lit",
          "kwargs": { "value": "$actual_value" }
        }
      }
    }
  ]
}
```

This will result in a column `"escaped_text"` with the literal string
`"$actual_value"` and a column `"real_value"` with the number `42.0`.

## Custom Functions

You can extend `polars-as-config` with your own Python functions. These
functions are typically applied using Polars' `map_elements` (or similar methods
like `apply` or `map_groups`).

### Defining and Registering Custom Functions

First, define your Python function:

```python
# In your Python code
def multiply_by_two(value: int) -> int:
    return value * 2

def hash_row(row: dict) -> str:
    import hashlib
    row_str = "".join(str(val) for val in row.values())
    return hashlib.sha256(row_str.encode()).hexdigest()
```

Then, register it with the `Config` object:

```python
from polars_as_config.config import Config

custom_functions_dict = {
    "multiply_by_two": multiply_by_two,
    "hash_row": hash_row
}

config_runner = Config().add_custom_functions(custom_functions_dict)
# Now use config_runner.run_config(your_json_config)
```

### Using Custom Functions in JSON

To use a registered custom function, specify its name within a
`"custom_function"` key:

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": { "source": "tests/test_data/xy.csv" }
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "x_doubled": {
          "expr": "map_elements",
          "on": { "expr": "col", "kwargs": { "name": "x" } },
          "kwargs": {
            "function": { "custom_function": "multiply_by_two" },
            "return_dtype": "Utf8"
          }
        },
        "row_hash": {
          "expr": "map_elements",
          "on": { "expr": "struct", "args": [{ "expr": "all" }] },
          "kwargs": {
            "function": { "custom_function": "hash_row" },
            "return_dtype": "Utf8"
          }
        }
      }
    }
  ]
}
```

In this example:

- `multiply_by_two` is applied element-wise to column `"x"`.
- `hash_row` is applied to a struct containing all columns, effectively hashing
  each row.

**Note:** Variables cannot be used to specify the name of a custom function
(e.g., `{"custom_function": "$my_func_name"}` is not supported). The function
name must be a literal string.

## Multiple Dataframes

`polars-as-config` supports working with multiple named dataframes
simultaneously within a single configuration. This enables complex
multi-dataframe operations like joins, concatenations, and cross-dataframe
transformations.

### Quick Overview

You can manage dataframes using:

- **`dataframe_in`**: Specifies which dataframe to read from
- **`dataframe_out`**: Specifies which dataframe to write the result to
- **`dataframe`** (legacy): Sets both input and output to the same dataframe

**Example:**

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "customers",
      "kwargs": { "source": "customers.csv" }
    },
    {
      "operation": "scan_csv",
      "dataframe_out": "orders",
      "kwargs": { "source": "orders.csv" }
    },
    {
      "operation": "join",
      "dataframe_in": "customers",
      "dataframe_out": "customer_orders",
      "kwargs": {
        "other": "orders",
        "on": "customer_id"
      }
    }
  ]
}
```

### Dataframe Reference Resolution

When an operation parameter expects a DataFrame or LazyFrame, you can reference
other dataframes by name using simple strings. The system automatically resolves
these references based on type hints:

```json
{
  "operation": "join",
  "dataframe_in": "customers",
  "dataframe_out": "result",
  "kwargs": {
    "other": "orders", // String reference automatically resolved
    "on": "customer_id"
  }
}
```

### For More Information

For comprehensive documentation on dataframe management, including:

- Default dataframe behavior
- Named dataframes
- Creating vs. modifying dataframes
- Legacy `dataframe` syntax
- Best practices and common patterns
- Complete examples

See the dedicated **[Dataframes](Dataframes)** page.

### Conversions

Using the `json_to_polars` and `polars_to_json` helpers, you can easily convert
between both formats.

The following test succeeds:

```python

def test_polars_to_json_to_polars():
    expected = """df = polars.read_csv('data.csv')
df = df.with_columns(polars.add(polars.col('a'), 10).alias('new_column', brrr='a'))
df = df.collect()"""
    code = JsonToPolars().json_to_polars(
        PolarsToJson().polars_to_json(expected), format="dataframe"
    )
    assert code == expected
```

The intermediate format is json (the config of this repository).
