# Polars as Config

Welcome to the **polars-as-config** documentation! This library allows you to
define Polars data processing operations using JSON configuration files, making
it easy to serialize, store, and share data transformation pipelines.

## 📖 Documentation

### [Technical Features](Technical-Features)

Complete guide to using polars-as-config including:

- Configuration format and structure
- Expression syntax and nested operations
- Variables and escaping
- Custom functions integration
- Examples and practical usage patterns

### [Dataframes](Dataframes)

Guide to dataframe management:

- Default dataframe behavior
- Named dataframes with `dataframe_in` and `dataframe_out`
- Legacy `dataframe` syntax
- Automatic dataframe reference resolution
- Best practices and common patterns

### [Conversions](Conversions)

Bidirectional conversion between Python Polars code and JSON configuration:

- Convert Python code to JSON configuration
- Convert JSON configuration back to Python code
- Support for complex expressions and custom functions
- Quick reference examples

### [Reasoning](Reasoning)

Background information on the design decisions and motivations behind
polars-as-config.

## 🚀 Quick Start

```python
from polars_as_config.config import Config

config = {
    "steps": [
        {"operation": "scan_csv", "kwargs": {"source": "data.csv"}},
        {
            "operation": "with_columns",
            "kwargs": {
                "total": {
                    "expr": "add",
                    "on": {"expr": "col", "kwargs": {"name": "price"}},
                    "kwargs": {"other": {"expr": "col", "kwargs": {"name": "tax"}}}
                }
            }
        }
    ]
}

result = Config().run_config(config)
```

## 🔗 Links

- [Polars](https://pola.rs)
- [GitHub Repository](https://github.com/mavills/polars-as-config)
- [PyPI Package](https://pypi.org/project/polars-as-config/)
