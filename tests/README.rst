Testing Udif Encoders and Decoders
==================================

run-tests is a program for running test cases through a Udif encoders and 
decoders.  If you do not explicitly specify an encoder or decoder, the tests in 
valid and invalid are run on the internal Python reference encoder and decoder.  
However, you may specify either and encoder or decoder or both, in which case 
external programs are used to implement the encoder and decoder.  In this way, 
implementations of Udif in different languages can be tested with this suite of 
tests.

An external encoder or decoder must be implemented as a program that takes input 
from stdin, writes to stdout, and returns an exit status of 0 if no errors were 
found and the desired transformation occurred otherwise it returns an exit 
status of 1.

An external encoder must accept *json* as input and write *udif* as output.
An 'external' encoder that actually uses the reference encoder is provided in 
*json-to-udif*

An external decoder must accept *udif* as input and write *json* as output.
An 'external' decoder that actually uses the reference decoder is provided in 
*udif-to-json*

For example, to run all tests on internal reference encoder and decoder::

    $ ./run-tests

To run tests on an external encoder use::

    $ ./run-tests --encoder=json-to-udif

To run tests on an external decoder use::

    $ ./run-tests --decoder=udif-to-json

To run tests on both an external encoder and decoder use::

    $ ./run-tests --encoder=json-to-udif --decoder=udif-to-json

Tests
-----

The tests are organized into two directories: *valid* for those tests expected 
to succeed and *invalid* for those expected to fail.

Encoder tests take the form of *json* files that are converted to *udif* and 
then converted back to *json* using the internal reference decoder.  The output 
of the reference decoder is compared to the content of the given *json* file to 
make sure the match.  For a *valid* test to succeed, the results must match.  
For an *invalid* test to succeed, the encoder must fail with an error (a 
successul conversion followed by a mismatch does not represent success for 
*invalid* test cases).

Decoder tests take the form of a pair of a *udif* and a *json* with the same 
base name.  The output of the decoder is compared with the contents of the 
*json* file to determine if they match.  For a *valid* test to succeed, the 
results must match.  For an *invalid* test to succeed, the decoder must fail 
with an error (a successul conversion followed by a mismatch does not represent 
success for *invalid* test cases).

An encoder test only requires a *json* file. A decoder test requires both 
a *json* file and a *udif* file.
