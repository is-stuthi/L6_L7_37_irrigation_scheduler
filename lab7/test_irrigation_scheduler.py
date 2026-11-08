from hypothesis import given, strategies as st
from irrigation_scheduler import parse_zone, moisture_average, water_needed

@given(st.text() | st.none())
def test_parse_zone_no_crash(s):

@given(st.text() | st.none())
def test_moisture_average_no_crash(s):

@given(st.text() | st.none())
def test_water_needed_no_crash(s):
