# Nodes (WIP)

As an extension to going from polars to JSON, we can use that JSON to create a
graph, and create a JSON configuration from a graph. The idea is that we can
then use this conversion to create a visual representation for non-technical
persona, such as a customer services team, a non-technical-abled data
analyst,...

## What are Nodes

Let's define nodes as the set of operations connected in a graph that represent
the execution of a transformation of structured tabular data into the same
format with different properties.

A node can represent an input file, an operation on a column, or a set of
columns, or it can be an output, writing to disk for example.

Nodes don't map 1:1 to JSON polars-steps. A `select` statement represents more
the way nodes are connected than a node in itself. Also, not all operations are
easily mapped to nodes; each operation requires careful consideration about how
it is represented.

## Going from JSON to nodes

Let's start with an example:

```python
import polars as pl

# Read data from a file. This can be a single node with some configuration options.
# The node should store which columns are in the file, so that it is able to represent
# that as outputs of the node. To do so, we could always enforce the need for a
# `match_to_schema` operation to be convertable to nodes, which then indicates which
# columns are needed in a file, and fails when they are not.
# Let's also always use the lazy API; there is no reason to use the eager one.
df = pl.read_csv("test.csv", infer_shema=False)
# Here we essentially do a string concatination. In a graph, we wouldn't care too much
# about the alias; the alias is only a key used to identify later on in the graph, or
# as output. Outputs can be defined later, so let's do that.
df = df.with_columns(pl.col("a").add("!").alias("a_lias"))
# This select statement then selects the final output. In the graph, we select part
# of the data from the first node (the input), column "b", and we select our newly
# added column. The only place a select is relevant is at the end, when
# we actually do something with the output.
# There is another case, when wanting to reduce memory when using non-LazyFrame
# solutions, but let's assume Polars can optimize the query because for those cases
# we use Lazyframes.
df = df.select("b", "a_lias")
# Lastly the output. This can just be a node in the graph.
df.write_csv("output.csv")
```

The above is simple enough; we can deduce what needs to be selected at the end,
and boil down everything else to the essense of what it is actually doing. If we
use LazyFrames, we're actually always ok with this transformation of the actual
code, as long as the effects stay the same.

It becomes much harder when we introduce more complex operations.

`join` always requires two dataframes in its input, and basically creates a
third. In code, you cannot perform a `select` on columns from different
dataframes in the same statement, but in a graph, you can connect dots from
different dataframes. Here we would need to place a restriction in some way.

Filters are also more difficult to represent. They also in some sense introduce
a new frame, where combinging results from the old frame and the new frame does
not work.

Both `join` and `filter` are examples of when the flow of a graph is disrupted
and cannot easily be composed. You could play around with ideas there with
colored inputs and unconnectable inputs from pre- and post operation nodes.

## Going from nodes to JSON
