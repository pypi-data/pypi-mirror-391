"""Processing and representation of ORCA output data."""

from pathlib import Path
from .main import JobOutput

__all__ = ["JobOutput", "from_base_name"]


def from_base_name(base_name: str | Path) -> JobOutput:
    """Load a job output from its base name.

    Parameters
    ----------
    base_name
        Base name of the ORCA output files for the job.
        This is the path to the directory containing the output files,
        plus the common prefix of the files (without extensions).
        All output file paths are expected to follow the standard ORCA naming conventions.
        For example, if the `base_name` is "~/orca_jobs/job1", then
        the GBW file is expected at "~/orca_jobs/job1.gbw",
        the property file is expected at "~/orca_jobs/job1.property.txt", etc.

    Returns
    -------
    A JobOutput instance that lazy-loads and processes the output data as needed.
    """
    return JobOutput(base_name)
