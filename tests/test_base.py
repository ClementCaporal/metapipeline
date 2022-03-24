import pytest
from metapipeline.base import StepInterface


@pytest.fixture
def step_auto_name():
    return StepInterface()


@pytest.fixture
def step_given_name():
    return StepInterface(name="new_step")


def test_name(step_auto_name, step_given_name):
    assert step_auto_name.name == "StepInterface"
    assert step_given_name.name == "new_step"
