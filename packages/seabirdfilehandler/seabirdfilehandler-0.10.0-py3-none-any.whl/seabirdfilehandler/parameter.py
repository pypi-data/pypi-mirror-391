from __future__ import annotations

import logging
import re
from collections import UserDict
from typing import Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class Parameters(UserDict):
    """
    A collection of all the parameters in a CnvFile.

    Allows for a much cleaner handling of parameter data and their metadata.
    Will be heavily expanded.

    Parameters
    ----------
    data: list
        The raw data as extraced by DataFile
    metadata: list
        The raw metadata as extraced by DataFile

    Returns
    -------

    """

    def __init__(
        self,
        data: list,
        metadata: list,
        only_header: bool = False,
    ):
        self.data = {}
        self.differentiate_table_description(metadata)
        parsed_metadata, self.duplicate_columns = self.reading_data_header(
            metadata
        )
        try:
            self.sample_rate = self.data_table_misc["interval"].split(":")
        except Exception:
            self.sample_rate = 1 / 24
        if not only_header:
            self.full_data_array = self.create_full_ndarray(data)
            self.create_parameter_instances(
                self.full_data_array, parsed_metadata
            )

    def get_full_data_array(self) -> np.ndarray:
        return np.array([parameter.data for parameter in self.data.values()]).T

    def get_names(self) -> list[str]:
        return [parameter.name for parameter in self.data.values()]

    def get_metadata(self) -> dict[str, dict]:
        return {
            parameter.name: parameter.metadata
            for parameter in self.data.values()
        }

    def get_parameter_list(self) -> list[Parameter]:
        """ """
        return list(self.data.values())

    def create_full_ndarray(self, data_table: list = []) -> np.ndarray:
        """
        Builds a numpy array representing the data table in a cnv file.

        Parameters
        ----------
        data_table: list :
            The data to work with
             (Default value = [])

        Returns
        -------
        A numpy array of the same shape as the cnv files data table

        """
        n = 11
        row_list = []
        for line in data_table:
            row_list.append(
                [
                    line[i : i + n].split()[0]
                    for i in range(0, len(line) - n, n)
                ]
            )
        return np.array(row_list, dtype=float)

    def sort_parameters(
        self,
        top: list = [
            "depSM",
            "prDM",
            "t090C",
            "t190C",
            "sal00",
            "sal11",
            "sbox0Mm/Kg",
            "sbox1Mm/Kg",
            "flECO-AFL",
            "turbWETntu0",
            "par",
            "spar",
        ],
        bottom: list = [
            "gsw_densityA0",
            "gsw_densityA1",
            "gsw_saA0",
            "gsw_saA1",
            "gsw_ctA0",
            "gsw_ctA1",
            "sbeox0ML/L",
            "sbeox1ML/L",
            "c0mS/cm",
            "c1mS/cm",
            "latitude",
            "longitude",
            "flag",
        ],
    ) -> dict:
        # ensure parameters at the top
        new_data = {}
        for shortname in top:
            for param in self.data.values():
                if shortname == param.name:
                    new_data[shortname] = param

        # ensure parameters at the bottom
        bottom_data = {}
        for shortname in bottom:
            for param in self.data.values():
                if shortname == param.name:
                    bottom_data[shortname] = param

        for param in self.data.values():
            if param.name not in [*top, *bottom]:
                new_data[param.name] = param

        self.data = {**new_data, **bottom_data}
        return new_data

    def create_parameter_instances(
        self,
        array_data: np.ndarray,
        metadata: dict[str, dict],
    ) -> dict[str, Parameter]:
        """
        Differentiates the individual parameter columns into separate parameter
        instances.

        Parameters
        ----------
        metadata: dict[str, dict] :
            The structured metadata dictionary
             (Default value = {})

        Returns
        -------
        A dictionary of parameter instances

        """
        parameter_dict = {}
        list_of_metadata_shortnames = list(metadata.keys())
        # if column number and metadata number is different, we are propably
        # working with duplicate_columns and will drop the duplicates
        if array_data.shape[1] != len(list_of_metadata_shortnames):
            array_data = np.delete(array_data, self.duplicate_columns, 1)
            assert array_data.shape[1] == len(list_of_metadata_shortnames)
            # rewrite the column number in the metadata header
            self.data_table_stats["nquan"] = str(
                int(self.data_table_stats["nquan"])
                - len(self.duplicate_columns)
            )
        for i in range(array_data.shape[1]):
            key = list_of_metadata_shortnames[i]
            parameter_dict[key] = self.create_parameter(
                data=array_data[:, i],
                metadata=metadata[key],
                name=key,
            )
        return parameter_dict

    def _form_data_table_info(self) -> list:
        """Recreates the data table descriptions, like column names and spans
        from the structured dictionaries these values were stored in."""
        new_table_info = []
        # 'data table stats'
        data_array = self.get_full_data_array()
        new_table_info.append(f"nquan = {data_array.shape[1]}\r\n")
        new_table_info.append(f"nvalues = {data_array.shape[0]}\r\n")
        units = (
            self.data_table_stats["units"]
            if "units" in list(self.data_table_stats.keys())
            else "specified"
        )
        new_table_info.append(f"units = {units}\r\n")
        # 'data tables names'
        for index, metadata in enumerate(self.get_metadata().values()):
            new_table_info.append(
                f"name {index} = {metadata['shortname']}: {metadata['longinfo']}\r\n"
            )
        # 'data table spans'
        for index, (minimum, maximum) in enumerate(self.get_spans()):
            new_table_info.append(
                f"span {index} = {minimum:2.4f}, {maximum:2.4f}\r\n"
            )
        # 'data table misc'
        for key, value in self.data_table_misc.items():
            new_table_info.append(f"{key} = {value}\r\n")
        return new_table_info

    def differentiate_table_description(self, metadata: list):
        """
        The original method that structures data table metadata.

        Needs heavy refactoring.
        """
        past_spans = False
        pre = []
        column_names = []
        column_value_spans = []
        post = []
        for line in metadata:
            if line.startswith("name"):
                column_names.append(line.split("=", 1)[1].strip())
            elif line.startswith("span"):
                past_spans = True
                column_value_spans.append(line.split("=", 1)[1].strip())
            else:
                if not past_spans:
                    pre.append(line)
                else:
                    post.append(line)
        assert len(column_names) == len(column_value_spans)
        self.data_table_stats = {
            line.split("=")[0].strip(): line.split("=", 1)[1].strip()
            for line in pre
        }
        self.data_table_names_and_spans = [
            (name, span)
            for name, span in zip(column_names, column_value_spans)
        ]
        self.data_table_misc = {
            line.split("=")[0].strip(): line.split("=", 1)[1].strip()
            for line in post
        }

    def add_parameter(self, parameter: Parameter, position: str = ""):
        """
        Adds one parameter instance to the collection.

        Parameters
        ----------
        parameter: Parameter :
            The new parameter

        """
        # add to parameter dict at given position
        if position:
            new_dict = {}
            for key, value in self.data.items():
                new_dict[key] = value
                if key == position:
                    new_dict[parameter.name] = parameter
            self.data = new_dict

        else:
            self.data[parameter.name] = parameter

    def create_parameter(
        self,
        data: np.ndarray | int | float | str | None,
        metadata: dict = {},
        name: str = "",
        position: str = "",
    ) -> Parameter:
        """
        Creates a new parameter instance with the given data and metadata.

        The input data is either a numpy array or a single value. The single
        value will be broadcasted to the shape of the data table. A use-case
        would be the addition of an 'event' or 'cast' column.

        Parameters
        ----------
        data: np.ndarray | int | float | str :
            Data to use or expand

        metadata: dict :
            Metadata for the new parameter
             (Default value = {})
        name: str :
            Name to use for missing metadata values
             (Default value = "")

        Returns
        -------
        The new parameter instance

        """
        if len(metadata) < 5:
            if len(name) > 0:
                metadata = self.add_default_metadata(
                    name=name, metadata=metadata
                )
            else:
                raise ValueError(
                    "Please specify either a name or sufficient metadata"
                )
        if not isinstance(data, np.ndarray):
            data = np.full(
                fill_value=data,
                shape=self.get_full_data_array().shape[0],
            )
        parameter = Parameter(data=data, metadata=metadata)
        self.add_parameter(parameter, position)
        return parameter

    def add_default_metadata(
        self,
        name: str,
        metadata: dict = {},
        list_of_keys: list = [
            "shortname",
            "longinfo",
            "name",
            "metainfo",
            "unit",
        ],
    ) -> dict:
        """
        Fills up missing metadata points with a default value.

        Parameters
        ----------
        name: str :
            The value to use as default
        metadata: dict :
            The present metadata
             (Default value = {})
        list_of_keys: list :
             The expected metadata keys

        Returns
        -------
        The full metadata dictionary

        """
        default = {}
        for key in list_of_keys:
            if key not in list(metadata.keys()):
                if key in ["metainfo", "unit"]:
                    default[key] = ""
                default[key] = name
        return {**metadata, **default}

    def update_spans(self):
        """Updates all spans of the parameters."""
        for parameter in self.get_parameter_list():
            parameter.update_span()

    def get_spans(self) -> list[tuple[int, int]]:
        """Returns all span tuples of the parameters."""
        # update spans first
        self.update_spans()
        return [parameter.span for parameter in self.get_parameter_list()]

    def get_pandas_dataframe(self) -> pd.DataFrame:
        """Returns a pandas DataFrame of the current parameter data."""
        data = np.array(
            [parameter.data for parameter in self.get_parameter_list()]
        ).T
        columns = [parameter.name for parameter in self.get_parameter_list()]
        assert data.shape[1] == len(columns)
        df = pd.DataFrame(data=data, columns=columns)
        for column in df.columns:
            try:
                df[column].astype("float64")
            except (TypeError, ValueError):
                df[columns].astype("str")
        return df

    def with_name_type(self, name_type: str = "shortname"):
        """
        Uses the given name_type as column descriptors.

        Parameters
        ----------
        name_type: str :
            The metadata name to use
             (Default value = "shortname")

        """
        for parameter in self.get_parameter_list():
            parameter.use_name(name_type)

    def reading_data_header(
        self, header_info: list = []
    ) -> Tuple[dict[str, dict], list[int]]:
        """Reads the tables header data from the header.

        Parameters
        ----------
        header_info : list:
            the header values from the file
        header_info: list :
             (Default value = [])

        Returns
        -------


        """
        table_header = {}
        duplicate_columns = []
        for line in header_info:
            if line.startswith("name"):
                header_meta_info = {}
                # get basic shortname and the full, non-differentiated info
                shortname = longinfo = line_info = line.split("=", 1)[
                    1
                ].strip()
                try:
                    shortname, longinfo = line_info.split(":", 1)
                except IndexError:
                    pass
                finally:
                    shortname = shortname.strip()
                    if shortname in list(table_header.keys()):
                        try:
                            duplicate_columns.append(
                                int(line.split("=", 1)[0].strip().split()[1])
                            )
                        except IndexError as error:
                            logger.error(
                                f"Could not resolve duplicate column: {
                                    shortname
                                }, {error}"
                            )
                    else:
                        header_meta_info["shortname"] = shortname
                        header_meta_info["longinfo"] = longinfo.strip()
                        metainfo = self._extract_data_header_meta_info(
                            longinfo.strip()
                        )
                        header_meta_info = {**header_meta_info, **metainfo}
                        table_header[shortname.strip()] = header_meta_info
        return table_header, duplicate_columns

    def _extract_data_header_meta_info(self, line: str) -> dict:
        """Extracts the individual information bits inside of the header lines

        Parameters
        ----------
        line : str:
            one header line, trimmed by the 'name =' prefix and the shortname
        line: str :


        Returns
        -------


        """
        regex_string = r"(?:(?P<name0>.+),\s(?P<metainfo0>.+)\s\[(?P<unit0>.+)\]|(?P<name2>.+)\s\[(?P<unit2>.+)\]|(?P<name3>.+),\s(?P<metainfo2>.[^\s]+)|(?P<name4>.+))"
        regex_check = re.search(regex_string, line, flags=re.IGNORECASE)
        if regex_check:
            regex_info = dict(regex_check.groupdict())
            regex_info = {
                key[:-1]: value
                for key, value in regex_info.items()
                if value is not None
            }
            if len(regex_info) > 2:
                # check for second sensors and adjust their names
                if regex_info["metainfo"][-1] == "2":
                    regex_info["name"] = regex_info["name"] + " 2"
                    regex_info["metainfo"] = regex_info["metainfo"][:-1]
                    if len(regex_info["metainfo"]) == 0:
                        regex_info.pop("metainfo")
            if regex_info["name"] == "flag":
                regex_info["metainfo"] = regex_info["name"]
                regex_info["unit"] = regex_info["name"]
            return regex_info
        return {}


class Parameter:
    """A representation of one parameter in a cnv file.

    Consists of the values of the parameter as well as the metadata.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(
        self,
        data: np.ndarray,
        metadata: dict,
    ) -> None:
        self.data = data
        self.metadata = metadata
        self.name = metadata["shortname"]
        self.param = re.split(r"[,\s]", metadata["name"])[0]
        self.sensor_number = 2 if metadata["name"][-1] == "2" else 1
        self.unit = metadata["unit"]
        self.type = "data" if self.data.dtype in ["float", "int"] else "meta"
        self.parse_to_float()
        self.update_span()

    def __str__(self) -> str:
        return str(self.metadata["longinfo"])

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.data == other.data

    def get_pandas_series(self) -> pd.Series:
        """Returns a pandas Series of the current parameter data."""
        return pd.Series(data=self.data, name=self.name)

    def use_name(self, name_type: str = "shortname"):
        """
        Uses the given name as parameter descriptor.

        Parameters
        ----------
        name_type: str :
            The metadata name to use
             (Default value = "shortname")

        """
        try:
            self.name = self.metadata[name_type]
        except KeyError:
            return

    def parse_to_float(self):
        """
        Tries to parse the data array type to float.
        """
        try:
            self.data = self.data.astype("float64")
        except ValueError:
            pass

    def update_span(self):
        """
        Updates the data span.

        Uses the first value if dtype is not numeric.
        """
        if self.data.dtype in ["float64", "int"]:
            self.span = (self.data.min(), self.data.max())
        else:
            self.span = (self.data[0], self.data[0])
