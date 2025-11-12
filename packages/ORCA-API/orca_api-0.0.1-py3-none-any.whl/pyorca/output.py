from pathlib import Path
import json
from typing import Literal

import pandas as pd
import pyshellman


class JobOutput:
    """Class representing the output of a single ORCA job."""

    def __init__(self, output_base_name: str | Path) -> None:
        self._output_base_name = Path(output_base_name).resolve()

        self._property = None
        self._gbw = None
        return

    @property
    def scf_energy(self) -> float:
        """Return the SCF energy from the properties."""
        return self.properties["Geometry_1"]["SCF_Energy"]["SCF_ENERGY"]

    @property
    def mos(self):
        """Return the molecular orbitals from the gbw data."""
        mol = self.gbw["Molecule"]
        hf_type = mol["HFTyp"]
        mos = mol["MolecularOrbitals"]
        mo_labels = mos["OrbitalLabels"]
        mo_details = mos["MOs"]
        if len(mo_labels) != len(mo_details):
            raise ValueError("Number of labels does not match number of MOs.")
        if hf_type == "RHF":
            df = self._mo_df(mo_labels, mo_details)
        elif hf_type == "UHF":
            if len(mo_details) % 2 != 0:
                raise ValueError("Number of MOs is not even for UHF.")
            n_mos = len(mo_details) // 2
            mo_a = self._mo_df(mo_labels[:n_mos], mo_details[:n_mos], spin="a")
            mo_b = self._mo_df(mo_labels[n_mos:], mo_details[n_mos:], spin="b")
            df = pd.concat([mo_a, mo_b], ignore_index=True)
        else:
            raise NotImplementedError(f"HF type '{hf_type}' is not supported.")

        df["homo"] = False
        df["lumo"] = False
        occupied = df.loc[df["occupancy"] > 0]
        unoccupied = df.loc[df["occupancy"] == 0]
        if not occupied.empty:
            homo_idx = occupied["energy_hartree"].idxmax()
            df.loc[homo_idx, "homo"] = True
        if not unoccupied.empty:
            lumo_idx = unoccupied["energy_hartree"].idxmin()
            df.loc[lumo_idx, "lumo"] = True
        main_labels = ["label", "spin", "sym_label", "symmetry", "occupancy", "homo", "lumo", "energy_hartree", "energy_ev"]
        coeff_labels = sorted([col for col in df.columns if col.startswith("coeff_")])
        df = df[main_labels + coeff_labels]
        return df.sort_values(
            by=["energy_hartree", "label", "spin"],
            ascending=[True, True, True]
        ).reset_index(drop=True).convert_dtypes()

    @property
    def properties(self):
        if self._property is not None:
            return self._property
        path = self._output_base_name.with_suffix(".property.json")
        if not path.exists():
            pyshellman.run(
                ["orca_2json", str(self._output_base_name), "-property"]
            )
        self._property = json.loads(path.read_text(encoding="utf-8"))
        return self._property

    @property
    def gbw(self):
        if self._gbw is not None:
            return self._gbw
        path = self._output_base_name.with_suffix(".json")
        if not path.exists():
            pyshellman.run(
                ["orca_2json", str(self._output_base_name.with_suffix(".gbw"))]
            )
        self._gbw = json.loads(path.read_text(encoding="utf-8"))
        return self._gbw

    @staticmethod
    def _mo_df(labels: list[str], mos: list[dict], spin: Literal["a", "b", "a/b"] = "a/b") -> pd.DataFrame:
        """Convert molecular orbitals to a pandas DataFrame."""
        data = []
        for label, mo in zip(labels, mos):
            label_parts = label.split()
            label_prefix = label_parts[0] if len(label_parts) > 1 else ""
            label_suffix = " ".join(label_parts[1:]) if len(label_parts) > 1 else label_parts[0]
            row = {
                "label_prefix": label_prefix,
                "label": label_suffix,
                "spin": spin,
                "sym_label": mo["OrbitalSymLabel"],
                "symmetry": mo["OrbitalSymmetry"],
                "occupancy": mo["Occupancy"],
                "energy_hartree": mo["OrbitalEnergy"],
                "energy_ev": mo["OrbitalEnergy"] * 27.2114,
                **{f"coeff_{i+1}": coeff for i, coeff in enumerate(mo["MOCoefficients"])},
            }
            data.append(row)
        return pd.DataFrame(data)