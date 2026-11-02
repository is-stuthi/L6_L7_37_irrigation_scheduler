import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


def test_wet_soil_no_irrigation():
    assert should_irrigate(70, 0, "seedling") is False

def test_seedling_volume():
    assert water_volume(10, "seedling", 20) == 20

def test_heavy_rain_no_irrigation():
    assert should_irrigate(30, 12, "seedling") is False

def test_seedling_dry_irrigates():
    assert should_irrigate(40, 0, "seedling") is True

def test_seedling_moderate_moisture_no_irrigation():
    assert should_irrigate(50, 0, "seedling") is False

def test_flowering_dry_irrigates():
    assert should_irrigate(50, 0, "flowering") is True

def test_light_rain_other_stage_no_irrigation():
    assert should_irrigate(30, 6, "vegetative") is False

def test_other_stage_dry_irrigates():
    assert should_irrigate(30, 0, "vegetative") is True

def test_invalid_area_raises():
    with pytest.raises(ValueError):
        water_volume(0, "seedling", 20)

def test_flowering_volume():
    assert water_volume(2, "flowering", 20) == 10

def test_other_stage_volume():
    assert water_volume(2, "vegetative", 20) == 8

def test_hot_temperature_volume():
    assert water_volume(10, "seedling", 40) == 30

def test_schedule_skips_wet_and_budgeted():
    zones = [("A", 10, 30, 0, "seedling", 20), ("B", 5, 70, 0, "seedling", 20)]
    assert schedule(zones, 100) == ["A"]
