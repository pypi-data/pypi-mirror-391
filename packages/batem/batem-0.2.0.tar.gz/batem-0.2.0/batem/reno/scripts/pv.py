import scripts.setup_path  # noqa: F401

from batem.reno.pv.creation import (
    PVPlantBuilder, PVPlantCreationExperiment,
    PVPlantFilePathBuilder, WeatherDataBuilder)
from batem.reno.utils import TimeSpaceHandler
from batem.reno.pv.services import ProductionExporter

if __name__ == "__main__":
    # python scripts/pv.py

    time_space_handler = TimeSpaceHandler(location="Bucharest",
                                          start_date="01/02/1998",
                                          end_date="01/02/1999")

    weather_data = WeatherDataBuilder().build(
        location=time_space_handler.location,
        latitude_north_deg=time_space_handler.latitude_north_deg,
        longitude_east_deg=time_space_handler.longitude_east_deg,
        from_datetime_string=time_space_handler.start_date,
        to_datetime_string=time_space_handler.end_date)

    pv_plant = PVPlantBuilder().build(weather_data=weather_data,
                                      peak_power_kW=0.5)

    path = PVPlantFilePathBuilder().get_pv_plant_path(
        time_space_handler,
        experiment=PVPlantCreationExperiment(name="pv plant basic creation",
                                             pv_plant=pv_plant))

    ProductionExporter(pv_plant).to_csv(path)
