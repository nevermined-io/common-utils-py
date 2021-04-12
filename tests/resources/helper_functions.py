import json
import os
import pathlib
from urllib.request import urlopen

from contracts_lib_py.utils import get_account

from common_utils_py.ddo.ddo import DDO

PUBLISHER_INDEX = 1
CONSUMER_INDEX = 0


def get_resource_path(dir_name, file_name):
    base = os.path.realpath(__file__).split(os.path.sep)[1:-1]
    if dir_name:
        return pathlib.Path(os.path.join(os.path.sep, *base, dir_name, file_name))
    else:
        return pathlib.Path(os.path.join(os.path.sep, *base, file_name))


def get_publisher_account():
    return get_account(0)


def get_consumer_account():
    return get_account(1)


def get_ddo_sample():
    return DDO(json_text=json.dumps(json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs"
        "/examples/access/v0.1/ddo1.json").read().decode(
        'utf-8'))))


def get_ddo_sample2():
    return DDO(json_text=json.dumps(json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs"
        "/examples/access/v0.1/ddo2.json").read().decode(
        'utf-8'))))


def get_ddo_did_sales_sample():
    return DDO(json_text=json.dumps(json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/access/v0.1"
        "/ddo_sales.json").read().decode(
        'utf-8'))))


def get_ddo_nft_sample():
    return DDO(json_text=json.dumps(json.loads(urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs/examples/access/v0.1"
        "/ddo_nft.json").read().decode(
        'utf-8'))))


def get_metadata():
    metadata = urlopen(
        "https://raw.githubusercontent.com/nevermined-io/docs/master/docs/architecture/specs"
        "/examples/metadata/v0.1/metadata1.json").read().decode(
        'utf-8')
    return json.loads(metadata)


def log_event(event_name):
    def _process_event(event):
        print(f'Received event {event_name}: {event}')

    return _process_event
