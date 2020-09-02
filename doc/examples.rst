Examples
========

JSON to NestedText
------------------

This example implements a command-line utility that converts a *JSON* file to 
*NestedText*.  It demonstrates the use of :func:`nestedtext.dumps()` and 
:exc:`nestedtext.NestedTextError`.

.. code-block:: python

    #!/usr/bin/env python3
    """
    Read a JSON file and convert it to NestedText.

    usage:
        json-to-nestedtext [options] [<filename>]

    options:
        -f, --force   force overwrite of output file

    If <filename> is not given, json input is taken from stdin and NestedText 
    output is written to stdout.
    """

    from docopt import docopt
    from inform import fatal, os_error
    from pathlib import Path
    import json
    import nestedtext
    import sys

    cmdline = docopt(__doc__)
    input_filename = cmdline['<filename>']

    try:
        if input_filename:
            input_path = Path(input_filename)
            json_content = input_path.read_text()
        else:
            json_content = sys.stdin.read()
        data = json.loads(json_content)
        nestedtext_content = nestedtext.dumps(data)
        if input_filename:
            output_path = input_path.with_suffix('.nt')
            if output_path.exists():
                if not cmdline['--force']:
                    fatal('file exists, use -f to force over-write.', culprit=output_path)
            output_path.write_text(nestedtext_content)
        else:
            sys.stdout.write(nestedtext_content)
    except OSError as e:
        fatal(os_error(e))
    except nestedtext.NestedTextError as e:
        e.terminate()
    except json.JSONDecodeError as e:
        fatal(e)


NestedText to JSON
------------------

This example implements a command-line utility that converts a *NestedText* file 
to *JSON*.  It demonstrates the use of :func:`nestedtext.loads()` and 
:exc:`nestedtext.NestedTextError`.

.. code-block:: python

    #!/usr/bin/env python3
    """
    Read a NestedText file and convert it to JSON.

    usage:
        nestedtext-to-json [options] [<filename>]

    options:
        -f, --force   force overwrite of output file

    If <filename> is not given, NestedText input is taken from stdin and JSON output 
    is written to stdout.
    """

    from docopt import docopt
    from inform import fatal, os_error
    from pathlib import Path
    import json
    import nestedtext
    import sys

    cmdline = docopt(__doc__)
    input_filename = cmdline['<filename>']

    try:
        if input_filename:
            input_path = Path(input_filename)
            nestedtext_content = input_path.read_text()
        else:
            nestedtext_content = sys.stdin.read()
        data = nestedtext.loads(nestedtext_content, input_filename)
        json_content = json.dumps(data, indent=4)
        if input_filename:
            output_path = input_path.with_suffix('.json')
            if output_path.exists():
                if not cmdline['--force']:
                    fatal('file exists, use -f to force over-write.', culprit=output_path)
            output_path.write_text(json_content)
        else:
            sys.stdout.write(json_content)
    except OSError as e:
        fatal(os_error(e))
    except nestedtext.NestedTextError as e:
        e.terminate()


Cryptocurrency Holdings
------------------------

This example implements a command-line utility that displays the current value 
of cryptocurrency holdings.  The program starts by reading a settings file held 
in ~/.config/cc that in this case holds::

    holdings:
        - 5 BTC
        - 50 ETH
        - 50,000 XLM
    currency: USD
    date format: h:mm A, dddd MMMM D
    screen width: 90

This file, of course, is in *NextedText* format.  After being read by 
:func:`nestedtext.loads()` it is processed by a `Voluptuous 
<https://github.com/alecthomas/voluptuous>`_ schema that does some checking on 
the form of the values specified and then converts the holdings to a list of 
`QuantiPhy <https://quantiphy.readthedocs.io>`_ quantities and the screen width 
to an integer.  The latest prices are then downloaded from `cryptocompare 
<https://www.cryptocompare.com>`_, the value of the holdings are computed, and 
then displayed. The result looks like this::

    Holdings as of 11:18 AM, Wednesday September 2.
    5 BTC = $56.8k @ $11.4k/BTC    68.4% ████████████████████████████████████▏
    50 ETH = $21.7k @ $434/ETH     26.1% █████████████▊
    50 kXLM = $4.6k @ $92m/XLM     5.5%  ██▉
    Total value = $83.1k.

And finally, the code:

.. code-block:: python

    #!/usr/bin/env python3

    from appdirs import user_config_dir
    from  nestedtext import loads, dumps, NestedTextError
    from voluptuous import Schema, Required, All, Length, Invalid
    from inform import display, fatal, is_collection, os_error, render_bar
    import arrow
    import requests
    from quantiphy import Quantity
    from pathlib import Path

    # configure preferences
    Quantity.set_prefs(prec=2, ignore_sf = True)
    currency_symbols = dict(USD='$', EUR='€', JPY='¥', GBP='£')

    # utility functions
    def coerce(type):
        def f(value):
            try:
                if is_collection(value):
                    return [type(each) for each in value]
                return type(value)
            except ValueError:
                raise Invalid(f'expected {type.__name__}, found {v.__class__.__name__}')
        return f

    try:
        # read settings
        settings_file = Path(user_config_dir('cc'), 'settings')
        settings_schema = Schema({
            Required('holdings'): All(coerce(Quantity), Length(min=1)),
            'currency': str,
            'date format': str,
            'screen width': coerce(int)
        })
        settings = settings_schema(loads(settings_file.read_text(), settings_file))
        currency = settings.get('currency', 'USD')
        currency_symbol = currency_symbols.get(currency, currency)
        screen_width = settings.get('screen width', 80)

        # download latest asset prices from cryptocompare.com
        params = dict(
            fsyms = ','.join(coin.units for coin in settings['holdings']),
            tsyms = currency,
        )
        url = 'https://min-api.cryptocompare.com/data/pricemulti'
        try:
            r = requests.get(url, params=params)
            if r.status_code != requests.codes.ok:
                r.raise_for_status()
        except Exception as e:
            raise Error('cannot access cryptocurrency prices:', codicil=str(e))
        prices = {k: Quantity(v['USD'], currency_symbol) for k, v in r.json().items()}

        # compute total
        total = Quantity(0, currency_symbol)
        for coin in settings['holdings']:
            price = prices[coin.units]
            value = price.scale(coin)
            total = total.add(value)

        # display holdings
        now = arrow.now().format(settings.get('date format', 'h:mm A, dddd MMMM D, YYYY'))
        print(f'Holdings as of {now}.')
        bar_width = screen_width - 37
        for coin in settings['holdings']:
            price = prices[coin.units]
            value = price.scale(coin)
            portion = value/total
            summary = f'{coin} = {value} @ {price}/{coin.units}'
            print(f'{summary:<30} {portion:<5.1%} {render_bar(portion, bar_width)}')
        print(f'Total value = {total}.')

    except NestedTextError as e:
        e.terminate()
    except Invalid as e:
        fatal(e)
    except OSError as e:
        fatal(os_error(e))
    except KeyboardInterrupt:
        pass
