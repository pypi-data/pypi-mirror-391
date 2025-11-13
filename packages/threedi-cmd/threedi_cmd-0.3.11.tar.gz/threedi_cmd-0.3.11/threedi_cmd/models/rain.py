import shutil
from pathlib import Path
from typing import Callable, Dict

from threedi_api_client.openapi.models import (
    BulkTimeseriesRain,
    ConstantLocalRain,
    ConstantRain,
    FileRasterRain,
    FileTimeseriesRain,
    LizardRasterRain,
    LizardTimeseriesRain,
    NetCDFRasterRain,
    NetCDFTimeseriesRain,
    TimeseriesLocalRain,
    TimeseriesRain,
    Upload,
    UploadEventFile,
)

from .base import EventWrapper
from .waitfor import WaitForEventValidation, WaitForProcessedFileWrapper


def filename_converter(config: dict, **kwargs: dict) -> dict:
    """Return environment corrected configuration"""
    config["filename"] = config.pop("file")
    return config


def reference_uuid_environment_converter(config: dict, **kwargs: dict) -> dict:
    """Return environment corrected configuration"""
    assert (
        "reference_uuid" in config
    ), f"Reference UUID not found in configuration: {config}"

    if isinstance(config["reference_uuid"], str):
        # Reference UUID is already a string, no need to resolve
        return config

    assert isinstance(config["reference_uuid"], dict), (
        f"Attempting to resolve reference UUID from environment "
        f"but config is not a dict: {config}"
    )

    environment = kwargs.get("environment", "production")
    config["reference_uuid"] = config["reference_uuid"][environment]
    return config


class ConstantRainWrapper(EventWrapper):
    model = ConstantRain
    api_path: str = "rain_constant"
    scenario_name = model.__name__.lower()


class LocalConstantRainWrapper(EventWrapper):
    model = ConstantLocalRain
    api_path: str = "rain_local_constant"
    scenario_name = model.__name__.lower()


class RainTimeseriesWrapper(EventWrapper):
    model = TimeseriesRain
    api_path: str = "rain_timeseries"
    scenario_name = model.__name__.lower()


class LocalRainTimeseriesWrapper(EventWrapper):
    model = TimeseriesLocalRain
    api_path: str = "rain_local_timeseries"
    scenario_name = model.__name__.lower()


class RainRasterLizardWrapper(EventWrapper):
    model = LizardRasterRain
    api_path: str = "rain_rasters_lizard"
    scenario_name = model.__name__.lower()
    converters: list[Callable] = [reference_uuid_environment_converter]


class RainTimeseriesLizardWrapper(EventWrapper):
    model = LizardTimeseriesRain
    api_path: str = "rain_timeseries_lizard"
    scenario_name = model.__name__.lower()
    converters: list[Callable] = [reference_uuid_environment_converter]


class WaitForProcessedTimeseriesFileWrapper(WaitForProcessedFileWrapper):
    model = FileTimeseriesRain
    scenario_name = model.__name__.lower()


class WaitForRainTimeseriesNetCDFWrapper(WaitForProcessedTimeseriesFileWrapper):
    model = NetCDFTimeseriesRain
    websocket_model_name = "NetCDFTimeseriesRain"
    scenario_name = model.__name__.lower()


class WaitForBulkTimeseriesRainWrapper(WaitForEventValidation):
    model = BulkTimeseriesRain
    scenario_name = model.__name__.lower()


class RainTimeseriesNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "rain_timeseries_netcdf"
    scenario_name = model.__name__.lower()
    filepath: Path = None

    def initialize_instance(self, data: Dict):
        self.filepath = Path(data.pop("filepath"))
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        data = {
            "file": {"state": "processed", "filename": self.instance.filename},
            "timeout": 30,
        }
        wait_for_validation = WaitForRainTimeseriesNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


class WaitForProcessedRasterFileWrapper(WaitForProcessedFileWrapper):
    model = FileRasterRain
    scenario_name = model.__name__.lower()


class WaitForRainRasterNetCDFWrapper(WaitForProcessedRasterFileWrapper):
    model = NetCDFRasterRain
    websocket_model_name = "NetCDFRasterRain"
    scenario_name = model.__name__.lower()


class RainRasterNetCDFWrapper(EventWrapper):
    model = Upload
    api_path: str = "rain_rasters_netcdf"
    scenario_name = model.__name__.lower()
    filepath = None

    def initialize_instance(self, data: Dict):
        self.filepath = Path(data.pop("filepath"))
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        data = {
            "file": {"state": "processed", "filename": self.instance.filename},
            "timeout": 30,
        }
        wait_for_validation = WaitForRainRasterNetCDFWrapper(
            data=data, api_client=self._api_client, simulation=self.simulation
        )
        return [wait_for_validation]


class BulkTimeseriesRainWrapper(EventWrapper):
    model = UploadEventFile
    api_path: str = "rain_timeseries_file"
    scenario_name = "bulktimeseriesrain"
    filepath: Path | None = None
    converters: list[Callable] = [filename_converter]
    extra_fields = ["epsg_code"]

    def __init__(self, data: Dict, *args, **kwargs):
        self.epsg_code = data.pop("epsg_code", 4326)
        super().__init__(data, *args, **kwargs)

    def initialize_instance(self, data: dict | None = None) -> None:
        # Create a copy of the file
        assert data is not None
        converted_file = f"{data['filename'].split('.')[0]}_converted.json"
        full_path = self._base_path / converted_file
        if full_path.exists():
            full_path.unlink()
        shutil.copy(self._base_path / data["filename"], full_path)

        # Set the filepath
        data["filename"] = converted_file
        self.filepath = Path(converted_file)
        super().initialize_instance(data)

    @property
    def extra_steps(self):
        bulk_timeseries_rain = self.api.simulations_events_rain_timeseries_file_list(
            simulation_pk=self.simulation.id
        )
        for bulk_event in bulk_timeseries_rain.results:
            if bulk_event.file and bulk_event.file.filename == self.instance.filename:
                bulk_event_instance = bulk_event
                break
        assert bulk_event_instance is not None

        # Patch in the epsg_code
        if self.epsg_code != 4326:
            bulk_event_instance.epsg_code = self.epsg_code
            self._api_client.simulations_events_rain_timeseries_file_partial_update(
                id=bulk_event_instance.id,
                simulation_pk=self.simulation.id,
                data={"epsg_code": self.epsg_code},
            )

        wait_for_validation = WaitForBulkTimeseriesRainWrapper(
            data={**bulk_event_instance.to_dict(), "timeout": 60},
            api_client=self._api_client,
            simulation=self.simulation,
        )
        return [wait_for_validation]


WRAPPERS = [
    BulkTimeseriesRainWrapper,
    ConstantRainWrapper,
    RainTimeseriesWrapper,
    RainRasterLizardWrapper,
    RainTimeseriesLizardWrapper,
    RainTimeseriesNetCDFWrapper,
    # WaitForRainTimeseriesNetCDFWrapper,
    RainRasterNetCDFWrapper,
    # WaitForRainTimeseriesNetCDFWrapper,
    LocalConstantRainWrapper,
    LocalRainTimeseriesWrapper,
]
