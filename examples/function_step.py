import os

from metapipeline.base import FunctionStep

# The goal of function step is to take any function
# and encapsulate it inside a Step object to add it
# to a pipeline.

# Create a function or load it from any package (for example 'os')
def add_stuff(a, b):
    return a+b

# Encapsulate add_stuff and os.system in a Step Object
# the 'inputs' should be similar to a **kwargs for the encapsulated function.
add_step = FunctionStep("AddStep", add_stuff, inputs={"a": 2, "b": 2})
ls_step = FunctionStep("ChownStep", os.system, inputs={"command": "echo Hello World"})

# Get result
print(add_step.outputs)
print(ls_step.outputs)
