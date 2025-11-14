# Setup Python path before imports
import scripts.setup_path  # noqa: F401


from enum import Enum
from batem.core import solar, weather
from batem.reno.battery.model import Battery
from batem.reno.house.creation import HouseBuilder
from batem.reno.house.model import House
from batem.reno.house.services import ConsumptionAggregator, ConsumptionTrimmer
from batem.reno.indicators import neeg
from batem.reno.pv.creation import PVPlantBuilder, WeatherDataBuilder
from batem.reno.pv.model import PVPlant
from batem.reno.utils import TimeSpaceHandler, parse_args
from scipy.optimize import differential_evolution


class PanelTypes(Enum):
    """
    Panel tyoess, with repsective power ratings in watts.
    """
    LOW_COST = "low_cost"
    STANDARD = "standard"
    HIGH_EFFICIENCY = "high_efficiency"


PANEL_TYPE_TO_POWER_MAP = {
    PanelTypes.LOW_COST: 0.2,
    PanelTypes.STANDARD: 0.5,
    PanelTypes.HIGH_EFFICIENCY: 0.6
}

PANEL_INDEX_TO_TYPE_MAP = {
    0: PanelTypes.LOW_COST,
    1: PanelTypes.STANDARD,
    2: PanelTypes.HIGH_EFFICIENCY
}

MOUNT_TYPE_INDEX_TO_TYPE_MAP = {
    0: solar.MOUNT_TYPES.PLAN,
    1: solar.MOUNT_TYPES.FLAT,
    2: solar.MOUNT_TYPES.BACK2BACK
}


def get_house_neeg(house: House, pv_plant: PVPlant,
                   battery: Battery | None = None) -> float:
    """
    Get the NEEG of a house with a PV plant.
    The result is in kWh.
    """
    pv_production = pv_plant.production.usage_hourly

    if house.consumption.usage_hourly is None:
        print("Warning: No hourly consumption data")
        return 0
    load_by_time = house.consumption.usage_hourly
    battery_power_by_time = (
        battery.get_battery_power_by_time() if battery else {})
    return neeg(load_by_time, pv_production, battery_power_by_time)


class SizingStrategy:
    def __init__(self, time_space_handler: TimeSpaceHandler,
                 max_surface_area_m2: float = 100.0):
        self.time_space_handler = time_space_handler
        self.max_surface_area_m2 = max_surface_area_m2

    def run(self):
        house = HouseBuilder().build_house_by_id(2000901)

        weather_data = WeatherDataBuilder().build(
            location=self.time_space_handler.location,
            latitude_north_deg=self.time_space_handler.latitude_north_deg,
            longitude_east_deg=self.time_space_handler.longitude_east_deg,
            from_datetime_string=self.time_space_handler.start_date,
            to_datetime_string=self.time_space_handler.end_date)

        pv_plant = PVPlantBuilder().build(weather_data=weather_data,
                                          exposure_deg=0,
                                          slope_deg=160,
                                          number_of_panels=10,
                                          peak_power_kW=5)

        ConsumptionTrimmer(house).trim_consumption_house(
            self.time_space_handler)
        house.consumption.usage_hourly = ConsumptionAggregator(
            house).get_total_consumption_hourly()

        initial_neeg = get_house_neeg(house, pv_plant)

        print(f"Initial NEEG: {initial_neeg:.3f}")

        bounds = [(1, 100), (0, 2), (0, 2)]  # (panels, panel_type, mount_type)

        result = differential_evolution(
            self.objective_function,
            args=(weather_data,
                  house,
                  self.max_surface_area_m2),
            bounds=bounds,
            workers=5,
            maxiter=10,
            popsize=20,
            disp=True,
            polish=True
        )

        optimal_panels = int(result.x[0])
        optimal_panel_index = int(round(result.x[1]))  # Convert to integer
        optimal_mount_type_index = int(
            round(result.x[2]))  # Convert to integer

        # Ensure panel_index is within valid range
        optimal_panel_index = max(0, min(optimal_panel_index, 2))
        optimal_mount_type_index = max(0, min(optimal_mount_type_index, 2))

        # get optimal panel type
        optimal_panel_type = PANEL_INDEX_TO_TYPE_MAP[optimal_panel_index]
        optimal_mount_type = \
            MOUNT_TYPE_INDEX_TO_TYPE_MAP[optimal_mount_type_index]
        panel_power_kW = PANEL_TYPE_TO_POWER_MAP[optimal_panel_type]

        peak_power_kW = panel_power_kW * optimal_panels

        # Calculate final surface area for reporting
        final_pv_plant = PVPlantBuilder().build(
            weather_data=weather_data,
            exposure_deg=0,
            slope_deg=160,
            number_of_panels=optimal_panels,
            peak_power_kW=peak_power_kW,
            mount_type=optimal_mount_type)

        final_surface_area = (optimal_panels *
                              final_pv_plant.panel_height_m *
                              final_pv_plant.panel_width_m)

        print(f"Optimal number of panels: {optimal_panels}")
        print(f"Optimal panel type: {optimal_panel_type}")
        print(f"Optimal peak power: {peak_power_kW:.3f} kW")
        print(f"Optimal mount type: {optimal_mount_type}")
        print(f"Total PV surface area: {final_surface_area:.2f} m²")
        print(f"Max allowed surface area: {self.max_surface_area_m2:.2f} m²")
        print(f"Best NEEG: {result.fun:.3f}")

    @staticmethod
    def objective_function(x,
                           weather_data: weather.SiteWeatherData,
                           house: House,
                           max_surface_area_m2: float):
        number_of_panels = int(x[0])
        panel_index = int(round(x[1]))  # Convert to integer index

        # Ensure panel_index is within valid range
        panel_index = max(0, min(panel_index, 2))
        panel_type = PANEL_INDEX_TO_TYPE_MAP[panel_index]
        mount_type_index = int(round(x[2]))  # Convert to integer index
        mount_type = MOUNT_TYPE_INDEX_TO_TYPE_MAP[mount_type_index]

        # get total plant peak power
        power_one_panel_kW = PANEL_TYPE_TO_POWER_MAP[panel_type]
        peak_power_kW = power_one_panel_kW * number_of_panels

        panel_height_m = 1.7
        panel_width_m = 1

        # Calculate total surface area
        total_surface_area_m2 = (number_of_panels *
                                 panel_height_m *
                                 panel_width_m)

        # Apply surface area constraint
        if total_surface_area_m2 > max_surface_area_m2:
            return float('inf')  # Penalty for exceeding surface constraint

        pv_plant = PVPlantBuilder().build(weather_data=weather_data,
                                          panel_height_m=panel_height_m,
                                          panel_width_m=panel_width_m,
                                          exposure_deg=0,
                                          slope_deg=160,
                                          number_of_panels=number_of_panels,
                                          peak_power_kW=peak_power_kW,
                                          mount_type=mount_type)

        neeg_value = get_house_neeg(house, pv_plant)

        return neeg_value


if __name__ == "__main__":

    # python scripts/pv_sizing_house.py

    args = parse_args()

    # You can modify the max_surface_area_m2 parameter as needed
    # Default is 100 m² but you can change it based on your constraints
    max_surface_area = 100.0  # m²

    SizingStrategy(TimeSpaceHandler(
        location=args.location,
        start_date=args.start_date,
        end_date=args.end_date),
        max_surface_area_m2=max_surface_area).run()
