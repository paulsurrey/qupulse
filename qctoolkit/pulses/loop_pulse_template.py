import logging
from typing import Dict, Set, List, Optional, Any, Union

"""RELATED THIRD PARTY IMPORTS"""

"""LOCAL IMPORTS"""
from .parameters import Parameter
from .pulse_template import PulseTemplate, MeasurementWindow
from .conditions import Condition, SoftwareCondition, ProxyCondition
from .instructions import InstructionBlock
from .sequencing import Sequencer
from qctoolkit.serialization import Serializer

logger = logging.getLogger(__name__)


class LoopPulseTemplate(PulseTemplate):
    """Conditional looping in a pulse.
    
    A LoopPulseTemplate is a PulseTemplate which is repeated
    during execution as long as a certain condition holds.
    """
    
    def __init__(self, condition: str, body: PulseTemplate, identifier: Optional[str]=None) -> None:
        super().__init__(identifier=identifier)
        self.__condition = condition
        self.__body = body

    def __str__(self) -> str:
        return "LoopPulseTemplate: Condition <{}>, Body <{}>".format(self.__condition, self.__body)

    @property
    def body(self) -> PulseTemplate:
        return self.__body

    @property
    def condition(self) -> str:
        return self.__condition

    @property
    def parameter_names(self) -> Set[str]:
        return self.__body.parameter_names

    def get_measurement_windows(self, parameters: Dict[str, Parameter] = None):
        raise NotImplemented()

    @property
    def parameter_declarations(self) -> Set[str]:
        return self.__body.parameter_declarations

    @property
    def is_interruptable(self) -> bool:
        return self.__body.is_interruptable

    def __obtain_condition_object(self, conditions: Dict[str, Condition]) -> Condition:
        try:
            return conditions[self.__condition]
        except:
            raise ConditionMissingException(self.__condition)

    def build_sequence(self,
                       sequencer: Sequencer,
                       parameters: Dict[str, Parameter],
                       conditions: Dict[str, Condition],
                       instruction_block: InstructionBlock) -> None:
        self.__obtain_condition_object(conditions).build_sequence_loop(self,
                                                                       self.__body,
                                                                       sequencer,
                                                                       parameters,
                                                                       conditions,
                                                                       instruction_block)

    def requires_stop(self, parameters: Dict[str, Parameter], conditions: Dict[str, Condition]) -> bool:
        return self.__obtain_condition_object(conditions).requires_stop()

    def get_serialization_data(self, serializer: Serializer) -> Dict[str, Any]:
        data = dict(
            type=serializer.get_type_identifier(self),
            condition=self.__condition,
            body=serializer._serialize_subpulse(self.__body)
        )
        return data

    @staticmethod
    def deserialize(serializer: Serializer,
                    condition: str,
                    body: Dict[str, Any],
                    identifier: Optional[str]=None) -> 'LoopPulseTemplate':
        body = serializer.deserialize(body)
        return LoopPulseTemplate(condition, body, identifier=identifier)


class ConditionMissingException(Exception):

    def __init__(self, condition_name: str) -> None:
        super().__init__()
        self.condition_name = condition_name

    def __str__(self) -> str:
        return "Condition <{}> was referred to but not provided in the conditions dictionary.".format(self.condition_name)