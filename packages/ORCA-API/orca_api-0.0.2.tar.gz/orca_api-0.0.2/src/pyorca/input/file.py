from typing import Sequence
from pathlib import Path

import pyorca
from pyorca.output import JobOutput
from pyorca.input.block.coords._base import CoordinatesInputBlock
from pyorca.input.block._base import InputBlock


class InputFile:
    def __init__(
        self,
        coordinates: CoordinatesInputBlock | None = None,
        keywords: Sequence[str] | None = None,
        blocks: dict[str, str | dict[str, str]] | None = None,
        *,
        indent: int = 3,
    ):
        self.keywords = keywords or []
        self.blocks = blocks or {}
        self.coordinates = coordinates
        self.indent = indent
        return

    def run(
        self,
        output_base_name: str | Path | None = None,
        args: str | None = None,
        orca_exe: str | Path | None = None,
        *,
        stream_stdout: bool = True,
        stream_stderr: bool = True,
        timeout: float | None = None,
    ) -> JobOutput:
        output_base_name = Path(output_base_name) or Path.cwd() / "orca_job"
        output_base_name.parent.mkdir(parents=True, exist_ok=True)
        input_path = output_base_name.with_suffix(".inp")
        input_path.write_text(str(self), encoding="utf-8")
        return pyorca.run(
            input_path=input_path,
            output_base_name=output_base_name,
            args=args,
            orca_exe=orca_exe,
            stream_stdout=stream_stdout,
            stream_stderr=stream_stderr,
            timeout=timeout,
        )

    def __str__(self) -> str:
        if not self.keywords and not self.blocks:
            raise ValueError("Input file must have at least one keyword or block.")
        lines = []
        if self.keywords:
            lines.append(f"! {' '.join(self.keywords)}")
        for block_name, block in self.blocks.items():
            if not isinstance(block, InputBlock):
                block = InputBlock(block_name, block)
            lines.append(str(block))
        if self.coordinates:
            lines.append(str(self.coordinates))
        return f"{'\n\n'.join(lines).strip()}\n"


def new(
    keywords: Sequence[str] | None = None,
    blocks: dict[str, str | dict[str, str]] | None = None,
    coordinates: CoordinatesInputBlock | None = None,
    *,
    indent: int = 3,
) -> InputFile:
    return InputFile(
        keywords=keywords,
        blocks=blocks,
        coordinates=coordinates,
        indent=indent,
)