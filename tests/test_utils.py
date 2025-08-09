from collections import OrderedDict
import importlib.util
from pathlib import Path

# Import call_server/utils.py without triggering call_server package imports
spec = importlib.util.spec_from_file_location("call_server.utils", Path(__file__).resolve().parents[1] / "call_server" / "utils.py")
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)
convert_to_dict = utils.convert_to_dict


def test_convert_to_dict_returns_dict_unchanged():
    data = {'a': 1, 'b': 2}
    assert convert_to_dict(data) == data


def test_convert_to_dict_converts_tuples_to_ordered_dict():
    data = (('a', 1), ('b', 2))
    assert convert_to_dict(data) == OrderedDict([('a', 1), ('b', 2)])
