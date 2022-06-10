"""
Metadata module.
Help to communicate with the metadata store.
"""
import json
import logging
import copy

from common_utils_py.metadata.exceptions import MetadataGenericError
from common_utils_py.ddo.ddo import DDO
from common_utils_py.ddo.service import Service
from common_utils_py.http_requests.requests_session import get_requests_session

logger = logging.getLogger('metadata')


class Metadata:
    """Metadata wrapper to call different endpoint of metadata component."""

    def __init__(self, metadata_url, account, pool_connections=25, pool_maxsize=25, pool_block=True):
        """
        The Metadata class is a wrapper on the Metadata Store, which has exposed a REST API.

        :param metadata_url: Url of the metadata instance.
        :param account: The account to use for the authenticated requests.
        :param pool_connections: The number of urllib3 connection pools to cache.
        :param pool_maxsize: The maximum number of connections to save in the pool.
        :param pool_block: Whether the connection pool should block for connections.
        """
        assert metadata_url, f'Invalid url "{metadata_url}"'
        # :HACK:
        if '/api/v1/metadata/assets' in metadata_url:
            metadata_url = metadata_url[:metadata_url.find('/api/v1/metadata/assets')]

        self._base_url = f'{metadata_url}/api/v1/metadata/assets'
        self._headers = {'content-type': 'application/json'}

        logging.debug(f'Metadata Store connected at {metadata_url}')
        logging.debug(f'Metadata Store API documentation at {metadata_url}/api/v1/docs')
        logging.debug(f'Metadata assets at {self._base_url}')

        self.requests_session = get_requests_session(
            metadata_url, account, pool_connections, pool_maxsize, pool_block)

    @property
    def root_url(self):
        return self._base_url[:self._base_url.find('/api/v1/')]

    @property
    def url(self):
        """Base URL of the metadata instance."""
        return f'{self._base_url}/ddo'

    def get_service_endpoint(self):
        """
        Retrieve the endpoint with the ddo for a given did.

        :return: Return the url of the the ddo location
        """
        return f'{self.url}/' + '{did}'

    def list_assets(self):
        """
        List all the assets registered in the metadata instance.

        :return: List of DID string
        """
        response = self.requests_session.get(self._base_url)
        if response.status_code == 404:
            return []

        if not response.ok:
            raise ValueError(response.content.decode('UTF-8'))

        return response.json()

    def get_asset_ddo(self, did):
        """
        Retrieve asset ddo for a given did.

        :param did: Asset DID string
        :return: DDO instance
        """
        response = self.requests_session.get(f'{self.url}/{did}')
        if response.status_code == 404:
            return {}
        try:
            parsed_response = json.loads(response.content)
        except TypeError:
            parsed_response = None
        except ValueError:
            raise ValueError(response.content.decode('UTF-8'))
        if parsed_response is None:
            return {}
        return DDO(dictionary=parsed_response)

    def get_asset_metadata(self, did):
        """
        Retrieve asset metadata for a given did.

        :param did: Asset DID string
        :return: metadata key of the DDO instance
        """
        response = self.requests_session.get(f'{self._base_url}/metadata/{did}')
        if response.status_code == 404:
            return {}
        try:
            parsed_response = json.loads(response.content)
        except TypeError:
            parsed_response = None
        except ValueError:
            raise ValueError(response.content.decode('UTF-8'))
        if parsed_response is None:
            return {}
        return parsed_response

    def list_assets_ddo(self):
        """
        List all the ddos registered in the metadata instance.

        :return: List of DDO instance
        """
        response = self.requests_session.get(self.url)
        if not response.ok:
            raise ValueError(response.content.decode('UTF-8'))

        return response.json()['results']

    def publish_asset_ddo(self, ddo):
        """
        Register asset ddo in metadata.

        :param ddo: DDO instance
        :return: API response (depends on implementation)
        """
        try:
            asset_did = ddo.did

            # add userid to payload - required for authorization
            ddo = ddo.as_dictionary()
            ddo['userId'] = self.requests_session.auth.userid
            response = self.requests_session.post(self.url, data=json.dumps(ddo),
                                                  headers=self._headers)
        except AttributeError:
            raise AttributeError('DDO invalid. Review that all the required parameters are filled.')
        if response.status_code == 409:
            raise ValueError(
                f'This Asset ID already exists! \n\tHTTP Error message: \n\t\t{response.text}')
        elif response.status_code != 201:
            raise Exception(f'{response.status_code} ERROR Full error: \n{response.text}')
        elif response.status_code == 201:
            response = json.loads(response.content)
            logger.debug(f'Published asset DID {asset_did}')
            return response
        else:
            raise Exception(f'Unhandled ERROR: status-code {response.status_code}, '
                            f'error message {response.text}')

    def update_asset_ddo(self, did, ddo):
        """
        Update the ddo of a did already registered.

        :param did: Asset DID string
        :param ddo: DDO instance
        :return: API response (depends on implementation)
        """

        # add userid to payload - required for authorization
        ddo = ddo.as_dictionary()
        ddo['userId'] = self.requests_session.auth.userid

        response = self.requests_session.put(f'{self.url}/{did}', data=json.dumps(ddo),
                                             headers=self._headers)
        if response.status_code == 200 or response.status_code == 201:
            return json.loads(response.content)
        else:
            raise Exception(f'Unable to update DDO: {response.content}')

    def text_search(self, text, sort=None, offset=100, page=1):
        """
        Search in metadata using text query.

        Given the string metadata will do a full-text query to search in all documents.

        Currently implemented are the MongoDB and Elastic Search drivers.

        For a detailed guide on how to search, see the MongoDB driver documentation:
        mongodb driverCurrently implemented in:
        https://docs.mongodb.com/manual/reference/operator/query/text/

        And the Elastic Search documentation:
        https://www.elastic.co/guide/en/elasticsearch/guide/current/full-text-search.html
        Other drivers are possible according to each implementation.

        :param text: String to be search.
        :param sort: 1/-1 to sort ascending or descending.
        :param offset: Integer with the number of elements displayed per page.
        :param page: Integer with the number of page.
        :return: List of DDO instance
        """
        assert page >= 1, f'Invalid page value {page}. Required page >= 1.'
        payload = {"text": text, "sort": sort, "offset": offset, "page": page}
        response = self.requests_session.get(
            f'{self.url}/query',
            params=payload,
            headers=self._headers
        )
        if response.status_code == 200:
            return self._parse_search_response(response.content)
        else:
            raise Exception(f'Unable to search for DDO: {response.content}')

    def query_search(self, search_query, sort=None, offset=100, page=1):
        """
        Search using a query.

        Currently implemented is the MongoDB query model to search for documents according to:
        https://docs.mongodb.com/manual/tutorial/query-documents/

        And an Elastic Search driver, which implements a basic parser to convert the query into
        elastic search format.

        Example: query_search({"price":[0,10]})

        :param search_query: Python dictionary, query following mongodb syntax
        :param sort: 1/-1 to sort ascending or descending.
        :param offset: Integer with the number of elements displayed per page.
        :param page: Integer with the number of page.
        :return: List of DDO instance
        """
        assert page >= 1, f'Invalid page value {page}. Required page >= 1.'
        search_query['sort'] = sort or {}
        search_query['offset'] = offset
        search_query['page'] = page
        response = self.requests_session.post(
            f'{self.url}/query',
            data=json.dumps(search_query),
            headers=self._headers
        )
        if response.status_code == 201:
            return self._parse_search_response(response.content)
        else:
            raise Exception(f'Unable to search for DDO: {response.content}')

    def retire_asset_ddo(self, did):
        """
        Retire asset ddo of metadata.

        :param did: Asset DID string
        :return: API response (depends on implementation)
        """
        response = self.requests_session.delete(f'{self.url}/{did}', headers=self._headers)
        if response.status_code == 200:
            logging.debug(f'Removed asset DID: {did} from metadata store')
            return response

        raise MetadataGenericError(f'Unable to remove DID: {response}')

    def retire_all_assets(self):
        """
        Retire all the ddo assets.
        :return: str
        """
        response = self.requests_session.delete(f'{self.url}', headers=self._headers)
        if response.status_code == 200:
            logging.debug(f'Removed all the assets successfully')
            return response

        raise MetadataGenericError(f'Unable to remove all the DID: {response}')

    def validate_metadata(self, metadata):
        """
        Validate that the metadata of your ddo is valid.

        :param metadata: conforming to the Metadata accepted by Nevermined, dict
        :return: bool
        """
        response = self.requests_session.post(
            f'{self.url}/validate',
            data=json.dumps(metadata),
            headers=self._headers
        )
        if response.content == b'true\n':
            return True
        else:
            logger.info(self._parse_search_response(response.content))
            return False

    def get_service_agreement(self, agreement_id):
        """
        Retrieve a service agreement for a given agreemend id.

        :param agreement_id: Service agreement id string
        :return: Service
        """
        response = self.requests_session.get(f'{self._base_url}/service/{agreement_id}')
        if response.status_code == 404:
            return None

        if response.status_code == 500:
            raise ValueError(response.content)

        parsed_response = json.loads(response.content)
        return Service.from_json(parsed_response)

    def store_service_agreement(self, agreement_id, service):
        """
        Store a service agreement for a given agreemend id.

        :param agreement_id: Service agreement id string
        :param service: Service
        :return: bool
        """
        service_json = service.as_dictionary()
        service_json['agreementId'] = agreement_id
        service_json['userId'] = self.requests_session.auth.userid
        response = self.requests_session.post(
            f'{self._base_url}/service',
            data=json.dumps(service_json),
            headers=self._headers
        )

        if response.status_code != 201:
            raise ValueError(response.content)
        return True

    @staticmethod
    def _parse_search_response(response):
        if not response:
            return {}
        try:
            parsed_response = json.loads(response)
        except TypeError:
            parsed_response = None

        if parsed_response is None:
            return []
        elif isinstance(parsed_response, dict):
            return parsed_response
        elif isinstance(parsed_response, list):
            return parsed_response
        else:
            raise ValueError(
                f'Unknown search response, expecting a list got {type(parsed_response)}.')
