from collections import namedtuple

import web3.constants
from contracts_lib_py import keeper
from eth_utils import add_0x_prefix
from web3 import Web3

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
        values['attributes']['serviceAgreementTemplate'] = service_agreement_template.__dict__['template']
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

        elif service_type == ServiceTypes.NFT721_SALES:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT721_SALES_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT721_SALES,
                             values, ServiceTypesIndices.DEFAULT_NFT721_SALES_INDEX)

        elif service_type == ServiceTypes.NFT_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_NFT_ACCESS_INDEX)

        elif service_type == ServiceTypes.NFT721_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT721_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT721_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_NFT721_ACCESS_INDEX)

        elif service_type == ServiceTypes.ASSET_ACCESS_PROOF:
            values['index'] = ServiceTypesIndices.DEFAULT_ACCESS_PROOF_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.ASSET_ACCESS_PROOF,
                             values, ServiceTypesIndices.DEFAULT_ACCESS_PROOF_INDEX)

        elif service_type == ServiceTypes.NFT_ACCESS_PROOF:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT_ACCESS_PROOF_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_ACCESS_PROOF,
                             values, ServiceTypesIndices.DEFAULT_NFT_ACCESS_PROOF_INDEX)

        elif service_type == ServiceTypes.NFT_ACCESS_SWAP:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT_ACCESS_SWAP_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_ACCESS_SWAP,
                             values, ServiceTypesIndices.DEFAULT_NFT_ACCESS_SWAP_INDEX)

        elif service_type == ServiceTypes.NFT_SALES_WITH_ACCESS:
            values['index'] = ServiceTypesIndices.DEFAULT_NFT_SALES_WITH_ACCESS_INDEX
            Service.__init__(self, service_endpoint,
                             ServiceTypes.NFT_SALES_WITH_ACCESS,
                             values, ServiceTypesIndices.DEFAULT_NFT_SALES_WITH_ACCESS_INDEX)

        else:
            raise ValueError(f'The service_type {service_type} is not currently supported.')

    def get_number_nfts(self):
        """
        Return the number of nfts

        :return: int
        """
        return int(self.get_param_value_by_name('_numberNfts'))

    def get_key_hash(self):
        """
        Return the key hash

        :return: Str
        """
        return self.attributes['main']['_hash']

    def get_provider_babyjub_key(self):
        """
        Return the provider babyjub key

        :return: Str[]
        """
        return self.attributes['main']['_providerPub']

    def get_nft_holder(self):
        """
        Return the NFT holder

        :return Str
        """
        return self.get_param_value_by_name('_nftHolder')

    def get_nft_contract_address(self, nft_type ='1155'):
        """
        Return the NFT Contract Address under the `_contractAddress` parameter

        :return Str
        """
        ddo_contract_address = self.get_param_value_by_name('_contractAddress')
        if ddo_contract_address is None or not Web3.isAddress(ddo_contract_address):
            if nft_type == '1155':
                return keeper.TransferNFTCondition.get_instance().get_nft_default_address()
            elif nft_type == '721':
                return keeper.TransferNFT721Condition.get_instance().get_nft_default_address()
            else:
                return web3.constants.ADDRESS_ZERO
        return Web3.toChecksumAddress(ddo_contract_address)

    def get_nft_transfer_or_mint(self):
        """
        Return the NFT holder

        :return Bool
        """
        nft_transfer = str(self.get_param_value_by_name('_nftTransfer')).lower()
        # If we get `false` we mint if anything else we transfer
        if nft_transfer == 'false' or nft_transfer == '0':
            return False
        else:
            return True

    def get_duration(self):
        """
        Return the duration in blocks (typically of a NFT subscription). If not defined 0

        :return Int
        """
        try:
            duration = int(self.get_param_value_by_name('_duration'))
            if duration > 0:
                return duration
            else:
                return 0
        except:
            return 0

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

    def get_nft_receiver(self):
        return self.get_param_value_by_name('_nft_receiver')

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

    def generate_agreement_condition_ids(self, agreement_id_seed, asset_id, consumer_address, keeper, init_agreement_address=None, token_address=None, babyjub_pk=None):
        """
        Generate the condition ids depending on the ServiceType
        :param agreement_id_seed: seed id of the agreement, hex str
        :param asset_id: unique identifier of the asset (DID), str
        :param consumer_address: ethereum account address of consumer, hex str
        :param keeper: keeper instance
        :param creator_address: ethereum address creating the asset, hex str
        :param token_address: token address to use in the transactions (ERC-20 or native), hex str
        :return: condition ids
        """
        if init_agreement_address is None:
            init_agreement_address = consumer_address
        agreement_id = keeper.agreement_manager.hash_id(agreement_id_seed, init_agreement_address)
        if token_address is None:
            token_address = keeper.token.address

        if self.type == ServiceTypes.NFT_ACCESS or self.type == ServiceTypes.NFT721_ACCESS:
            number_nfts = self.get_number_nfts()
            nft_holder_cond_id = self.generate_nft_holder_condition_id(keeper, agreement_id, asset_id, consumer_address, number_nfts)
            access_cond_id = self.generate_nft_access_condition_id(keeper, agreement_id, asset_id, consumer_address)
            return (agreement_id_seed, agreement_id), access_cond_id, nft_holder_cond_id

        if self.type == ServiceTypes.NFT_ACCESS_PROOF:
            number_nfts = self.get_number_nfts()
            nft_holder_cond_id = self.generate_nft_holder_condition_id(keeper, agreement_id, asset_id, consumer_address, number_nfts)
            access_cond_id = self.generate_access_proof_condition_id(keeper, agreement_id, asset_id, babyjub_pk)
            return (agreement_id_seed, agreement_id), access_cond_id, nft_holder_cond_id

        # TODO: not working
        if self.type == ServiceTypes.NFT_ACCESS_SWAP:
            number_nfts = self.get_number_nfts()
            nft_receiver = self.get_nft_receiver()
            amounts = self.get_amounts_int()
            receivers = self.get_receivers()
            lock_cond_id = self.generate_lock_condition_id(keeper, agreement_id, asset_id, keeper.escrow_payment_condition.address,  token_address, amounts, receivers)
            access_cond_id = self.generate_access_proof_condition_id(keeper, agreement_id, asset_id, babyjub_pk)
            escrow_cond_id = self.generate_nft_escrow_condition_id(keeper, agreement_id, asset_id, consumer_address, keeper.escrow_payment_condition.address, number_nfts, nft_receiver, token_address, lock_cond_id[1], [access_cond_id[1], transfer_cond_id[1]])
            return (agreement_id_seed, agreement_id), access_cond_id, lock_cond_id, escrow_cond_id

        amounts = self.get_amounts_int()
        receivers = self.get_receivers()
        lock_cond_id = self.generate_lock_condition_id(keeper, agreement_id, asset_id, keeper.escrow_payment_condition.address, token_address, amounts, receivers)

        if self.type == ServiceTypes.NFT_SALES_WITH_ACCESS:
            number_nfts = self.get_number_nfts()
            nft_receiver = self.get_nft_receiver()
            nft_holder = self.get_nft_holder()
            nft_contract_address = self.get_nft_contract_address()            
            nft_transfer = self.get_nft_transfer_or_mint()
            duration = self.get_duration()

            transfer_cond_id = self.generate_transfer_nft_condition_id(keeper, agreement_id, asset_id, nft_holder, consumer_address, number_nfts, lock_cond_id[1], nft_contract_address, nft_transfer)

            access_cond_id = self.generate_access_proof_condition_id(keeper, agreement_id, asset_id, babyjub_pk)
            escrow_cond_id = self.generate_escrow_condition_multi_id(keeper, agreement_id, asset_id, consumer_address, keeper.escrow_payment_condition.address, amounts, receivers, token_address, lock_cond_id[1], [transfer_cond_id[1], access_cond_id[1]])
            return (agreement_id_seed, agreement_id), transfer_cond_id, lock_cond_id, escrow_cond_id, access_cond_id

        if self.type == ServiceTypes.ASSET_ACCESS:
            access_cond_id = self.generate_access_condition_id(keeper, agreement_id, asset_id, consumer_address)

        elif self.type == ServiceTypes.ASSET_ACCESS_PROOF:
            access_cond_id = self.generate_access_proof_condition_id(keeper, agreement_id, asset_id, babyjub_pk)

        elif self.type == ServiceTypes.CLOUD_COMPUTE:
            access_cond_id = self.generate_compute_condition_id(keeper, agreement_id, asset_id, consumer_address)

        elif self.type == ServiceTypes.DID_SALES:
            access_cond_id = self.generate_transfer_did_condition_id(keeper, agreement_id, asset_id, consumer_address)

        elif self.type == ServiceTypes.NFT_SALES or self.type == ServiceTypes.NFT721_SALES:
            number_nfts = self.get_number_nfts()
            nft_holder = self.get_nft_holder()
            nft_contract_address = self.get_nft_contract_address()
            nft_transfer = self.get_nft_transfer_or_mint()

            access_cond_id = self.generate_transfer_nft_condition_id(keeper, agreement_id, asset_id, nft_holder, consumer_address, number_nfts, lock_cond_id[1], nft_contract_address, nft_transfer)
        else:
            raise Exception(
                'Error generating the condition ids, the service_agreement type is not valid.')

        escrow_cond_id = self.generate_escrow_condition_id(keeper, agreement_id, asset_id, consumer_address, keeper.escrow_payment_condition.address, amounts, receivers, token_address, lock_cond_id[1], access_cond_id[1])
        return (agreement_id_seed, agreement_id), access_cond_id, lock_cond_id, escrow_cond_id

    def generate_nft_holder_condition_id(self, keeper, agreement_id, asset_id, holder_address, number_nfts):
        _hash = add_0x_prefix(
            keeper.nft_holder_condition.hash_values(asset_id, holder_address, number_nfts).hex())
        return (_hash, add_0x_prefix(
            keeper.nft_holder_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_access_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        _hash = add_0x_prefix(
            keeper.access_condition.hash_values(asset_id, consumer_address).hex())
        return (_hash, add_0x_prefix(
            keeper.access_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_access_proof_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        keyhash = self.get_key_hash()
        provider_address = self.get_provider_babyjub_key()
        _hash = add_0x_prefix(
            keeper.access_proof_condition.hash_values(keyhash, consumer_address, provider_address).hex())
        return (_hash, add_0x_prefix(
            keeper.access_proof_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_nft_access_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        _hash = add_0x_prefix(
            keeper.nft_access_condition.hash_values(asset_id, consumer_address).hex())
        return (_hash, add_0x_prefix(
            keeper.nft_access_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_compute_condition_id(self, keeper, agreement_id, asset_id, consumer_address):
        _hash = add_0x_prefix(
            keeper.compute_execution_condition.hash_values(asset_id, consumer_address).hex())
        return (_hash, add_0x_prefix(
            keeper.compute_execution_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_transfer_did_condition_id(self, keeper, agreement_id, asset_id, receiver_address):
        _hash = add_0x_prefix(
            keeper.transfer_did_condition.hash_values(asset_id, receiver_address).hex())
        return (_hash, add_0x_prefix(
            keeper.transfer_did_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_transfer_nft_condition_id(self, keeper, agreement_id, asset_id, nft_holder, receiver_address, number_nfts, lock_cond_id, nft_contract_address, transfer_nft):
        if self.type == ServiceTypes.NFT_SALES or self.type == ServiceTypes.NFT_SALES_WITH_ACCESS:
            transfer_condition = keeper.transfer_nft_condition 
        else:
            transfer_condition = keeper.transfer_nft721_condition
            
        _hash = add_0x_prefix(
            transfer_condition.hash_values(asset_id, nft_holder, receiver_address, number_nfts, lock_cond_id, nft_contract_address, transfer_nft).hex())
        return (_hash, add_0x_prefix(
            transfer_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))


    def generate_lock_condition_id(self, keeper, agreement_id, asset_id, escrow_condition_address, token_address, amounts, receivers):
        _hash = add_0x_prefix(
            keeper.lock_payment_condition.hash_values(asset_id, escrow_condition_address, token_address, amounts, receivers).hex())
        return (_hash, add_0x_prefix(
            keeper.lock_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_nft_lock_condition_id(self, keeper, agreement_id, asset_id, escrow_condition_address, token_address, amount, receiver):
        _hash = add_0x_prefix(
            keeper.nft_lock_payment_condition.hash_values(asset_id, escrow_condition_address, token_address, amount, receiver).hex())
        return (_hash, add_0x_prefix(
            keeper.nft_lock_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_escrow_condition_id(self, keeper, agreement_id, asset_id, consumer_address, escrow_condition_address, amounts, receivers,token_address, lock_cond_id, access_or_compute_id):
        _hash = add_0x_prefix(
            keeper.escrow_payment_condition.hash_values(asset_id, amounts, receivers, consumer_address, escrow_condition_address, token_address, lock_cond_id, access_or_compute_id).hex())
        return (_hash, add_0x_prefix(
            keeper.escrow_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_escrow_condition_multi_id(self, keeper, agreement_id, asset_id, consumer_address, escrow_condition_address, amounts, receivers,token_address, lock_cond_id, access_or_compute_id):
        _hash = add_0x_prefix(
            keeper.escrow_payment_condition.hash_values_multi(asset_id, amounts, receivers, consumer_address, escrow_condition_address, token_address, lock_cond_id, access_or_compute_id).hex())
        return (_hash, add_0x_prefix(
            keeper.escrow_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def generate_nft_escrow_condition_id(self, keeper, agreement_id, asset_id, consumer_address, escrow_condition_address, amounts, receivers,token_address, lock_cond_id, access_or_compute_id):
        _hash = add_0x_prefix(
            keeper.nft_escrow_payment_condition.hash_values(asset_id, amounts, receivers, consumer_address, escrow_condition_address, token_address, lock_cond_id, access_or_compute_id).hex())
        return (_hash, add_0x_prefix(
            keeper.nft_escrow_payment_condition.contract.functions.generateId(agreement_id, _hash).call().hex()))

    def get_service_agreement_hash(
            self, agreement_id, asset_id, consumer_address, publisher_address, keeper, babyjub_pk=None):
        """Return the hash of the service agreement values to be signed by a consumer.

        :param agreement_id:id of the agreement, hex str
        :param asset_id:
        :param consumer_address: ethereum account address of consumer, hex str
        :param publisher_address: ethereum account address of publisher, hex str
        :param keeper:
        :return:
        """
        ((_, _), *conditions) = self.generate_agreement_condition_ids(
                agreement_id, asset_id, consumer_address, keeper, publisher_address, babyjub_pk=babyjub_pk)
        condition_ids = [c[0] for c in conditions]
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self.template_id,
            condition_ids,
            self.conditions_timelocks,
            self.conditions_timeouts,
            agreement_id,
            keeper.generate_multi_value_hash
        )
        return agreement_hash
