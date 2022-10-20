from metapipeline.base import FunctionStep, ListParam


def add_stuff(a, b):
    return a+b


add_step0 = FunctionStep("AddStep0", add_stuff,
                         {"a": ListParam([1, 2, 3]), "b": 2})
add_step = FunctionStep("AddStep", add_stuff,
                        {"a": add_step0, "b": 2})
add_step2 = FunctionStep("AddStep2", add_stuff,
                         {"a": add_step, "b": 2})

print("name", add_step2.name)
print("inputs", add_step2.inputs)
print("function", add_step2.function)
print("explicit input", add_step2.explicit_inputs)
print("scenarios", add_step2.scenarios)
print("get explicit scenarios", add_step2.get_explicit_scenario())
print("outputs", add_step2.outputs)
print("All steps params", add_step2.get_pipeline_params())
