Proposed Replacement Official NestedText Test Suite
===================================================


Issues with Previous Test Suite
-------------------------------

The previous test suite had the following issues.

1. It contained symbolic links, which caused problems on Windows.

2. The tests contain invisible characters in the form of tabs, end-of-line 
   spaces, unicode white spaces, control characters, and line termination 
   characters.  These invisible characters were often confusing and could easily 
   be lost.

3. The tests were too tailored to the specific behavior of the Python 
   *NestedText* implementation.

4. The tests were categorized and numbered.  Both the categorization and 
   numbering were problematic.  Each test often fit into many categories but 
   could only be placed in one.  The numbering implied an order where no natural 
   order exists.

5. Important tests were missing from the test suite.


The New Test Suite
------------------

These test cases are focused on assuring that valid *NestedText* input is 
properly read and invalid NestedText is properly identified by an implementation 
of *NestedText*.  No attempt is made to assure that the implementation produces 
valid *NestedText*.  There is considerably flexibility in the way that 
*NestedText* may be generated.  In light of this flexibility the best way to 
test a *NestedText* writer is to couple it with a *NestedText* reader and 
perform a round trip through both, which can be performed with these test cases.

The test cases are contained in *tests.nt*.  The convert command converts these 
test cases into JSON (*tests.json*).  It is expected this JSON file is what is 
used to test *NestedText* implementations.  The *NestedText* file of test cases, 
*tests.nt*, is used to generate *tests.json*, and is only needed if you plan to 
add or modify tests.  Do not modify the JSON file directly, as any changes will 
be overridden whenever *convert* is run.

Each test case in *tests.nt* is a dictionary entry.  The key is used as the name 
of the test.  The keys must be unique and are largely chosen at random, but any 
words that are expected to be found within the test cases are avoided.  This 
allows test cases to be quickly found by searching for their name.

The fields that may be specified are:

description (str):
    Simply describes the test.  Is optional and unused.

string_in (str):
    This is a string that will be fed into a *NestedText* load function.  This 
    string contains a *NestedText* document, though that document may contain 
    errors.  This string may contain Unicode characters and Unicode escape 
    sequences.  It is generally recommended that Unicode white space be given 
    using escape sequences so that there presence is obvious.

bytes_in (str):
    This is an alternate to *string_in*.  In this case the *NestedText* document 
    is constrained to consist of ASCII characters and escape sequences such as 
    \\t, \\r, \\n, etc.  Also supported are binary escape sequences, \\x00 to 
    \\xFF.

encoding (str):
    The desired encoding for the *NestedText* document.  The default encoding is 
    UTF-8.  If you specify *bytes* as the encoding, no encoding is used.

load_out (None | str | list | dict):
    The expected output from the *NestedText* load function if no errors are 
    expected.  If a string is given and if the first character in the string is 
    ‘!’, then the mark is removed and what remains is evaluated by Python, with 
    the result becoming the expected output.

load_err (dict):
    Details about the error that is expected to be found and reported by the 
    *NestedText* load function.  It consists of 4 fields:

    message (str):
        The error message that is emitted by the Python implementation of 
        *NestedText*.

    line (str):
        The text of the line in the *NestedText* input from *load_in* or 
        *bytes_in* that contains the error.

    lineno (None, int):
        The line number of the line that contains the error.  The first line 
        is line 0.

    colno (None, int):
        The number of the column where the error is likely to be.  The first 
        column is column 0.

Here is an example of a test with a valid *NestedText* document::

    pundit:
        description: a single-level dictionary
        load_in:
            > key 1: value 1
            > key 2: value 2
            >
        load_out:
            key 1: value 1
            key 2: value 2

And here is an example of a test with an invalid *NestedText* document::

    foundling:
        load_in:
            > ingredients:
            >   - 3 green chilies
            >     - 3 red chilies
        load_err:
            message: invalid indentation
            line:     - 3 red chilies
            lineno: 2
            colno: 2

The test keys (*pundit* and *foundling*) are arbitrary.

Control characters and Unicode white space characters are expected to be 
backslash escaped in *load_in*, *bytes_in*, *load_out*, and *load_err.lines*.  
Here are some specific cases where backslash escapes should be used:

**Line Terminations**  Newlines are replaced by line feed (LF) characters unless 
the newline is preceded by either \\r or \\n or both.  The \\r is replaced by 
a carriage return (CR) and the \\n is replaced by a line feed (LF).  In this way 
the line termination characters can be specified explicitly on a per line basis.  
For example::

    key 1: this line ends with CR & LF\r\n
    key 2: this line ends with CR\r
    key 3: this line ends with LF\n
    key 4: this line also ends with LF
    key 5: this line, being the last, has no line termination character

**White Space**  All white space other than ASCII spaces and newlines should be 
made explicit by using backslash escape sequences.  Specifically tabs should be 
specified as \\t and the Unicode white spaces should be specified using their 
\\x or \\u code (ex. \\xa0 or \\u00a0 for the no-break space).  In addition, end 
of line spaces are optionally made explicit by replacing them with \\x20 if they 
are important and there is concern that they may be accidentally lost.

**Other Special Characters**  Backslash escape codes should also be used for 
control codes (\\a for bell, \\b for backspace, \\x7f for delete, \\x1b for 
escape, etc) and for backslash itself (\\\\).


tests.json
----------

The *convert* command creates *tests.json*, but if you do not wish to add or 
modify the tests, you can simply use *tests.json* from the GitHub repository.

*tests.json* is a file suitable for use with `parametrize_from_file 
<https://parametrize-from-file.readthedocs.io/en/latest/api/parametrize_from_file.html>`_, 
which is a *pytest* plugin suitable for testing Python projects (*test_nt.py* 
uses *parametrize_from_file* to apply *tests.json* to the Python implementation 
of *NestedText*).  However, you can use *tests.json* directly to implement tests 
for any *NestedText* implementation in any language.

It contains dictionary with a single key, *load_tests*.  The value of this key 
is a nested dictionary where each key-value pair is one test.  The key is the 
name of the test and the value is the test.  The test consists of the following 
fields:

load_in:
    This is a string that contains the *NestedText* document to be loaded for 
    the test.  The string is a base64 encoded string of bytes.

load_out:
    The expected output from the *NestedText* loader if no error is expected.  
    The structure of this value is dependent on the *NestedText* document 
    encoded in *load_in*.  It may be a nested collection of lists, dictionaries 
    and strings, or it may be *null*.

load_err:
    Details about an expected error.  *load_err* supports the following 
    subfields:

    message:
        The message generated by the Python implementation of *NestedText* for 
        the expected error.

    line:
        The line in the input document where the error occurs.

    lineno:
        The line number of the line where the error occurs.  0 represents the 
        first line in the document.  Is *null* or missing if the line number is 
        unknown.

    colno:
        The column number where the error occurs.  0 represents the first 
        column.  Is *null* or missing if the column number is unknown.

encoding:
    The encoding for the *NestedText* document.  The default encoding is UTF-8.

types:
    A dictionary of line-type counts.  It contains the count of each type of 
    line contained in the input document.  These counts can be used to filter 
    the tests if desired.

    The line types are::

        blank
        comment
        dict item
        inline dict
        inline list
        key item
        list item
        string item
        unrecognized


Caveats
-------

Be aware that this is a trial version of the official *NestedText* tests, and so 
is subject to change.

This is the second trial version of this new test suite.  It was uploaded on 23 
March 2025 and again on 24 March with more tests (there are now 143 tests).

Version 3.7 of the Python implementation of *NestedText* does not yet pass all 
of these tests.
