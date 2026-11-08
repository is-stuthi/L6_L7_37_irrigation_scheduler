import math

from hypothesis import given, settings, strategies as st
from irrigation_scheduler import parse_zone, moisture_average, water_needed

# Arbitrary junk: text, None, and other non-string types.
anything = st.one_of(
    st.text(), st.none(), st.integers(), st.floats(), st.binary(),
    st.lists(st.integers()),
)


# ---------------------------------------------------------------------------
# Part 1: "must not crash" fuzz tests (completed starter tests)
# ---------------------------------------------------------------------------
@settings(max_examples=500)
@given(st.text() | st.none())
def test_parse_zone_no_crash(s):
    try:
        parse_zone(s)
    except Exception as e:
        assert False, f"parse_zone crashed with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_moisture_average_no_crash(s):
    try:
        moisture_average(s)
    except Exception as e:
        assert False, f"moisture_average crashed with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_water_needed_no_crash(s):
    try:
        water_needed(s)
    except Exception as e:
        assert False, f"water_needed crashed with: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Part 2: structure-aware fuzzing (inputs shaped like the real format, so the
# fuzzer gets past the first split and reaches the numeric logic)
# ---------------------------------------------------------------------------
numberish = st.one_of(
    st.floats(allow_nan=True, allow_infinity=True).map(repr),
    st.integers().map(str),
    st.text(max_size=12),
    st.sampled_from(["nan", "inf", "-inf", "1e999", "-0", "1_0", " 5 ", ""]),
)


@settings(max_examples=500)
@given(st.text(max_size=20), numberish)
def test_parse_zone_structured_no_crash(name, area):
    try:
        parse_zone(f"{name}:{area}")
    except Exception as e:
        assert False, f"parse_zone crashed with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.lists(numberish, max_size=10))
def test_moisture_average_structured_no_crash(items):
    try:
        moisture_average(",".join(items))
    except Exception as e:
        assert False, f"moisture_average crashed with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(numberish, numberish)
def test_water_needed_structured_no_crash(a, b):
    try:
        water_needed(f"{a}|{b}")
    except Exception as e:
        assert False, f"water_needed crashed with: {type(e).__name__}: {e}"


@settings(max_examples=300)
@given(anything)
def test_all_functions_non_string_no_crash(x):
    for fn in (parse_zone, moisture_average, water_needed):
        try:
            fn(x)
        except Exception as e:
            assert False, f"{fn.__name__} crashed with: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Part 3: correctness properties (outputs must be sane, not merely non-crashing)
# ---------------------------------------------------------------------------
@settings(max_examples=300)
@given(st.text(alphabet=st.characters(whitelist_categories=("L",),
                                      max_codepoint=127),
               min_size=1, max_size=20),
       st.floats(min_value=0.01, max_value=1e6, allow_nan=False))
def test_parse_zone_valid_roundtrip(name, area):
    res = parse_zone(f"{name}:{area:.2f}")
    assert res is not None
    assert res[0] == name.strip().title()
    assert math.isfinite(res[1]) and res[1] > 0


@settings(max_examples=300)
@given(st.text(max_size=30))
def test_parse_zone_output_invariants(s):
    res = parse_zone(s)
    if res is not None:
        name, area = res
        assert name and name == name.strip()
        assert math.isfinite(area) and area > 0


@settings(max_examples=300)
@given(st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=50))
def test_moisture_average_within_bounds(vals):
    res = moisture_average(",".join(map(str, vals)))
    assert res is not None
    assert min(vals) <= res <= max(vals)


@settings(max_examples=200)
@given(st.lists(st.integers(), min_size=1, max_size=10).filter(
    lambda v: any(x < 0 or x > 100 for x in v)))
def test_moisture_average_rejects_out_of_range(vals):
    assert moisture_average(",".join(map(str, vals))) is None


@settings(max_examples=200)
@given(st.integers(min_value=0, max_value=1000), st.text(max_size=5))
def test_moisture_average_rejects_malformed_element(v, junk):
    # Any non-digit junk element (empty, letters, signs, spaces-only...)
    # inside an otherwise valid list must be rejected.
    if junk.strip().isascii() and junk.strip().isdigit():
        return
    assert moisture_average(f"{v % 101},{junk},{v % 101}") is None


@settings(max_examples=300)
@given(st.floats(min_value=0, max_value=1e6, allow_nan=False),
       st.floats(min_value=0, max_value=1e6, allow_nan=False))
def test_water_needed_non_negative_and_finite(area, rain):
    res = water_needed(f"{area:.3f}|{rain:.3f}")
    assert res is not None
    assert math.isfinite(res) and res >= 0


@settings(max_examples=300)
@given(st.text(max_size=30))
def test_water_needed_output_invariants(s):
    res = water_needed(s)
    if res is not None:
        assert math.isfinite(res) and res >= 0


# ---------------------------------------------------------------------------
# Part 4: regression tests for the specific bugs fuzzing exposed
# ---------------------------------------------------------------------------
def test_regression_known_bad_inputs():
    assert parse_zone(None) is None            # AttributeError originally
    assert parse_zone("north") is None         # ValueError (no ':')
    assert parse_zone("a:b:c") is None         # ValueError (too many ':')
    assert parse_zone("north:abc") is None     # ValueError (non-numeric)
    assert parse_zone("north:nan") is None     # NaN accepted originally
    assert parse_zone("north:inf") is None     # inf accepted originally
    assert parse_zone("north:-5") is None      # negative area accepted
    assert parse_zone(":50") is None           # empty name accepted
    assert moisture_average("") is None        # ValueError originally
    assert moisture_average(None) is None      # AttributeError originally
    assert moisture_average("1,,3") is None    # ValueError originally
    assert moisture_average("40,abc") is None  # ValueError originally
    assert moisture_average("-50,200") is None # out-of-range accepted
    assert water_needed(None) is None          # AttributeError originally
    assert water_needed("120") is None         # ValueError (no '|')
    assert water_needed("nan|5") is None       # returned NaN originally
    assert water_needed("inf|inf") is None     # returned NaN originally
    assert water_needed("1e308|0") is None     # overflow to inf originally


def test_regression_valid_inputs_unchanged():
    assert parse_zone(" north : 120 ") == ("North", 120.0)
    assert moisture_average("40,35,50") == 41
    assert water_needed("120|8") == 592.0
    assert water_needed("1|100") == 0.0
