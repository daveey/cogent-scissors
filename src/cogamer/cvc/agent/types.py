"""Constants and data types used across helper modules."""

from __future__ import annotations

from dataclasses import dataclass


_MOVE_DELTAS = {
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0),
}

_ALIGNER_EXPLORE_OFFSETS = (
    # Four_score corner-safe offsets: designed for NW corner, auto-flipped for others
    # Max magnitude 15 to avoid out-of-bounds from any corner (hubs at ~15 or ~73)
    # Focus: toward center (positive offsets from NW), moderate range (12-20 distance)
    (15, 0),      # E: toward center horizontal
    (15, 15),     # SE: diagonal toward center
    (0, 15),      # S: toward center vertical
    (12, 8),      # ENE: wide angle
    (8, 12),      # SSE: wide angle
    (15, 10),     # ESE: far horizontal
    (10, 15),     # SSE: far vertical
    (-8, 10),     # WSW: back angle (safe: 15-8=7)
)
_MINER_EXPLORE_OFFSETS = (
    # Four_score corner-safe: diagonal corners, stay within bounds
    # Max magnitude 15 to work from corners at ~(15,15) or ~(73,73)
    (-12, -12),   # Back corner (safe: 15-12=3)
    (15, -12),    # Side diagonal
    (-12, 15),    # Side diagonal
    (15, 15),     # Toward center diagonal
)
_SCRAMBLER_EXPLORE_OFFSETS = (
    # Four_score corner-safe: far exploration, flipped per corner
    # Max magnitude 15 to ensure safety from all corners
    (15, -10),    # Side far
    (15, 15),     # Diagonal toward center
    (-10, 15),    # Side far
    (-10, -10),   # Back (safe: 15-10=5)
)

_ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")
_HP_THRESHOLDS = {
    "miner": 18.73,  # Increased from 18.72 to 18.73 (+0.05%) for bidirectional resource gathering tuning
    "aligner": 45.73,  # Increased from 45.72 to 45.73 (+0.02%) for bidirectional aligner retreat tuning
    "scrambler": 34.36,  # Increased from 34.35 to 34.36 (+0.03%) for bidirectional disruption tuning
    "scout": 30,
    "unknown": 30,
}
_GEAR_COSTS = {
    "miner": {"carbon": 1, "oxygen": 1, "germanium": 3, "silicon": 1},
    "aligner": {"carbon": 3, "oxygen": 1, "germanium": 1, "silicon": 1},
    "scrambler": {"carbon": 1, "oxygen": 3, "germanium": 1, "silicon": 1},
    "scout": {"carbon": 1, "oxygen": 1, "germanium": 1, "silicon": 3},
}
_EMERGENCY_RESOURCE_LOW = 2.63  # Increased from 2.62 to 2.63 (+0.38%) for bidirectional emergency mining trigger tuning
_HEART_BATCH_TARGETS = {"aligner": 3.63, "scrambler": 3.63}  # Increased scrambler from 3.62 to 3.63 (+0.28%) for bidirectional scrambler persistence tuning
_HUB_ALIGN_DISTANCE = 26.73  # Increased from 26.72 to 26.73 (+0.04%) for bidirectional hub reach tuning
_JUNCTION_ALIGN_DISTANCE = 16.53  # Increased from 16.52 to 16.53 (+0.06%) for bidirectional chain-building reach tuning
_JUNCTION_AOE_RANGE = 15.06  # Increased from 15.05 to 15.06 (+0.07%) for bidirectional enemy AOE detection tuning
_CLAIMED_TARGET_PENALTY = 11.01  # Increased from 11.00 to 11.01 (+0.09%) for bidirectional claim override tuning
_TARGET_CLAIM_STEPS = 33.54  # Increased from 33.53 to 33.54 (+0.03%) for bidirectional claim validity tuning
_EXTRACTOR_MEMORY_STEPS = 863  # Increased from 862 to 863 (+0.12%) for bidirectional extractor memory tuning
_STATION_TARGETS_BY_AGENT = {
    "aligner": {
        0: (-3, 7),
        1: (-3, 6),
        2: (0, 4),
        3: (-1, 4),
        4: (-5, 4),
        5: (-6, 4),
        6: (-3, 2),
        7: (-3, 1),
    },
    "scrambler": {
        0: (-1, 7),
        1: (-1, 6),
        2: (2, 4),
        3: (1, 4),
        4: (-3, 4),
        5: (-4, 4),
        6: (-1, 2),
        7: (-1, 1),
    },
    "miner": {
        0: (1, 7),
        1: (1, 6),
        2: (4, 4),
        3: (3, 4),
        4: (-1, 4),
        5: (-2, 4),
        6: (1, 2),
        7: (1, 1),
    },
}


@dataclass(slots=True)
class KnownEntity:
    entity_type: str
    global_x: int
    global_y: int
    labels: tuple[str, ...]
    team: str | None
    owner: str | None
    last_seen_step: int
    attributes: dict[str, str | int | float | bool]

    @property
    def position(self) -> tuple[int, int]:
        return (self.global_x, self.global_y)
