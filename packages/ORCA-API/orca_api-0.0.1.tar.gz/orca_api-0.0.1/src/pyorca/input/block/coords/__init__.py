from typing import Literal
from pathlib import Path

from pyorca.input.block.coords._base import CoordinatesInputBlock


def from_file(
    path: str | Path,
    charge: int,
    mult: int,
    *,
    file_type: Literal["xyz", "gzmt"] | None = None,
) -> CoordinatesInputBlock:
    path = Path(path)
    if file_type is None:
        suffix = path.suffix.lower()
        if suffix == ".xyz":
            file_type = "xyz"
        elif suffix == ".gzmt":
            file_type = "gzmt"
        else:
            raise ValueError(
                f"Could not infer file type from suffix '{suffix}'. "
                "Please specify 'file_type' explicitly."
            )
    return CoordinatesInputBlock(
        coordinates=path,
        charge=charge,
        mult=mult,
        type=f"{file_type}file",
    )


