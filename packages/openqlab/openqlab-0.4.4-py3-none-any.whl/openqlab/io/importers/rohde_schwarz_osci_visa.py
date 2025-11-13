from pathlib import Path
from typing import IO, List, Optional, Union
from warnings import warn

import numpy as np

from openqlab.io.base_importer import VisaImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers import utils


class RohdeSchwarzOsciVisa(VisaImporter):
    NAME = "RohdeSchwarzOsciVisa"
    AUTOIMPORTER = True
    IDN_STARTS_WITH: str = "Rohde&Schwarz,RTB"
    MAX_COLUMNS = 4

    def __init__(
        self,
        data: Union[str, IO, Path],
        inst: None = None,
        stop_scope: bool = True,
        number_of_points: Optional[str] = None,  # "max", "dmax", "default"
    ):
        super().__init__(data, inst=inst)
        self.STOP_SCOPE = stop_scope
        if not number_of_points in [None, "default", "max", "dmax"]:
            raise ValueError("number_of_points must be dmax, max or default.")

        errors = self.query("syst:err:all?").strip()
        if not errors == '0,"No error"':
            warn(errors, UserWarning)

        # set resolution?
        resolution = "hres"  # samp
        self.write(f"chan:type {resolution}")

        # data format
        self.write("form ascii")

        # number of data points
        if number_of_points is not None:
            self.write(f"chan:data:poin {number_of_points}")

    def read(self) -> DataContainer:
        data = self._read_data()
        output = DataContainer.concat(data, axis=1)
        output.index.name = "Time"
        output.header = self._header

        return output

    def _read_data(self) -> List[DataContainer]:
        # check for errors
        if self.STOP_SCOPE:
            self.write(":STOP")

        self._read_meta_data()

        self._index = np.linspace(  # type:ignore
            self._header["xstart"],
            self._header["xstop"],
            self._header["points"],
            endpoint=True,
        )

        data = []
        for i in range(1, 1 + self.MAX_COLUMNS):
            channel_active = bool(int(self.query(f"chan{i}:state?").strip()))
            if channel_active:
                data.append(DataContainer({i: self._read_column(i)}, index=self._index))

        if not data:
            raise utils.ImportFailed(
                f"'{self.NAME}' importer: No active trace on the scope"
            )

        if self.STOP_SCOPE:
            self.write(":RUN")

        return data

    def _read_meta_data(self) -> None:
        head = self.query("chan:data:head?").strip().split(",")
        self._header = {
            "xUnit": "s",
            "yUnitUnit": "V",
            "xstart": float(head[0]),
            "xstop": float(head[1]),
            "points": int(head[2]),
        }

        for chan in range(1, 1 + self.MAX_COLUMNS):
            for chan_setting in [
                "bandwidth",
                "coupling",
                "label",
                "offset",
                "polarity",
                "position",
                "range",
                "scale",
                "skew",
                "state",
                "threshold",
                "type",
                "zoffset",
            ]:
                self._header[f"chan{chan}_{chan_setting}"] = self.query(
                    f"chan{chan}:{chan_setting}?"
                ).strip()

    def _read_column(self, channel: int) -> np.ndarray:
        """
        The data looks like this:

        8.995056E-05,9.498596E-05,1.110077E-04,1.139069E-04,1.152802E-04,1.061249E-04, ...
        """
        raw_data = self.query(f"chan{channel}:data?").strip()

        if not raw_data:
            raise utils.ImportFailed(f"{self.NAME}: There is no data!")

        try:
            data = np.array(raw_data.split(","), dtype=float)
            points = self._header["points"]
            if len(data) != points:
                raise utils.ImportFailed(
                    f"Channel {channel} should have {points} data points, but got {len(data)}"
                )
            if np.isnan(data).any():
                warn("There are NaN values in the data.", UserWarning)
        except (ValueError, AssertionError):
            raise utils.ImportFailed(
                f"{self.NAME}: Could not process the data"
            ) from None

        return data
