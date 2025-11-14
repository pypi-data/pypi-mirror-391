import scripts.setup_path  # noqa: F401

from batem.reno.pv.creation import PVPlantBuilder, WeatherDataBuilder


from batem.reno.house.creation import HouseBuilder, HouseCreationExperiment
from batem.reno.plot.base import Plotter
from batem.reno.plot.house import (
    AppliancePlotRenderer, AppliancesAxesConfigurator, AppliancesData,
    AppliancesFigureSaver, AppliancesPlotterConfig,
    AppliancesPlotterDataProcessor,
    HousePlotterAxesConfigurator, HousePlotterDataProcessor,
    HousePlotterFilePathBuilder, HousePlotterPlotRenderer
)
from batem.reno.utils import TimeSpaceHandler, parse_args


if __name__ == "__main__":
    # python scripts/plot_house_appliances_pv.py
    house_id = 2000900
    # house_id = 2000917

    args = parse_args()

    # Define time setting
    time_space_handler = TimeSpaceHandler(location=args.location,
                                          start_date=args.start_date,
                                          end_date=args.end_date)

    house = HouseBuilder().build_house_by_id(house_id)

    weather_data = WeatherDataBuilder().build(
        location=time_space_handler.location,
        latitude_north_deg=time_space_handler.latitude_north_deg,
        longitude_east_deg=time_space_handler.longitude_east_deg,
        from_datetime_string=time_space_handler.start_date,
        to_datetime_string=time_space_handler.end_date)

    pv_plant = PVPlantBuilder().build(weather_data=weather_data,
                                      exposure_deg=0,
                                      slope_deg=160,
                                      number_of_panels=2,
                                      peak_power_kW=0.78)

    # Define experiment accoridng to the house id
    experiment = HouseCreationExperiment(
        name="house_appliances_pv",
        house_id=house_id)

    # Set up config for appliance plotting, at hourly interval
    hourly_config = AppliancesPlotterConfig(
        as_png=False,
        file_path="",
        size=(20, 10),
        experiment=experiment,
        time_space_handler=time_space_handler,
        hourly=True,
        show=False,
        has_production=True
    )

    # Set up file path for appliance plotting
    hourly_config.file_path = HousePlotterFilePathBuilder().build_plot_path(
        house,
        experiment,
        hourly_config,
        appliances=True)

    # Plot appliances at hourly interval
    Plotter(
        config=hourly_config,
        data_processor=AppliancesPlotterDataProcessor(),
        renderer=AppliancePlotRenderer(),
        axes_configurator=AppliancesAxesConfigurator(),
        figure_saver=AppliancesFigureSaver()
    ).plot(AppliancesData(
        house=house,
        pv_plant=pv_plant))

    # Adapt just the path for the house plotter, at hourly interval
    hourly_config.file_path = HousePlotterFilePathBuilder().build_plot_path(
        house,
        experiment,
        hourly_config,
        appliances=False)

    Plotter(
        config=hourly_config,
        data_processor=HousePlotterDataProcessor(),
        renderer=HousePlotterPlotRenderer(),
        axes_configurator=HousePlotterAxesConfigurator(),
        figure_saver=AppliancesFigureSaver()
    ).plot(AppliancesData(
        house=house,
        pv_plant=pv_plant))
