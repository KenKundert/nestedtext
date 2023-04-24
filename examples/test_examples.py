# encoding: utf8

from pathlib import Path
from shlib import Run, cd, cwd, to_path
from textwrap import dedent
import pytest
import sys

tests_dir = Path(__file__).parent

def strip_comments(text):
     return '\n'.join(
        l for l in text.splitlines()
        if l.strip() and not l.strip().startswith('#')
    )

def test_nestedtext_to_json():
     with cd(tests_dir):
        stimulus = Path('address.nt').read_text()
        expected = Path('address.json').read_text()
        nt2json = Run('./nestedtext-to-json', stdin=stimulus, modes='sOEW')
        assert nt2json.stdout.strip() == expected.strip()

def test_nestedtext_to_json_fumiko():
     with cd(tests_dir):
        stimulus = Path('fumiko.nt').read_text()
        expected = Path('fumiko.json').read_text()
        nt2json = Run('./nestedtext-to-json', stdin=stimulus, modes='sOEW')
        assert nt2json.stdout.strip() == expected.strip()

def test_json_to_nestedtext():
     with cd(tests_dir):
        stimulus = Path('address.json').read_text()
        expected = strip_comments(Path('address.nt').read_text())
        json2nt = Run('./json-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert json2nt.stdout.strip() == expected.strip()

def test_json_to_nestedtext_fumiko():
     with cd(tests_dir):
        stimulus = Path('fumiko.json').read_text()
        expected = strip_comments(Path('fumiko.nt').read_text())
        json2nt = Run('./json-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert json2nt.stdout.strip() == expected.strip()

def test_yaml_to_nestedtext():
     with cd(tests_dir):
        stimulus = Path('github-orig.yaml').read_text()
        expected = strip_comments(Path('github-orig.nt').read_text())
        yaml2nt = Run('./yaml-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert yaml2nt.stdout.strip() == expected.strip()

def test_nestedtext_to_yaml():
     with cd(tests_dir):
        stimulus = Path('github-intent.nt').read_text()
        expected = Path('github-intent.yaml').read_text()
        nt2yaml = Run('./nestedtext-to-yaml', stdin=stimulus, modes='sOEW')
        assert nt2yaml.stdout.strip() == expected.strip()

def test_toml_to_nestedtext():
     with cd(tests_dir):
        stimulus = Path('sparekeys.toml').read_text()
        expected = Path('sparekeys.nt').read_text()
        toml2nt = Run('./toml-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert toml2nt.stdout.strip() == expected.strip()

def test_csv_to_nestedtext():
     with cd(tests_dir):
        stimulus = Path('percent_bachelors_degrees_women_usa.csv').read_text()
        expected = Path('percent_bachelors_degrees_women_usa.nt').read_text()
        csv2nt = Run('./csv-to-nestedtext -n', stdin=stimulus, modes='sOEW')
        assert csv2nt.stdout.strip() == expected.strip()

def test_deploy_pydantic():
     with cd(tests_dir):
        expected = Path('deploy_pydantic.out').read_text()
        dp = Run('python3 deploy_pydantic.py', modes='sOEW')
        assert dp.stdout.strip() == expected.strip()

def test_deploy_voluptuous():
     with cd(tests_dir):
        expected = Path('deploy_voluptuous.out').read_text()
        dv = Run('python3 deploy_voluptuous.py', modes='sOEW')
        assert dv.stdout.strip() == expected.strip()

def test_address():
     if sys.version_info < (3, 8):
         return  # address example uses walrus operator
     with cd(tests_dir):
        fumiko = Run('./address fumiko', modes='sOEW')
        assert fumiko.stdout.strip() == dedent("""
            Fumiko Purvis:
                Position: Treasurer
                Address:
                    3636 Buffalo Ave
                    Topeka, Kansas 20692
                Phone: 1-268-555-0280
                EMail: fumiko.purvis@hotmail.com
        """).strip()

def test_michael_jordan():
     if sys.version_info < (3, 8):
         return  # address example uses walrus operator
     with cd(tests_dir):
        mj = Run('./michael_jordan', modes='sOEW')
        expected = Path('./michael_jordan.out').read_text()
        assert mj.stdout.strip() == expected.strip()

def test_cryptocurrency():
     if sys.version_info < (3, 8):
         return  # cryptocurrency example uses walrus operator
     with cd(tests_dir):
        # the cryptocurrency example outputs the current prices, so just do some
        # simple sanity checking on the output.
        cc = Run('./cryptocurrency', modes='sOEW')
        assert '5 BTC =' in cc.stdout
        assert '50 ETH =' in cc.stdout
        assert '50 kXLM =' in cc.stdout

def test_postmortem():
     if sys.version_info < (3, 8):
         return  # postmortem example uses walrus operator
     with cd(tests_dir):
        expected = Path('postmortem.expanded.nt').read_text()
        user_home_dir = str(to_path('~'))
        expected = expected.replace('~', user_home_dir)

        pm = Run('./postmortem', modes='sOEW')
        assert pm.stdout.strip() == expected.strip()

def test_diet():
     with cd(tests_dir):
        mj = Run('./diet', modes='sOEW')
        expected = Path('./diet.nt').read_text()
        assert mj.stdout.strip() == expected.strip()
