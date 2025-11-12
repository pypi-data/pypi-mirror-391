# %%
from __future__ import annotations
from numbers import Number
from typing import List, Literal, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

import numpy as np

B0B1Model = Literal[
    'Bil-2000',
    'ABT-2009',
    'Gulayeva-1987'
]  # [3, 30] [T,T], [F,T], [F,F]
FoF2Model = Literal['CCIR', 'URSI']  # [4] T, F
NiModel = Literal['DS-95 & DY-85', 'RBV-2010 & TBT-2015']  # [5] T, F
NeMode = Literal['Standard', 'Lay-function']  # [10] T, F
MagField = Literal['IGRF', 'POGO68']  # [17] T, F
F1Model = Literal['Probabilistic', 'Probabilistic+L',
                  'Classic', 'None']  # [18, 19] [T,T], [T,F], [F,T], [F,F]
TeTopModel = Literal['Bil-1985', 'TBT-2012']  # [22] T, F
DRegionModel = Literal['IRI-90', 'FT-2001 & DRS-1995']  # [23] T, F
TopsideModel = Literal['IRI-90', 'IRICor', 'NeQuick',
                       'IRICor2']  # [28,29] [T,T], [F,T], [F,F], [T,F]

# [38,39] [T, T], [F, T], [F, F], [T, F]
HmF2Model = Literal['IRI-90', 'AMTB', 'Shubin', 'None']
IonTempModel = Literal['Tru-2021', 'Bil-1981']  # [47] T, F
PlasmasphereModel = Literal['Ozhogin', 'Gallagher']  # [48] T, F


def _b0b1model_flags(inp: B0B1Model) -> List[Tuple[int, bool]]:
    if inp == 'Bil-2000':
        return [(3, True), (30, True)]
    elif inp == 'ABT-2009':
        return [(3, False), (30, True)]
    elif inp == 'Gulayeva-1987':
        return [(3, False), (30, False)]
    else:
        raise ValueError(f"Unknown B0B1Model: {inp}")


def _fof2model_flags(inp: FoF2Model) -> List[Tuple[int, bool]]:
    if inp == 'CCIR':
        return [(4, True)]
    elif inp == 'URSI':
        return [(4, False)]
    else:
        raise ValueError(f"Unknown FoF2Model: {inp}")


def _ni_model_flags(inp: NiModel) -> List[Tuple[int, bool]]:
    if inp == 'DS-95 & DY-85':
        return [(5, True)]
    elif inp == 'RBV-2010 & TBT-2015':
        return [(5, False)]
    else:
        raise ValueError(f"Unknown NiModel: {inp}")


def _nemode_flags(inp: NeMode) -> List[Tuple[int, bool]]:
    if inp == 'Standard':
        return [(10, True)]
    elif inp == 'Lay-function':
        return [(10, False)]
    else:
        raise ValueError(f"Unknown NeMode: {inp}")


def _magfield_flags(inp: MagField) -> List[Tuple[int, bool]]:
    if inp == 'IGRF':
        return [(17, True)]
    elif inp == 'POGO68':
        return [(17, False)]
    else:
        raise ValueError(f"Unknown MagField: {inp}")


def _f1model_flags(inp: F1Model) -> List[Tuple[int, bool]]:
    if inp == 'Probabilistic':
        return [(18, True), (19, True)]
    elif inp == 'Probabilistic+L':
        return [(18, True), (19, False)]
    elif inp == 'Classic':
        return [(18, False), (19, True)]
    elif inp == 'None':
        return [(18, False), (19, False)]
    else:
        raise ValueError(f"Unknown F1Model: {inp}")


def _tetopmodel_flags(inp: TeTopModel) -> List[Tuple[int, bool]]:
    if inp == 'Bil-1985':
        return [(22, True)]
    elif inp == 'TBT-2012':
        return [(22, False)]
    else:
        raise ValueError(f"Unknown TeTopModel: {inp}")


def _dregionmodel_flags(inp: DRegionModel) -> List[Tuple[int, bool]]:
    if inp == 'IRI-90':
        return [(23, True)]
    elif inp == 'FT-2001 & DRS-1995':
        return [(23, False)]
    else:
        raise ValueError(f"Unknown DRegionModel: {inp}")


def _topsidemodel_flags(inp: TopsideModel) -> List[Tuple[int, bool]]:
    if inp == 'IRI-90':
        return [(28, True), (29, True)]
    elif inp == 'IRICor':
        return [(28, False), (29, True)]
    elif inp == 'NeQuick':
        return [(28, False), (29, False)]
    elif inp == 'IRICor2':
        return [(28, True), (29, False)]
    else:
        raise ValueError(f"Unknown TopsideModel: {inp}")


def _hmF2model_flags(inp: HmF2Model) -> List[Tuple[int, bool]]:
    if inp == 'IRI-90':
        return [(38, True), (39, True)]
    elif inp == 'AMTB':
        return [(38, False), (39, True)]
    elif inp == 'Shubin':
        return [(38, False), (39, False)]
    elif inp == 'None':
        return [(38, True), (39, False)]
    else:
        raise ValueError(f"Unknown HmF2Model: {inp}")


def _iontempmodel_flags(inp: IonTempModel) -> List[Tuple[int, bool]]:
    if inp == 'Tru-2021':
        return [(47, True)]
    elif inp == 'Bil-1981':
        return [(47, False)]
    else:
        raise ValueError(f"Unknown IonTempModel: {inp}")


def _plasmaspheremodel_flags(inp: PlasmasphereModel) -> List[Tuple[int, bool]]:
    if inp == 'Ozhogin':
        return [(48, True)]
    elif inp == 'Gallagher':
        return [(48, False)]
    else:
        raise ValueError(f"Unknown PlasmasphereModel: {inp}")


@dataclass
class Settings:
    """Settings for IRI-2020 model evaluation.
    """
    # compute_ne: bool = True  # 0
    # """Compute electron density [default: True]
    # """
    # compute_temp: bool = True  # 1
    # """Compute electron and ion temperatures [default: True]
    # """
    # compute_ions: bool = True  # 2
    # """Compute ion densities [default: True]
    # """
    b0_b1_model: B0B1Model = 'ABT-2009'  # [3,30]
    """B0-B1 model. Available options are:
    - 'Bil-2000'
    - 'ABT-2009' [default]
    - 'Gulayeva-1987'
    """
    fof2_model: FoF2Model = 'URSI'  # [4]
    """FoF2 model. Available options are:
    - 'CCIR'
    - 'URSI' [default]
    """
    ni_model: NiModel = 'RBV-2010 & TBT-2015'  # [5]
    """Neutral ion model. Available options are:
    - 'DS-95 & DY-85'
    - 'RBV-2010 & TBT-2015' [default]
    """
    ne_f107_limit: bool = True  # [6] F10.7 is limited to < 188
    """Limit F10.7 to < 188 for electron density calculations [default: True]
    """
    foF2: Optional[Number] = None  # [7] Bool -> True
    """User-defined foF2 value in MHz or NmF2 in m-3. If None, foF2 is computed by IRI [default: None]
    """
    hmF2: Optional[Number] = None  # [8] Bool -> True
    """User-defined hmF2 value in km or M(3000)F2. If None, hmF2 is computed by IRI [default: None]
    """
    te_mode: Optional[Tuple[Number, Number]] = None  # [9]
    """Electron temperature from model or using Te/Ne correlation.
    If using Te/Ne correlation, provide values of Ne (m-3) at two altitudes.
    If TE Topside model is TBT-2012, the altitudes are 300 km and 550 km.
    If TE Topside model is Bil-1985, the altitudes are 300 km and 400 km.
    If None, electron temperature is computed by IRI [default: None]
    """
    ne_mode: NeMode = 'Standard'  # [10]
    """Electron density mode. Available options are:
    - 'Standard' [default]
    - 'Lay-function'
    """
    # None -> [(11, True), (33, False)], Path -> [(11, False), (33, True)]
    logfile: Optional[Path] = None
    """Path to logfile. If None, no logfile is created [default: None]
    """
    foF1: Optional[Number] = None  # [12] Bool -> True
    """User-defined foF1 value in MHz or NmF1 in m-3. If None, foF1 is computed by IRI [default: None]
    """
    hmF1: Optional[Number] = None  # [13] Bool -> True + Ne Lay-function
    """User-defined hmF1 value in km. If None, hmF1 is computed by IRI [default: None]
    """
    foE: Optional[Number] = None  # [14] Bool -> True
    """User-defined foE value in MHz or NmE in m-3. If None, foE is computed by IRI [default: None]
    """
    hmE: Optional[Number] = None  # [15] Bool -> True
    """User-defined hmE value in km. If None, hmE is computed by IRI [default: None]
    """
    rz12: Optional[Number] = None  # [16] Bool -> True, OARR[32]
    """User-defined Rz12 value. If None, Rz12 is read from data files [default: None]
    """
    magfield: MagField = 'IGRF'  # [17] True -> IGRF, False -> POGO68
    """Magnetic field model. Available options are:
    - 'IGRF' [default]
    - 'POGO68'
    """
    F1_model: F1Model = 'Probabilistic'  # [18, 19]
    """F1 layer model. Available options are:
    - 'Probabilistic' [default]
    - 'Probabilistic+L'
    - 'Classic'
    - 'None'
    """
    ion_drift: bool = True  # [20]
    """Compute ion drift [default: True]
    """
    # ion densities in m3: [21] -> False
    te_topside: TeTopModel = 'TBT-2012'  # [22] -> F
    """Electron temperature topside model. Available options are:
    - 'Bil-1985'
    - 'TBT-2012' [default]
    """
    d_region: DRegionModel = 'IRI-90'  # [23] -> T
    """D-region model. Available options are:
    - 'IRI-90' [default]
    - 'FT-2001 & DRS-1995'
    """
    # [24, 31] Bool -> [True, True], OARR[40, 45]
    f107: Optional[Tuple[Number, Number]] = None
    """F10.7 and F10.7A values. If None, F10.7 and F10.7A are read from data files [default: None]
    """
    fof2_storm_model: bool = True  # [25]
    """Enable FoF2 storm model [default: True]
    """
    ig12: Optional[Number] = None  # [26] Bool -> True, OARR[38]
    """User-defined IG12 value. If None, IG12 is read from data files [default: None]
    """
    spread_f_probability: bool = True  # [27]
    """Compute spread-F probability [default: True]
    """
    topside_model: TopsideModel = 'IRICor2'  # [28,29] -> [T,F]
    """Topside model. Available options are:
    - 'IRI-90'
    - 'IRICor'
    - 'NeQuick'
    - 'IRICor2' [default]
    """
    auroral_boundary: bool = False  # [32]
    """Compute auroral boundary [default: False]
    """
    foe_storm: bool = False  # [34]
    """Enable foE storm model [default: False]
    """
    hmf2_with_fof2_storm: bool = True  # [35]
    """Enable hmF2 variation with FoF2 storm model [default: True]
    """
    topside_without_fof2_storm: bool = True  # [36]
    """Enable topside variation without FoF2 storm model [default: True]
    """
    # [37] -> True [Turn off writes in IRIFLIP]
    hmf2_model: HmF2Model = 'Shubin'  # [38, 39] -> [False, False]
    """hmF2 model. Available options are:
    - 'IRI-90'
    - 'AMTB'
    - 'Shubin' [default]
    - 'None'
    """
    # [40] -> True [F10.7 yearly average], False -> function of IG12
    cov_src: bool = True
    """Source of F10.7 yearly average value.
    - True: Uses measured value from data file.
    - False: Derives from IG12.
    """
    te_with_f107_dependency: bool = True  # [41] -> True
    """Enable electron temperature dependence on F10.7 [default: True]
    """
    b0_value: Optional[Number] = None  # [42] Bool -> True, OARR[9]
    """User-defined B0 value. If None, B0 is computed by IRI [default: None]
    """
    b1_value: Optional[Number] = None  # [43] Bool -> True, OARR[35]
    """User-defined B1 value. If None, B1 is computed by IRI [default: None]
    """
    es_occ_prob: bool = True  # [44] -> True
    es_prob_no_solar: bool = True  # [45] -> True
    cgm_compute: bool = False  # [46] -> False
    """Compute CGM [default: False]
    """
    ion_temp_model: IonTempModel = 'Tru-2021'  # [47] -> True
    """Ion temperature model. Available options are:
    - 'Tru-2021' [default]
    - 'Bil-1981'
    """
    plasmasphere: PlasmasphereModel = 'Ozhogin'  # [48] -> True
    """Plasmasphere model. Available options are:
    - 'Ozhogin' [default]
    - 'Gallagher'
    """
    plasmapause: bool = True  # [49] -> True
    """Compute plasmapause [default: True]
    """

    def to_json(self) -> str:
        """Convert settings to JSON string.

        Returns:
            str: JSON string representation of settings.
        """
        import json
        from dataclasses import asdict
        settings = asdict(self)
        settings['logfile'] = str(
            self.logfile) if self.logfile is not None else None
        return json.dumps(settings)


@dataclass
class ComputedSettings:
    """Computed settings for IRI-2020 model evaluation.
    DO NOT create this class directly; use :obj:`ComputedSettings.from_settings()` instead.
    """
    jf: np.ndarray
    oarr: np.ndarray
    logfile: str

    @staticmethod
    def from_settings(settings: Settings) -> ComputedSettings:
        """Build a ComputedSettings low-level settings
        structure from a Settings structure.

        Args:
            settings (Settings): IRI-2020 Settings.

        Raises:
            IsADirectoryError: If logfile is a directory.

        Returns:
            ComputedSettings: Low-level settings.
        """
        jf = np.full(50, True, dtype=bool)
        oarr = np.full(100, -1, dtype=float)
        jf[11] = False
        jf[33] = True
        # Set flags based on settings
        jf[6] = settings.ne_f107_limit
        if settings.foF2 is not None:
            jf[7] = False
            oarr[0] = settings.foF2
        if settings.hmF2 is not None:
            jf[8] = False
            oarr[1] = settings.hmF2
        if settings.te_mode is not None:
            jf[9] = False
            oarr[14] = settings.te_mode[0]
            oarr[15] = settings.te_mode[1]
        if settings.logfile is not None and settings.logfile != '':
            if settings.logfile.exists() and settings.logfile.is_dir():
                raise IsADirectoryError(settings.logfile)
            logfile_str = str(settings.logfile)
        else:
            logfile_str = '/dev/null'
        if settings.foF1 is not None:
            jf[12] = False
            oarr[2] = settings.foF1
        if settings.hmF1 is not None:
            jf[13] = False
            oarr[3] = settings.hmF1
        if settings.foE is not None:
            jf[14] = False
            oarr[4] = settings.foE
        if settings.hmE is not None:
            jf[15] = False
            oarr[5] = settings.hmE
        if settings.rz12 is not None:
            jf[16] = False
            oarr[32] = settings.rz12
        jf[20] = settings.ion_drift
        jf[21] = False  # Ion densities in m3 always

        if settings.f107 is not None:
            jf[24] = False
            jf[31] = False
            oarr[40] = settings.f107[0]
            oarr[45] = settings.f107[1]

        jf[25] = settings.fof2_storm_model
        if settings.ig12 is not None:
            jf[26] = False
            oarr[38] = settings.ig12
        jf[27] = settings.spread_f_probability
        jf[32] = settings.auroral_boundary
        jf[34] = settings.foe_storm
        jf[35] = settings.hmf2_with_fof2_storm
        jf[36] = settings.topside_without_fof2_storm
        jf[37] = True  # Turn off writes in IRIFLIP
        jf[40] = settings.cov_src
        jf[41] = settings.te_with_f107_dependency
        if settings.b0_value is not None:
            jf[42] = False
            oarr[9] = settings.b0_value
        if settings.b1_value is not None:
            jf[43] = False
            oarr[35] = settings.b1_value
        jf[44] = settings.es_occ_prob
        jf[45] = settings.es_prob_no_solar
        jf[46] = settings.cgm_compute
        jf[49] = settings.plasmapause

        funcs = [
            _b0b1model_flags,
            _fof2model_flags,
            _ni_model_flags,
            _nemode_flags,
            _magfield_flags,
            _f1model_flags,
            _tetopmodel_flags,
            _dregionmodel_flags,
            _topsidemodel_flags,
            _hmF2model_flags,
            _iontempmodel_flags,
            _plasmaspheremodel_flags,
        ]
        vals = [
            settings.b0_b1_model,
            settings.fof2_model,
            settings.ni_model,
            settings.ne_mode,
            settings.magfield,
            settings.F1_model,
            settings.te_topside,
            settings.d_region,
            settings.topside_model,
            settings.hmf2_model,
            settings.ion_temp_model,
            settings.plasmasphere,
        ]
        for func, val in zip(funcs, vals):
            for index, flag in func(val): # type: ignore
                jf[index] = flag

        # Additional flags and oarr values would be set here...

        return ComputedSettings(jf=jf, oarr=oarr.astype(np.float32), logfile=logfile_str)
