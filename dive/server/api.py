from dive.server.resources.datasets import UploadFile, Dataset, Datasets, PreloadedDatasets, SelectPreloadedDataset, DeselectPreloadedDataset
from dive.server.resources.documents import NewDocument, Document, Documents
from dive.server.resources.fields import Field
from dive.server.resources.projects import Project, Projects
from dive.server.resources.field_properties_resources import FieldProperties
from dive.server.resources.specs import Specs, VisualizationFromSpec, GeneratingProcedures

from dive.server.resources.statistics_resources import ComparisonFromSpec, CorrelationsFromSpec, RegressionEstimator, \
    RegressionFromSpec, AggregationFromSpec, InteractionTerms, \
    InitialRegressionModelRecommendation

from dive.server.resources.exported_specs import ExportedSpecs, VisualizationFromExportedSpec
from dive.server.resources.exported_analyses import ExportedAnalyses, ExportedRegression, DataFromExportedRegression, \
    ExportedCorrelation, DataFromExportedCorrelation, ExportedAggregation, DataFromExportedAggregation, \
    ExportedComparison, DataFromExportedComparison

from dive.server.resources.transform import Reduce, Unpivot, Join
from dive.server.resources.task_resources import TaskResult, RevokeTask, RevokeChainTask
from dive.server.resources.auth_resources import Register, Login, Logout, User, Confirm_Token, Resend_Email, Reset_Password_Link, Reset_Password_With_Token, AnonymousUser, DeleteAnonymousData

from flask import request, make_response
from dive.server.resources.feedback import Feedback
from dive.base.serialization import jsonify

from flask_restful import Resource

class Test(Resource):
    def get(self):
        return make_response(jsonify({ 'result': 'Success' }))


def add_resources(api):
    api.add_resource(Test,                          '/api/test')

    api.add_resource(TaskResult,                    '/api/tasks/v1/result/<task_id>')
    api.add_resource(RevokeTask,                    '/api/tasks/v1/revoke/<task_id>')
    api.add_resource(RevokeChainTask,               '/api/tasks/v1/revoke')

    api.add_resource(Projects,                      '/api/projects/v1/projects')
    api.add_resource(Project,                       '/api/projects/v1/projects/<project_id>')

    api.add_resource(UploadFile,                    '/api/datasets/v1/upload')
    api.add_resource(Datasets,                      '/api/datasets/v1/datasets')
    api.add_resource(Dataset,                       '/api/datasets/v1/datasets/<int:dataset_id>')
    api.add_resource(PreloadedDatasets,             '/api/datasets/v1/preloaded_datasets')
    api.add_resource(SelectPreloadedDataset,        '/api/datasets/v1/select_preloaded_dataset')
    api.add_resource(DeselectPreloadedDataset,      '/api/datasets/v1/deselect_preloaded_dataset')

    api.add_resource(Reduce,                        '/api/datasets/v1/reduce')
    api.add_resource(Unpivot,                       '/api/datasets/v1/unpivot')
    api.add_resource(Join,                          '/api/datasets/v1/join')

    api.add_resource(Field,                         '/api/datasets/v1/fields/<int:field_id>')

    api.add_resource(FieldProperties,               '/api/field_properties/v1/field_properties')

    api.add_resource(Specs,                         '/api/specs/v1/specs')
    api.add_resource(VisualizationFromSpec,         '/api/specs/v1/specs/<int:spec_id>/visualization')
    api.add_resource(GeneratingProcedures,          '/api/specs/v1/generating_procedures')

    api.add_resource(ExportedSpecs,                 '/api/exported_specs/v1/exported_specs')
    api.add_resource(VisualizationFromExportedSpec, '/api/exported_specs/v1/exported_specs/<int:exported_spec_id>/visualization')

    api.add_resource(InteractionTerms,              '/api/statistics/v1/interaction_term')

    api.add_resource(RegressionFromSpec,            '/api/statistics/v1/regression')
    api.add_resource(AggregationFromSpec,           '/api/statistics/v1/aggregation')

    api.add_resource(ComparisonFromSpec,            '/api/statistics/v1/comparison')
    api.add_resource(CorrelationsFromSpec,          '/api/statistics/v1/correlations')
    api.add_resource(RegressionEstimator,           '/api/statistics/v1/regression_estimator')
    api.add_resource(InitialRegressionModelRecommendation, '/api/statistics/v1/initial_regression_state')

    api.add_resource(ExportedAnalyses,               '/api/exported_analyses/v1/exported_analyses')

    api.add_resource(ExportedRegression,            '/api/exported_regression/v1/exported_regression')
    api.add_resource(DataFromExportedRegression,    '/api/exported_regression/v1/exported_regression/<int:exported_spec_id>/data')

    api.add_resource(ExportedCorrelation,           '/api/exported_correlation/v1/exported_correlation')
    api.add_resource(DataFromExportedCorrelation,   '/api/exported_correlation/v1/exported_correlation/<int:exported_spec_id>/data')

    api.add_resource(ExportedAggregation,           '/api/exported_aggregation/v1/exported_aggregation')
    api.add_resource(DataFromExportedAggregation,   '/api/exported_aggregation/v1/exported_aggregation/<int:exported_spec_id>/data')

    api.add_resource(ExportedComparison,            '/api/exported_comparison/v1/exported_comparison')
    api.add_resource(DataFromExportedComparison,    '/api/exported_comparison/v1/exported_comparison/<int:exported_spec_id>/data')

    api.add_resource(Documents,                     '/api/compose/v1/documents')
    api.add_resource(NewDocument,                   '/api/compose/v1/document')
    api.add_resource(Document,                      '/api/compose/v1/document/<int:document_id>')

    api.add_resource(Confirm_Token,                 '/api/auth/v1/confirm/<string:token>')
    api.add_resource(Register,                      '/api/auth/v1/register')
    api.add_resource(Login,                         '/api/auth/v1/login')
    api.add_resource(Logout,                        '/api/auth/v1/logout')
    api.add_resource(User,                          '/api/auth/v1/user')
    api.add_resource(Resend_Email,                  '/api/auth/v1/resend')
    api.add_resource(Reset_Password_Link,           '/api/auth/v1/reset_password')
    api.add_resource(Reset_Password_With_Token,     '/api/auth/v1/reset_password/<string:token>')
    api.add_resource(AnonymousUser,                 '/api/auth/v1/anonymous_user')
    api.add_resource(DeleteAnonymousData,           '/api/auth/v1/delete_anonymous_data/<int:user_id>')

    api.add_resource(Feedback,                      '/api/feedback/v1/feedback')

    return api
