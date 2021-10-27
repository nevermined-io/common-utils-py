from common_utils_py.oauth2.jwk_utils import account_to_jwk
from authlib.oauth2.rfc7523.jwt_bearer import JWTBearerGrant
from common_utils_py.utils import keytransfer

BASE_AUD_URL = "/api/v1/gateway/services"


class NeverminedJWTBearerGrant(JWTBearerGrant):
    def create_claims_options(self):
        """Create a claims_options to verify JWT payload claims.
        """
        # https://tools.ietf.org/html/rfc7523#section-3
        claims = {}
        public_claims = {
            'iss': {'essential': True},
            'sub': {
                'essential': False,
                'validate': validate_sub,
            },
            'aud': {
                'essential': True,
                'values': [
                    BASE_AUD_URL + '/access',
                    BASE_AUD_URL + '/access-proof',
                    BASE_AUD_URL + '/nft-access',
                    BASE_AUD_URL + '/compute',
                    BASE_AUD_URL + '/download',
                    BASE_AUD_URL + '/execute'
                ],
            },
            'exp': {'essential': True},
        }
        claims.update(public_claims)

        # private claims are non registered names and may lead to collisions
        private_claims = {
            'did': {
                'essential': False,
                'validate': validate_did
            },
            'execution_id': {
                'essential': False,
                'validate': validate_execution_id
            },
            'eths': {
                'essential': False,
                'values': [
                    "personal"
                ]
            }
        }
        claims.update(private_claims)

        return claims


def validate_sub(claims, value):
    if claims["aud"] == BASE_AUD_URL + "/access" and value is None:
        return False

    return True


def validate_did(claims, value):
    if value is None and claims["aud"] != BASE_AUD_URL + "/compute":
        return False

    return True


def validate_execution_id(claims, value):
    if claims["aud"] != BASE_AUD_URL + "/compute" and value is None:
        return False

    return True


def generate_access_grant_token(account, service_agreement_id, did, uri="/access"):
    # create jwt bearer grant
    jwk = account_to_jwk(account)
    assertion = NeverminedJWTBearerGrant.sign(
        jwk,
        issuer=account.address,
        audience=BASE_AUD_URL + uri,
        subject=service_agreement_id,
        claims={
            "did": did
        },
        header={
            "alg": "ES256K"
        })

    return assertion

def generate_access_proof_grant_token(account, service_agreement_id, did, buyer_secret, uri="/access-proof"):
    # create jwt bearer grant
    jwk = account_to_jwk(account)
    address_num = int(account.address, 16)
    assertion = NeverminedJWTBearerGrant.sign(
        jwk,
        issuer=account.address,
        audience=BASE_AUD_URL + uri,
        subject=service_agreement_id,
        claims={
            "did": did,
            "babysig": keytransfer.sign(buyer_secret, address_num),
            "buyer": keytransfer.make_public(buyer_secret),
        },
        header={
            "alg": "ES256K"
        })

    return assertion


def generate_download_grant_token(account, did):
    # create jwt bearer grant
    jwk = account_to_jwk(account)
    assertion = NeverminedJWTBearerGrant.sign(
        jwk,
        issuer=account.address,
        audience=BASE_AUD_URL + '/download',
        claims={
            "did": did
        },
        header={
            "alg": "ES256K"
        })

    return assertion


def generate_execute_grant_token(account, service_agreement_id, workflow_did):
    # create jwt bearer grant
    jwk = account_to_jwk(account)
    assertion = NeverminedJWTBearerGrant.sign(
        jwk,
        issuer=account.address,
        audience=BASE_AUD_URL + "/execute",
        subject=service_agreement_id,
        claims={
            "did": workflow_did
        },
        header={
            "alg": "ES256K"
        })

    return assertion


def generate_compute_grant_token(account, service_agreement_id, execution_id):
    # create jwt bearer grant
    jwk = account_to_jwk(account)
    assertion = NeverminedJWTBearerGrant.sign(
        jwk,
        issuer=account.address,
        audience=BASE_AUD_URL + "/compute",
        subject=service_agreement_id,
        claims={
            "execution_id": execution_id
        },
        header={
            "alg": "ES256K"
        })

    return assertion
