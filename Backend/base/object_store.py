from base.fhir_search_obj import _FhirClassObject
from base.cds_hooks_table import _HooksConfigTable
from base.resource_route_table import _FhirResourceRoute
from base.feature_table import _FeatureTable
from base.training_sets_table import _TrainingSetTable
from base.transformation_table import _TransformationTable
from base.fhir_bulk_obj import BulkDataClient

fhir_class_obj = _FhirClassObject()
cds_hooks_config_table = _HooksConfigTable()
fhir_resources_route = _FhirResourceRoute()
feature_table = _FeatureTable()
model_feature_table = _TransformationTable()
bulk_server = BulkDataClient()

# Used for training pipline
training_feature_table = _FeatureTable("./config/continuous_training/features.csv")
training_model_feature_table = _TransformationTable("./config/continuous_training/transformation.csv")
training_sets_table = _TrainingSetTable()

pass
