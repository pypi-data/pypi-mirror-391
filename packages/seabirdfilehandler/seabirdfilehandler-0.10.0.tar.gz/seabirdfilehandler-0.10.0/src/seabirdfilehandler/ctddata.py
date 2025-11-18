import importlib.metadata
import logging
from datetime import datetime, timezone
from pathlib import Path

import xmltodict

import seabirdfilehandler as fh
from seabirdfilehandler.hexfile import HexFile
from seabirdfilehandler.parameter import Parameters
from seabirdfilehandler.processing_steps import CnvProcessingSteps

logger = logging.getLogger(__name__)


class CTDData:
    def __init__(
        self,
        parameters: Parameters,
        metadata_source: HexFile | fh.CnvFile,
    ) -> None:
        self.parameters = parameters
        if isinstance(metadata_source, HexFile):
            self.sensor_data = self.parse_xmlcon_sensor_data(
                metadata_source.xmlcon.data
            )
            self.processing_steps = CnvProcessingSteps([])
            self.sample_rate = 1 / 24
        else:
            self.sensor_data = [
                f"# {data}" for data in metadata_source.sensor_data
            ]
            self.processing_steps = metadata_source.processing_steps
            self.sample_rate = 1 / 24
        self.sbe9_data = metadata_source.sbe9_data
        self.metadata = metadata_source.metadata
        self.metadata_source = metadata_source

    def array2cnv(self) -> list:
        result = []
        for row in self.parameters.get_full_data_array():
            formatted_row = "".join(f"{elem:2.4f}".rjust(11) for elem in row)
            result.append(formatted_row + "\r\n")
        return result

    def parse_xmlcon_sensor_data(self, sensor_info: dict) -> list:
        sensor_info = sensor_info["SBE_InstrumentConfiguration"]["Instrument"][
            "SensorArray"
        ]
        # rename sensor array size -> count
        sensor_info = {
            "@count" if k == "@Size" else k: v for k, v in sensor_info.items()
        }
        # rename Sensor -> sensor
        sensor_info = {
            "sensor" if k == "Sensor" else k: v for k, v in sensor_info.items()
        }
        for sensor in sensor_info["sensor"]:
            # remove redudant SensorID
            sensor.pop("@SensorID")
            # rename index -> Channel
            sensor["@Channel"] = str(int(sensor.pop("@index")) + 1)

        out_list = [
            f"# {data}\r\n"
            for data in xmltodict.unparse(
                {"Sensors": sensor_info},
                pretty=True,
                indent=2,
            ).split("\n")
        ][1:]
        return out_list

    def get_processing_info(self) -> list:
        if len(self.processing_steps) == 0:
            timestamp = datetime.now(timezone.utc).strftime(
                "%Y.%m.%d %H:%M:%S"
            )
            try:
                version = (
                    f", v{importlib.metadata.version('seabirdfilehandler')}"
                )
            except Exception:
                version = ""
            self.processing_steps.add_info(
                module="hex2py",
                key="metainfo",
                value=f"{timestamp}, seabirdfilehandler python package{version}",
            )

        return self.processing_steps._form_processing_info()

    def create_header(self) -> list:
        """Re-creates the cnv header."""
        data_table_description = self.parameters._form_data_table_info()
        system_utc = self.sbe9_data[-1]
        processing_info = self.get_processing_info()
        header = [
            *[f"* {data.strip()}\r\n" for data in self.sbe9_data[:-1]],
            *[
                f"** {key} = {value}\r\n" if value else f"** {key}\r\n"
                for key, value in self.metadata.items()
            ],
            f"* {system_utc.strip()}\r\n",
            *[f"# {data}" for data in data_table_description],
            *self.extra_data_table_desc(data_table_description, system_utc),
            *self.sensor_data,
            *[f"# {data}" for data in processing_info],
            "*END*\r\n",
        ]
        return header

    def extra_data_table_desc(
        self,
        data_table_description: list,
        system_utc: str,
    ) -> list:
        out_list = []
        if not [
            line
            for line in data_table_description
            if line.startswith("interval")
        ]:
            nmea_time = [
                line for line in self.sbe9_data if line.startswith("NMEA UTC")
            ]
            if system_utc.startswith("System"):
                start_time_string = f"{system_utc.split('=')[1].strip()} [System UTC, first data scan.]"
            elif nmea_time:
                start_time_string = f"{nmea_time[0].split('=')[1].strip()} [NMEA time, first data scan.]"
            else:
                start_time_string = "unknown"

            out_list = [
                "# interval = seconds: 0.0416667\r\n",
                f"# start_time = {start_time_string}\r\n",
                "# bad_flag = -9.990e-29\r\n",
            ]

        return out_list

    def to_cnv(self, file_path: Path | str = "") -> list:
        file_path = (
            Path(file_path) if file_path else self.metadata_source.path_to_file
        )
        self.parameters.sort_parameters()
        data = self.array2cnv()
        header = self.create_header()
        file_data = [*header, *data]
        # writing content out
        try:
            with open(
                file_path.with_suffix(".cnv"), "w", encoding="latin-1"
            ) as file:
                for line in file_data:
                    try:
                        file.write(line)
                    except TypeError:
                        logger.error(line)

        except IOError as error:
            logger.error(f"Could not write cnv file: {error}")

        return file_data
