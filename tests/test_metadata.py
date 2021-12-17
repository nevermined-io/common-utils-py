from common_utils_py.agreements.service_agreement import ServiceAgreement
from common_utils_py.ddo.service import Service


def test_store_and_retrieve_service(metadata_instance, json_service):
    agreement_id = ServiceAgreement.create_new_agreement_id()
    service = Service.from_json(json_service)

    # store the service agreement
    result = metadata_instance.store_service_agreement(agreement_id, service)
    assert result is True

    result = metadata_instance.get_service_agreement(agreement_id)
    assert result.type == service.type
    assert result.index == service.index
    assert result.service_endpoint == service.service_endpoint
    assert result.attributes == service.attributes
