from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.sharpsat_metamodel.models import SharpSATModel


class FmToSharpSAT(ModelToModel):
    """Transform a feature model into a SharpSAT (CNF) model.

    The CNF is produced by reusing the SAT metamodel's ``FmToPysat`` transformation, so
    the same constraint encoding (and the optional Tseytin encoding via ``cnf_method``) is
    available here.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'fm'

    @staticmethod
    def get_destination_extension() -> str:
        return 'sharpsat'

    def __init__(self, source_model: FeatureModel, cnf_method: str = 'distributive') -> None:
        self.source_model = source_model
        self.cnf_method = cnf_method
        self.destination_model = SharpSATModel()

    def transform(self) -> SharpSATModel:
        # Only pass cnf_method when a non-default encoding is requested, so the plugin also
        # works against releases of flamapy-sat that predate the Tseytin cnf_method option.
        if self.cnf_method == 'distributive':
            sat_model = FmToPysat(self.source_model).transform()
        else:
            sat_model = FmToPysat(self.source_model, cnf_method=self.cnf_method).transform()
        model = self.destination_model
        model.clauses = [list(clause) for clause in sat_model.get_all_clauses().clauses]
        model.variables = dict(sat_model.variables)
        model.features = dict(sat_model.features)
        model.auxiliary_variables = set(sat_model.auxiliary_variables)
        model.original_model = self.source_model
        return model
