"""Occupant behavior and comfort assessment module for building energy analysis.

This module provides comprehensive tools for modeling occupant behavior, preferences,
and comfort assessment in building energy systems. It implements occupant preference
models that consider thermal comfort, air quality, energy costs, and behavioral
patterns to evaluate building performance from the occupant's perspective.

The module provides:
- Contiguous: Time series analysis for identifying contiguous periods of specific conditions
- Preference: Comprehensive occupant preference model with comfort and cost assessment

Key features:
- Thermal comfort assessment with preferred and extreme temperature ranges
- Air quality evaluation using CO2 concentration thresholds
- Energy cost calculation with COP (Coefficient of Performance) considerations
- Occupant behavior modeling including configuration change frequency
- ICONE indicator for air quality confinement assessment
- Multi-objective optimization balancing comfort and energy costs
- Time series analysis for identifying problematic periods
- Comprehensive assessment reporting with detailed comfort metrics
- Support for different HVAC modes and their efficiency factors
- Integration with building energy simulation and control systems

The module is designed for building energy analysis, occupant comfort studies,
and building performance evaluation from the user's perspective.

Author: stephane.ploix@grenoble-inp.fr
License: GNU General Public License v3.0
"""
import math
from collections.abc import Iterable
from datetime import datetime
from batem.core.timemg import datetime_to_stringdate
from batem.core.comfort import icone


class Contiguous:
    """Time series analysis for identifying and displaying contiguous periods of specific conditions.

    This class helps identify and analyze contiguous time periods where specific
    conditions occur (e.g., extreme temperatures, poor air quality). It provides
    methods to track time slots and generate formatted output showing the duration
    and timing of these periods.
    """

    def __init__(self, name: str, datetimes: list[datetime]):
        self.name: str = name
        self.datetimes: list[datetime] = datetimes
        self.time_slots: list[int] = list()

    def add(self, k: int) -> None:
        self.time_slots.append(k)

    def __str__(self) -> None:
        string: str = f"Period of {self.name}: "
        if len(self.time_slots) == 0:
            return string + "\nempty"
        k_start: int = self.time_slots[0]
        counter: int = 1
        for i in range(1, len(self.time_slots)):
            if self.time_slots[i] != k_start + counter:
                string += "\n%s (k=%i): %i hours, " % (datetime_to_stringdate(self.datetimes[k_start]), k_start, counter)
                counter = 1
                k_start = self.time_slots[i]
            else:
                counter += 1
        return string


class Preference:
    """Comprehensive occupant preference model for comfort and cost assessment.

    This class provides a complete model of occupant preferences that considers
    thermal comfort, air quality, energy costs, and behavioral patterns. It
    implements multi-objective optimization that balances comfort satisfaction
    with energy consumption costs, taking into account occupant behavior and
    system efficiency factors.
    """

    def __init__(
        self,
        preferred_temperatures: tuple[float, float] = (20, 26),
        extreme_temperatures: tuple[float, float] = (16, 30),
        preferred_CO2_concentration: tuple[float, float] = (500, 1700),
        temperature_weight_wrt_CO2: float = 0.5,
        power_weight_wrt_comfort: float = 0.5,
        sleeping_hours: Iterable[int] | None = (23, 0, 1, 2, 3, 4, 5, 6),
        mode_cop: dict[int, float] = {},
    ):
        """Initialise the preference model and configure comfort weights.

        :param preferred_temperatures: Target indoor temperature interval in degrees Celsius.
        :param extreme_temperatures: Lower/upper bounds of tolerable temperatures in degrees Celsius.
        :param preferred_CO2_concentration: Acceptable indoor CO₂ concentration range in ppm.
        :param temperature_weight_wrt_CO2: Weight of thermal comfort relative to air-quality comfort (``1`` means temperature only).
        :param power_weight_wrt_comfort: Weight of energy cost relative to combined comfort (``1`` means cost only).
        :param sleeping_hours: Sequence of integer hours (``0``–``23``) that represent sleeping periods. Thermal indicators ignore these slots while air-quality indicators still include them.
        :param mode_cop: Mapping from HVAC mode identifiers to coefficient of performance values used when translating power to energy cost.
        """
        self.preferred_temperatures = preferred_temperatures
        self.extreme_temperatures = extreme_temperatures
        self.preferred_CO2_concentration = preferred_CO2_concentration
        self.temperature_weight_wrt_CO2 = temperature_weight_wrt_CO2
        self.power_weight_wrt_comfort = power_weight_wrt_comfort
        self.mode_cop = mode_cop
        self.sleeping_hours: set[int] = {int(hour) % 24 for hour in sleeping_hours} if sleeping_hours is not None else set()

    def change_dissatisfaction(self, occupancy, action_set=None):
        """Compute the ratio of the number of hours where occupants have to change their home configuration divided by the number of hours with presence.

        :param occupancy: a vector of occupancies
        :type occupancy: list[float]
        :param action_set: different vectors of actions
        :type action_set: tuple[list[float]]
        :return: the number of hours where occupants have to change their home configuration divided by the number of hours with presence
        :rtype: float
        """
        number_of_changes = 0
        number_of_presences = 0
        previous_actions = [actions[0] for actions in action_set]
        for k in range(len(occupancy)):
            if occupancy[k] > 0:
                number_of_presences += 1
                for i in range(len(action_set)):
                    actions = action_set[i]
                    if actions[k] != previous_actions[i]:
                        number_of_changes += 1
                        previous_actions[i] = actions[k]
        return number_of_changes / number_of_presences if number_of_presences > 0 else 0

    def thermal_comfort_dissatisfaction(self, temperatures: list[float], occupancies: list[float], hours: Iterable[int] | None = None) -> float:
        """Compute the average thermal discomfort over occupied hours.

        :param temperatures: Hourly indoor air temperatures aligned with ``occupancies``.
        :param occupancies: Occupancy levels per hour (values ``> 0`` indicate presence).
        :param hours: Optional iterable of hour indices (``0``–``23``). When provided, entries whose hour
            is part of :attr:`sleeping_hours` are excluded from the calculation.
        :returns: Average thermal dissatisfaction score in the ``[0, +inf)`` range.
        """
        temps = list(temperatures) if isinstance(temperatures, Iterable) else [temperatures]
        occs = list(occupancies) if isinstance(occupancies, Iterable) else [occupancies]
        hrs = list(hours) if hours is not None else None
        if hrs is not None and len(hrs) != len(temps):
            raise ValueError("hours length must match temperatures length")
        if len(temps) != len(occs):
            raise ValueError("temperatures and occupancies must have the same length")

        considered_indices: list[int] = [
            i for i, occ in enumerate(occs)
            if occ and (hrs is None or hrs[i] not in self.sleeping_hours)
        ]
        if not considered_indices:
            return 0.0

        dissatisfaction = 0.0
        for i in considered_indices:
            temp = float(temps[i])
            if temp < self.preferred_temperatures[0]:
                dissatisfaction += (self.preferred_temperatures[0] - temp) / (self.preferred_temperatures[0] - self.extreme_temperatures[0])
            elif temp > self.preferred_temperatures[1]:
                dissatisfaction += (temp - self.preferred_temperatures[1]) / (self.extreme_temperatures[1] - self.preferred_temperatures[1])
        return dissatisfaction / len(considered_indices)

    def air_quality_dissatisfaction(self, CO2_concentrations: list[float], occupancies: list[float]) -> float:
        """Compute the average air-quality dissatisfaction considering occupied hours only.

        :param CO2_concentrations: Indoor CO₂ concentrations in ppm.
        :param occupancies: Occupancy levels per hour (values ``> 0`` indicate presence).
        :returns: Average dissatisfaction in the ``[0, +inf)`` range.
        """
        if type(CO2_concentrations) is not list:
            CO2_concentrations = [CO2_concentrations]
            occupancies = [occupancies]
        dissatisfaction = 0.0
        denom = (self.preferred_CO2_concentration[1] - self.preferred_CO2_concentration[0]) or 1.0
        n = 0
        for value, occupancy in zip(CO2_concentrations, occupancies):
            if occupancy:
                dissatisfaction += max(0.0, (float(value) - self.preferred_CO2_concentration[0]) / denom)
                n += 1
        return dissatisfaction / n if n else 0.0

    def comfort_dissatisfaction(self, temperatures: list[float], CO2_concentrations: list[float], occupancies: list[float], hours: list[int] = None) -> float:
        """Blend thermal and air-quality dissatisfaction into a single KPI.

        :param temperatures: Indoor temperature profile aligned with ``occupancies``.
        :param CO2_concentrations: Indoor CO₂ concentration profile.
        :param occupancies: Occupancy signal used to ignore vacant periods.
        :param hours: Optional hourly indices (``0``–``23``) to remove sleeping hours from the thermal term.
        :returns: Weighted comfort dissatisfaction value.
        """
        return (
            self.temperature_weight_wrt_CO2 * self.thermal_comfort_dissatisfaction(temperatures, occupancies, hours)
            + (1 - self.temperature_weight_wrt_CO2) * self.air_quality_dissatisfaction(CO2_concentrations, occupancies)
        )

    def daily_cost_euros(self, Pheat: list[float], modes: list[int] = None, kWh_price: float = 0.13) -> float:
        """Compute the heating cost.

        :param Pheat: list of heating power consumptions
        :type Pheat: list[float]
        :param kWh_price: tariff per kWh, defaults to .13
        :type kWh_price: float, optional
        :return: energy cost
        :rtype: float
        """
        needed_energy_Wh = 0
        for k in range(len(Pheat)):
            if modes is not None and modes[k] != 0 and modes[k] in self.mode_cop:
                needed_energy_Wh += abs(Pheat[k]) / self.mode_cop[modes[k]]
            else:  # consider a COP = 1
                needed_energy_Wh += abs(Pheat[k])
            # else:
            #     cost_Wh = sum(Pheat)
        return 24 * needed_energy_Wh / len(Pheat) / 1000 * kWh_price

    def icone(self, CO2_concentration, occupancy) -> float:
        """Compute the ICONE indicator dealing with confinement regarding air quality.

        :param CO2_concentration: list of CO2 concentrations
        :type CO2_concentration: list[float]
        :param occupancy: list of occupancies
        :type occupancy: list[float]
        :return: value between 0 and 5
        :rtype: float
        """
        n_presence = 0
        n1_medium_containment = 0
        n2_high_containment = 0
        for k in range(len(occupancy)):
            if occupancy[k] > 0:
                n_presence += 1
                if 1000 <= CO2_concentration[k] < 1700:
                    n1_medium_containment += 1
                elif CO2_concentration[k] >= 1700:
                    n2_high_containment += 1
        f1 = n1_medium_containment / n_presence if n_presence > 0 else 0
        f2 = n2_high_containment / n_presence if n_presence > 0 else 0
        return 8.3 * math.log10(1 + f1 + 3 * f2)

    def assess(self, Pheater: list[float], temperatures: list[float], CO2_concentrations: list[float], occupancies: tuple[list[float]], hours: list[int] = None, modes: list[float] = None) -> float:
        """Evaluate the aggregated objective combining comfort and energy cost.

        :param Pheater: Thermal power time series supplied by the HVAC system (W).
        :param temperatures: Indoor temperature time series (°C).
        :param CO2_concentrations: Indoor CO₂ concentration time series (ppm).
        :param occupancies: Occupancy profiles aligned with ``temperatures``.
        :param hours: Optional hourly indices to pass to :meth:`thermal_comfort_dissatisfaction`.
        :param modes: HVAC operating modes used to determine the effective COP when computing energy cost.
        :returns: Scalar objective value (lower is better).
        """
        return (
            self.daily_cost_euros(Pheater, modes) * self.power_weight_wrt_comfort
            + (1 - self.power_weight_wrt_comfort) * self.comfort_dissatisfaction(temperatures, CO2_concentrations, occupancies, hours)
        )

    def print_assessment(self, datetimes: datetime, PHVAC: list[float], temperatures: list[float], CO2_concentrations: list[float], occupancies: list[float], action_sets: tuple[list[float]] | None = None,  modes: list[float] = None, list_extreme_hours: bool = False):
        """Pretty-print comfort and cost indicators derived from a simulation run.

        :param datetimes: Time axis associated with the input time series.
        :param PHVAC: HVAC power time series (W).
        :param temperatures: Indoor temperature series (°C).
        :param CO2_concentrations: Indoor CO₂ concentration series (ppm).
        :param occupancies: Occupancy signal used to detect presence.
        :param action_sets: Optional tuple of action series used to evaluate configuration changes.
        :param modes: Optional HVAC mode time series used for COP-aware energy cost.
        :param list_extreme_hours: When ``True`` the function lists contiguous periods of extreme thermal conditions.
        """
        hours = [dt.hour for dt in datetimes]
        hour_quality_counters: dict[str, int] = {'extreme cold': 0, 'cold': 0, 'perfect': 0, 'warm': 0, 'extreme warm': 0}
        n_hours_with_presence = 0
        total_presence_hours = 0
        sleeping_presence_hours = 0
        sleeping_temperatures: list[float] = []
        sleeping_co2_concentrations: list[float] = []
        sleeping_hours_set = self.sleeping_hours
        extreme_cold_contiguous = Contiguous('Extreme cold', datetimes)
        extreme_warm_contiguous = Contiguous('Extreme warm', datetimes)

        for k, temperature in enumerate(temperatures):
            if occupancies[k] > 0:
                total_presence_hours += 1
                if hours[k] in sleeping_hours_set:
                    sleeping_presence_hours += 1
                    sleeping_temperatures.append(float(temperature))
                    sleeping_co2_concentrations.append(float(CO2_concentrations[k]))
                    continue
                n_hours_with_presence += 1
                if temperature < self.extreme_temperatures[0]:
                    hour_quality_counters['extreme cold'] += 1
                    extreme_cold_contiguous.add(k)
                elif temperature < self.preferred_temperatures[0]:
                    hour_quality_counters['cold'] += 1
                elif temperature > self.extreme_temperatures[1]:
                    hour_quality_counters['extreme warm'] += 1
                    extreme_warm_contiguous.add(k)
                elif temperature > self.preferred_temperatures[1]:
                    hour_quality_counters['warm'] += 1
                else:
                    hour_quality_counters['perfect'] += 1
        print(f'\nThe assessed period covers {round(len(temperatures)/24)} days with a total HVAC energy of {int(round(sum([abs(P) / 1000 for P in PHVAC])))}kWh (heating: {int(round(sum([P / 1000 if P > 0 else 0 for P in PHVAC])))}kWh / cooling: {int(round(sum([-P / 1000 if P < 0 else 0 for P in PHVAC])))}kWh):')
        print('- global objective: %s' % self.assess(PHVAC, temperatures, CO2_concentrations, occupancies, hours, modes))
        print('- average thermal dissatisfaction: %.2f%%' % (self.thermal_comfort_dissatisfaction(temperatures, occupancies, hours) * 100))
        for hour_quality_counter in hour_quality_counters:
            ratio = (100 * hour_quality_counters[hour_quality_counter] / n_hours_with_presence) if n_hours_with_presence > 0 else 0.0
            print('- %% of %s hours: %.2f' % (hour_quality_counter, ratio))
        if sleeping_presence_hours > 0:
            avg_sleep_temp = sum(sleeping_temperatures) / len(sleeping_temperatures)
            avg_sleep_co2 = sum(sleeping_co2_concentrations) / len(sleeping_co2_concentrations)
            share_sleep = 100 * sleeping_presence_hours / total_presence_hours if total_presence_hours > 0 else 0.0
            print('- %% of sleeping hours: %.0f%% at average temperature %.1f°C and CO2 %.0fppm' % (share_sleep, avg_sleep_temp, avg_sleep_co2))
        else:
            print('- %% of sleeping hours: 0.00')
        print('- average CO2 dissatisfaction: %.2f%%' % (self.air_quality_dissatisfaction(CO2_concentrations, occupancies) * 100))
        print('- ICONE: %.2f' % (icone(CO2_concentrations, occupancies)))
        print('- average comfort dissatisfaction: %.2f%%' % (self.comfort_dissatisfaction(temperatures, CO2_concentrations, occupancies, hours) * 100))
        if action_sets is not None:
            print('- change dissatisfaction (number of changes / number of time slots with presence): %.2f%%' % (self.change_dissatisfaction(occupancies, action_sets) * 100))
        print('- heating cost: %.2f euros/day' % self.daily_cost_euros(PHVAC, modes))

        temperatures_when_presence = list()
        CO2_concentrations_when_presence = list()
        for i in range(len(occupancies)):
            if occupancies[i] > 0:
                if sleeping_hours_set and hours[i] in sleeping_hours_set:
                    continue
                temperatures_when_presence.append(temperatures[i])
                CO2_concentrations_when_presence.append(CO2_concentrations[i])
        if len(temperatures_when_presence) > 0:
            temperatures_when_presence.sort()
            CO2_concentrations_when_presence.sort()
            office_temperatures_estimated_presence_lowest = temperatures_when_presence[:math.ceil(len(temperatures_when_presence) * 0.1)]
            office_temperatures_estimated_presence_highest = temperatures_when_presence[math.floor(len(temperatures_when_presence) * 0.9):]
            office_co2_concentrations_estimated_presence_lowest = CO2_concentrations_when_presence[:math.ceil(len(CO2_concentrations_when_presence) * 0.1)]
            office_co2_concentrations_estimated_presence_highest = CO2_concentrations_when_presence[math.floor(len(CO2_concentrations_when_presence) * 0.9):]
            print('- average temperature during presence: %.1f' % (sum(temperatures_when_presence) / len(temperatures_when_presence)))
            print('- average 10%% lowest temperature during presence: %.1f' % (sum(office_temperatures_estimated_presence_lowest) / len(office_temperatures_estimated_presence_lowest)))
            print('- average 10%% highest temperature during presence: %.1f' % (sum(office_temperatures_estimated_presence_highest) / len(office_temperatures_estimated_presence_highest)))
            print('- average CO2 concentration during presence: %.0f' % (sum(CO2_concentrations_when_presence) / len(CO2_concentrations_when_presence)))
            print('- average 10%% lowest CO2 concentration during presence: %.0f' % (sum(office_co2_concentrations_estimated_presence_lowest) / len(office_co2_concentrations_estimated_presence_lowest)))
            print('- average 10%% highest CO2 concentration during presence: %.0f' %
                  (sum(office_co2_concentrations_estimated_presence_highest) / len(office_co2_concentrations_estimated_presence_highest)))
        if sleeping_temperatures:
            print('- average temperature during sleeping hours: %.1f' % (sum(sleeping_temperatures) / len(sleeping_temperatures)))
        if sleeping_co2_concentrations:
            print('- average CO2 concentration during sleeping hours: %.0f' % (sum(sleeping_co2_concentrations) / len(sleeping_co2_concentrations)))
        if list_extreme_hours:
            print('Contiguous periods:')
            print(extreme_cold_contiguous)
            print(extreme_warm_contiguous)

    def __str__(self):
        """Return a description of the defined preferences.

        :return: a descriptive string of characters.
        :rtype: str
        """
        string = 'Preference:\ntemperature in %f<%f..%f>%f\n concentrationCO2 %f..%f\n' % (
            self.extreme_temperatures[0], self.preferred_temperatures[0], self.preferred_temperatures[1], self.extreme_temperatures[1], self.preferred_CO2_concentration[0], self.preferred_CO2_concentration[1])
        string += 'overall: %.3f * cost + %.3f disT + %.3f disCO2' % (self.power_weight_wrt_comfort, (1-self.power_weight_wrt_comfort) * self.temperature_weight_wrt_CO2, (1-self.power_weight_wrt_comfort) * (1-self.temperature_weight_wrt_CO2))
        return string
