# encoding: utf8

from shlib import Run, to_path, set_prefs
from textwrap import dedent

def strip_comments(text):
     return '\n'.join(
        l for l in text.splitlines()
        if l.strip() and not l.strip().startswith('#')
    )

def test_nestedtext_to_json():
     stimulus = to_path('address.nt').read_text()
     expected = to_path('address.json').read_text()
     nt2json = Run('./nestedtext-to-json', stdin=stimulus, modes='sOEW')
     assert nt2json.stdout.strip() == expected.strip()

def test_json_to_nestedtext():
     stimulus = to_path('address.json').read_text()
     expected = strip_comments(to_path('address.nt').read_text())
     json2nt = Run('./json-to-nestedtext', stdin=stimulus, modes='sOEW')
     assert json2nt.stdout.strip() == expected.strip()

def test_csv_to_nestedtext():
     stimulus = to_path('percent_bachelors_degrees_women_usa.csv').read_text()
     expected = to_path('percent_bachelors_degrees_women_usa.nt').read_text()
     csv2nt = Run('./csv-to-nestedtext -n', stdin=stimulus, modes='sOEW')
     assert csv2nt.stdout.strip() == expected.strip()

def test_deploy_pydantic():
     expected = to_path('deploy_pydantic.nt').read_text()
     dp = Run('python3 deploy_pydantic.py', modes='sOEW')
     assert dp.stdout.strip() == expected.strip()

def test_deploy_voluptuous():
     expected = to_path('deploy_voluptuous.nt').read_text()
     dv = Run('python3 deploy_voluptuous.py', modes='sOEW')
     assert dv.stdout.strip() == expected.strip()

def test_cryptocurrency():
     # the cryptocurrency example outputs the current prices, so just do some
     # simple sanity checking on the output.
     cc = Run('./cryptocurrency', modes='sOEW')
     assert '5 BTC =' in cc.stdout
     assert '50 ETH =' in cc.stdout
     assert '50 kXLM =' in cc.stdout

def test_postmortem():
     expected = to_path('postmortem.json').read_text()
     pm = Run('python3 postmortem.py', modes='sOEW')
     assert pm.stdout.strip() == expected.strip()
