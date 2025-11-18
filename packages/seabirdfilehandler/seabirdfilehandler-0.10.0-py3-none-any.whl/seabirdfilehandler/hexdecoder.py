import logging
import sys
from math import floor
from pathlib import Path

import gsw
import numpy as np
import pandas as pd
from seabirdscientific import cal_coefficients as sbs_cal
from seabirdscientific import conversion as sbs_con
from seabirdscientific import instrument_data as sbs_id

from seabirdfilehandler.ctddata import CTDData
from seabirdfilehandler.hexfile import HexFile
from seabirdfilehandler.parameter import Parameters
from seabirdfilehandler.xmlfiles import XMLCONFile

logger = logging.getLogger(__name__)


class ParameterMapping:
    def __init__(
        self,
        xmlcon_part: dict,
        raw_data: pd.DataFrame,
        parameters: Parameters,
        voltage_sensors_start: int = 6,
    ) -> None:
        self.source = xmlcon_part
        self.name = xmlcon_part["SensorName"]
        self.raw_data = raw_data
        self.voltage_sensors_start = voltage_sensors_start
        if self.name[-1] == "2":
            self.name = self.name[:-1]
            self.second_sensor = True
        else:
            self.second_sensor = False
        self.parameters = parameters
        self.param_types = [p.param for p in parameters.get_parameter_list()]
        self.sample_interval = 1 / 24
        self.sensor_data = self.locate_sensor_data(raw_data)
        if isinstance(self.sensor_data, np.ndarray):
            self.coefficients = self.extract_coefficients(xmlcon_part)
            self.metadata = self.map_metadata()

    def extract_coefficients(self, source: dict):
        if self.name == "Temperature":
            if source["UseG_J"] == "1":
                self.convert_freq_temperature()
            else:
                self.convert_temperature()

        elif self.name == "Conductivity":
            if source["Coefficients"][0]["@equation"] == "1":
                logger.error(
                    "Unsupported Conductivity coefficients given, please use the new coefficients."
                )
            self.convert_conductivity()
        elif self.name == "Pressure":
            self.convert_pressure()
        elif self.name == "Oxygen":
            if source["CalibrationCoefficients"][0]["@equation"] == "1":
                logger.error(
                    "Unsupported Oxygen coefficients given, please use the new coefficients."
                )
            self.convert_oxygen()
        elif self.name == "PAR_BiosphericalLicorChelsea":
            self.coef = sbs_cal.PARCoefficients
            self.coef.im = float(source["M"])
            self.coef.a0 = float(source["CalibrationConstant"])
            self.coef.a1 = float(source["Offset"])
            self.coef.multiplier = float(source["Multiplier"])
            # TODO: get Sea-Bird function to work
            # self.converted_data = sbs_con.convert_par_logarithmic(
            #     volts=self.sensor_data,
            #     coefs=self.coef,
            # )
            self.converted_data = (
                self.coef.multiplier
                * (
                    (10**9 * 10 ** (self.sensor_data / self.coef.im))
                    / self.coef.a0
                )
                + self.coef.a1
            )

        elif self.name == "Altimeter":
            self.coef = sbs_cal.AltimeterCoefficients
            self.coef.slope = float(source["ScaleFactor"])
            self.coef.offset = float(source["Offset"])
            self.converted_data = sbs_con.convert_altimeter(
                volts=self.sensor_data,
                coefs=self.coef,
            )
        elif self.name in ["FluoroWetlabECO_AFL_FL", "FluoroWetlabCDOM"]:
            self.coef = sbs_cal.ECOCoefficients
            self.coef.slope = float(source["ScaleFactor"])
            self.coef.offset = float(source["Vblank"])
            self.converted_data = sbs_con.convert_eco(
                raw=self.sensor_data,
                coefs=self.coef,
            )
        elif self.name == "TurbidityMeter":
            self.coef = sbs_cal.ECOCoefficients
            self.coef.slope = float(source["ScaleFactor"])
            self.coef.offset = float(source["DarkVoltage"])
            self.converted_data = sbs_con.convert_eco(
                raw=self.sensor_data,
                coefs=self.coef,
            )
        elif self.name == "SPAR":
            self.coef = sbs_cal.SPARCoefficients
            self.coef.conversion_factor = float(source["ConversionFactor"])
            self.converted_data = sbs_con.convert_spar_biospherical(
                volts=self.sensor_data,
                coefs=self.coef,
            )

        else:
            logger.warning(
                f"Could not find convertion information for {self.name}"
            )

    def locate_sensor_data(self, raw_data: dict) -> np.ndarray | None:
        if self.name in ["Temperature", "Conductivity"]:
            name = self.name.lower()
            if self.second_sensor:
                name = "secondary " + name

        elif self.name == "Pressure":
            name = "digiquartz pressure"
        elif self.name == "SPAR":
            name = "surface par"
        else:
            sensor_index = int(self.source["Channel"])
            name = f"volt {sensor_index - self.voltage_sensors_start}"

        try:
            sensor_data = raw_data[name].values
        except Exception as error:
            logger.error(
                f"Could not locate sensor data for {self.name}: {error}"
            )
            sensor_data = None
        return sensor_data

    def create_parameter(self, data, metadata: dict = {}, name: str = ""):
        try:
            self.parameters.create_parameter(
                data=data,
                metadata=metadata,
                name=name,
            )
        except AttributeError:
            logger.error(f"{name} had no succesfull mapping.")

    def convert_freq_temperature(self):
        self.coef = sbs_cal.TemperatureFrequencyCoefficients
        for param in ["G", "H", "I", "J", "F0"]:
            setattr(self.coef, param.lower(), float(self.source[param]))
        self.converted_data = sbs_con.convert_temperature_frequency(
            frequency=self.sensor_data,
            coefs=self.coef,
            standard="ITS90",
            units="C",
        )

    def convert_temperature(self):
        self.coef = sbs_cal.TemperatureCoefficients
        for index, param in enumerate(["A", "B", "C", "D"]):
            setattr(self.coef, f"a{index}", float(self.source[param]))
        self.converted_data = sbs_con.convert_temperature(
            frequency=self.sensor_data,
            coefs=self.coef,
            standard="ITS90",
            units="C",
        )

    def convert_pressure(self):
        self.coef = sbs_cal.PressureDigiquartzCoefficients
        for param in self.source:
            if param in [
                "Channel",
                "SensorName",
                "@SensorID",
                "SerialNumber",
                "CalibrationDate",
                "Slope",
                "Offset",
            ]:
                continue
            setattr(
                self.coef,
                param if param.startswith("A") else param.lower(),
                float(self.source[param]),
            )
        self.converted_data = sbs_con.convert_pressure_digiquartz(
            pressure_count=self.sensor_data,
            compensation_voltage=self.raw_data["temperature compensation"]
            .astype(float)
            .values,
            coefs=self.coef,
            units="dbar",
            sample_interval=self.sample_interval,
        )
        # apply correction on data
        self.converted_data = self.converted_data * float(
            self.source["Slope"]
        ) + float(self.source["Offset"])

    def convert_conductivity(self):
        self.coef = sbs_cal.ConductivityCoefficients
        for param in ["G", "H", "I", "J", "CPcor", "CTcor", "WBOTC"]:
            setattr(
                self.coef,
                param.lower(),
                float(self.source["Coefficients"][1][param]),
            )
        if "Pressure" not in self.param_types:
            return
        p_values = self.parameters["prDM"].data
        if "Temperature" in self.param_types:
            if self.second_sensor:
                t_values = self.parameters["t190C"].data
            else:
                t_values = self.parameters["t090C"].data
        else:
            return

        self.converted_data = sbs_con.convert_conductivity(
            conductivity_count=self.sensor_data,
            temperature=t_values,
            pressure=p_values,
            coefs=self.coef,
            scalar=1,
        )
        self.convert_salinity(self.converted_data, t_values, p_values)

    def convert_salinity(
        self,
        conductivity: np.ndarray,
        t_values: np.ndarray,
        p_values: np.ndarray,
    ):
        # TODO: allow selection of baltic salinity conversion here
        converted_data = gsw.SP_from_C(
            C=conductivity,
            t=t_values,
            p=p_values,
        )
        self.create_parameter(converted_data, self.map_metadata("Salinity"))

    def convert_sbe43_oxygen(
        self,
        voltage: np.ndarray,
        temperature: np.ndarray,
        pressure: np.ndarray,
        salinity: np.ndarray,
        coefs: sbs_cal.Oxygen43Coefficients,
        apply_tau_correction: bool = False,
        apply_hysteresis_correction: bool = False,
        window_size: float = 1,
        sample_interval: float = 1,
    ):
        """Overwrite of Sea-Birds super slow function."""
        # start with all 0 for the dvdt
        dvdt_values = np.zeros(len(voltage))
        if apply_tau_correction:
            # Calculates how many scans to have on either side of our median
            # point, accounting for going out of index bounds
            scans_per_side = floor(window_size / 2 / sample_interval)
            for i in range(scans_per_side, len(voltage) - scans_per_side):
                ox_subset = voltage[
                    i - scans_per_side : i + scans_per_side + 1
                ]

                time_subset = np.arange(
                    0,
                    len(ox_subset) * sample_interval,
                    sample_interval,
                    dtype=float,
                )

                def manual_linregress(x, y):
                    x_mean, y_mean = np.mean(x), np.mean(y)
                    cov = np.sum((x - x_mean) * (y - y_mean))
                    var = np.sum((x - x_mean) ** 2)
                    slope = cov / var
                    intercept = y_mean - slope * x_mean
                    return slope, intercept

                slope, _ = manual_linregress(time_subset, ox_subset)

                dvdt_values[i] = slope

        correct_ox_voltages = voltage.copy()
        if apply_hysteresis_correction:
            # Hysteresis starts at 1 because 0 can't be corrected
            for i in range(1, len(correct_ox_voltages)):
                # All Equation info from APPLICATION NOTE NO. 64-3
                d = 1 + coefs.h1 * (np.exp(pressure[i] / coefs.h2) - 1)
                c = np.exp(-1 * sample_interval / coefs.h3)
                ox_volts = correct_ox_voltages[i] + coefs.v_offset

                prev_ox_volts_new = correct_ox_voltages[i - 1] + coefs.v_offset
                ox_volts_new = (
                    (ox_volts + prev_ox_volts_new * c * d)
                    - (prev_ox_volts_new * c)
                ) / d
                ox_volts_final = ox_volts_new - coefs.v_offset
                correct_ox_voltages[i] = ox_volts_final

        oxygen = sbs_con._convert_sbe43_oxygen(
            correct_ox_voltages,
            temperature,
            pressure,
            salinity,
            coefs,
            dvdt_values,
        )
        return oxygen

    def convert_oxygen(self):
        self.coef = sbs_cal.Oxygen43Coefficients
        for param, value in self.source["CalibrationCoefficients"][1].items():
            param = f"v_{param}" if param == "offset" else param
            param = "tau_20" if param == "Tau20" else param
            setattr(self.coef, param.lower(), float(value))
        if "Pressure" not in self.param_types:
            return
        p_values = self.parameters["prDM"].data
        if "Temperature" in self.param_types:
            if self.second_sensor:
                t_values = self.parameters["t190C"].data
            else:
                t_values = self.parameters["t090C"].data
        else:
            return
        if "Salinity" in self.param_types:
            if self.second_sensor:
                s_values = self.parameters["sal00"].data
            else:
                s_values = self.parameters["sal11"].data
        else:
            return
        converted_data = self.convert_sbe43_oxygen(
            voltage=self.sensor_data,
            temperature=t_values,
            pressure=p_values,
            salinity=s_values,
            coefs=self.coef,
            apply_tau_correction=True,
            apply_hysteresis_correction=True,
            window_size=2,
            sample_interval=self.sample_interval,
        )
        self.create_parameter(
            converted_data,
            self.map_metadata("Oxygen mlL"),
        )
        # TODO: flexibilize this
        # give out umol/kg
        absolute_salinity = gsw.SA_from_SP(
            SP=s_values,
            p=p_values,
            lon=self.raw_data["NMEA Latitude"],
            lat=self.raw_data["NMEA Latitude"],
        )
        self.create_parameter(
            absolute_salinity,
            self.map_metadata("Absolute Salinity"),
        )
        conservative_temperature = gsw.conversions.CT_from_t(
            SA=absolute_salinity,
            t=t_values,
            p=p_values,
        )
        self.create_parameter(
            conservative_temperature,
            self.map_metadata("Conservative Temperature"),
        )
        # TODO: flexibile sigma selection
        potential_density = gsw.density.sigma0(
            SA=absolute_salinity,
            CT=conservative_temperature,
        )
        self.create_parameter(potential_density, self.map_metadata("Density"))
        self.converted_data = sbs_con.convert_oxygen_to_umol_per_kg(
            ox_values=converted_data,
            potential_density=potential_density,
        )

    def map_metadata(self, name: str = "") -> dict:
        name = name if name else self.name
        if self.second_sensor:
            name = name + " 2"

        mapper = {
            "Pressure": {
                "shortname": "prDM",
                "longinfo": "Pressure, Digiquartz [db]",
                "name": "Pressure",
                "metainfo": "Digiquartz",
                "unit": "db",
            },
            "Temperature": {
                "shortname": "t090C",
                "longinfo": "Temperature [ITS-90, deg C]",
                "name": "Temperature",
                "unit": "ITS-90, deg C",
                "metainfo": "t090C",
            },
            "Temperature 2": {
                "shortname": "t190C",
                "longinfo": "Temperature, 2 [ITS-90, deg C]",
                "name": "Temperature 2",
                "unit": "ITS-90, deg C",
                "metainfo": "t190C",
            },
            "Conductivity": {
                "shortname": "c0mS/cm",
                "longinfo": "Conductivity [mS/cm]",
                "name": "Conductivity",
                "unit": "mS/cm",
                "metainfo": "c0mS/cm",
            },
            "Conductivity 2": {
                "shortname": "c1mS/cm",
                "longinfo": "Conductivity, 2 [mS/cm]",
                "name": "Conductivity 2",
                "unit": "mS/cm",
                "metainfo": "c1mS/cm",
            },
            "Salinity": {
                "shortname": "sal00",
                "longinfo": "Salinity, Practical [PSU]",
                "name": "Salinity",
                "metainfo": "Practical",
                "unit": "PSU",
            },
            "Salinity 2": {
                "shortname": "sal11",
                "longinfo": "Salinity, Practical, 2 [PSU]",
                "name": "Salinity, Practical 2",
                "unit": "PSU",
                "metainfo": "sal11",
            },
            "Oxygen": {
                "shortname": "sbox0Mm/Kg",
                "longinfo": "Oxygen, SBE 43 [umol/kg]",
                "name": "Oxygen",
                "metainfo": "SBE 43",
                "unit": "umol/kg",
            },
            "Oxygen 2": {
                "shortname": "sbox1Mm/Kg",
                "longinfo": "Oxygen, SBE 43, 2 [umol/kg]",
                "name": "Oxygen, SBE 43 2",
                "unit": "umol/kg",
                "metainfo": "sbox1Mm/Kg",
            },
            "Oxygen mlL": {
                "shortname": "sbeox0ML/L",
                "longinfo": "Oxygen, SBE 43 [ml/l]",
                "name": "Oxygen, SBE 43",
                "unit": "ml/l",
                "metainfo": "sbeox0ML/L",
            },
            "Oxygen mlL 2": {
                "shortname": "sbeox1ML/L",
                "longinfo": "Oxygen, SBE 43, 2 [ml/l]",
                "name": "Oxygen, SBE 43 2",
                "unit": "ml/l",
                "metainfo": "sbeox1ML/L",
            },
            "Altimeter": {
                "shortname": "altM",
                "longinfo": "Altimeter [m]",
                "name": "Altimeter",
                "unit": "m",
                "metainfo": "altM",
            },
            "FluoroWetlabECO_AFL_FL": {
                "shortname": "flECO-AFL",
                "longinfo": "Fluorescence, WET Labs ECO-AFL/FL [mg/m^3]",
                "name": "Fluorescence",
                "metainfo": "WET Labs ECO-AFL/FL",
                "unit": "mg/m^3",
            },
            "TurbidityMeter": {
                "shortname": "turbWETntu0",
                "longinfo": "Turbidity, WET Labs ECO [NTU]",
                "name": "Turbidity",
                "metainfo": "WET Labs ECO",
                "unit": "NTU",
            },
            "PAR_BiosphericalLicorChelsea": {
                "shortname": "par",
                "longinfo": "PAR/Irradiance, Biospherical/Licor",
                "name": "PAR/Irradiance",
                "metainfo": "Biospherical/Licor",
                "unit": "par",
            },
            "SPAR": {
                "shortname": "spar",
                "longinfo": "SPAR, Biospherical/Licor",
                "name": "SPAR",
                "metainfo": "Biospherical/Licor",
                "unit": "spar",
            },
            "Density": {
                "shortname": "gsw_densityA0",
                "longinfo": "density, TEOS-10 [density, kg/m^3]",
                "name": "density",
                "unit": "kg/m^3",
                "metainfo": "TEOS-10",
            },
            "Density 2": {
                "shortname": "gsw_densityA1",
                "longinfo": "density, TEOS-10, 2 [density, kg/m^3]",
                "name": "density 2",
                "unit": "kg/m^3",
                "metainfo": "TEOS-10",
            },
            "Conservative Temperature": {
                "shortname": "gsw_ctA0",
                "longinfo": "Conservative Temperature [ITS-90, deg C]",
                "name": "Conservative Temperature",
                "unit": "ITS-90, deg C",
                "metainfo": "TEOS-10",
            },
            "Conservative Temperature 2": {
                "shortname": "gsw_ctA1",
                "longinfo": "Conservative Temperature, 2 [ITS-90, deg C]",
                "name": "Conservative Temperature 2",
                "unit": "ITS-90, deg C",
                "metainfo": "TEOS-10",
            },
            "Absolute Salinity": {
                "shortname": "gsw_saA0",
                "longinfo": "Absolute Salinity [g/kg]",
                "name": "Absolute Salinity",
                "unit": "g/kg",
                "metainfo": "TEOS-10",
            },
            "Absolute Salinity 2": {
                "shortname": "gsw_saA1",
                "longinfo": "Absolute Salinity, 2 [g/kg]",
                "name": "Absolute Salinity 2",
                "unit": "g/kg",
                "metainfo": "TEOS-10",
            },
        }
        try:
            return mapper[name]
        except KeyError:
            return {}


def hex_reading(hex: HexFile) -> pd.DataFrame:
    instrument_info = hex.xmlcon["SBE_InstrumentConfiguration"]["Instrument"]
    instrument_name = instrument_info["Name"]
    # TODO: extend this
    device_mapping = {"SBE 911plus": sbs_id.InstrumentType.SBE911Plus}
    try:
        for device in device_mapping.keys():
            if instrument_name.startswith(device):
                instrument_type = device_mapping[device]
        assert instrument_type

    except Exception:
        sys.exit(f"Unknown instrument: {instrument_name}. Aborting.")
    enabled_sensors = []

    sensor_info = hex.xmlcon.sensor_info
    sensor_names = [s["SensorName"] for s in sensor_info]
    if "Temperature" in sensor_names:
        enabled_sensors.append(sbs_id.Sensors.Temperature)
    if "Conductivity" in sensor_names:
        enabled_sensors.append(sbs_id.Sensors.Conductivity)
    if "Pressure" in sensor_names:
        enabled_sensors.append(sbs_id.Sensors.Pressure)
    if "Temperature2" in sensor_names:
        enabled_sensors.append(sbs_id.Sensors.SecondaryTemperature)
    if "Conductivity2" in sensor_names:
        enabled_sensors.append(sbs_id.Sensors.SecondaryConductivity)

    voltage_sensors = [
        sbs_id.Sensors.ExtVolt0,
        sbs_id.Sensors.ExtVolt1,
        sbs_id.Sensors.ExtVolt2,
        sbs_id.Sensors.ExtVolt3,
        sbs_id.Sensors.ExtVolt4,
        sbs_id.Sensors.ExtVolt5,
        sbs_id.Sensors.ExtVolt6,
        sbs_id.Sensors.ExtVolt7,
    ]
    i = 0
    for sensor in sensor_info:
        if sensor["SensorName"].startswith(
            ("Temperature", "Conductivity", "Pressure", "SPAR")
        ):
            continue
        enabled_sensors.append(voltage_sensors[i])
        i += 1

    if instrument_info["SurfaceParVoltageAdded"] == "1":
        enabled_sensors.append(sbs_id.Sensors.SPAR)
    if instrument_info["NmeaPositionDataAdded"] == "1":
        enabled_sensors.append(sbs_id.Sensors.nmeaLocation)
    if instrument_info["NmeaDepthDataAdded"] == "1":
        enabled_sensors.append(sbs_id.Sensors.nmeaDepth)
    if instrument_info["NmeaTimeAdded"] == "1":
        enabled_sensors.append(sbs_id.Sensors.nmeaTime)
    else:
        enabled_sensors.append(sbs_id.Sensors.SystemTime)

    # use own function to read hex file
    with open(hex.path_to_file, "r") as f:
        result = f.readlines()

    array_data = []
    for line in result:
        if line.startswith("*"):
            continue
        hex_data = sbs_id.read_hex(
            instrument_type,
            line,
            enabled_sensors,
        )
        array_data.append(hex_data)

    data = pd.DataFrame(array_data)

    return data


def sorting_parameters(
    sensor_info: list,
    rule: list = [
        "Pressure",
        "Temperature",
        "Temperature2",
        "Conductivity",
        "Conductivity2",
    ],
) -> list:
    out_list = []
    for name in rule:
        for param in sensor_info:
            if name == param["SensorName"]:
                out_list.append(param)

    for param in sensor_info:
        if param["SensorName"] not in rule:
            out_list.append(param)

    return out_list


def decode_hex(
    hex: HexFile | Path | str,
    xmlcon: XMLCONFile | Path | str = "",
) -> CTDData:
    # input check
    if not isinstance(hex, HexFile):
        try:
            hex = HexFile(hex)
        except Exception as error:
            message = f"Could not open hex file {hex}: {error}"
            logger.error(message)
            sys.exit(message)

    if xmlcon:
        if not isinstance(xmlcon, XMLCONFile):
            try:
                xmlcon = XMLCONFile(xmlcon)
            except Exception as error:
                message = f"Could not open xmlcon file {xmlcon}: {error}"
                logger.warning(message)
        hex.xmlcon = xmlcon

    if not hex.xmlcon:
        sys.exit(
            f"No corresponding xmlcon for hex file {hex} found. Aborting."
        )
    parameters = Parameters([], [], True)
    raw_data = hex_reading(hex)
    for sensor in sorting_parameters(hex.xmlcon.sensor_info):
        sensor_name = sensor["SensorName"]
        if sensor_name in ["FluoroWetlabCDOM"]:
            continue
        mapping = ParameterMapping(sensor, raw_data, parameters)
        try:
            parameters.create_parameter(
                data=mapping.converted_data,
                metadata=mapping.metadata,
                name=sensor_name,
            )
        except AttributeError:
            logger.error(f"{sensor_name} had no succesfull mapping.")

    # add lat and lon column
    if "NMEA Latitude" in raw_data.columns:
        parameters.create_parameter(
            raw_data["NMEA Latitude"],
            {
                "shortname": "latitude",
                "longinfo": "Latitude [deg]",
                "name": "Latitude",
                "unit": "deg",
                "metainfo": "latitude",
            },
        )
        parameters.create_parameter(
            raw_data["NMEA Longitude"],
            {
                "shortname": "longitude",
                "longinfo": "Longitude [deg]",
                "name": "Longitude",
                "unit": "deg",
                "metainfo": "longitude",
            },
        )

    # add flag column
    data_length = raw_data.shape[0]
    parameters.create_parameter(data=np.zeros(data_length), name="flag")
    # CTDData instance to collect all info
    return CTDData(parameters=parameters, metadata_source=hex)
