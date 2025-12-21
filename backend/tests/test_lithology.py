from coreview3d.core.lithology import (
    get_lithology_color,
    get_all_lithologies,
    lithology_to_rgb
)


def test_get_lithology_color_valid():
    color = get_lithology_color("GRANITE")
    assert color.startswith('#')
    assert len(color) == 7


def test_get_lithology_color_case_insensitive():
    assert get_lithology_color("granite") == get_lithology_color("GRANITE")
    assert get_lithology_color("GrAnItE") == get_lithology_color("GRANITE")


def test_get_lithology_color_unknown():
    color = get_lithology_color("NONEXISTENT_ROCK")
    unknown_color = get_lithology_color("UNKNOWN")
    assert color == unknown_color


def test_get_all_lithologies():
    lithologies = get_all_lithologies()
    
    assert isinstance(lithologies, dict)
    assert len(lithologies) > 0
    assert "GRANITE" in lithologies
    assert "UNKNOWN" in lithologies


def test_lithology_to_rgb():
    rgb = lithology_to_rgb("GRANITE")
    
    assert isinstance(rgb, tuple)
    assert len(rgb) == 3
    assert all(0 <= c <= 255 for c in rgb)


def test_lithology_to_rgb_white():
    rgb = lithology_to_rgb("QUARTZ_VEIN")
    assert rgb == (255, 255, 255)
