import base64
import json
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from web3 import Web3
from authlib.jose import JWTClaims
from authlib.jose.errors import ExpiredTokenError
from common_utils_py.exceptions import AuthError

from common_utils_py.oauth2.token import NeverminedJWTBearerGrantEth

logger = logging.getLogger(__name__)

class EthJwtAuth(requests.auth.AuthBase):
    """JWT client assertion implementation with seckp256k1 and keccak"""
    def __init__(self, metadata_url, account):
        self.metadata_url = metadata_url
        self.account = account
        self._access_token = None
        self._claim = None
        self._userid = None

    def __call__(self, r):
        # check if token expired
        try:
            self.claim.validate_exp(int(time.time()), leeway=0)
        except ExpiredTokenError as error:
            # token has expired
            self._access_token = None
            self._claim = None
            self._userid = None
            self.login()

        if 'Authorization' not in r.headers:
            r.headers.update({'Authorization': f'Bearer {self.access_token}'})
        return r

    def login(self):
        client_assertion = NeverminedJWTBearerGrantEth.sign(
            key=self.account,
            issuer=Web3.toChecksumAddress(self.account.address),
            header={
                "alg": "ES256K"
            })
        response = requests.post(
            f'{self.metadata_url}/api/v1/auth/login',
            data={
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': client_assertion.decode()
            })

        if not response.ok:
            raise AuthError(response.json().get('message'))

        access_token = response.json()['access_token']
        [header, payload, _] = access_token.split('.')
        decoded_header = json.loads(base64.b64decode(header + '=='))
        decoded_payload = json.loads(base64.b64decode(payload + '=='))
        self._claim = JWTClaims(decoded_payload, decoded_header)
        self._userid = self.claim['sub']
        self._access_token = access_token

    @property
    def userid(self):
        if self._userid is None:
            self.login()
        return self._userid

    @property
    def access_token(self):
        if self._access_token is None:
            self.login()
        return self._access_token

    @property
    def claim(self):
        if self._claim is None:
            self.login()
        return self._claim

def get_requests_session(metadata_url=None, account=None, pool_connections=25, pool_maxsize=25, pool_block=True):
    """
    Set connection pool maxsize and block value to avoid `connection pool full` warnings.

    :return: requests session
    """
    session = requests.sessions.Session()

    if account is None:
        logger.warning('Since no account was specified the only public metadata endpoints will be available.')
    else:
        session.auth = EthJwtAuth(metadata_url, account)

    session.mount('http://', HTTPAdapter(pool_connections, pool_maxsize, pool_block))
    session.mount('https://', HTTPAdapter(pool_connections, pool_maxsize, pool_block))
    return session
