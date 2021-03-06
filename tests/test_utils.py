from web3 import Web3

from common_utils_py.utils import utilities


def test_convert():
    input_text = "my text"
    text_bytes = utilities.convert_to_bytes(Web3, input_text)
    print("output %s" % utilities.convert_to_string(Web3, text_bytes))
    assert input_text == utilities.convert_to_text(Web3, text_bytes)
