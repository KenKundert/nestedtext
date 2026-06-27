# encoding: utf8

from pathlib import Path
from shlib import Run, cd, to_path
from textwrap import dedent
from inform import Color
import sys
import re

tests_dir = Path(__file__).parent

def strip_comments(text):
     return '\n'.join(
        l for l in text.splitlines()
        if l.strip() and not l.strip().startswith('#')
    )

def test_nestedtext_to_json():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('../addresses/address.nt').read_text()
        expected = Path('../addresses/address.json').read_text()
        nt2json = Run('./nestedtext-to-json', stdin=stimulus, modes='sOEW')
        assert nt2json.stdout.strip() == expected.strip()

def test_nestedtext_to_json_fumiko():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('../addresses/fumiko.nt').read_text()
        expected = Path('../addresses/fumiko.json').read_text()
        nt2json = Run('./nestedtext-to-json', stdin=stimulus, modes='sOEW')
        assert nt2json.stdout.strip() == expected.strip()

def test_json_to_nestedtext():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('../addresses/address.json').read_text()
        expected = strip_comments(Path('../addresses/address.nt').read_text())
        json2nt = Run('./json-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert json2nt.stdout.strip() == expected.strip()

def test_json_to_nestedtext_fumiko():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('../addresses/fumiko.json').read_text()
        expected = strip_comments(Path('../addresses/fumiko.nt').read_text())
        json2nt = Run('./json-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert json2nt.stdout.strip() == expected.strip()

def test_yaml_to_nestedtext():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('github-orig.yaml').read_text()
        expected = strip_comments(Path('github-orig.nt').read_text())
        yaml2nt = Run('./yaml-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert yaml2nt.stdout.strip() == expected.strip()

def test_nestedtext_to_yaml():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('github-intent.nt').read_text()
        expected = Path('github-intent.yaml').read_text()
        nt2yaml = Run('./nestedtext-to-yaml', stdin=stimulus, modes='sOEW')
        assert nt2yaml.stdout.strip() == expected.strip()

def test_toml_to_nestedtext():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('sparekeys.toml').read_text()
        expected = Path('sparekeys.nt').read_text()
        toml2nt = Run('./toml-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert toml2nt.stdout.strip() == expected.strip()

def test_csv_to_nestedtext():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('percent_bachelors_degrees_women_usa.csv').read_text()
        expected = Path('percent_bachelors_degrees_women_usa.nt').read_text()
        csv2nt = Run('./csv-to-nestedtext -n', stdin=stimulus, modes='sOEW')
        assert csv2nt.stdout.strip() == expected.strip()

def test_xml_to_nestedtext():
     with cd(tests_dir / "conversion-utilities"):
        stimulus = Path('dmarc.xml').read_text()
        expected = Path('dmarc.nt').read_text()
        xml2nt = Run('./xml-to-nestedtext', stdin=stimulus, modes='sOEW')
        assert xml2nt.stdout.strip() == expected.strip()

def test_deploy_pydantic():
     with cd(tests_dir / "validation"):
        expected = Path('deploy_pydantic.out').read_text()
        dp = Run('python3 deploy_pydantic.py', modes='sOEW')
        assert dp.stdout.strip() == expected.strip()

def test_deploy_voluptuous():
     with cd(tests_dir / "validation"):
        expected = Path('deploy_voluptuous.out').read_text()
        dv = Run('python3 deploy_voluptuous.py', modes='sOEW')
        assert dv.stdout.strip() == expected.strip()

def test_address():
     if sys.version_info < (3, 8):
         return  # address example uses walrus operator
     with cd(tests_dir / "addresses"):
        fumiko = Run('./address fumiko', modes='sOEW')
        assert fumiko.stdout.strip() == dedent("""
            # Contact information for our officers

            Fumiko Purvis:
                Position: Treasurer
                    # Fumiko's term is ending at the end of the year.
                Address:
                    3636 Buffalo Ave
                    Topeka, Kansas 20692
                Phone: 1-268-555-0280
                EMail: fumiko.purvis@hotmail.com
        """).strip()

def test_michael_jordan():
     if sys.version_info < (3, 8):
         return  # address example uses walrus operator
     with cd(tests_dir / "deduplication"):
        mj = Run('./michael_jordan', modes='sOEW')
        expected = Path('./michael_jordan.out').read_text()
        assert mj.stdout.strip() == expected.strip()

# def test_cryptocurrency():
#      if sys.version_info < (3, 8):
#          return  # cryptocurrency example uses walrus operator
#      with cd(tests_dir / "cryptocurrency"):
#         # the cryptocurrency example outputs the current prices, so just do some
#         # simple sanity checking on the output.
#         cc = Run('./cryptocurrency', modes='sOEW')
#         assert '5 BTC =' in cc.stdout
#         assert '50 ETH =' in cc.stdout
#         assert '50 kXLM =' in cc.stdout

def test_postmortem():
     if sys.version_info < (3, 8):
         return  # postmortem example uses walrus operator
     with cd(tests_dir / "postmortem"):
        expected = Path('postmortem.expanded.nt').read_text()
        user_home_dir = str(to_path('~'))
        expected = expected.replace('~', user_home_dir)

        pm = Run('./postmortem', modes='sOEW')
        assert pm.stdout.strip() == expected.strip()

def test_diet():
     with cd(tests_dir / "references"):
        mj = Run('./diet', modes='sOEW')
        expected = Path('./diet.nt').read_text()
        assert mj.stdout.strip() == expected.strip()

def test_long_lines():
     with cd(tests_dir / "long_lines"):
        ll = Run('./long_lines_backslash', modes='sOEW')
        expected = Path('./long_lines.out').read_text()
        assert ll.stdout.strip() == expected.strip()

        ll = Run('./long_lines_space', modes='sOEW')
        expected = Path('./long_lines.out').read_text()
        assert ll.stdout.strip() == expected.strip()

def test_error_reporting():
    with cd(tests_dir / "errors"):
        test = Run(["./test"], modes="sOEW")
        stderr = Color.strip_colors(test.stderr)
        stdout = Color.strip_colors(test.stdout)
        expected = dedent("""\
            test error: test_cases.nt@3, 0›expected, expr=2**8: test failed.
                result=256 ≠ expected=255
            test error: test_cases.nt@5, 1›expr: invalid literal for int() with base 10: 'x'
                   5 ❬    expr: int('x')❭
            test error: test_cases.nt@8, 2›expr: '(' was never closed (<string>, line 1)
                   8 ❬    expr: math.log2(4096❭
                                          ▲
        """)
        assert test.status == 0
        assert stderr == ""
        assert stdout == expected

def test_includes():
    with cd(tests_dir / "includes"):
        test = Run(["./includes", "first.nt"], modes="sOEW")
        stderr = Color.strip_colors(test.stderr)
        stdout = Color.strip_colors(test.stdout)
        expected = dedent("""\
            table_2:
                row_21:
                    col_211: value 211
                    col_212: value 212
            table_1:
                row_11:
                    col_111: value 111
                row_12:
                    col_121: value 121
            table_3:
                row_31:
                    col_311: value 311
        """)
        assert test.status == 0
        assert stderr == ""
        assert stdout == expected

def test_includes_with_error():
    with cd(tests_dir / "includes"):
        test = Run(["./includes", "first-with-error.nt"], modes="sOEW1")
        stderr = Color.strip_colors(test.stderr)
        stdout = Color.strip_colors(test.stdout)
        expected = dedent("""\
            includes error: /.*/children/third-with-error.nt@8, table 3›row 32›col 321:
                Bad value.
                       8 ❬        col 321: ERROR❭
        """)
        assert test.status == 1
        assert stdout == ""
        assert re.match(expected, stderr)

def test_commenting():
    with cd(tests_dir / "weight"):
        test = Run(["./weight"], modes="sOEW")
        assert test.stdout == ""
        assert test.stderr == ""
        plain = Path("plain.nt").read_text()
        expected = dedent("""\
            name: Zachery Farrell
            height: 6-2
            diary:
                2025-09-10: 207.8
                2025-09-19: 206.4
                2025-09-21: 205.8
                2025-10-07: 203
                2025-10-20: 203.6
                2025-10-29: 203.8
                2025-11-10: 209.2
                2025-11-24: 208.4
                2025-12-07: 207.5
                2025-12-17: 208.5
                2026-01-05: 210
                2026-01-19: 207.4
                2026-01-30: 203.4
        """)
        assert plain == expected
        commented = Path("commented.nt").read_text()
        expected = dedent("""\
            # Weight diary for Zachery Farrell

            name: Zachery Farrell
            height: 6-2
                    # feet-inches

            diary:

                # 2025
                # September
                2025-09-10: 207.8
                2025-09-19: 206.4
                2025-09-21: 205.8

                # October
                2025-10-07: 203
                2025-10-20: 203.6
                2025-10-29: 203.8

                # November
                2025-11-10: 209.2
                2025-11-24: 208.4

                # December
                2025-12-07: 207.5
                2025-12-17: 208.5

                # 2026
                # January
                2026-01-05: 210
                2026-01-19: 207.4
                2026-01-30: 203.4

            # All weights given in pounds.
        """)
        assert commented == expected
