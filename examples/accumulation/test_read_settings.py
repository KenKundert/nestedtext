# imports {{{1
from flatten_dict import flatten
from functools import partial
from inform import Error
from parametrize_from_file import parametrize
from voluptuous import Schema, Required, Optional, Any
from settings import read_settings
import pytest


# parameterization {{{1
# Adapt parametrize_for_file to read dictionary rather than list {{{2
def name_from_dict_keys(cases):
    return [{**v, 'scenario': k} for k,v in cases.items()]

parametrize = partial(parametrize, preprocess=name_from_dict_keys)


class Checker:
    def __init__(self, scenario):
        self.scenario = scenario

    def check_dicts(self, expected, results):
        try:
            if expected[0] == '!':
                expected = eval(expected[1:])
        except KeyError:
            pass
        self.expected = expected
        self.results = results
        assert expected == results, self.cmp_dicts(expected, results)

    def check_text(self, expected, results):
        self.expected = expected
        self.results = results
        assert expected == results, self.cmp_text(expected, results)

    def cmp_dicts(self, expected, results):
        expected = flatten(expected)
        results = flatten(results)
        message = [f"scenario: {self.scenario}"]
        missing = expected.keys() - results.keys()
        if missing:
            message.append(f"missing from results: {', '.join('.'.join(k) for k in missing)}")
        extra = results.keys() - expected.keys()
        if extra:
            message.append(f"extra in results: {', '.join('.'.join(k) for k in extra)}")
        for key in expected.keys() & results.keys():
            if expected[key] != results[key]:
                message.append(f"{key} differs:")
                message.append(f" e: {expected[key]}")
                message.append(f" r: {results[key]}")
        return '\n'.join(message)

    def cmp_text(self, expected, results):
        message = [f"scenario: {self.scenario}"]
        message.append(f"  expected: {expected}")
        message.append(f"    result: {results}")
        return '\n'.join(message)

# schema for test cases {{{1
scenario_schema = Schema({
    Required("scenario"): str,
    Required("given"): str,
    Optional("expected", default=""): Any(str, list, dict),
    Optional("error", default=""): str,
}, required=True)

@parametrize(
    key = "basic_tests",
    schema = scenario_schema,
)
def test_basic(tmp_path, scenario, given, expected, error):
    checker = Checker(scenario)
    path = tmp_path / 'settings.nt'
    path.write_text(given)
    if expected:
        settings = read_settings(path)
        checker.check_dicts(expected, settings)
        return
    with pytest.raises(Error) as exception:
        read_settings(path)
    result = exception.value.get_message()
    # _, _, message = message.rpartition('/')
    checker.check_text(error, result)
