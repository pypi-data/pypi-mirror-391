# %%
from __future__ import annotations
from .iri20shim import iri20_init, iri20_eval  # type: ignore
from datetime import datetime, UTC, timedelta
import os
from pathlib import Path
from dataclasses import dataclass
from time import perf_counter_ns
from typing import Any, Dict, Optional, Tuple, SupportsFloat as Numeric

import numpy as np
from xarray import Dataset

from .utils import Singleton, iridate
from .settings import Settings, ComputedSettings

DIRNAME = Path(os.path.dirname(__file__))
DATADIR = DIRNAME / "data"
DATADIR = DATADIR.resolve()


@dataclass
class Attribute:
    value: Any
    units: Optional[str]
    long_name: str
    description: Optional[str] = None

    def to_json(self) -> str:
        from json import dumps
        from dataclasses import asdict
        return dumps(asdict(self))


class Iri2020(Singleton):
    """IRI-2020 Model.

    Args:
        settings (Optional[Settings], optional): Configuration settings. Defaults to None.
    """

    def _init(self, settings: Optional[Settings] = None):
        iri20_init(str(DATADIR))
        self.settings: Settings = settings or Settings()
        self._benchmark = False
        self._call = 0
        self._setup = 0.0
        self._fortran = 0.0
        self._ds_build = 0.0
        self._ds_attrib = 0.0
        self._ds_settings = 0.0
        self._total = 0.0

    @property
    def benchmark(self) -> bool:
        return self._benchmark

    @benchmark.setter
    def benchmark(self, value: bool):
        if value != self._benchmark:
            self._call = 0
            self._setup = 0
            self._fortran = 0
            self._ds_build = 0
            self._ds_attrib = 0
            self._ds_settings = 0
            self._total = 0
        self._benchmark = value

    def get_benchmark(self) -> Optional[Dict[str, timedelta]]:
        """Get benchmark data.

        Returns:
            Optional[Dict[str, timedelta]]: Metric and measured time.
        """
        if not self._benchmark or self._call == 0:
            return None
        return {
            'setup': timedelta(milliseconds=self._setup / self._call),
            'fortran': timedelta(milliseconds=self._fortran / self._call),
            'ds_build': timedelta(milliseconds=self._ds_build / self._call),
            'ds_attrib': timedelta(milliseconds=self._ds_attrib / self._call),
            'ds_settings': timedelta(milliseconds=self._ds_settings / self._call),
            'total': timedelta(milliseconds=self._total / self._call),
        }

    def _iricall(self, lat: Numeric, lon: Numeric, alt: np.ndarray, year: int, day: int, ut: Numeric, settings: ComputedSettings) -> Dataset:
        start = perf_counter_ns()
        outf = np.zeros((20, len(alt)), dtype=np.float32, order='F')
        ds = Dataset()
        ds.coords['alt_km'] = (
            ('alt_km',), alt.copy(), {'units': 'km', 'long_name': 'Altitude'})
        alt = alt.astype(np.float32, order='F')
        setup = perf_counter_ns()
        iri20_eval(
            settings.jf, 0, lat, lon, year, -day, (float(ut) / 3600.0) + 25,
            alt, outf, settings.oarr, str(DATADIR), settings.logfile
        )
        fortran = perf_counter_ns()
        densities = ['Ne', 'O+', 'H+', 'He+', 'O2+', 'NO+', 'Cluster', 'N+']
        den_names = [
            'Electron', 'Oxygen Ion', 'Hydrogen Ion', 'Helium Ion', 'Oxygen Molecular Ion',
            'Nitric Oxide Ion', 'Cluster Ion', 'Nitrogen Ion'
        ]
        density_idx = [0, 4, 5, 6, 7, 8, 9, 10]
        temperatures = ['Tn', 'Te', 'Ti']
        temperature_names = [
            'Neutral Temperature',
            'Electron Temperature', 'Ion Temperature'
        ]
        temperature_idx = [1, 3, 2]
        for idx, name, desc in zip(density_idx, densities, den_names):
            ds[name] = (('alt_km',), np.array(outf[idx]*1e-6, dtype=float),
                        {'units': 'cm^-3', 'long_name': f'{desc} Density'})
        for idx, name, desc in zip(temperature_idx, temperatures, temperature_names):
            ds[name] = (('alt_km',), np.array(outf[idx], dtype=float), {
                        'units': 'K', 'long_name': f'{desc} Temperature'})
        ds_build = perf_counter_ns()
        ds.attrs['attributes'] = 'Stored as JSON strings'
        ds.attrs['description'] = 'IRI 2020 model output'
        oarr = settings.oarr.copy().astype(float)
        attrs = {}
        attrs['nmF2'] = Attribute(
            oarr[0]*1e-6, 'cm^-3', 'F2 Peak Density', 'F2 layer peak electron density')
        attrs['hmF2'] = Attribute(
            oarr[1], 'km', 'F2 Peak Height', 'F2 layer peak height')
        attrs['nmF1'] = Attribute(
            oarr[2]*1e-6, 'cm^-3', 'F1 Peak Density', 'F1 layer peak electron density')
        attrs['hmF1'] = Attribute(
            oarr[3], 'km', 'F1 Peak Height', 'F1 layer peak height')
        attrs['nmE'] = Attribute(
            oarr[4]*1e-6, 'cm^-3',
            'E Layer Peak Density', 'E layer peak electron density'
        )
        attrs['hmE'] = Attribute(
            oarr[5], 'km', 'E Layer Peak Height', 'E layer peak height')
        attrs['nmD'] = Attribute(
            oarr[6]*1e-6, 'cm^-3', 'D Layer inflection point density')
        attrs['hmD'] = Attribute(
            oarr[7], 'km', 'D-region inflection point')
        attrs['hhalf'] = Attribute(
            oarr[8], 'km', 'Half Height', 'Height used by Gulyaeva B0 model')
        attrs['B0'] = Attribute(oarr[9], 'km',
                                'B0', 'Bottomside thickness parameter')
        attrs['valley_base'] = Attribute(
            oarr[10]*1e-6, 'cm^-3', 'Density at E-valley base')
        attrs['valley_top'] = Attribute(
            oarr[11], 'km', 'Height of E-valley top')
        attrs['Te-Peak'] = Attribute(oarr[12], 'K', 'Te Peak')
        attrs['hTe-Peak'] = Attribute(
            oarr[13],
            'km', 'hTe Peak', 'Peak Te altitude'
        )
        attrs['Te-MOD(300km)'] = Attribute(
            oarr[14], 'K',
            'Te MOD(300km)', 'Electron temperature at 300 km altitude'
        )
        attrs['Te-MOD(400km)'] = Attribute(
            oarr[15], 'K',
            'Te MOD(400km)', 'Electron temperature at 400 km altitude'
        )
        attrs['Te-MOD(600km)'] = Attribute(
            oarr[16], 'K',
            'Te MOD(600km)', 'Electron temperature at 600 km altitude'
        )
        attrs['Te-MOD(1400km)'] = Attribute(
            oarr[17], 'K',
            'Te MOD(1400km)', 'Electron temperature at 1400 km altitude'
        )
        attrs['Te-MOD(3000km)'] = Attribute(
            oarr[18], 'K',
            'Te MOD(3000km)', 'Electron temperature at 3000 km altitude'
        )
        attrs['Te-MOD(120km)'] = Attribute(
            oarr[19], 'K', 'Te MOD(120km)',
            'Electron temperature at 120 km altitude, Te = Ti = Tn')
        attrs['Ti-MOD(430km)'] = Attribute(
            oarr[20], 'K',
            'Ti MOD(430km)', 'Ion temperature at 430 km altitude'
        )
        attrs['Ti-Te-Eq'] = Attribute(
            oarr[21], 'km', 'Ti-Te-Eq',
            'Height at which ion and electron temperatures are at equilibrium'
        )
        attrs['sza'] = Attribute(
            oarr[22], 'degrees', 'Solar Zenith Angle',
            'Solar zenith angle at the specified location and time'
        )
        attrs['sun_dec'] = Attribute(
            oarr[23], 'degrees', 'Solar Declination', 'Solar declination angle at the specified time')
        attrs['dip'] = Attribute(
            oarr[24], 'degrees', 'Magnetic Dip Angle',
            'Magnetic dip angle at the specified location'
        )
        attrs['dip-lat'] = Attribute(
            oarr[25], 'degrees', 'Magnetic Dip Latitude', 'Magnetic dip latitude')
        attrs['dip-lat-mod'] = Attribute(
            oarr[26], 'degrees', 'Magnetic Dip Latitude (Modified)', 'Modified magnetic dip latitude')
        attrs['lat'] = Attribute(
            oarr[27], 'degrees', 'Latitude', 'Geographic Latitude')
        attrs['sunrise'] = Attribute(
            oarr[28], 'hours', 'Sunrise Time', 'Local time of sunrise')
        attrs['sunset'] = Attribute(
            oarr[29], 'hours', 'Sunset Time', 'Local time of sunset')
        attrs['season'] = Attribute(oarr[30], None, 'Season',
                                    'Season indicator: 1=Spring, 2=Summer, 3=Fall, 4=Winter')
        attrs['lon'] = Attribute(
            oarr[31], 'degrees', 'Longitude', 'Geographic Longitude')
        attrs['RZ12'] = Attribute(
            oarr[32], None, 'RZ12 Solar Index',
            '12-month running average of the solar radio flux at 10.7 cm'
        )
        attrs['cov'] = Attribute(oarr[33], None, 'Covington Index')
        attrs['B1'] = Attribute(
            oarr[34], None,
            'B1', 'Bottomside shape parameter'
        )
        attrs['M(3000)F2'] = Attribute(
            oarr[35], 'MHz', 'M(3000)F2',
            'Maximum usable frequency for a 3000 km path in the F2 layer'
        )
        # attrs['TEC'] = Attribute(oarr[36]*1e16, 'm^-2', 'Total Electron Content', 'Total electron content along a vertical column through the ionosphere')
        # attrs['TEC_top'] = Attribute(oarr[37]*1e16, 'm^-2', 'Total Electron Content top of ionosphere')
        attrs['IG12'] = Attribute(
            oarr[38], None, 'IG12 Solar Index',
            '12-month running average of the IG12 solar index'
        )
        attrs['F1_prob'] = Attribute(
            oarr[39], None, 'F1 Layer Probability', 'Probability of occurrence of the F1 layer')
        attrs['F10.7'] = Attribute(
            oarr[40], 'sfu', 'F10.7 Solar Flux', 'Daily solar radio flux at 10.7 cm wavelength')
        attrs['c1'] = Attribute(oarr[41], None, 'c1 Coefficient',
                                'Coefficient c1 used in F1 shape calculation')
        attrs['daynr'] = Attribute(
            oarr[42], None, 'Day Numeric', 'Day number within the year (1-365/366)')
        attrs['vert_ion_drift'] = Attribute(
            oarr[43], 'm/s', 'Equatorial Vertical Ion Drift', 'Vertical ion drift velocity'
        )
        attrs['foF2_rat'] = Attribute(
            oarr[44], None, 'Storm foF2 / Quiet foF2',
            'Ratio of the F2 layer critical frequency during storm conditions to quiet conditions'
        )
        attrs['F10.7_81'] = Attribute(
            oarr[45], 'sfu', '81-day Averaged F10.7 Solar Flux',
            '81-day averaged solar radio flux at 10.7 cm wavelength'
        )
        attrs['foE_rat'] = Attribute(
            oarr[46], None, 'Storm foE / Quiet foE',
            'Ratio of the E layer critical frequency during storm conditions to quiet conditions'
        )
        attrs['spread_f_prob'] = Attribute(
            oarr[47], None, 'Spread F Probability', 'Probability of occurrence of spread F conditions')
        attrs['geomag_lat'] = Attribute(
            oarr[48], 'degrees', 'Geomagnetic Latitude', 'Geomagnetic latitude at the specified location')
        attrs['geomag_lon'] = Attribute(
            oarr[49], 'degrees', 'Geomagnetic Longitude', 'Geomagnetic longitude at the specified location')
        attrs['ap'] = Attribute(
            oarr[50], None, 'Ap Geomagnetic Index', 'Planetary geomagnetic index Ap')
        attrs['ap_daily'] = Attribute(
            oarr[51], None, 'Daily Ap Geomagnetic Index', 'Daily planetary geomagnetic index Ap')
        attrs['invdip'] = Attribute(
            oarr[52], 'degrees', 'Invariant Dip Latitude', 'Invariant dip latitude')
        attrs['MLT-Te'] = Attribute(oarr[53], 'hours', 'MLT-Te')
        attrs['cgm_lat'] = Attribute(
            oarr[54], 'degrees', 'CGM Latitude', 'Corrected geomagnetic latitude')
        attrs['cgm_lon'] = Attribute(
            oarr[55], 'degrees', 'CGM Longitude', 'Corrected geomagnetic longitude')
        attrs['cgm_mlt'] = Attribute(
            oarr[56], 'hours', 'CGM MLT', 'Corrected geomagnetic local time')
        attrs['cgm_lat_auroral_boundary'] = Attribute(
            oarr[57], 'degrees', 'CGM Latitude Auroral Boundary', 'Corrected geomagnetic latitude of the auroral boundary')
        attrs['cgm_lat_mlt_00'] = Attribute(
            oarr[58], 'degrees', 'CGM Latitude MLT 00', 'Corrected geomagnetic latitude at magnetic local time 00')
        attrs['cgm_lat_mlt_01'] = Attribute(
            oarr[59], 'degrees', 'CGM Latitude MLT 01', 'Corrected geomagnetic latitude at magnetic local time 01')
        attrs['cgm_lat_mlt_02'] = Attribute(
            oarr[60], 'degrees', 'CGM Latitude MLT 02', 'Corrected geomagnetic latitude at magnetic local time 02')
        attrs['cgm_lat_mlt_03'] = Attribute(
            oarr[61], 'degrees', 'CGM Latitude MLT 03', 'Corrected geomagnetic latitude at magnetic local time 03')
        attrs['cgm_lat_mlt_04'] = Attribute(
            oarr[62], 'degrees', 'CGM Latitude MLT 04', 'Corrected geomagnetic latitude at magnetic local time 04')
        attrs['cgm_lat_mlt_05'] = Attribute(
            oarr[63], 'degrees', 'CGM Latitude MLT 05', 'Corrected geomagnetic latitude at magnetic local time 05')
        attrs['cgm_lat_mlt_06'] = Attribute(
            oarr[64], 'degrees', 'CGM Latitude MLT 06', 'Corrected geomagnetic latitude at magnetic local time 06')
        attrs['cgm_lat_mlt_07'] = Attribute(
            oarr[65], 'degrees', 'CGM Latitude MLT 07', 'Corrected geomagnetic latitude at magnetic local time 07')
        attrs['cgm_lat_mlt_08'] = Attribute(
            oarr[66], 'degrees', 'CGM Latitude MLT 08', 'Corrected geomagnetic latitude at magnetic local time 08')
        attrs['cgm_lat_mlt_09'] = Attribute(
            oarr[67], 'degrees', 'CGM Latitude MLT 09', 'Corrected geomagnetic latitude at magnetic local time 09')
        attrs['cgm_lat_mlt_10'] = Attribute(
            oarr[68], 'degrees', 'CGM Latitude MLT 10', 'Corrected geomagnetic latitude at magnetic local time 10')
        attrs['cgm_lat_mlt_11'] = Attribute(
            oarr[69], 'degrees', 'CGM Latitude MLT 11', 'Corrected geomagnetic latitude at magnetic local time 11')
        attrs['cgm_lat_mlt_12'] = Attribute(
            oarr[70], 'degrees', 'CGM Latitude MLT 12', 'Corrected geomagnetic latitude at magnetic local time 12')
        attrs['cgm_lat_mlt_13'] = Attribute(
            oarr[71], 'degrees', 'CGM Latitude MLT 13', 'Corrected geomagnetic latitude at magnetic local time 13')
        attrs['cgm_lat_mlt_14'] = Attribute(
            oarr[72], 'degrees', 'CGM Latitude MLT 14', 'Corrected geomagnetic latitude at magnetic local time 14')
        attrs['cgm_lat_mlt_15'] = Attribute(
            oarr[73], 'degrees', 'CGM Latitude MLT 15', 'Corrected geomagnetic latitude at magnetic local time 15')
        attrs['cgm_lat_mlt_16'] = Attribute(
            oarr[74], 'degrees', 'CGM Latitude MLT 16', 'Corrected geomagnetic latitude at magnetic local time 16')
        attrs['cgm_lat_mlt_17'] = Attribute(
            oarr[75], 'degrees', 'CGM Latitude MLT 17', 'Corrected geomagnetic latitude at magnetic local time 17')
        attrs['cgm_lat_mlt_18'] = Attribute(
            oarr[76], 'degrees', 'CGM Latitude MLT 18', 'Corrected geomagnetic latitude at magnetic local time 18')
        attrs['cgm_lat_mlt_19'] = Attribute(
            oarr[77], 'degrees', 'CGM Latitude MLT 19', 'Corrected geomagnetic latitude at magnetic local time 19')
        attrs['cgm_lat_mlt_20'] = Attribute(
            oarr[78], 'degrees', 'CGM Latitude MLT 20', 'Corrected geomagnetic latitude at magnetic local time 20')
        attrs['cgm_lat_mlt_21'] = Attribute(
            oarr[79], 'degrees', 'CGM Latitude MLT 21', 'Corrected geomagnetic latitude at magnetic local time 21')
        attrs['cgm_lat_mlt_22'] = Attribute(
            oarr[80], 'degrees', 'CGM Latitude MLT 22', 'Corrected geomagnetic latitude at magnetic local time 22')
        attrs['cgm_lat_mlt_23'] = Attribute(
            oarr[81], 'degrees', 'CGM Latitude MLT 23', 'Corrected geomagnetic latitude at magnetic local time 23')
        attrs['kp'] = Attribute(
            oarr[82], None, 'Kp Geomagnetic Index', 'Planetary geomagnetic index Kp')
        attrs['declination'] = Attribute(
            oarr[83], 'degrees', 'Magnetic Declination', 'Magnetic declination angle at the specified location')
        attrs['L-value'] = Attribute(
            oarr[84],
            None, 'L-value', 'McIlwain L-parameter'
        )
        attrs['dipole-moment'] = Attribute(
            oarr[85], 'Unknown',
            'Dipole Moment', 'Earth\'s magnetic dipole moment'
        )
        attrs['SAX300'] = Attribute(
            oarr[86], 'hours', 'SAX300', 'Sunrise at 300km altitude')
        attrs['SUX300'] = Attribute(
            oarr[87], 'hours', 'SUX300', 'Sunset at 300km altitude')
        attrs['HNEA'] = Attribute(
            oarr[88], 'km', 'HNEA', 'Lower boundary of Ne valid range')
        attrs['HNEE'] = Attribute(
            oarr[89], 'km', 'HNEE', 'Upper boundary of Ne valid range')
        attrs['es_occ_prob'] = Attribute(
            oarr[90], '%', 'Es Occurrence Probability', 'Sporadic E layer occurrence probability')

        for key, attr in attrs.items():
            if isinstance(attr, Attribute):
                ds.attrs[key] = attr.to_json()
            elif attr is not None:
                ds.attrs[key] = str(attr)
        ds_attrib = perf_counter_ns()
        ds.attrs['settings'] = self.settings.to_json()
        ds_settings = perf_counter_ns()
        if self._benchmark:
            self._call += 1
            self._setup += (setup - start)*1e-6
            self._fortran += (fortran - setup)*1e-6
            self._ds_build += (ds_build - fortran)*1e-6
            self._ds_attrib += (ds_attrib - ds_build)*1e-6
            self._ds_settings += (ds_settings - ds_attrib)*1e-6
            self._total += (ds_settings - start)*1e-6
        return ds

    def evaluate(
        self,
        time: datetime,
        lat: Numeric, lon: Numeric, alt: np.ndarray,
        settings: Optional[Settings | ComputedSettings] = None,
        *,
        tzaware: bool = False
    ) -> Tuple[ComputedSettings, Dataset]:
        """Evaluate the IRI-2020 model.

        Args:
            time (datetime): Datetime object. 
            lat (Numeric): Geographic latitude.
            lon (Numeric): Geographic longitude.
            alt (np.ndarray): Altitude in kilometers.
            settings (Optional[Settings  |  ComputedSettings], optional): Settings to use. Defaults to None.
            tzaware (bool, optional): If time is time zone aware. If true, `time` is recast to 'UTC' using `time.astimezone(pytz.utc)`. Defaults to False.
        Returns:
            Tuple[ComputedSettings, Dataset]: Computed settings and dataset. Passing in Settings will return ComputedSettings. For subsequent calls, pass in the returned ComputedSettings to avoid recomputation.
        """
        if tzaware:
            time = time.astimezone(UTC)
        year, idate, utsec = iridate(time)
        lon = float(lon) % 360  # ensure lon is in 0-360 range
        (settings, ds) = self.lowlevel(
            lat, lon, alt, year, idate, utsec, settings)
        ds.attrs['date'] = time.isoformat()
        return (settings, ds)

    def lowlevel(self, lat: Numeric, lon: Numeric, alt: np.ndarray, year: int, day: int, ut: Numeric, settings: Optional[Settings | ComputedSettings] = None) -> Tuple[ComputedSettings, Dataset]:
        """Low level call to evaluate IRI-2020 model.
        Bypasses date and time calculations.

        Args:
            lat (Numeric): Geographic latitude
            lon (Numeric): Geographic longitude
            alt (np.ndarray): Altitude in kilometers
            year (int): Year (four digits)
            day (int): Day of the year (1-365 or 366)
            ut (Numeric): Universal time in seconds
            settings (Optional[Settings  |  ComputedSettings], optional): Settings to use. Defaults to None.

        Raises:
            TypeError: If settings is not of type Settings or ComputedSettings.

        Returns:
            Tuple[ComputedSettings, Dataset]: Computed settings and dataset. Passing in Settings will return ComputedSettings. For subsequent calls, pass in the returned ComputedSettings to avoid recomputation.
        """
        if settings is None:
            settings = self.settings
        if isinstance(settings, Settings):
            self.settings = settings
            settings = ComputedSettings.from_settings(settings)
        if not isinstance(settings, ComputedSettings):
            raise TypeError(
                "settings must be of type Settings or ComputedSettings")
        ds = self._iricall(lat, lon, alt, year, day, ut, settings)
        return settings, ds


# %%
def test():
    import matplotlib.pyplot as plt
    from pprint import pprint
    from iri20py import Iri2020, alt_grid
    from iri20py.settings import Settings
    settings = Settings(logfile=Path('iri_log.txt'))
    iri = Iri2020()
    date = datetime(2022, 3, 21, 12, 0, 0, tzinfo=UTC)
    set, ds1 = iri.evaluate(
        date,
        40.0, 105.0,
        alt_grid(),
        settings
    )
    # iri.benchmark = True
    # for idx in range(int(1e4)):
    #     if idx > 0 and idx % 1000 == 0:
    #         print(f"{idx}/{int(1e4)} calculations done")
    #     _ = iri.calculate(
    #         date,
    #         40.0, 105.0,
    #         alt_grid(),
    #         set
    #     )
    # pprint(iri.get_benchmark())
    pprint(ds1)
    _, ds2 = iri.evaluate(
        datetime(2022, 3, 21, 0, 0, 0, tzinfo=UTC),
        40.0, 105.0,
        alt_grid(),
        set
    )
    fig, ax = plt.subplots(1, 2, sharey=True)
    ds1.Ne.plot(ax=ax[0], y='alt_km')
    ds2.Ne.plot(ax=ax[1], y='alt_km')
    ax[0].set_xscale('log')
    ax[1].set_xscale('log')
    ax[0].set_ylabel('Altitude (km)')
    ax[0].set_title('Ne at 12:00 UTC')
    ax[1].set_title('Ne at 00:00 UTC')
    plt.show()
    # ds1.to_netcdf('iri_output.nc')


# %%
