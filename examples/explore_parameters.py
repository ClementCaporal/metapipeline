from metapipeline.base import FunctionStep, ListParam
import random

# The ListParam object indicate to the Step object
# that its element are different values of the same
# parameter. This allow to test multiple parameter
# for big pipelines in multiple step and the best
# parameter scenario for this pipeline and initial input.

# create ListParam for b
b = ListParam([1, 2, 10, 100])

# create dummy function
def add_stuff(a, b):
    return a+b

# Create the first steps
first_step = FunctionStep("FirstStep", add_stuff, inputs={"a": b, "b": b})
second_step = FunctionStep("SecondStep", add_stuff, inputs={"a": first_step, "b": b})

# show result
print(second_step.outputs)

# you can find the scenario 10 that leads to the result 10
print(f"The result {second_step.outputs[10]} is obtained using the scenario "
      f"with params nb {second_step.get_explicit_scenario(10)}")

# If you want a resume of each step with its possible params
print(second_step.get_pipeline_params())