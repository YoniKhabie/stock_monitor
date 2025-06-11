from dataclasses import dataclass

@dataclass
class Gap:
    index: int
    price_level: float
    gap_from: float
    gap_to: float
    gap_type: str
    volume: float
    ref_price: float
    filled: bool = False


@dataclass
class KeyLevel:
    price: float
    start_index: int
    gap_count: int


@dataclass
class Island:
    high: float
    low: float
    start_index: int
    end_index: int