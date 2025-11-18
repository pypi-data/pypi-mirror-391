"""Main output processing user interface.

This module provides the `JobOutput` class,
which serves as the primary interface
for accessing and processing
the output data from ORCA calculations.
"""

from pathlib import Path
import json

import pyshellman

from pyorca.output.gbw import GBWOutput
from pyorca.output.prop import PropertyOutput


class JobOutput:
    """Main interface for accessing and processing ORCA job output data.

    This class provides lazy loading and processing
    of ORCA output files, including GBW and property files.

    Parameters
    ----------
    output_base_name
        Base name of the ORCA output files for the job.
        This is the path to the directory containing the output files,
        plus the common prefix of the files (without extensions).
        All output file paths are expected to follow the standard ORCA naming conventions.
        For example, if the `base_name` is "~/orca_jobs/job1", then
        the GBW file is expected at "~/orca_jobs/job1.gbw",
        the property file is expected at "~/orca_jobs/job1.property.txt", etc.
    """

    def __init__(self, output_base_name: str | Path) -> None:
        self._output_base_name = Path(output_base_name).resolve()

        self._property = None
        self._gbw = None
        return

    @property
    def gbw(self) -> GBWOutput:
        """GBW file output data."""
        if self._gbw is not None:
            return self._gbw
        path = self._output_base_name.with_suffix(".json")
        if not path.exists():
            pyshellman.run(
                ["orca_2json", str(self._output_base_name.with_suffix(".gbw"))]
            )
        self._gbw = GBWOutput(json.loads(path.read_text(encoding="utf-8")))
        return self._gbw

    @property
    def prop(self) -> PropertyOutput:
        """Property file output data."""
        if self._property is not None:
            return self._property
        path = self._output_base_name.with_suffix(".property.json")
        if not path.exists():
            pyshellman.run(
                ["orca_2json", str(self._output_base_name), "-property"]
            )
        self._property = PropertyOutput(json.loads(path.read_text(encoding="utf-8")))
        return self._property
