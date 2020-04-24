from common_utils_py.agreements.access_sla_template import ACCESS_SLA_TEMPLATE
from common_utils_py.agreements.compute_sla_template import COMPUTE_SLA_TEMPLATE
from common_utils_py.agreements.service_types import ServiceTypes


def get_sla_template(service_type=ServiceTypes.ASSET_ACCESS):
    """
    Get the template for a ServiceType.

    :param service_type: ServiceTypes
    :return: template dict
    """
    if service_type == ServiceTypes.ASSET_ACCESS:
        return ACCESS_SLA_TEMPLATE.copy()
    elif service_type == ServiceTypes.CLOUD_COMPUTE:
        return COMPUTE_SLA_TEMPLATE.copy()
    else:
        raise ValueError(f'Invalid/unsupported service agreement type {service_type}')
