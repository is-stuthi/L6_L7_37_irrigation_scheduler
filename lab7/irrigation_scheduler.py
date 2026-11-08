"""Irrigation scheduler -- hardened version (Lab 7).

All three public functions are *total*: for ANY input (including None,
non-strings, malformed text, NaN/inf, huge numbers) they return a value
and never raise. Invalid input is signalled by returning ``None``.
"""
import math
import re

MAX_NAME_LEN = 100        # max characters in a zone name
MAX_TOKEN_LEN = 32        # max characters in one numeric token
MAX_READINGS = 10_000     # max moisture readings per CSV line (DoS guard)
MOISTURE_MIN, MOISTURE_MAX = 0, 100   # soil moisture is a percentage

# ASCII-only plain decimals: "12", "12.5", "12.", ".5". No sign, exponent,
# underscores, "nan"/"inf" or non-ASCII digits (all accepted by float()).
_DECIMAL = re.compile(r"\d+(?:\.\d*)?|\.\d+", re.ASCII)
_INTEGER = re.compile(r"\d+", re.ASCII)


def _to_float(token):
    """Strictly parse a non-negative, finite decimal; None if invalid."""
    token = token.strip()
    if not token or len(token) > MAX_TOKEN_LEN or not _DECIMAL.fullmatch(token):
        return None
    value = float(token)
    return value if math.isfinite(value) else None


def parse_zone(text):
    """Parse 'name:area' -> (Title-Cased name, area_m2) or None if invalid.

    Rules: str input, exactly one ':', non-empty printable name
    (<= MAX_NAME_LEN), area a finite number > 0.
    """
    if not isinstance(text, str):
        return None
    parts = text.split(":")
    if len(parts) != 2:
        return None
    name = parts[0].strip()
    if not name or len(name) > MAX_NAME_LEN or not name.isprintable():
        return None
    area = _to_float(parts[1])
    if area is None or area <= 0:
        return None
    return name.title(), area


def moisture_average(readings_csv):
    """Integer (floored) mean of comma-separated moisture readings, or None.

    Rules: str input, 1..MAX_READINGS readings, each an unsigned ASCII
    integer in [0, 100]. Empty/blank elements (e.g. '1,,3', trailing comma)
    are invalid.
    """
    if not isinstance(readings_csv, str):
        return None
    tokens = readings_csv.split(",")
    if not 1 <= len(tokens) <= MAX_READINGS:
        return None
    values = []
    for tok in tokens:
        tok = tok.strip()
        if not tok or len(tok) > 3 or not _INTEGER.fullmatch(tok):
            return None
        v = int(tok)
        if not MOISTURE_MIN <= v <= MOISTURE_MAX:
            return None
        values.append(v)
    return sum(values) // len(values)


def water_needed(text):
    """Parse 'area|rainfall' -> water needed (>= 0, finite float) or None.

    need = area * 5 - rainfall, floored at 0. Rules: str input, exactly one
    '|', area and rainfall finite numbers >= 0, finite result.
    """
    if not isinstance(text, str):
        return None
    parts = text.split("|")
    if len(parts) != 2:
        return None
    plot = _to_float(parts[0])
    rain = _to_float(parts[1])
    if plot is None or rain is None:
        return None
    need = plot * 5 - rain
    if not math.isfinite(need):
        return None
    return max(need, 0.0)


def main():
    try:
        print("==== Running parse_zone ====")
        user_input = input("Enter zone:area in m2 (e.g. north:120): ")
        result = parse_zone(user_input)
        print("Zone and Area:", result if result is not None
              else "Invalid input (expected name:area, area > 0)")

        print("\n==== Running moisture_average ====")
        user_input = input("Enter moisture readings as CSV (e.g. 40,35,50): ")
        result = moisture_average(user_input)
        print("Average Moisture:", result if result is not None
              else "Invalid input (expected integers 0-100, comma-separated)")

        print("\n==== Running water_needed ====")
        user_input = input("Enter area|rainfall (e.g. 120|8): ")
        result = water_needed(user_input)
        print("Water Needed:", result if result is not None
              else "Invalid input (expected area|rainfall, both >= 0)")
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")


if __name__ == "__main__":
    main()
