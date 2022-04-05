"Base class"
from abc import ABCMeta, abstractmethod
from itertools import product
from typing import Dict, Optional, Sequence, Tuple


class ListParam(list):

    def __init__(self, *args):
        super().__init__(args[0])


class StepInterface(metaclass=ABCMeta):

    def __init__(self,
                 name: Optional[str] = None,
                 inputs: Optional[Dict] = None,
                 ) -> None:
        if name is None:
            name = type(self).__name__
        self.name = name
        if inputs is None:
            inputs = {}
        self.inputs = inputs

    @property
    def name(self) -> str:
        """
        name step's name

        `name` is used to vizualise the pipeline in a graph
        """
        return self._name

    @name.setter
    def name(self, val: str):
        if val is None:
            val = type(self).__name__
        self._name = val

    @property
    def outputs(self) -> Sequence:
        if not hasattr(self, "_outputs"):
            self.execute()
        return self._outputs

    @outputs.setter
    def outputs(self, val: Sequence):
        self._outputs = val

    @property
    def inputs(self) -> Dict:
        return self._inputs

    @inputs.setter
    def inputs(self, val: Dict):
        self._inputs = val

    @property
    def scenarios(self) -> Sequence[Tuple[int]]:
        if ~hasattr(self, "_scenarios"):
            self.create_step_scenarios()
        return self._scenarios

    @scenarios.setter
    def scenarios(self, val: Sequence[Tuple[int]]):
        self._scenarios = val

    @property
    def explicit_inputs(self) -> Dict[str, ListParam]:
        if ~hasattr(self, "_explicit_inputs"):
            self.create_explicit_inputs()
        return self._explicit_inputs

    @explicit_inputs.setter
    def explicit_inputs(self, val: Dict[str, ListParam]):
        self._explicit_inputs = val

    def create_explicit_inputs(self):
        explicit_inputs: Dict[str, ListParam] = {}
        for key, val in self.inputs.items():
            if isinstance(val, StepInterface):
                explicit_inputs[key] = ListParam(val.outputs)
            elif isinstance(val, ListParam):
                explicit_inputs[key] = val
            else:
                explicit_inputs[key] = ListParam([val])
        self.explicit_inputs = explicit_inputs

    def create_step_scenarios(self):
        scenarios = (range(len(self.explicit_inputs[key]))
                     for key, _ in self.explicit_inputs.items())
        self.scenarios = list(product(*scenarios))

    @abstractmethod
    def run_scenario(self, scenario):
        pass

    def execute(self):
        outputs = []
        for scenario in self.scenarios:
            outputs.append(self.run_scenario(scenario))
        self.outputs = outputs

    def get_explicit_scenario(self,
                              scenario_nb: Optional[int] = None):
        explicit_scenario = []
        for scenario in self.scenarios:
            base = {}
            for i, key in enumerate(self.inputs.keys()):
                val = None
                if isinstance(self.inputs[key], StepInterface):
                    val = self.inputs[key].get_explicit_scenario(scenario[i])
                else:
                    val = scenario[i]
                base[f'{self.name}_{key}'] = val
            explicit_scenario.append(base)
        if scenario_nb is None:
            return explicit_scenario
        return explicit_scenario[scenario_nb]

    def recursive_step_parameters(self,
                                  base=None):
        if base is None:
            base = {}
        params = {}
        for key, val in self.inputs.items():
            if isinstance(val, StepInterface):
                base = val.recursive_step_parameters(base)
            else:
                params[key] = val
        base[self.name] = params
        return base


class Step(StepInterface):

    def run_scenario(self, scenario):
        raise NotImplementedError(
            f'run_scenario is not implemented for {self}'
            )


class DaskStep(Step):

    @property
    def lazy(self) -> bool:
        if ~hasattr(self, "_lazy"):
            self.execute()
        return self._lazy

    @lazy.setter
    def lazy(self, val: bool):
        self._lazy = val

    def __init__(self,
                 name: Optional[str] = None,
                 lazy=True,
                 **inputs) -> None:
        super().__init__(name, **inputs)
        self.lazy = lazy


class ExampleStep(Step):

    def run_scenario(self, scenario):
        params_dict = self.get_scenario_inputs(scenario)
        return params_dict

