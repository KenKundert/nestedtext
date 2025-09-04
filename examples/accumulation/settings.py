from inform import Error, full_stop, os_error
import nestedtext as nt

schema = dict(
    name = str,
    limit = float,
    actions = dict,
    patterns = list,
)
list_settings = set(k for k, v in schema.items() if v == list)
dict_settings = set(k for k, v in schema.items() if v == dict)

def de_dup(key, state):
    if key not in state:
        state[key] = 1
    state[key] += 1
    return f"{key}#{state[key]}"

def normalize_key(key, parent_keys):
    return '_'.join(key.lower().split())  # convert key to snake case

def read_settings(path, processed=None):
    if processed is None:
        processed = {}

    try:
        keymap = {}
        settings = nt.load(
            path,
            top = dict,
            normalize_key = normalize_key,
            on_dup = de_dup,
            keymap = keymap
        )
    except OSError as e:
        raise Error(os_error(e))

    def report_error(msg):
        keys = key_as_given,
        offset = key_as_given.index(key)
        raise Error(
            full_stop(msg),
            culprit = path,
            codicil = nt.get_location(keys, keymap=keymap).as_line('key', offset=offset)
        )

    # process settings
    for key_as_given, value in settings.items():

        # remove any decorations on the key
        key = key_as_given

        accumulate = '+' in key_as_given
        if accumulate:
            cruft, _, key = key_as_given.partition('+')
            if cruft:
                report_error("‘+’ must precede setting name")

        if '#' in key:  # get original name for duplicate key
            key, _, _ = key.partition('#')

        key = key.strip('_')
        if not key.isidentifier():
            report_error("expected identifier")

        # check the type of the value
        if key in list_settings:
            if isinstance(value, str):
                value = value.split()
            if not isinstance(value, list):
                report_error(f"expected list, found {value.__class__.__name__}")
            if accumulate:
                base = processed.get(key, [])
                value = base + value
        elif key in dict_settings:
            if value == "":
                value = {}
            if not isinstance(value, dict):
                report_error(f"expected dict, found {value.__class__.__name__}")
            if accumulate:
                base = processed.get(key, {})
                base.update(value)
                value = base
        elif key in schema:
            if accumulate:
                report_error("setting is unsuitable for accumulation")
            value = schema[key](value)  # cast to desired type
        else:
            report_error("unknown setting")
        processed[key] = value

    return processed
