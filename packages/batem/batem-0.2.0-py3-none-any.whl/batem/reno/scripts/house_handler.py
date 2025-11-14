import scripts.setup_path  # noqa: F401

from batem.reno.house.creation import (
    HouseBuilder, HouseCreationExperiment, HouseFilePathBuilder)

from batem.reno.house.services import ConsumptionExporter


if __name__ == "__main__":

    # python scripts/house_handler.py

    # python -m cProfile -o scripts/house_creation.prof scripts/house_handler.py
    # snakeviz scripts/house_creation.prof

    experiment = HouseCreationExperiment(
        name="house_creation",
        house_id=2000900)

    house = HouseBuilder().build_house_by_id(house_id=experiment.house_id)

    path_builder = HouseFilePathBuilder()

    path = path_builder.get_house_consumption_path(experiment)
    ConsumptionExporter(house).to_csv(path)

    hourly_path = path_builder.get_house_consumption_path(
        experiment, hourly=True)
    ConsumptionExporter(house).to_csv(hourly_path, hourly=True)

    path = path_builder.get_house_consumption_path(experiment)
    house = HouseBuilder().build_house_from_csv(experiment.house_id, path)
