from typing import Optional

from flamapy.core.models import VariabilityModel


class SharpSATModel(VariabilityModel):
    """A CNF model for approximate model counting and almost-uniform sampling.

    It mirrors the variable/feature bookkeeping of the SAT metamodel: ``clauses`` is the
    CNF, ``variables`` maps a feature name to its SAT variable id and ``features`` the
    reverse, while ``auxiliary_variables`` holds ids that are not features (e.g. Tseytin
    gates) and must be projected out when counting or sampling configurations.
    """

    @staticmethod
    def get_extension() -> str:
        return 'sharpsat'

    def __init__(self) -> None:
        self.clauses: list[list[int]] = []
        self.variables: dict[str, int] = {}  # feature name -> id
        self.features: dict[int, str] = {}  # id -> feature name
        self.auxiliary_variables: set[int] = set()
        self.original_model: Optional[VariabilityModel] = None

    def feature_variables(self) -> list[int]:
        """SAT variable ids that correspond to features (auxiliary ids excluded)."""
        return list(self.features.keys())
