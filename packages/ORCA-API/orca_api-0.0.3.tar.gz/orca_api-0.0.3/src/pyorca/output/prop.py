
import numpy as np
import pandas as pd


class PropertyOutput:
    def __init__(self, data: dict):
        self._data = data

        self._geometries = None
        self._coordinates = None
        return

    @property
    def data(self) -> dict:
        """Raw property data as a dictionary."""
        return self._data

    @property
    def geometries(self) -> list[dict]:
        """List of geometries in the property output."""
        if self._geometries is not None:
            return self._geometries
        # ORCA 6.1 lists geometries as a list under `$.Geometries`
        # - https://www.faccts.de/docs/orca/6.1/manual/contents/utilitiesvisualization/property_file.html
        if "Geometries" in self.data:
            self._geometries = self.data["Geometries"]
            return self._geometries
        # ORCA 6.0 lists geometries as separate keys starting with `Geometry_`.
        # The number of geometries is stored in `$.Calculation_Status.GeometryIndex`;
        # Keys are named `Geometry_1`, `Geometry_2`, ..., up to the value of `GeometryIndex`.
        geometry_index = self.data["Calculation_Status"]["GeometryIndex"]
        self._geometries = [
            self.data[f"Geometry_{i}"]
            for i in range(1, geometry_index + 1)
        ]
        return self._geometries

    @property
    def n_geometries(self) -> int:
        """Number of geometries in the property output."""
        return len(self.geometries)

    @property
    def energies_scf(self) -> np.ndarray:
        """SCF energies (in Hartree) of all geometries."""
        return np.array([
            geom["SCF_Energy"]["SCF_ENERGY"]
            for geom in self.geometries
        ])

    @property
    def energy_scf(self) -> float:
        """SCF energy (in Hartree) of the final geometry."""
        return self.energies_scf[-1]

    @property
    def coordinates_type(self) -> str:
        """Type of coordinates used in the geometries (e.g., 'Cartesians' or 'Internal')."""
        return self.geometries[0]["Coordinates"]["Type"]

    @property
    def coordinates_unit(self) -> str:
        """Unit of the coordinates used in the geometries (e.g., 'Angstrom' or 'Bohr')."""
        return self.geometries[0]["Coordinates"]["Unit"]

    @property
    def coordinates(self) -> pd.DataFrame:
        """Coordinates of each atom in each geometry."""
        if self._coordinates is not None:
            return self._coordinates
        rows = []
        for geom in self.geometries:
            geom_block = geom["Geometry"]
            for atom_idx, (element_symbol, x, y, z) in enumerate(geom_block["Coordinates"]["Cartesians"]):
                row = {
                    "geometry_idx": geom_block["GeometryIndex"],
                    "atom_idx": atom_idx,
                    "element": element_symbol["Symbol"],
                    "x": x,
                    "y": y,
                    "z": z,
                }
                rows.append(row)
        self._coordinates = pd.DataFrame(rows)
        return self._coordinates

    @property
    def thermochemistry(self) -> dict:
        """Thermochemistry data of the final geometry.

        This is typically available for frequency calculations,
        and includes quantities like Zero-Point Energy, Enthalpy, Entropy, etc.
        """
        return self.geometries[-1].get("THERMOCHEMISTRY_Energies", {})

    @property
    def vibrational_frequencies(self) -> np.ndarray:
        """Vibrational frequencies (in cm^-1) of the final geometry."""
        freq_data = self.thermochemistry.get("FREQ", [])
        return np.array([freq[0] for freq in freq_data])
