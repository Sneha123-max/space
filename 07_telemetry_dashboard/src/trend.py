"""Pure function that turns numbers into a block-character trend line."""

BLOCKS = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    """Scale values to 8 block heights: lowest value -> ▁, highest -> █."""
    if not values:
        return ""
    low, high = min(values), max(values)
    if high == low:  # flat data: avoid dividing by zero, draw a middle-height line
        return BLOCKS[3] * len(values)
    steps = len(BLOCKS) - 1
    return "".join(BLOCKS[round((v - low) / (high - low) * steps)] for v in values)
