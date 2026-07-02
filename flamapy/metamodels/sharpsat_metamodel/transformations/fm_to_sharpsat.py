from flamapy.core.transformations import ModelToModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel, ClauseSet
from flamapy.metamodels.sharpsat_metamodel.models import SharpSATModel


class FmToSharpSAT(ModelToModel):
    """Transform a feature model into a SharpSAT (CNF) model.

    The CNF is produced by the feature-model ``ClauseSet`` (no SAT-solver dependency), so the
    same constraint encoding (and the optional Tseytin encoding via ``cnf_method``) is available
    here.
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
        clause_set = ClauseSet.from_feature_model(self.source_model, cnf_method=self.cnf_method)
        model = self.destination_model
        model.clauses = [list(clause) for clause in clause_set.clauses]
        model.variables = dict(clause_set.variables)
        model.features = dict(clause_set.features)
        model.auxiliary_variables = set(clause_set.auxiliary_variables)
        model.original_model = self.source_model
        return model
