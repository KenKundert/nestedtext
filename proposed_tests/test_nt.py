# IMPORTS {{{1
from functools import partial
from inform import cull, render
from parametrize_from_file import parametrize
from pathlib import Path
from voluptuous import Schema, Required, Any
from base64 import b64decode
import nestedtext as nt
import os
import pytest

# GLOBALS {{{1
TEST_SUITE = Path('tests.json')
TEST_DIR = Path(__file__).parent

# PARAMETERIZATION {{{1
# Adapt parametrize_for_file to read dictionary rather than list {{{2
def name_from_dict_keys(cases):
    return [{**v, 'id': k} for k,v in cases.items()]
        # the name 'id' is special, do not change it
parametrize = partial(parametrize, preprocess=name_from_dict_keys)


# SCHEMA {{{1
def as_int(arg):
    return int(arg)

schema = Schema({
    Required("id", default='❬not given❭'): str,
    Required("load_in"): str,
    Required("load_out", default=None): Any(dict, list, str, None),
    Required("load_err", default={}): dict(
        message = str,
        line = str,
        lineno = Any(None, as_int),
        colno = Any(None, as_int)
    ),
    Required("encoding", default='utf-8'): str,
    Required("types"): {str:int},
})


# Checker {{{1
class Checker:
    def __init__(self, test_name):
        self.test_name = test_name

    def check(self, expected, result, phase):
        self.expected = expected
        self.result = result
        self.phase = phase
        assert expected == result, self.fail_message()

    def fail_message(self):
        expected = list(render(self.expected).splitlines())
        result = list(render(self.result).splitlines())

        for i, lines in enumerate(zip(expected, result)):
            eline, rline = lines
            if eline != rline:
                break
        else:
            elen = len(expected)
            rlen = len(result)
            i += 1
            if elen > rlen:
                eline = expected[i]
                rline = '❬not available❭'
            else:
                eline = '❬not available❭'
                rline = result[i]

        expected = f"expected[{i}]: {eline}"
        result = f"  result[{i}]: {rline}"
        desc = f"{self.test_name} while {self.phase}"

        return '\n'.join([desc, expected, result])

# HELPER FUNCTIONS FOR FILE INTERFACE TESTING {{{1
def prepare_load_input(content_bytes, input_type, tmp_path):
    """
    Convert test content to specified input type for nt.load() or nt.loads().

    Returns: (input_object, cleanup_function, loader_function)
    - loader_function: nt.loads or nt.load depending on input type
    """
    cleanup = lambda: None  # default no-op cleanup

    if input_type == "string":
        # Return content directly for nt.loads()
        return content_bytes, cleanup, nt.loads

    elif input_type == "str_path":
        path = tmp_path / "input.nt"
        path.write_bytes(content_bytes)
        return str(path), cleanup, nt.load

    elif input_type == "pathlib":
        path = tmp_path / "input.nt"
        path.write_bytes(content_bytes)
        return path, cleanup, nt.load

    elif input_type == "file_handle":
        path = tmp_path / "input.nt"
        path.write_bytes(content_bytes)
        fh = open(path, 'r', encoding='utf-8-sig')  # utf-8-sig strips BOM
        cleanup = lambda: fh.close()
        return fh, cleanup, nt.load

    elif input_type == "fd":
        path = tmp_path / "input.nt"
        path.write_bytes(content_bytes)
        fd = os.open(str(path), os.O_RDONLY)
        # nt.load() closes the FD, so cleanup should handle already-closed FD
        def cleanup_fd():
            try:
                os.close(fd)
            except OSError:
                pass  # FD already closed by nt.load()
        return fd, cleanup_fd, nt.load

    elif input_type == "iterator":
        # Write to file and read with universal newlines to match file behavior
        path = tmp_path / "input.nt"
        path.write_bytes(content_bytes)
        fh = open(path, 'r', encoding='utf-8-sig')  # utf-8-sig strips BOM
        # Create an iterator from the file handle (mimics file iteration with proper universal newlines)
        cleanup = lambda: fh.close()
        return iter(fh), cleanup, nt.load


def prepare_dump_output(output_type, tmp_path):
    """
    Prepare output destination for nt.dump() or indicate nt.dumps().

    Returns: (dest_object, result_path, cleanup_function, dumper_function)
    - dumper_function: nt.dumps or nt.dump depending on output type
    - For dumps: dest_object and result_path will be None
    """
    cleanup = lambda: None  # default no-op cleanup

    if output_type == "string":
        # Return None for nt.dumps() (returns string directly)
        return None, None, cleanup, nt.dumps

    elif output_type == "str_path":
        path = tmp_path / "output.nt"
        return str(path), path, cleanup, nt.dump

    elif output_type == "pathlib":
        path = tmp_path / "output.nt"
        return path, path, cleanup, nt.dump

    elif output_type == "file_handle":
        path = tmp_path / "output.nt"
        fh = open(path, 'w', encoding='utf-8')
        cleanup = lambda: fh.close()
        return fh, path, cleanup, nt.dump

    elif output_type == "fd":
        path = tmp_path / "output.nt"
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT, 0o644)
        # nt.dump() may close the FD, so cleanup should handle already-closed FD
        def cleanup_fd():
            try:
                os.close(fd)
            except OSError:
                pass  # FD already closed by nt.dump()
        return fd, path, cleanup_fd, nt.dump

# TESTS {{{1
@parametrize(
    path = TEST_DIR / TEST_SUITE,
    key = "load_tests",
    schema = schema,
)
def test_nt(tmp_path, load_in, load_out, load_err, encoding, types, request):
    checker = Checker(request.node.callspec.id)

    # check load
    content = b64decode(load_in.encode('ascii'))
    try:
        result = nt.loads(content, top=any)
        if load_err:
            checker.check("@@@ an error @@@", result, "loading")
            return
        else:
            checker.check(load_out, result, "loading")
    except nt.NestedTextError as e:
        result = dict(
            message = e.get_message(),
            line = e.line,
            lineno = e.lineno,
            colno = e.colno
        )
        checker.check(cull(load_err), cull(result), "loading")
        return
    except UnicodeDecodeError as e:
        problematic = e.object[e.start:e.end]
        prefix = e.object[:e.start]
        lineno = prefix.count(b'\n')
        _, _, bol = prefix.rpartition(b'\n')
        eol, _, _ = e.object[e.start:].partition(b'\n')
        line = bol + eol
        colno = line.index(problematic)

        if encoding != 'bytes':
            line = line.decode(encoding)
        else:
            line = line.decode('ascii', errors='backslashreplace')
            load_err['line'] = load_err['line'].encode(
                'ascii', errors='backslashreplace'
            ).decode('ascii')

        result = dict(
            message = e.reason,
            line = line,
            lineno = lineno,
            colno = colno,
        )
        checker.check(load_err, result, "loading")
        return

    # check dump by doing a round-trip through load
    # the stimulus file does not have expected dump results because they can
    # vary between implementations and with dump options.
    try:
        dumped = nt.dumps(result)
    except nt.NestedTextError:
        checker.check(None, result, "dumping")

    try:
        result = nt.loads(dumped, top=any)
        checker.check(load_out, result, "re-loading")
    except nt.NestedTextError:
        checker.check(None, result, "re-loading")


# NEW INTERFACE TESTS {{{1
@parametrize(
    path = TEST_DIR / TEST_SUITE,
    key = "load_tests",
    schema = schema,
)
@pytest.mark.parametrize("input_type", ["string", "str_path", "pathlib", "file_handle", "fd", "iterator"])
def test_nt_load_interfaces(tmp_path, input_type, load_in, load_out, load_err, encoding, types, request):
    """Test nt.load() and nt.loads() with all supported input interface types"""
    checker = Checker(f"{request.node.callspec.id}/{input_type}")

    # Prepare input in specified format
    content = b64decode(load_in.encode('ascii'))
    input_obj, cleanup, loader = prepare_load_input(content, input_type, tmp_path)

    try:
        # Test load or loads using the returned loader function
        result = loader(input_obj, top=any)

        if load_err:
            checker.check("@@@ an error @@@", result, f"loading via {input_type}")
            return
        else:
            checker.check(load_out, result, f"loading via {input_type}")

    except nt.NestedTextError as e:
        result = dict(
            message = e.get_message(),
            line = e.line,
            lineno = e.lineno,
            colno = e.colno
        )
        checker.check(cull(load_err), cull(result), f"loading via {input_type}")
        return

    except UnicodeDecodeError as e:
        # Handle unicode errors (same logic as test_nt)
        problematic = e.object[e.start:e.end]
        prefix = e.object[:e.start]
        lineno = prefix.count(b'\n')
        _, _, bol = prefix.rpartition(b'\n')
        eol, _, _ = e.object[e.start:].partition(b'\n')
        line = bol + eol
        colno = line.index(problematic)

        if encoding != 'bytes':
            line = line.decode(encoding)
        else:
            line = line.decode('ascii', errors='backslashreplace')
            load_err['line'] = load_err['line'].encode(
                'ascii', errors='backslashreplace'
            ).decode('ascii')

        result = dict(
            message = e.reason,
            line = line,
            lineno = lineno,
            colno = colno,
        )
        checker.check(load_err, result, f"loading via {input_type}")
        return

    finally:
        cleanup()


@parametrize(
    path = TEST_DIR / TEST_SUITE,
    key = "load_tests",
    schema = schema,
)
@pytest.mark.parametrize("output_type", ["string", "str_path", "pathlib", "file_handle", "fd"])
def test_nt_dump_interfaces(tmp_path, output_type, load_in, load_out, load_err, encoding, types, request):
    """Test nt.dump() and nt.dumps() with all supported output interface types"""
    checker = Checker(f"{request.node.callspec.id}/{output_type}")

    # Skip if test expects a load error (nothing to dump)
    if load_err:
        pytest.skip("Test case expects load error, nothing to dump")

    # First load the data using loads()
    content = b64decode(load_in.encode('ascii'))
    obj = nt.loads(content, top=any)

    # Prepare output destination
    dest, result_path, cleanup, dumper = prepare_dump_output(output_type, tmp_path)

    try:
        # Dump using the returned dumper function
        if dumper is nt.dumps:
            dumped_content = dumper(obj)
        else:
            dumper(obj, dest)
            # For file handles/descriptors, need to close before reading
            cleanup()
            # Read back the dumped content
            dumped_content = result_path.read_text(encoding='utf-8')
            # Verify trailing newline is present (dump() adds it, dumps() doesn't)
            assert dumped_content.endswith('\n'), f"dump() should add trailing newline via {output_type}"

        # Verify content can be loaded back and matches original
        reloaded = nt.loads(dumped_content, top=any)
        checker.check(load_out, reloaded, f"dump via {output_type} then reload")

    except nt.NestedTextError:
        # Some data structures may not be dumpable
        checker.check(None, obj, f"dumping via {output_type}")


def test_nt_dump_trailing_newline(tmp_path):
    """Verify that dump() adds trailing newline while dumps() does not"""
    test_cases = [
        {"key": "value"},
        ["item1", "item2"],
        "simple string"
    ]

    for data in test_cases:
        # Get dumps() result (no trailing newline unless already in content)
        dumps_result = nt.dumps(data)

        # Test with string path
        path = tmp_path / "test_newline.nt"
        nt.dump(data, str(path))
        file_content = path.read_text()

        # Verify dump() adds exactly one trailing newline
        assert file_content.endswith('\n'), "dump() should add trailing newline"
        assert not file_content.endswith('\n\n'), "dump() should not add double newline"
        assert file_content == dumps_result + '\n', "dump() should be dumps() + newline"
