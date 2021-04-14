elementwise_functions = {
    'add': '+',
    'subtract': '-',
    'multiply': '*',
    'divide': '/'
}

# Value indicates whether function has been implemented
binning_procedures = {
    'freedman': True,
    'sturges': False,
    'scott': False,
    'shimazaki': False,
    'bayesian': False
}

from dive.worker.visualization.marginal_spec_functions.single_field_single_type_specs import *
from dive.worker.visualization.marginal_spec_functions.single_field_multi_type_specs import *
from dive.worker.visualization.marginal_spec_functions.multi_field_single_type_specs import *
from dive.worker.visualization.marginal_spec_functions.mixed_field_multi_type_specs import *
from dive.worker.visualization.marginal_spec_functions.multi_field_multi_type_specs import *
