"""Exceptions for common_utils_py."""


class InvalidContractAddress(Exception):
    """Raised when an invalid address is passed to the contract loader."""


class DIDUnknownValueType(Exception):
    """Raised when a requested DID or a DID in the chain cannot be found."""


class DIDAlreadyExist(Exception):
    """Raised when a requested DID is already published in Metadata API."""


class InvalidMetadata(Exception):
    """Raised when some value in the metadata is invalid."""


class InvalidServiceAgreementSignature(Exception):
    """Raised when the SLA signature is not valid."""


class ServiceAgreementExists(Exception):
    """Raised when the SLA already exists."""


class InitializeServiceAgreementError(Exception):
    """Error on invoking purchase endpoint"""


class EncryptAssetUrlsError(Exception):
    """Error invoking the encrypt endpoint"""


class ServiceConsumeError(Exception):
    """ Error invoking a purchase endpoint"""


class InvalidAgreementTemplate(Exception):
    """ Error when agreement template is not valid or not approved"""
