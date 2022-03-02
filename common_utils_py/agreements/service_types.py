class ServiceTypes:
    """Types of Service allowed in ocean protocol DDO services."""
    AUTHORIZATION = 'authorization'
    METADATA = 'metadata'
    ASSET_ACCESS = 'access'
    ASSET_ACCESS_PROOF = 'access-proof'
    CLOUD_COMPUTE = 'compute'
    DID_SALES = 'did-sales'
    NFT_SALES = 'nft-sales'
    NFT_ACCESS = 'nft-access'
    NFT721_ACCESS = 'nft721-access'
    NFT_ACCESS_PROOF = 'nft-access-proof'
    NFT_ACCESS_SWAP = 'nft-access-swap'
    NFT_SALES_WITH_ACCESS = 'nft-sales-with-access'

class ServiceTypesIndices:
    DEFAULT_METADATA_INDEX = 0
    DEFAULT_PROVENANCE_INDEX = 1
    DEFAULT_AUTHORIZATION_INDEX = 2
    DEFAULT_ACCESS_INDEX = 3
    DEFAULT_COMPUTING_INDEX = 4
    DEFAULT_DID_SALES_INDEX = 5
    DEFAULT_NFT_SALES_INDEX = 6
    DEFAULT_NFT_ACCESS_INDEX = 7
    DEFAULT_NFT721_ACCESS_INDEX = 9
    DEFAULT_ACCESS_PROOF_INDEX = 10
    DEFAULT_NFT_ACCESS_PROOF_INDEX = 11
    DEFAULT_NFT_ACCESS_SWAP_INDEX = 12
    DEFAULT_NFT_SALES_WITH_ACCESS_INDEX = 13

class ServiceAuthorizationTypes:
    SECRET_STORE = 'SecretStore'
    PSK_ECDSA = 'PSK-ECDSA'
    PSK_RSA = 'PSK-RSA'
