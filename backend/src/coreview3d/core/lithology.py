from typing import Dict, Any

LITHOLOGY_COLORS: Dict[str, str] = {
    "GRANITE": "#FF6B6B",
    "DIORITE": "#EE5A6F",
    "GABBRO": "#4A5568",
    "BASALT": "#2D3748",
    "ANDESITE": "#718096",
    "RHYOLITE": "#FCA5A5",
    
    "SANDSTONE": "#F6E05E",
    "SHALE": "#A0AEC0",
    "LIMESTONE": "#E2E8F0",
    "MUDSTONE": "#805AD5",
    "CONGLOMERATE": "#D69E2E",
    
    "SCHIST": "#48BB78",
    "GNEISS": "#38A169",
    "QUARTZITE": "#F7FAFC",
    "SLATE": "#2C5282",
    "MARBLE": "#E2E8F0",
    
    "ORE": "#F59E0B",
    "QUARTZ_VEIN": "#FFFFFF",
    "SULFIDES": "#FCD34D",
    "OXIDE": "#DC2626",
    "MASSIVE_SULFIDE": "#B91C1C",
    
    "ALTERED": "#EC4899",
    "WEATHERED": "#BE185D",
    "FRESH": "#047857",
    
    "UNKNOWN": "#94A3B8",
    "NO_RECOVERY": "#1E293B"
}


def get_lithology_color(lithology: str) -> str:
    lithology_upper = lithology.upper().strip()
    return LITHOLOGY_COLORS.get(lithology_upper, LITHOLOGY_COLORS["UNKNOWN"])


def get_all_lithologies() -> Dict[str, str]:
    return LITHOLOGY_COLORS.copy()


def lithology_to_rgb(lithology: str) -> tuple[int, int, int]:
    hex_color = get_lithology_color(lithology).lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_lithology_colors_api() -> Dict[str, Any]:
    return {
        "success": True,
        "lithologies": [
            {
                "name": name,
                "color": color,
                "rgb": lithology_to_rgb(name)
            }
            for name, color in LITHOLOGY_COLORS.items()
        ]
    }