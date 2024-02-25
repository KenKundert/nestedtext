from inform import cull, error, full_stop
import nestedtext as nt

voluptuous_error_msg_mappings = {
    "extra keys not allowed": ("unknown key", "key"),
    "expected a dictionary": ("expected a key-value pair", "value"),
    "required key not provided": ("required key is missing", "value"),
}

def report_voluptuous_errors(multiple_invalid, keymap, source=None, sep="›"):
    for err in multiple_invalid.errors:

        # convert message to something easier for non-savvy user to understand
        msg, kind = voluptuous_error_msg_mappings.get(
            err.msg, (err.msg, 'value')
        )

        # get metadata about error
        culprit = nt.get_keys(err.path, keymap=keymap, strict="found", sep=sep)
        line_nums = nt.get_line_numbers(err.path, keymap, kind=kind, sep="-", strict=False)
        loc = nt.get_location(err.path, keymap)
        if loc:
            codicil = loc.as_line(kind)
        else:  # required key is missing
            missing = nt.get_keys(err.path, keymap, strict="missing", sep=sep)
            codicil = f"‘{missing}’ was not found."

        if not source:
            source = ""
        file_and_lineno = f"{source!s}@{line_nums}"
        culprit = cull((file_and_lineno, culprit))

        # report error
        error(full_stop(msg), culprit=culprit, codicil=codicil)
