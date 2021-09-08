from common_utils_py.agreements.access_sla_template import ACCESS_SLA_TEMPLATE
from common_utils_py.agreements.compute_sla_template import COMPUTE_SLA_TEMPLATE
from common_utils_py.agreements.did_sales_template import DID_SALES_TEMPLATE
from common_utils_py.agreements.nft_sales_template import NFT_SALES_TEMPLATE
from common_utils_py.agreements.nft_access_template import NFT_ACCESS_TEMPLATE
from common_utils_py.agreements.access_proof_sla_template import ACCESS_PROOF_SLA_TEMPLATE
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
    elif service_type == ServiceTypes.DID_SALES:
        return DID_SALES_TEMPLATE.copy()
    elif service_type == ServiceTypes.NFT_SALES:
        return NFT_SALES_TEMPLATE.copy()
    elif service_type == ServiceTypes.NFT_ACCESS:
        return NFT_ACCESS_TEMPLATE.copy()
    elif service_type == ServiceTypes.ASSET_ACCESS_PROOF:
        return ACCESS_PROOF_SLA_TEMPLATE.copy()
    else:
        raise ValueError(f'Invalid/unsupported service agreement type {service_type}')
