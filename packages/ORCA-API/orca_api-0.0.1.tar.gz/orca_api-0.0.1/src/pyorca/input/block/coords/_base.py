from typing import Literal, Sequence
from pathlib import Path

from pyorca.input.block._base import InputBlock


class CoordinatesInputBlock(InputBlock):
    def __init__(
        self,
        coordinates: Path | str | Sequence[Sequence],
        charge: int,
        mult: int,
        unit: Literal["angs", "bohrs"] = "angs",
        type: Literal["xyz", "internal", "gzmt", "xyzfile", "gzmtfile"] | None = None,
    ):
        self.coords = coordinates
        self.type = type
        self.charge = charge
        self.mult = mult
        self.unit = unit
        super().__init__("coords", {})
        return

    def __str__(self) -> str:
        if self.type in {"xyzfile", "gzmtfile"}:
            return f'* {self.type} {self.charge} {self.mult} "{self.coords}"'
        self.settings = {
            "CTyp": self.type,
            "Charge": self.charge,
            "Mult": self.mult,
            "Units": self.unit,
            "Coords": self._coords_to_list(),
        }
        return super().__str__()

    def _coords_to_list(self) -> list[str]:
        lines = []
        for atom in self.coords:
            lines.append(" ".join(str(x) for x in atom))
        return lines
