"Base class"
import __future__

from abc import ABCMeta, abstractmethod
from itertools import product
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Union


class ListParam(list):
    """
    ListParam Collection of element to be considered as the same parameter
    with different values to test


    Parameters
    ----------
    list : _type_
        List of element corresponding to the same parameter
        with different values.
    """

    def __init__(self, *args) -> None:
        super().__init__(args[0])


class StepInterface(metaclass=ABCMeta):
    """
    StepInterface interface of Step Object

    Will use all the input to call its `run_scenario` function to
    create a output list
    """

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
    def outputs(self) -> ListParam:
        """
        outputs result of the step given the inputs

        Returns
        -------
        ListParam
            outputs of the step
        """
        if not hasattr(self, "_outputs"):
            self.execute()
        return self._outputs

    @outputs.setter
    def outputs(self, val: ListParam):
        self._outputs = val

    @property
    def inputs(self) -> Dict:
        """
        inputs input necessary for the compute function

        Returns
        -------
        Dict
            Dictionnary of the **kwargs to give to the `compute` function
        """
        return self._inputs

    @inputs.setter
    def inputs(self, val: Dict):
        self._inputs = val

    @property
    def scenarios(self) -> Sequence[Tuple[int]]:
        """
        scenarios

        Scenarios is a list of tuple where each tuple
        correspond to the id of input to use in case there are
        multiple values for one parameter

        Returns
        -------
        Sequence[Tuple[int]]
        """
        if ~hasattr(self, "_scenarios"):
            self.create_step_scenarios()
        return self._scenarios

    @scenarios.setter
    def scenarios(self, val: Sequence[Tuple[int]]):
        self._scenarios = val

    def create_step_scenarios(self):
        """
        create_step_scenario will create the a list of all the possible
        scenarios with their variables values.

        Returns
        -------
        None
        """
        scenarios = (range(len(self.explicit_inputs[key]))
                     for key, _ in self.explicit_inputs.items())
        self.scenarios = list(product(*scenarios))

    @property
    def explicit_inputs(self) -> Dict[str, ListParam]:
        """
        explicit_inputs

        return a dictionnary with key as name of the inputs
        and values a list of the different values they can take.
        The difference with "inputs" is that the other step input object
        are replaced wirth their outputs values.

        Returns
        -------
        Dict[str, ListParam]
        """
        if ~hasattr(self, "_explicit_inputs"):
            self.create_explicit_inputs()
        return self._explicit_inputs

    @explicit_inputs.setter
    def explicit_inputs(self, val: Dict[str, ListParam]):
        self._explicit_inputs = val

    def create_explicit_inputs(self) -> None:
        """
        create_explicit_inputs

        Create output for each inputs that is a Step object
        """
        explicit_inputs: Dict[str, ListParam] = {}
        for key, val in self.inputs.items():
            if isinstance(val, StepInterface):
                explicit_inputs[key] = ListParam(val.outputs)
            elif isinstance(val, ListParam):
                explicit_inputs[key] = val
            else:
                explicit_inputs[key] = ListParam([val])
        self.explicit_inputs = explicit_inputs

    @abstractmethod
    def run_scenario(self, scenario):
        pass

    def execute(self) -> None:
        """
        execute

        Compute all the outputs depending on the scenarios
        """
        outputs = []
        for scenario in range(len(self.scenarios)):
            outputs.append(self.run_scenario(scenario))
        self.outputs = ListParam(outputs)

    def get_explicit_scenario(
            self,
            scenario_nb: Optional[int] = None
        ) -> Union[
                Sequence[Dict[str, Any]],
                Dict[str, Any]]:
        """
        get_explicit_scenario

        return the pipeline step and their params for a given scenario number

        Parameters
        ----------
        scenario_nb : Optional[int], optional
            number of the scenario to get, by default None.
            If None, return a list of all scenario and their parameters id

        Returns
        -------
        Union[ Sequence[Dict[str, Any]], Dict[str, Any]]
        """
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

    def get_pipeline_params(self, base=None) -> Dict[str, Any]:
        """
        get_pipeline_params

        Returns a dictionnary with key the `name` of the
        steps in the pipeline and value its inputs.
        If the input is a step object, its name is given.

        Parameters
        ----------
        base : _type_, optional
            recusrive dictionnary, by default None

        Returns
        -------
        Dict[str, Any]
            Pipeline steps with their inputs
        """
        if base is None:
            base = {}
        params = {}
        for key, val in self.inputs.items():
            if isinstance(val, StepInterface):
                base = val.get_pipeline_params(base)
                params[key] = val.name
            else:
                params[key] = val
        base[self.name] = params
        return base

    def get_scenario_inputs(self, scenario) -> Dict[str, Any]:
        """
        get_scenario_inputs

        _extended_summary_

        Parameters
        ----------
        scenario : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        explicit_inputs = [
            self.explicit_inputs[param][self.scenarios[scenario][i]]
            for i, param in enumerate(self.explicit_inputs)
            ]
        params_dict = dict(zip(self.explicit_inputs.keys(),
                               explicit_inputs))
        return params_dict


class ExampleStep(StepInterface):
    """
    ExampleStep

    example of step that you can implement using the
    StepInterface object
    """
    def run_scenario(self, scenario) -> dict:
        params_dict = self.get_scenario_inputs(scenario)
        return params_dict


class FunctionStep(StepInterface):
    """
    FunctionStep

    Implementation of Stepinterface that use a `self.function`
    in the `run_scenario` function. The inputs has to be a dict
    with the key corresponding to a **kwargs for the `self.function`
    """
    def __init__(self,
                 name: Optional[str] = None,
                 function: Callable = NotImplementedError,
                 inputs: Dict = None,
                 ) -> None:
        super().__init__(name, inputs)
        self.function = function

    @property
    def function(self) -> Callable:
        return self._function

    @function.setter
    def function(self, val: Callable):
        self._function = val

    def run_scenario(self, scenario):
        params_dict = self.get_scenario_inputs(scenario)
        return self.function(**params_dict)
