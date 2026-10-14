"""Input helpers for the CLI (Engineer B)."""

from validation import ValidationError, validate_affected_users


def parse_affected_users(text):
    """Turn typed text into an int. Only plain digits are accepted here; the
    strict type check then happens in validate_affected_users."""
    text = str(text).strip()
    if not text.isdigit():
        raise ValidationError("Affected users must be a positive whole number.")
    return validate_affected_users(int(text))


def optional(parser):
    """Wrap a parser so a blank answer means 'no value' (None)."""
    def wrapper(text):
        return None if str(text).strip() == "" else parser(text)
    return wrapper


def ask_valid(input_fn, output_fn, prompt, parser):
    """Keep asking until `parser` accepts the answer."""
    while True:
        try:
            return parser(input_fn(prompt))
        except ValidationError as err:
            output_fn(f"Error: {err}")
