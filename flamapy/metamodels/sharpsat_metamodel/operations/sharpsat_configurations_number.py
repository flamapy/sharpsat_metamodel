from typing import cast

import pyunigen

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import ConfigurationsNumber
from flamapy.metamodels.sharpsat_metamodel.models import SharpSATModel


class SharpSATConfigurationsNumber(ConfigurationsNumber):
    """Approximate the number of valid configurations with ApproxMC.

    Counting is projected onto the feature variables, so auxiliary variables (e.g. Tseytin
    gates) do not inflate the result. ApproxMC gives an (epsilon, delta) probabilistic
    approximation that scales far better than exact enumeration.

    The count is obtained through UniGen's binding (``pyunigen`` with ``num=0``, which runs
    ApproxMC's projected count without drawing samples). The standalone ``pyapproxmc`` binding
    mis-configures ApproxMC's projected counting on feature-model CNFs with implied variables
    (the root and mandatory-relation unit clauses), undercounting by a factor of two; UniGen's
    ApproxMC invocation does not have that problem.
    """

    def __init__(self, seed: int = 1) -> None:
        self._result = 0
        self._seed = seed

    def get_configurations_number(self) -> int:
        return self._result

    def get_result(self) -> int:
        return self._result

    def execute(self, model: VariabilityModel) -> 'SharpSATConfigurationsNumber':
        sharpsat_model = cast(SharpSATModel, model)
        counter = pyunigen.Sampler(seed=self._seed)
        for clause in sharpsat_model.clauses:
            counter.add_clause(clause)
        cell_count, hash_count, _samples = counter.sample(
            num=0, sampling_set=sharpsat_model.feature_variables()
        )
        self._result = cell_count * (2 ** hash_count)
        return self
