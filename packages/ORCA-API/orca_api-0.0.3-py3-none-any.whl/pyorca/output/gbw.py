"""GBW file output processing user interface.

This module provides the `GBWOutput` class,
which represents and processes the output of GBW files,
containing molecular orbital information from ORCA calculations.
"""

import re

import pandas as pd
import numpy as np

from pyorca.const import HARTREE_TO_EV_FACTOR, PERIODIC_TABLE


MO_COLUMN_DESCRIPTION = {
    "mo_idx": "MO index number",
    "spin": r"Spin type of the MO (\alpha or \beta for UHF, \alpha\beta otherwise)",
    "occupancy": "Number of electrons in the MO",
    "energy_eh": "Energy of the MO in Hartree",
    "energy_ev": "Energy of the MO in electronvolts",
    "sym_label": "Symmetry label of the MO",
    "sym_idx": "Symmetry index of the MO",
    "homo": "Whether the MO is the HOMO",
    "lumo": "Whether the MO is the LUMO",
    "norm_c2": r"Norm of coefficients $\lVert \mathbf{c} \rVert_2 = \sqrt{\sum_i c_i^2}$",
    "pr": r"Participation ratio $P = \frac{1}{\sum_i c_i^4}$ (effective number of AOs contributing)",
    "n_contrib": "Number of atoms whose AOs contribute more than 1% (by $c^2$)",
    "phase_prod": "Product of signed AO sums per atom ($>0$: bonding-like, $<0$: antibonding-like)",
    "max_abs": "Dominant AO (by $|c|$) and its coefficient",
    "frac": "s:p:d:f ratio of AOs (by $c^2$)",
    "lead_atom": "Leading atom (by $c^2$) and its fraction",
    "lead_element": "Leading element (by $c^2$) and its fraction",
    "lead_l": "Leading angular momentum character (by $c^2$) and its fraction",
}


class GBWOutput:
    """GBW file output data representation and processing interface.

    Parameters
    ----------
    data
        Raw data from the GBW file in JSON format as a dictionary.
    """

    def __init__(self, data: dict):
        self._data = data
        molecule = data["Molecule"]
        mo_block = molecule["MolecularOrbitals"]
        mos = mo_block["MOs"]
        ao_labels = mo_block["OrbitalLabels"]
        self._mos, self._mo_coeffs, self._aos = _parse_mos(mos=mos, ao_labels=ao_labels)
        self._atoms, self._ao_coeffs, self._ao_exponents = _parse_atoms(molecule["Atoms"])
        self._formula = _create_formula(self._atoms)
        return

    @property
    def data(self) -> dict:
        """Raw GBW data as a dictionary."""
        return self._data

    @property
    def mos(self) -> pd.DataFrame:
        """Molecular orbitals table.

        Each row corresponds to one MO, with columns:

        mo_idx : int
            Unique (zero-based) index number of the MO;
            used to link to coefficients in `mo_coeffs`.
        spin : {'a', 'b', 'ab'}
            Spin type of the MO:
            - 'a' : alpha spin (for UHF)
            - 'b' : beta spin (for UHF)
            - 'ab': both spins (for RHF)
        occupancy : float
            Number of electrons in the MO.
        energy_eh : float
            Energy of the MO in Hartree.
        energy_ev : float
            Energy of the MO in electronvolts.
        sym_label : str
            Symmetry label of the MO.
        sym_idx : str
            Symmetry index of the MO.
        homo : bool
            Whether the MO is the highest occupied molecular orbital (HOMO).
        lumo : bool
            Whether the MO is the lowest unoccupied molecular orbital (LUMO).

        In addition, the following coefficient-analysis-derived columns are included:

        norm_c2 : float
            Sum of c^2;
            should be ~1.0 in an orthonormal AO basis.
        pr : float
            1 / sum(c^4);
            effective number of AOs contributing, i.e.,
            PR ≈ 1 for strongly localized MOs, and
            PR ≈ N_AO for strongly delocalized MOs.
        n_contrib : int
            Number of atoms contributing ≥1% (by c^2).
        phase_prod : float or NaN
            Product of signed AO-sums per atom (heuristic; no overlap used)
            if exactly two distinct atom indices exist (otherwise NaN).
            Sign diagnostic:
             - >0: bonding-like
             - <0: antibonding-like
        max_abs_* : * in {ao_idx, atom_idx, element, n, l, component, coeff}
            Corresponding values from the `mo_coeffs` table
            for the dominant (|c|-largest) AO.
        frac_* : float for * in {'s','p','d','f'}
            Angular-momentum fractions:
            sum(c^2) within each l-character (0..1, sum≈1).
        lead_* : * in {atom_idx, element, l}
            Leading entity (by sum c^2) for each type.
        lead_*_frac : float for * in {atom_idx, element, l}
            Fraction (by sum c^2) of the leading entity.
        contrib_* : dict for * in {atom_idx, element, l}
            Dictionaries mapping entity → fraction (sum to ~1.0).
            Useful for further analysis.
        """
        return self._mos

    @property
    def mo_coeffs(self) -> pd.DataFrame:
        """MO coefficients data.

        This is a long-form dataframe where each row corresponds to
        a single AO coefficient of a single MO, with columns:

        mo_idx : int
            Unique (zero-based) index number of the MO;
            links to `mos`.
        ao_idx : int
            Unique (zero-based) index number of the AO;
            links to `aos`.
        atom_idx : int
            Unique (zero-based) index number of the AO's atom.
        element : str
            Chemical symbol of the AO's element.
        n : int
            Principal quantum number of the AO.
        l : str
            Angular momentum character of the AO (e.g., 's','p','d','f','g','h', ...).
        component : str
            Component of the AO (e.g., 'x', 'y', 'z' for p orbitals).
        coeff : float
            Coefficient of the AO in the MO.
        coeff_abs : float
            Absolute value of the coefficient.
        coeff_sq : float
            Squared value of the coefficient.
        """
        return self._mo_coeffs

    @property
    def aos(self) -> pd.DataFrame:
        """Atomic orbitals metadata.

        Each row corresponds to one AO, with columns:

        ao_idx : int
            Unique (zero-based) index number of the AO.
        atom_idx : int
            Unique (zero-based) index number of the AO's atom.
        element : str
            Chemical symbol of the AO's element.
        n : int
            Principal quantum number of the AO.
        l : str
            Angular momentum character of the AO (e.g., 's','p','d','f','g','h', ...).
        component : str
            Component of the AO (e.g., 'x', 'y', 'z' for p orbitals).
        nl : str
            Principal quantum number and angular momentum character (e.g., '2p').
        label : str
            Full label for the AO, as given in the GBW file (e.g., "0F   2px").
        """
        return self._aos

    @property
    def ao_coeffs(self) -> pd.DataFrame:
        """AO coefficients data.

        This is a long-form dataframe where each row corresponds to
        a single coefficient of a single basis function of a single AO, with columns:

        atom_idx : int
            Unique (zero-based) index number of the AO's atom.
        basis_idx : int
            Unique (zero-based) index number of the basis function within the AO.
        coeff_idx : int
            Unique (zero-based) index number of the coefficient within the basis function.
        coeff : float
            Coefficient value.
        shell : str
            Shell type of the basis function (e.g., 's', 'p', 'd', etc.).
        """
        return self._ao_coeffs

    @property
    def ao_exponents(self) -> pd.DataFrame:
        """AO exponents data.

        This is a long-form dataframe where each row corresponds to
        a single exponent of a single basis function of a single AO, with columns:

        atom_idx : int
            Unique (zero-based) index number of the AO's atom.
        basis_idx : int
            Unique (zero-based) index number of the basis function within the AO.
        exp_idx : int
            Unique (zero-based) index number of the exponent within the basis function.
        exp : float
            Exponent value.
        shell : str
            Shell type of the basis function (e.g., 's', 'p', 'd', etc.).
        """
        return self._ao_exponents

    @property
    def atoms(self) -> pd.DataFrame:
        """Atoms metadata.

        Each row corresponds to one atom, with columns:

        atom_idx : int
            Unique (zero-based) index number of the atom.
        element : str
            Chemical symbol of the atom.
        z : int
            Atomic number of the atom.
        z_eff : float
            Effective nuclear charge of the atom.
        charge_loewdin : float
            Löwdin charge of the atom.
        charge_mulliken : float
            Mulliken charge of the atom.
        spin_loewdin : float
            Löwdin spin population of the atom.
        spin_mulliken : float
            Mulliken spin population of the atom.
        x : float
            X coordinate of the atom.
        y : float
            Y coordinate of the atom.
        z : float
            Z coordinate of the atom.
        """
        return self._atoms

    @property
    def homo(self) -> pd.Series:
        """HOMO data."""
        return self.mos.loc[self.mos["homo"]].iloc[0]

    @property
    def lumo(self) -> pd.Series:
        """LUMO data."""
        return self.mos.loc[self.mos["lumo"]].iloc[0]

    @property
    def unit_energy(self) -> str:
        """Unit of the energy values."""
        return self.data["Molecule"]["MolecularOrbitals"]["EnergyUnit"]

    @property
    def unit_coordinates(self) -> str:
        """Unit of the coordinates values."""
        return self.data["Molecule"]["CoordinateUnits"]

    @property
    def multiplicity(self) -> int:
        """Multiplicity of the system."""
        return self.data["Molecule"]["Multiplicity"]

    @property
    def charge(self) -> int:
        """Charge of the system."""
        return self.data["Molecule"]["Charge"]

    @property
    def hf_type(self) -> str:
        """Hartree-Fock type (RHF or UHF)."""
        return self.data["Molecule"]["HFTyp"]

    @property
    def point_group(self) -> str:
        """Point group symmetry."""
        return self.data["Molecule"]["PointGroup"]

    @property
    def origin(self) -> np.ndarray:
        """Origin of the coordinate system."""
        return np.array(self.data["Molecule"]["Origin"])

    @property
    def formula(self) -> dict[str, int]:
        """Chemical formula of the system as a dictionary mapping element symbols to their counts.

        The elements are sorted following the standard IUPAC convention:
        - If carbon is present, it is listed first, followed by hydrogen,
          and then the other elements in alphabetical order.
        - Otherwise, from least to most electronegative element.
        """
        return self._formula

    @property
    def formula_latex(self) -> str:
        """Chemical formula of the system formatted for LaTeX.

        The elements are sorted following the standard IUPAC convention:
        - If carbon is present, it is listed first, followed by hydrogen,
          and then the other elements in alphabetical order.
        - Otherwise, from least to most electronegative element.

        The formula also includes the charge of the system as a superscript.
        """
        parts = []
        for element, count in self.formula.items():
            if count == 1:
                parts.append(f"{element}")
            else:
                parts.append(rf"{element}\textsubscript{{{count}}}")
        charge = self.charge
        if charge != 0:
            parts.append(rf"\textsuperscript{{{abs(charge)}{"+" if charge > 0 else "–"}}}")
        return "".join(parts)

    def mo_table_latex(
        self,
        columns: dict[str, str] = {
            "mo_idx": "MO",
            "spin": "Spin",
            "occupancy": "Occ.",
            "remark": "Remark",
            "energy_eh": r"\varepsilon~[\Eh]",
            "energy_ev": r"\varepsilon~[eV]",
            "pr": "PR",
            "n_contrib": r"$N_{\mathrm{contrib}}$",
            "max_abs": r"$\mathrm{AO}_{\max(c)}$",
            "frac": "s:p:d:f",
            "lead_atom": r"$\mathrm{Atom}_{\mathrm{lead}}$",
            "lead_element": r"$\mathrm{Elem.}_{\mathrm{lead}}$",
            "lead_l": r"$l_{\mathrm{lead}}$",
            "phase_prod": "Phase Prod.",
        },
        label: str = "tab:mo-{formula}_{charge}_{mult}",
        caption: str | None = "Orbital energies of {caption_system}, calculated using {caption_method}. {column_description}",
        caption_system: str = "{formula} ($M = {mult}$)",
        caption_method: str = "the {hf_type} method",
        position: str = "h!",
        position_float: str = "centering",
        hrules: bool = True,
        siunitx: bool = True,
        **kwargs,
    ) -> str:
        df = self.mos.copy()

        # Remove columns that are not applicable
        if "phase_prod" in columns and len(self.atoms) != 2:
            columns.pop("phase_prod")

        for col_df, col_latex in columns.items():
            if col_df == "spin":
                df["spin"] = df["spin"].map({"a": r"\alpha", "b": r"\beta", "ab": r"\alpha\beta"})
            elif col_df == "max_abs":
                def format_max_abs(row: pd.Series) -> str:
                    atom_idx = row["max_abs_atom_idx"]
                    element = row["max_abs_element"]
                    n = row["max_abs_n"]
                    l = row["max_abs_l"]
                    component = row["max_abs_component"]
                    coeff = row["max_abs_coeff"]
                    ao = f"{n}{l}_{{{component}}}" if component else f"{n}{l}"
                    return rf"{atom_idx}{element} {ao} ({coeff:.2f})"
                df[col_latex] = df.apply(format_max_abs, axis=1)
            elif col_df == "frac":
                fracs = df[["frac_s", "frac_p", "frac_d", "frac_f"]].to_numpy(dtype=float)
                min_vals = np.min(fracs, axis=1, keepdims=True)
                fracs_norm = np.round(fracs / min_vals, 2)
                ratios = [
                    ":".join(f"{val:.2f}".rstrip("0").rstrip(".") for val in row)
                    for row in fracs_norm
                ]
                df[col_latex] = ratios
            elif col_df == "lead_atom":
                def format_lead_atom(row: pd.Series) -> str:
                    atom_idx = row["lead_atom_idx"]
                    frac = row["lead_atom_idx_frac"]
                    element = self.atoms.loc[self.atoms["atom_idx"] == atom_idx, "element"].values[0]
                    return rf"{atom_idx}{element} ({frac:.2f})"
                df[col_latex] = df.apply(format_lead_atom, axis=1)
            elif col_df == "lead_element":
                def format_lead_element(row: pd.Series) -> str:
                    element = row["lead_element"]
                    frac = row["lead_element_frac"]
                    return rf"{element} ({frac:.2f})"
                df[col_latex] = df.apply(format_lead_element, axis=1)
            elif col_df == "lead_l":
                def format_lead_l(row: pd.Series) -> str:
                    l = row["lead_l"]
                    frac = row["lead_l_frac"]
                    return rf"{l} ({frac:.2f})"
                df[col_latex] = df.apply(format_lead_l, axis=1)
            elif col_df == "remark":
                df[col_latex] = ""
                system_is_atomic = len(self.atoms) == 1
                df.loc[df["homo"], col_latex] = "HOAO" if system_is_atomic else "HOMO"
                df.loc[df["lumo"], col_latex] = "LUAO" if system_is_atomic else "LUMO"
            else:
                df[col_latex] = df[col_df]
        return (
            df[list(columns.values())]
            .style.to_latex(
                position=position,
                position_float=position_float,
                hrules=hrules,
                label=label.format(symbol=symbol, charge=charge, mult=mult) if label else None,
                caption=caption.format(
                    caption_system=caption_system.format(
                        formula=self.formula_late,
                        mult=self.multiplicity,
                        point_group=self.point_group,
                    ),
                    caption_method=caption_method.format(hf_type=self.hf_type),
                    column_description=column_description,
                ) if caption else None,
                siunitx=siunitx,
                **kwargs,
            )
        )


def _parse_mos(mos: list[dict], ao_labels: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Parse MO data from GBW JSON data.

    Parameters
    ----------
    mos
        List of molecular orbitals from the GBW JSON data
        at `$.Molecule.MolecularOrbitals.MOs`.
    ao_labels
        List of atomic orbital labels from the GBW JSON data
        at `$.Molecule.MolecularOrbitals.OrbitalLabels`.

    Returns
    -------
    mo_df
        MO dataframe with one row per MO.
    coeff_df
        Long-form (MO × AO) coefficients dataframe with AO metadata.
    ao_df
        Atomic orbitals metadata dataframe.

    Raises
    ------
    KeyError
        If required keys are missing from the JSON.
    ValueError
        If detected dimensions do not align.
    """
    # Determine spin for each MO by block position (α then β if unrestricted)
    n_mo = len(mos)
    n_mo_coeff = len(mos[0]["MOCoefficients"])
    n_ao_labels = len(ao_labels)
    if n_ao_labels == n_mo_coeff:
        # One set of AOs for all MOs -> RHF
        spins = ["ab"] * n_mo
    elif n_ao_labels == 2 * n_mo_coeff:
        if ao_labels[:n_mo_coeff] != ao_labels[n_mo_coeff:]:
            raise ValueError("AO labels do not match for alpha and beta sets.")
        # Two sets of AOs (alpha and beta) -> UHF
        spins = ["a" if i < n_mo_coeff else "b" for i in range(n_mo)]
        ao_labels = ao_labels[:n_mo_coeff]
    else:
        raise ValueError("Number of AO labels does not match number of MO coefficients.")

    # AO metadata dataframe
    ao_meta = [_parse_ao_label(lbl) for lbl in ao_labels]
    ao_df = pd.DataFrame(ao_meta)
    ao_df["ao_idx"] = np.arange(len(ao_df), dtype=int)
    ao_df_cols = ["ao_idx", "atom_idx", "element", "n", "l", "component", "nl", "label"]
    ao_df = ao_df[ao_df_cols].convert_dtypes()

    # Long-form coefficients dataframe
    coeff_df = _create_coeff_df(mos, ao_meta).convert_dtypes()

    # MO dataframe
    mo_df = _create_mo_df(mos, spins)
    mo_df = _add_homo_lumo_columns(mo_df)
    mo_df = _augment_mo_df(mo_df, coeff_df)
    # Ensure consistent column ordering (important fields first)
    mo_cols = [
        "mo_idx",
        "spin",
        "occupancy",
        "energy_eh",
        "energy_ev",
        "sym_label",
        "sym_idx",
        "homo",
        "lumo",

        "norm_c2",
        "pr",
        "n_contrib",
        "phase_prod",

        "max_abs_ao_idx",
        "max_abs_atom_idx",
        "max_abs_element",
        "max_abs_n",
        "max_abs_l",
        "max_abs_component",
        "max_abs_coeff",

        "frac_s",
        "frac_p",
        "frac_d",
        "frac_f",
        "frac_g",
        "frac_h",

        "lead_atom_idx",
        "lead_element",
        "lead_l",

        "lead_atom_idx_frac",
        "lead_element_frac",
        "lead_l_frac",

        "contrib_atom_idx",
        "contrib_element",
        "contrib_l",
    ]
    # Reorder, sort, and convert dtypes
    mo_df = (
        mo_df[mo_cols]
        .sort_values(
            by=["energy_eh", "occupancy", "spin", "mo_idx"],
            ascending=[True, False, True, True],
            ignore_index=True,
        )
        .convert_dtypes()
    )

    return mo_df, coeff_df, ao_df


def _create_mo_df(mos: list[dict], spins: list[str]) -> pd.DataFrame:
    """Create the MO dataframe from raw MO data."""
    rows: list[dict] = []
    for idx, (mo, spin) in enumerate(zip(mos, spins)):
        rows.append(
            {
                "mo_idx": idx,
                "spin": spin,
                "occupancy": float(mo["Occupancy"]),
                "energy_eh": float(mo["OrbitalEnergy"]),
                "energy_ev": float(mo["OrbitalEnergy"]) * HARTREE_TO_EV_FACTOR,
                "sym_label": mo["OrbitalSymLabel"],
                "sym_idx": mo["OrbitalSymmetry"],
            }
        )
    return pd.DataFrame(rows)


def _create_coeff_df(mos: list[dict], ao_meta: list[dict]) -> pd.DataFrame:
    """Create long-form MO coefficients dataframe with AO metadata."""
    # Build (MO × AO) by repeating AO metadata and attaching coefficients.
    rows: list[dict] = []
    n_aos = len(ao_meta)
    for idx_mo, mo in enumerate(mos):
        coeffs = mo["MOCoefficients"]
        if len(coeffs) != n_aos:
            raise ValueError(
                f"MO {idx_mo}: coefficients length {len(coeffs)} != expected n_ao {n_aos}"
            )
        for idx_ao, (ao, coeff) in enumerate(zip(ao_meta, coeffs)):
            coeff = float(coeff)
            rows.append(
                {
                    "mo_idx": idx_mo,
                    "ao_idx": idx_ao,
                    "atom_idx": ao["atom_idx"],
                    "element": ao["element"],
                    "n": ao["n"],
                    "l": ao["l"],
                    "component": ao["component"],
                    "coeff": coeff,
                    "coeff_abs": abs(coeff),
                    "coeff_sq": coeff**2,
                }
            )
    return pd.DataFrame(rows)


def _parse_ao_label(label: str) -> dict[str, int | str]:
    """Parse an ORCA atomic orbital labels (i.e. MO coefficient labels).

    Parameters
    ----------
    label
        ORCA AO label (from `$.Molecule.MolecularOrbitals.OrbitalLabels`),
        e.g., "0F   2px", "1H   1s", "0F   1dz2".

    Returns
    -------
    Dictionary with keys:
        atom_idx : int
            Atom index of the AO.
        element : str
            Chemical symbol of the atom.
        n : int
            Principal quantum number n.
        l : str
            Angular momentum character, lowercased (e.g., 's','p','d','f','g','h', ...).
        component : str
            Optional real-harmonic component suffix (may be empty),
            captured verbatim (e.g., 'z', 'xy', 'x2y2', 'z3', 'x3-3xy2').
        nl : str
            Concise shell string like '2p', '3d', computed from n and l (lowercase).
        label : str
            Original label, stripped.

    Raises
    ------
    ValueError
        If the label does not match the expected ORCA AO format.

    Notes
    -----
    - We deliberately accept *any* non-space component to support higher-l real harmonics and
      implementation-specific mnemonics. Validation can be layered on top if you want to enforce
      a particular naming scheme.
    """
    match = _REGEX_AO_LABEL.match(label)
    if not match:
        raise ValueError(f"Unrecognized AO label format: {label!r}")
    label_comp = match.groupdict()
    n = int(label_comp["n"])
    l = label_comp["l"].lower()
    component = (label_comp["component"] or "").strip()
    return {
        "atom_idx": int(label_comp["atom_idx"]),
        "element": label_comp["element"],
        "n": n,
        "l": l,
        "component": component,
        "nl": f"{n}{l}",
        "label": label.strip(),
    }


def _augment_mo_df(
    mo_df: pd.DataFrame,
    coeff_df: pd.DataFrame
) -> pd.DataFrame:
    """Add coefficient-analysis features to the MO dataframe.

    Parameters
    ----------
    mo_df
        Base MO dataframe.
    coeff_df
        Long-form coefficients dataframe.

    Returns
    -------
    A copy of `mo_df` with additional columns derived from the coefficients:

    Raises
    ------
    KeyError
        If required columns are missing.

    Notes
    -----
    - All quantities are computed from raw coefficients (no AO overlap matrix).
      For rigorous populations, use Mulliken/Löwdin/NBO.
      Here we stick to coefficient-based diagnostics.
    - The `phase_prod` is a simple, basis-coefficient heuristic;
      it cannot replace proper bonding analysis (requires overlap and visualization).
    """
    # Group coefficients by MO
    coeff_group = coeff_df.groupby("mo_idx", sort=False)

    # Norm (sum(c^2))
    norm_c2 = coeff_group["coeff_sq"].sum().rename("norm_c2")

    # Participation ratio (1 / sum(c^4))
    pr = (1.0 / coeff_group["coeff_sq"].apply(lambda x: (x**2).sum())).rename("pr")

    # Dominant AO (by |c|)
    def _dominant_row(d: pd.DataFrame) -> pd.Series:
        i = d["coeff_abs"].values.argmax()
        row = d.iloc[i]
        return pd.Series(
            {
                "max_abs_ao_idx": row["ao_idx"],
                "max_abs_atom_idx": row["atom_idx"],
                "max_abs_element": row["element"],
                "max_abs_n": row["n"],
                "max_abs_l": row["l"],
                "max_abs_component": row["component"],
                "max_abs_coeff": row["coeff"],
            }
        )

    dom = coeff_group.apply(_dominant_row)

    # Angular momentum fractions (sum c^2 within each l-char)
    def _l_fracs(d: pd.DataFrame) -> pd.Series:
        totals = d.groupby("l")["coeff_sq"].sum()
        total = d["coeff_sq"].sum()
        out = {f"frac_{l}": (totals.get(l, 0.0) / total) for l in list("spdf")}
        return pd.Series(out)

    lfracs = coeff_group.apply(_l_fracs)

    # Atom and element contributions (fractions)
    def _fraction_map(d: pd.DataFrame, key: str) -> tuple[dict[str, float], str, float]:
        totals = d.groupby(key)["coeff_sq"].sum()
        total = d["coeff_sq"].sum()
        fracs = (totals / total).to_dict()
        # Leading entry
        lead_k = max(fracs, key=fracs.get)
        lead_v = float(fracs[lead_k])
        return fracs, lead_k, lead_v

    maps_atom_idx = coeff_group.apply(lambda d: _fraction_map(d, "atom_idx"))
    maps_element = coeff_group.apply(lambda d: _fraction_map(d, "element"))
    maps_l = coeff_group.apply(lambda d: _fraction_map(d, "l"))

    contrib_map_atom_idx = maps_atom_idx.apply(lambda t: t[0]).rename("contrib_atom_idx")
    contrib_map_element = maps_element.apply(lambda t: t[0]).rename("contrib_element")
    contrib_map_l = maps_l.apply(lambda t: t[0]).rename("contrib_l")

    lead_atom_idx = maps_atom_idx.apply(lambda t: t[1]).rename("lead_atom_idx")
    lead_element = maps_element.apply(lambda t: t[1]).rename("lead_element")
    lead_l = maps_l.apply(lambda t: t[1]).rename("lead_l")

    leadfrac_atom_idx = maps_atom_idx.apply(lambda t: float(t[2])).rename("lead_atom_idx_frac")
    leadfrac_element = maps_element.apply(lambda t: float(t[2])).rename("lead_element_frac")
    leadfrac_l = maps_l.apply(lambda t: float(t[2])).rename("lead_l_frac")

    # Count atoms with ≥ 1% contribution
    def _n_atoms_gt_thresh(d: dict[str, float], thresh: float = 0.01) -> int:
        return int(sum(1 for v in d.values() if v >= thresh))

    n_contrib = contrib_map_atom_idx.apply(_n_atoms_gt_thresh).rename("n_contrib")

    # Diatomic phase product heuristic (only if exactly two distinct atoms present globally)
    atom_indices_all = sorted(set(coeff_df["atom_idx"].tolist()))
    if len(atom_indices_all) == 2:
        # For each MO, compute (sum c over atom A) * (sum c over atom B)
        def _phase_product(d: pd.DataFrame) -> float:
            s_by_atom = d.groupby("atom_idx")["coeff"].sum()
            if len(s_by_atom) != 2:
                return float("nan")
            vals = list(s_by_atom.values)
            return float(vals[0] * vals[1])

        phase_prod = coeff_group.apply(_phase_product).rename("phase_prod")
    else:
        phase_prod = pd.Series(index=mo_df["mo_idx"], dtype=float, name="phase_prod")

    # Assemble augmentation table
    aug = (
        pd.concat(
            [
                norm_c2,
                pr,
                dom,
                lfracs,
                contrib_map_atom_idx,
                contrib_map_element,
                contrib_map_l,
                lead_atom_idx,
                lead_element,
                lead_l,
                leadfrac_atom_idx,
                leadfrac_element,
                leadfrac_l,
                n_contrib,
                phase_prod,
            ],
            axis=1,
        )
        .reset_index()
    )

    # Merge with mo_df (do not mutate original)
    return mo_df.merge(aug, on="mo_idx", how="left")


def _add_homo_lumo_columns(mos: pd.DataFrame) -> pd.DataFrame:
    """Add HOMO and LUMO indicators to the MO dataframe.

    This function identifies the highest occupied molecular orbital (HOMO)
    and the lowest unoccupied molecular orbital (LUMO) based on their
    energies and occupancy.

    The dataframe is modified in place to include the new columns:
    - "homo": boolean indicator for HOMO
    - "lumo": boolean indicator for LUMO
    """
    mos["homo"] = False
    mos["lumo"] = False
    occupied = mos.loc[mos["occupancy"] > 0]
    unoccupied = mos.loc[mos["occupancy"] == 0]
    if not occupied.empty:
        homo_idx = occupied["energy_eh"].idxmax()
        mos.loc[homo_idx, "homo"] = True
    if not unoccupied.empty:
        lumo_idx = unoccupied["energy_eh"].idxmin()
        mos.loc[lumo_idx, "lumo"] = True
    return mos


def _parse_atoms(atoms: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Parse atom data from GBW JSON data.

    Parameters
    ----------
    atoms
        List of atom data from the GBW JSON data
        at `$.Molecule.Atoms`.

    Returns
    -------
    atom_df
        Atom dataframe with one row per atom.
    coeff_df
        Basis coefficients dataframe with one row per basis coefficient of each atom.
    ao_df
        Basis exponents dataframe with one row per basis exponent of each atom.

    Raises
    ------
    KeyError
        If required keys are missing from the JSON.
    """
    atom_rows: list[dict] = []
    basis_coeff_rows: list[dict] = []
    basis_exponent_rows: list[dict] = []
    for atom in atoms:
        atom_idx = atom["Idx"]
        atom_rows.append(
            {
                "atom_idx": atom_idx,
                "element": atom["ElementLabel"],
                "z": atom["ElementNumber"],
                "z_eff": atom["NuclearCharge"],
                "charge_loewdin": atom["LoewdinCharge"],
                "charge_mulliken": atom["MullikenCharge"],
                "spin_loewdin": atom["LoewdinSpin"],
                "spin_mulliken": atom["MullikenSpin"],
                "x": atom["Coords"][0],
                "y": atom["Coords"][1],
                "z": atom["Coords"][2],
            }
        )
        for basis_idx, basis in enumerate(atom["Basis"]):
            shell = basis["Shell"]
            for coeff_idx, coeff in enumerate(basis["Coefficients"]):
                basis_coeff_rows.append(
                    {
                        "atom_idx": atom_idx,
                        "basis_idx": basis_idx,
                        "coeff_idx": coeff_idx,
                        "coeff": coeff,
                        "shell": shell,
                    }
                )
            for exp_idx, exponent in enumerate(basis["Exponents"]):
                basis_exponent_rows.append(
                    {
                        "atom_idx": atom_idx,
                        "basis_idx": basis_idx,
                        "exp_idx": exp_idx,
                        "exp": exponent,
                        "shell": shell,
                    }
                )
    return pd.DataFrame(atom_rows), pd.DataFrame(basis_coeff_rows), pd.DataFrame(basis_exponent_rows)


def _create_formula(atom_df: pd.DataFrame) -> dict[str, int]:
    """Return unique element counts as a dictionary.

    Parameters
    ----------
    atom_df
        Atom DataFrame with one row per atom containing an "element" column.

    Returns
    -------
    A dictionary mapping element symbols to their counts.
    The elements are sorted following the standard IUPAC convention:
    - If carbon is present, it is listed first, followed by hydrogen,
      and then the other elements in alphabetical order.
    - Otherwise, from least to most electronegative element.
    """
    counts = atom_df["element"].value_counts().to_dict()
    if "C" in counts:
        sorted_elements = ["C", "H"] + sorted(e for e in counts if e not in ("C", "H"))
    else:
        df = PERIODIC_TABLE.set_index("symbol")
        # Sort by electronegativity ascending (lowest first = most electropositive)
        sorted_elements = sorted(
            counts.keys(),
            key=lambda s: float("inf") if pd.isna(df.at[s, "en_pauling"]) else df.at[s, "en_pauling"],
        )
    formula = {el: counts[el] for el in sorted_elements}
    return formula


_REGEX_AO_LABEL = re.compile(
    r"""
    ^\s*                        # optional leading whitespace
    (?P<atom_idx>-?\d+)         # atom index (may be negative)
    (?P<element>[A-Za-z]{1,3})  # element symbol (1–3 letters)
    \s+                         # whitespace
    (?P<n>\d+)                  # principal quantum number n
    (?P<l>[A-Za-z])         # angular momentum quantum number label (e.g., s, p, d, f, g, h, i, ...)
    (?P<component>[^\s]*)       # optional real-harmonic component suffix (e.g., z, xy, x2y2, z3, x3-3xy2)
    \s*$                        # optional trailing whitespace
    """,
    re.VERBOSE,
)
"""Regular expression to parse ORCA atomic orbital labels (i.e. MO coefficient labels).

Example labels:
- "0H   1s"
- "1O   2px"
- "2C   3dxy"
"""
