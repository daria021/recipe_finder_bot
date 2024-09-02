from typing import Any


def chunk(buttons: list[Any], chunk_size: int = 2):
    layout = []
    while len(buttons) > 0:
        layout.append(buttons[:chunk_size])
        buttons = buttons[chunk_size:]
    return layout
