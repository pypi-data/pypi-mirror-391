# Dataframe Management

This page covers everything you need to know about managing dataframes in
polars-as-config, including the default dataframe behavior, named dataframes,
and the new explicit `dataframe_in`/`dataframe_out` syntax.

## Table of Contents

- [Overview](#overview)
- [Default Dataframe Behavior](#default-dataframe-behavior)
- [Named Dataframes](#named-dataframes)
- [Explicit Dataframe Management with `dataframe_in` and `dataframe_out`](#explicit-dataframe-management-with-dataframe_in-and-dataframe_out)
- [Legacy `dataframe` Syntax](#legacy-dataframe-syntax)
- [Automatic Dataframe Reference Resolution](#automatic-dataframe-reference-resolution)
- [Return Values](#return-values)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Overview

`polars-as-config` supports working with multiple dataframes simultaneously
within a single configuration. This enables complex multi-dataframe operations
like joins, concatenations, and cross-dataframe transformations.

Each step in your configuration can specify:

- Which dataframe to read from (`dataframe_in`)
- Which dataframe to write the result to (`dataframe_out`)

This explicit approach gives you fine-grained control over your data processing
pipeline.

## Default Dataframe Behavior

When no dataframe field is specified in a step, the operation uses the **default
dataframe** identified internally by `None`. This maintains backward
compatibility with existing single-dataframe configurations.

**Example:**

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "kwargs": { "source": "data.csv" }
    },
    {
      "operation": "with_columns",
      "kwargs": {
        "new_col": { "expr": "lit", "kwargs": { "value": "default" } }
      }
    },
    {
      "operation": "collect"
    }
  ]
}
```

Both steps above operate on the same default dataframe (identified internally as
`None`). This is the simplest way to work with polars-as-config when you only
need a single dataframe.

**Python Usage:**

```python
from polars_as_config.config import Config

config = {
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "data.csv"}},
    {"operation": "with_columns", "kwargs": {"x_doubled": {"expr": "mul", "on": {"expr": "col", "kwargs": {"name": "x"}}, "kwargs": {"other": 2}}}}
  ]
}

result = Config().run_config(config)
# result is a dict: {None: LazyFrame}

df = result[None].collect()  # Get the default dataframe
```

For convenience, the standalone `run_config()` function returns only the default
dataframe:

```python
from polars_as_config.config import run_config

result = run_config(config)  # Returns the default dataframe directly
df = result.collect()
```

## Named Dataframes

You can create and manage multiple dataframes by giving them names. Each
dataframe maintains its own state throughout the configuration.

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
      "operation": "with_columns",
      "dataframe_in": "customers",
      "dataframe_out": "customers",
      "kwargs": {
        "customer_type": { "expr": "lit", "kwargs": { "value": "premium" } }
      }
    },
    {
      "operation": "with_columns",
      "dataframe_in": "orders",
      "dataframe_out": "orders",
      "kwargs": {
        "order_status": { "expr": "lit", "kwargs": { "value": "active" } }
      }
    }
  ]
}
```

In this example:

- The first step creates a dataframe named `"customers"`
- The second step creates a separate dataframe named `"orders"`
- The third step modifies the `"customers"` dataframe
- The fourth step modifies the `"orders"` dataframe

Both dataframes exist independently and can be accessed from the result.

## Explicit Dataframe Management with `dataframe_in` and `dataframe_out`

The `dataframe_in` and `dataframe_out` fields provide explicit control over
which dataframe each operation reads from and writes to.

### `dataframe_in`

Specifies which dataframe the operation should read from. If omitted, defaults
to `None` (the default dataframe).

### `dataframe_out`

Specifies which dataframe the operation result should be assigned to. If
omitted, defaults to `None` (the default dataframe).

### Creating New Dataframes

When `dataframe_out` differs from `dataframe_in`, you create a new dataframe
without modifying the original:

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "raw_data",
      "kwargs": { "source": "data.csv" }
    },
    {
      "operation": "filter",
      "dataframe_in": "raw_data",
      "dataframe_out": "filtered_data",
      "kwargs": {
        "predicate": {
          "expr": "gt",
          "on": { "expr": "col", "kwargs": { "name": "age" } },
          "kwargs": { "other": 18 }
        }
      }
    },
    {
      "operation": "filter",
      "dataframe_in": "raw_data",
      "dataframe_out": "premium_data",
      "kwargs": {
        "predicate": {
          "expr": "eq",
          "on": { "expr": "col", "kwargs": { "name": "tier" } },
          "kwargs": { "other": "premium" }
        }
      }
    }
  ]
}
```

This creates three dataframes:

- `raw_data`: The original data
- `filtered_data`: Only rows where age > 18
- `premium_data`: Only rows where tier == "premium"

### Modifying Dataframes In-Place

When `dataframe_in` and `dataframe_out` are the same, you modify the dataframe
in-place:

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "data",
      "kwargs": { "source": "data.csv" }
    },
    {
      "operation": "with_columns",
      "dataframe_in": "data",
      "dataframe_out": "data",
      "kwargs": {
        "new_column": { "expr": "lit", "kwargs": { "value": 42 } }
      }
    }
  ]
}
```

The `data` dataframe is modified to include the new column.

### Operations Without Input Dataframes

Some operations, like `scan_csv` or `read_parquet`, don't operate on an existing
dataframe. For these, you typically only specify `dataframe_out`:

```json
{
  "operation": "scan_csv",
  "dataframe_out": "my_data",
  "kwargs": { "source": "file.csv" }
}
```

Internally, when `dataframe_in` is omitted (or `None`), the operation is called
on the `polars` module directly (e.g., `pl.scan_csv(...)`), or on the default
(`None`) dataframe if it was initialized. It is therefor advised to specify all
dataframes or none, not an unclear mix.

## Legacy `dataframe` Syntax

For backward compatibility, the original `dataframe` field continues to work.
When used, it sets both `dataframe_in` and `dataframe_out` to the same value.
The legacy system is not adviced to be used, it is only there for backwards
compatibilty.

**Legacy Syntax:**

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe": "customers",
      "kwargs": { "source": "customers.csv" }
    },
    {
      "operation": "with_columns",
      "dataframe": "customers",
      "kwargs": {
        "customer_type": { "expr": "lit", "kwargs": { "value": "premium" } }
      }
    }
  ]
}
```

**Equivalent New Syntax:**

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "customers",
      "kwargs": { "source": "customers.csv" }
    },
    {
      "operation": "with_columns",
      "dataframe_in": "customers",
      "dataframe_out": "customers",
      "kwargs": {
        "customer_type": { "expr": "lit", "kwargs": { "value": "premium" } }
      }
    }
  ]
}
```

### Restrictions

**You cannot mix legacy and new syntax in the same step.** Attempting to use
both `dataframe` and either `dataframe_in` or `dataframe_out` in the same step
will raise a `ValueError`:

```json
{
  "operation": "with_columns",
  "dataframe": "my_data",
  "dataframe_out": "new_data",  // ERROR: Cannot mix syntaxes
  "kwargs": {...}
}
```

## Automatic Dataframe Reference Resolution

One of the most powerful features of the multiple dataframes system is
**automatic dataframe reference resolution**. When an operation parameter
expects a DataFrame or LazyFrame (detected through Python type hints), you can
reference other dataframes by name using simple strings.

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
        "other": "orders", // String reference to the "orders" dataframe
        "left_on": "customer_id",
        "right_on": "customer_id",
        "how": "inner"
      }
    }
  ]
}
```

In the `join` operation:

- The operation reads from the `"customers"` dataframe
- The `"other"` parameter references the `"orders"` dataframe by name
- The system automatically detects that `other` expects a DataFrame/LazyFrame
  and substitutes the actual dataframe object
- The result is stored in a new `"customer_orders"` dataframe

### How It Works

The system inspects the type hints of Polars methods. When a parameter is
annotated as expecting a `DataFrame` or `LazyFrame`, string values for that
parameter are treated as dataframe references rather than literal strings.

This means the feature works seamlessly with any Polars operation that accepts
dataframes as parameters, including:

- `join()` operations
- `concat()` operations
- `union()` operations
- Any custom operations that accept DataFrame/LazyFrame parameters

### Type-Safe Resolution

The type-hint based detection is robust and handles:

- Direct type annotations (`pl.DataFrame`, `pl.LazyFrame`)
- String-based forward references (`"DataFrame"`, `"LazyFrame"`)
- Union types (`Union[DataFrame, LazyFrame]`)
- TypeVar constraints

This ensures that only parameters that truly expect dataframes are resolved,
preventing accidental substitution of string values.

## Return Values

### Using `Config.run_config()`

When using the `Config` class directly, `run_config()` returns a dictionary
mapping dataframe names to their final states:

```python
from polars_as_config.config import Config

config = {
  "steps": [
    {"operation": "scan_csv", "dataframe_out": "df1", "kwargs": {"source": "file1.csv"}},
    {"operation": "scan_csv", "dataframe_out": "df2", "kwargs": {"source": "file2.csv"}}
  ]
}

result = Config().run_config(config)
# result is a dict: {"df1": LazyFrame, "df2": LazyFrame}

df1_final = result["df1"].collect()
df2_final = result["df2"].collect()
```

### Using the Standalone `run_config()` Function

For backward compatibility, the standalone `run_config()` function returns only
the default dataframe:

```python
from polars_as_config.config import run_config

config = {
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "file.csv"}},
    {"operation": "filter", "kwargs": {"predicate": ...}}
  ]
}

result = run_config(config)  # Returns the default dataframe directly
df = result.collect()
```

## Error Handling

The system provides clear error messages when things go wrong:

### Non-Existent Dataframe Reference

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "customers",
      "kwargs": { "source": "customers.csv" }
    },
    {
      "operation": "join",
      "dataframe_in": "customers",
      "dataframe_out": "result",
      "kwargs": {
        "other": "nonexistent_orders", // This dataframe doesn't exist
        "left_on": "id",
        "right_on": "customer_id"
      }
    }
  ]
}
```

**Error:**

```
ValueError: Dataframe nonexistent_orders not found in current dataframes.
It is possible that the dataframe was not created in the previous steps.
```

### Mixing Legacy and New Syntax

```json
{
  "operation": "with_columns",
  "dataframe": "my_data",
  "dataframe_in": "my_data",  // ERROR
  "kwargs": {...}
}
```

**Error:**

```
ValueError: use of old and new `dataframe` syntax is not allowed
```

## Best Practices

### 1. Be Explicit with `dataframe_in` and `dataframe_out`

Even when modifying in-place, explicitly specify both fields for clarity:

```json
{
  "operation": "with_columns",
  "dataframe_in": "customers",
  "dataframe_out": "customers",
  "kwargs": {...}
}
```

### 2. Optionally use the Default Dataframe for Simple Cases

For simple single-dataframe transformations, omitting the dataframe fields keeps
your config lean:

```json
{
  "steps": [
    {"operation": "scan_csv", "kwargs": {"source": "data.csv"}},
    {"operation": "with_columns", "kwargs": {...}},
    {"operation": "collect"}
  ]
}
```

## Common Patterns

### Pattern 1: Loading Multiple Data Sources

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
      "operation": "scan_csv",
      "dataframe_out": "products",
      "kwargs": { "source": "products.csv" }
    }
  ]
}
```

### Pattern 2: Creating Multiple Views of the Same Data

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "all_data",
      "kwargs": { "source": "data.csv" }
    },
    {
      "operation": "filter",
      "dataframe_in": "all_data",
      "dataframe_out": "active_users",
      "kwargs": {
        "predicate": {
          "expr": "eq",
          "on": { "expr": "col", "kwargs": { "name": "status" } },
          "kwargs": { "other": "active" }
        }
      }
    },
    {
      "operation": "filter",
      "dataframe_in": "all_data",
      "dataframe_out": "inactive_users",
      "kwargs": {
        "predicate": {
          "expr": "eq",
          "on": { "expr": "col", "kwargs": { "name": "status" } },
          "kwargs": { "other": "inactive" }
        }
      }
    }
  ]
}
```

### Pattern 3: Multi-Step Join Pipeline

```json
{
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "orders",
      "kwargs": { "source": "orders.csv" }
    },
    {
      "operation": "scan_csv",
      "dataframe_out": "products",
      "kwargs": { "source": "products.csv" }
    },
    {
      "operation": "scan_csv",
      "dataframe_out": "customers",
      "kwargs": { "source": "customers.csv" }
    },
    {
      "operation": "join",
      "dataframe_in": "orders",
      "dataframe_out": "orders_with_products",
      "kwargs": {
        "other": "products",
        "left_on": "product_id",
        "right_on": "id",
        "how": "left"
      }
    },
    {
      "operation": "join",
      "dataframe_in": "orders_with_products",
      "dataframe_out": "complete_orders",
      "kwargs": {
        "other": "customers",
        "left_on": "customer_id",
        "right_on": "id",
        "how": "left"
      }
    }
  ]
}
```

### Pattern 6: Using Variables with Multiple Dataframes

```json
{
  "variables": {
    "customer_file": "customers.csv",
    "orders_file": "orders.csv",
    "join_key": "customer_id"
  },
  "steps": [
    {
      "operation": "scan_csv",
      "dataframe_out": "customers",
      "kwargs": { "source": "$customer_file" }
    },
    {
      "operation": "scan_csv",
      "dataframe_out": "orders",
      "kwargs": { "source": "$orders_file" }
    },
    {
      "operation": "join",
      "dataframe_in": "customers",
      "dataframe_out": "result",
      "kwargs": { "other": "orders", "on": "$join_key", "how": "inner" }
    }
  ]
}
```
