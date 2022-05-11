from base64 import urlsafe_b64encode
import calendar
import datetime
import time
from common_utils_py.oauth2.jwk_utils import account_to_jwk
from authlib.oauth2.rfc7523.jwt_bearer import JWTBearerGrant
from authlib.jose import JWSHeader
from authlib.common.encoding import to_bytes, json_dumps, json_b64encode
from common_utils_py.utils import keytransfer
from common_utils_py.utils.crypto import sign_message

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
                    BASE_AUD_URL + '/nft-access-proof',
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


class NeverminedJWTBearerGrantEth(JWTBearerGrant):
    @staticmethod
    def sign(key, issuer, subject=None, issued_at=None, expires_at=None, claims=None, **kwargs):
        return NeverminedJWTBearerGrantEth._sign_jwt_bearer_assertion(
            key, issuer, subject, issued_at,
            expires_at, claims, **kwargs)

    @staticmethod
    def _sign_jwt_bearer_assertion(key, issuer, subject=None, issued_at=None,expires_at=None, claims=None, header=None, **kwargs):
        if header is None:
            header = {}
        alg = kwargs.pop('alg', None)
        if alg:
            header['alg'] = alg
        if 'alg' not in header:
            raise ValueError('Missing "alg" in header')

        payload = {'iss': issuer}

        # subject is not required in Google service
        if subject:
            payload['sub'] = subject

        if not issued_at:
            issued_at = int(time.time())

        expires_in = kwargs.pop('expires_in', 3600)
        if not expires_at:
            expires_at = issued_at + expires_in

        payload['iat'] = issued_at
        payload['exp'] = expires_at

        if claims:
            payload.update(claims)

        return NeverminedJWTBearerGrantEth._encode(header, payload, key)

    @staticmethod
    def _encode(header, payload, key):
        """Encode a JWT with the given header, payload and key.

        :param header: A dict of JWS header
        :param payload: A dict to be encoded
        :param key: key used to sign the signature
        :return: bytes
        """
        header['typ'] = 'JWT'

        for k in ['exp', 'iat', 'nbf']:
            # convert datetime into timestamp
            claim = payload.get(k)
            if isinstance(claim, datetime.datetime):
                payload[k] = calendar.timegm(claim.utctimetuple())

        text = to_bytes(json_dumps(payload))
        return NeverminedJWTBearerGrantEth._serialize_compact(header, text, key)

    @staticmethod
    def _serialize_compact(protected, payload, key):
        """Generate a JWS Compact Serialization. The JWS Compact Serialization
        represents digitally signed or MACed content as a compact, URL-safe
        string, per `Section 7.1`_.

        .. code-block:: text

            BASE64URL(UTF8(JWS Protected Header)) || '.' ||
            BASE64URL(JWS Payload) || '.' ||
            BASE64URL(JWS Signature)

        :param protected: A dict of protected header
        :param payload: A bytes/string of payload
        :param key: Private key used to generate signature
        :return: byte
        """
        jws_header = JWSHeader(protected, None)

        protected_segment = json_b64encode(jws_header.protected).replace(b'=', b'')
        payload_segment = urlsafe_b64encode(to_bytes(payload)).replace(b'=', b'')

        # calculate signature
        signing_input = b'.'.join([protected_segment, payload_segment])
        signature = NeverminedJWTBearerGrantEth._sign_web3(signing_input.decode(), key)
        signature = urlsafe_b64encode(signature).replace(b'=', b'')

        return b'.'.join([protected_segment, payload_segment, signature])

    @staticmethod
    def _sign_web3(signing_input, account):
        return sign_message(signing_input, account)
