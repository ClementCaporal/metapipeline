from metapipeline.base import FunctionStep

# The Step object can be combined in pipeline
# When the Step_A is the input of Step_B, Step_B
# will take the output of Step_A to feed its own
# 'run_scenario' function.

# create dummy function
def add_stuff(a, b):
    return a+b

# Create the first steps
add_step_A = FunctionStep("AddStepA", add_stuff, inputs={"a": 20, "b": 20})
add_step_B = FunctionStep("AddStepB", add_stuff, inputs={"a": 2, "b": 2})

# Create the third step using the two first steps.
add_step_C = FunctionStep("AddStepB", add_stuff, inputs={"a": add_step_A, "b": add_step_B})

# show result
print(add_step_C.outputs)