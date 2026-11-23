"""Helpers for the Elden Ring tests."""

from unittest.mock import create_autospec

from soulsgym.core.game_memory import GameMemory
from soulsgym.games.eldenring import EldenRing
from soulsgym.games.game import StaticGameData


def simulated_game(**values: int | float | bytes) -> EldenRing:
    """Create a game interface for a simulated game without a game process.

    The memory follows the ``GameMemory`` API, so calls that do not match it raise a ``TypeError``.
    All records hold small values unless ``values`` overrides them by record name.

    Args:
        values: The values of the records that should not hold a small default value.

    Returns:
        The game interface.
    """
    game = object.__new__(EldenRing)  # Skips attaching to the game process
    game.data = StaticGameData(EldenRing.game_id)
    names = {id(record): name for name, record in game.data.addresses.items()}
    values = {"LastGrace": next(iter(game.data.bonfires.values())), **values}

    def read_record(record: dict) -> int | float | bytes:
        name = names[id(record)]
        if name in values:
            return values[name]
        return {"int": 1, "float": 0.5, "bytes": bytes(record.get("length", 0))}[record["type"]]

    game.mem = create_autospec(GameMemory, instance=True)
    game.mem.read_record.side_effect = read_record
    game.mem.resolve_record.return_value = 0x1000
    game.mem.read_int.return_value = 1
    return game
