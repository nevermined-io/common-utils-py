from collections import namedtuple

from eth_utils import add_0x_prefix

from common_utils_py.agreements.service_agreement_template import ServiceAgreementTemplate
from common_utils_py.agreements.service_types import ServiceTypes, ServiceTypesIndices
from common_utils_py.ddo.service import Service
from common_utils_py.utils.utilities import generate_prefixed_id
from common_utils_py.utils.utilities import to_checksum_addresses

Agreement = namedtuple('Agreement', ('template', 'conditions'))


class ServiceAgreement(Service):
    """Class representing a Service Agreement."""
    SERVICE_INDEX = 'index'
    AGREEMENT_TEMPLATE = 'serviceAgreementTemplate'
    SERVICE_ATTRIBUTES = 'attributes'
    SERVICE_CONDITIONS = 'conditions'
    SERVICE_ENDPOINT = 'serviceEndpoint'

    def __init__(self, attributes, service_agreement_template, service_endpoint=None,
                 service_type=None):
        """

        :param attributes: attributes
        :param service_agreement_template: ServiceAgreementTemplate instance
        :param service_endpoint: str URL to use for requesting service defined in this agreement
        :param service_type: str like ServiceTypes.ASSET_ACCESS
        """
        self.service_agreement_template = service_agreement_template
        values = dict()
        values[ServiceAgreementTemplate.TEMPLATE_ID_KEY] = self.template_id
        values['attributes'] = dict()
        values['attributes'] = attributes
        values['attributes']['serviceAgreementTemplate'] = service_agreement_template.__dict__
        if service_type == ServiceTypes.ASSET_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.ASSET_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_ACCESS_INDEX)

        elif service_type == ServiceTypes.CLOUD_COMPUTE:
            values['index'] = ServiceTypesIndices.DEFAULT_COMPUTING_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.CLOUD_COMPUTE,
                             values, ServiceTypesIndices.DEFAULT_COMPUTING_INDEX)

        elif service_type == ServiceTypes.DID_SALES:
            values['index'] = ServiceTypesIndices.DEFAULT_DID_SALES_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.DID_SALES,
                             values, ServiceTypesIndices.DEFAULT_DID_SALES_INDEX)

        elif service_type == ServiceTypes.NFT_SALES:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT_SALES_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_SALES,
                             values, ServiceTypesIndices.DEFAULT_NFT_SALES_INDEX)

        elif service_type == ServiceTypes.NFT_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_NFT_ACCESS_INDEX)

        elif service_type == ServiceTypes.NFT721_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT721_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_NFT721_ACCESS_INDEX)

        else:
            raise ValueError(f'The service_type {service_type} is not currently supported.')

    def get_number_nfts(self):
        """
        Return the number of nfts

        :return: int
        """
        return int(self.get_param_value_by_name('_numberNfts'))

    def get_nft_holder(self):
        """
        Return the NFT holder

        :return Str
        """
        return self.get_param_value_by_name('_nftHolder')

    def get_amounts(self):
        """
        Return the list of amounts/rewards to distribute

        :return: Str[]
        """
        return self.get_param_value_by_name('_amounts')

    def get_amounts_int(self):
        """
        Return the list of amounts/rewards to distribute

        :return: Int[]
        """
        return list(map(int, self.get_amounts()))

    def get_receivers(self):
        """
        Return the list of receivers addresses

        :return: str[]
        """
        return to_checksum_addresses(self.get_param_value_by_name('_receivers'))

    def get_price(self):
        """
        Return the price from the conditions parameters.

        :return: Int
        """
        price = 0
        _amounts = self.get_param_value_by_name('_amounts')
        for amount in _amounts:
            price = price + int(amount)
        return price

    def get_param_value_by_name(self, name):
        """
        Return the value from the conditions parameters given the param name.

        :return: Object
        """
        for cond in self.conditions:
            for p in cond.parameters:
                if p.name == name:
                    return p.value

    @property
    def service_endpoint(self):
        """

        :return:
        """
        return self._service_endpoint

    @property
    def agreement(self):
        """

        :return:
        """
        return Agreement(self.template_id, self.conditions[:])

    @property
    def template_id(self):
        """

        :return:
        """
        return self.service_agreement_template.template_id

    @property
    def conditions(self):
        """

        :return:
        """
        return self.service_agreement_template.conditions

    @property
    def condition_by_name(self):
        """

        :return:
        """
        return {cond.name: cond for cond in self.conditions}

    @property
    def conditions_params_value_hashes(self):
        """

        :return:
        """
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(cond.values_hash)

        return value_hashes

    @property
    def conditions_timeouts(self):
        """

        :return:
        """
        return [cond.timeout for cond in self.conditions]

    @property
    def conditions_timelocks(self):
        """

        :return:
        """
        return [cond.timelock for cond in self.conditions]

    @property
    def conditions_contracts(self):
        """

        :return:
        """
        return [cond.contract_name for cond in self.conditions]

    @classmethod
    def from_ddo(cls, service_type, ddo):
        """

        :param service_type: identifier of the service inside the asset DDO, str
        :param ddo:
        :return:
        """
        service = ddo.get_service(service_type)
        if service is None:
            raise ValueError(
                f'Service of type {service_type} is not found in this DDO.')

        return cls.from_service_dict(service.as_dictionary())

    @classmethod
    def from_service_index(cls, service_index, ddo):
        """

        :param service_index: index of the service inside the asset DDO, str
        :param ddo:
        :return:
        """
        service = ddo.get_service_by_index(service_index)
        if service is None:
            raise ValueError(
                f'Service of type {service_index} is not found in this DDO.')

        return cls.from_service_dict(service.as_dictionary())

    @classmethod
    def from_service_dict(cls, service_dict):
        """

        :param service_dict:
        :return:
        """
        return cls(
            service_dict[cls.SERVICE_ATTRIBUTES],
            ServiceAgreementTemplate(service_dict['templateId'],
                                     service_dict[cls.SERVICE_ATTRIBUTES]['main']['name'],
                                     service_dict[cls.SERVICE_ATTRIBUTES]['main']['creator'],
                                     service_dict[cls.SERVICE_ATTRIBUTES]),
            service_dict.get(cls.SERVICE_ENDPOINT),
            service_dict.get('type')
        )

    @staticmethod
    def generate_service_agreement_hash(template_id, values_hash_list, timelocks, timeouts,
                                        agreement_id, hash_function):
        """

        :param template_id:
        :param values_hash_list:
        :param timelocks:
        :param timeouts:
        :param agreement_id: id of the agreement, hex str
        :param hash_function: reference to function that will be used to compute the hash (sha3
        or similar)
        :return:
        """
        return hash_function(
            ['address', 'bytes32[]', 'uint256[]', 'uint256[]', 'bytes32'],
            [template_id, values_hash_list, timelocks, timeouts, agreement_id]
        )

    @staticmethod
    def create_new_agreement_id():
        """

        :return:
        """
        return generate_prefixed_id()

    def generate_agreement_condition_ids(self, agreement_id, asset_id, consumer_address, keeper, token_address=None):
        """
        Generate the condition ids depending on the ServiceType
        :param agreement_id: id of the agreement, hex str
        :param asset_id:
        :param consumer_address: ethereum account address of consumer, hex str
        :param keeper:
        :param token_address:
        :return:
        """
        if token_address is None:
            token_address = keeper.token.address

        if self.type == ServiceTypes.NFT_ACCESS:
            number_nfts = self.get_number_nfts()
            nft_holder_cond_id = self.generate_nft_holder_condition_id(keeper, agreement_id, asset_id, consumer_address, number_nfts)
            access_cond_id = self.generate_nft_access_condition_id(keeper, agreement_id, asset_id, consumer_address)
            return access_cond_id, nft_holder_cond_id

        amounts = self.get_amounts_int()
        receivers = self.get_receivers()
        lock_cond_id = self.generate_lock_condition_id(keeper, agreement_id, asset_id, keeper.escrow_payment_condition.address, token_address, amounts, receivers)

        if self.type == ServiceTypes.ASSET_ACCESS:
            access_cond_id = self.generate_access_condition_id(keeper, agreement_id, asset_id, consumer_address)

        elif self.type == ServiceTypes.CLOUD_COMPUTE:
            access_cond_id = self.generate_compute_condition_id(keeper, agreement_id, asset_id, consumer_address)

        elif self.type == ServiceTypes.DID_SALES:
            access_cond_id = self.generate_transfer_did_condition_id(keeper, agreement_id, asset_id, consumer_address)

        elif self.type == ServiceTypes.NFT_SALES:
            number_nfts = self.get_number_nfts()
            nft_holder = self.get_nft_holder()
            access_cond_id = self.generate_transfer_nft_condition_id(keeper, agreement_id, asset_id, nft_holder, consumer_address, number_nfts, lock_cond_id)

        else:
            raise Exception(
                'Error generating the condition ids, the service_agreement type is not valid.')

        escrow_cond_id = self.generate_escrow_condition_id(keeper, agreement_id, asset_id, keeper.escrow_payment_condition.address, amounts, receivers, token_address, lock_cond_id, access_cond_id)
        return access_cond_id, lock_cond_id, escrow_cond_id

    def generate_nft_holder_condition_id(self, keeper, agreement_id, asset_id, holder_address, number_nfts):
        _hash = add_0x_prefix(
            keeper.nft_holder_condition.hash_values(asset_id, holder_address, number_nfts).hex())
        return add_0x_prefix(
            keeper.nft_holder_condition.contract.functions.generateId(agreement_id, _hash).call().hex())


    def generate_access_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        _hash = add_0x_prefix(
            keeper.access_condition.hash_values(asset_id, consumer_address).hex())
        return add_0x_prefix(
            keeper.access_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def generate_nft_access_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        _hash = add_0x_prefix(
            keeper.nft_access_condition.hash_values(asset_id, consumer_address).hex())
        return add_0x_prefix(
            keeper.nft_access_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def generate_compute_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        _hash = add_0x_prefix(
            keeper.compute_execution_condition.hash_values(asset_id, consumer_address).hex())
        return add_0x_prefix(
            keeper.compute_execution_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def generate_transfer_did_condition_id(self, keeper, agreement_id, asset_id, receiver_address):
        _hash = add_0x_prefix(
            keeper.transfer_did_condition.hash_values(asset_id, receiver_address).hex())
        return add_0x_prefix(
            keeper.transfer_did_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def generate_transfer_nft_condition_id(self, keeper, agreement_id, asset_id, nft_holder, receiver_address, number_nfts, lock_cond_id):
        _hash = add_0x_prefix(
            keeper.transfer_nft_condition.hash_values(asset_id, nft_holder, receiver_address, number_nfts, lock_cond_id).hex())
        return add_0x_prefix(
            keeper.transfer_nft_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def generate_lock_condition_id(self, keeper, agreement_id, asset_id, escrow_condition_address, token_address, amounts, receivers):
        _hash = add_0x_prefix(
            keeper.lock_payment_condition.hash_values(asset_id, escrow_condition_address, token_address, amounts, receivers).hex())
        return add_0x_prefix(
            keeper.lock_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def generate_escrow_condition_id(self, keeper, agreement_id, asset_id, escrow_condition_address, amounts, receivers,token_address, lock_cond_id, access_or_compute_id):
        _hash = add_0x_prefix(
            keeper.escrow_payment_condition.hash_values(asset_id, amounts, receivers, escrow_condition_address, token_address, lock_cond_id, access_or_compute_id).hex())
        return add_0x_prefix(
            keeper.escrow_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex())

    def get_service_agreement_hash(
            self, agreement_id, asset_id, consumer_address, publisher_address, keeper):
        """Return the hash of the service agreement values to be signed by a consumer.

        :param agreement_id:id of the agreement, hex str
        :param asset_id:
        :param consumer_address: ethereum account address of consumer, hex str
        :param publisher_address: ethereum account address of publisher, hex str
        :param keeper:
        :return:
        """
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self.template_id,
            self.generate_agreement_condition_ids(
                agreement_id, asset_id, consumer_address, keeper),
            self.conditions_timelocks,
            self.conditions_timeouts,
            agreement_id,
            keeper.generate_multi_value_hash
        )
        return agreement_hash
