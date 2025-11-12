from pathlib import Path

import pyshellman

from pyorca import settings
from pyorca.output import JobOutput


def run(
    input_path: str | Path,
    output_base_name: str | Path | None = None,
    args: str | None = None,
    orca_exe: str | Path | None = None,
    *,
    stream_stdout: bool = False,
    stream_stderr: bool = False,
    timeout: float | None = None,
) -> JobOutput:
    """Execute ORCA on a given input file and write stdout to output file.

    Parameters
    ----------
    input_path
        Path to the ORCA job input file.
    outpath_path
        Path to write the .out file.

    Raises
    ------
    FileNotFoundError
        If ORCA executable cannot be launched.
    RuntimeError
        If ORCA exits with non-zero code.
    """
    command = [orca_exe or settings.orca_exe, str(input_path)]
    if args:
        command.append(args)
    output = pyshellman.run(
        command,
        stream_stdout=stream_stdout,
        stream_stderr=stream_stderr,
        raise_execution=True,
        raise_timeout=True,
        raise_exit_code=True,
        raise_stderr=False,
        timeout=timeout,
    )
    output_base_name = output_base_name or Path(input_path).with_suffix("")
    output_base_name.with_suffix(".out").write_text(output.out, encoding="utf-8")
    if output.err:
        output_base_name.with_suffix(".err").write_text(output.err, encoding="utf-8")
    return JobOutput(output_base_name)
