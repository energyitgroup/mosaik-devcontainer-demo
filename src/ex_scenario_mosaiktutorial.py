# Example Mosaik scenario simulation
# - from Mosaik tutorial https://mosaik.readthedocs.io/en/latest/tutorials/a-first-scenario.html
# - Output is in dict format and outputted to terminal

import mosaik
import mosaik.util
import random
from pprint import pprint
from mosaik.async_scenario import Entity
from mosaik.scenario import ModelFactory

SIM_CONFIG: mosaik.SimConfig = {
    "Weather": {"python": "mosaik.basic_simulators:InputSimulator"},
    "PV": {"python": "mosaik_components.pv.pvsimulator:PVSimulator"},
    "Grid": {"python": "mosaik_components.pandapower:Simulator"},
    "Output": {"python": "mosaik.basic_simulators:OutputSimulator"},
}

with mosaik.World(SIM_CONFIG) as world:

    # ---- initializing simulators ----
    weathersim: ModelFactory = world.start("Weather", sim_id="Weather", step_size=900)
    pvsim: ModelFactory = world.start("PV", sim_id="PV", step_size=900, start_date="2023-06-01 12:00:00")
    gridsim: ModelFactory = world.start("Grid", sim_id="Grid", step_size=900)
    outputsim: ModelFactory = world.start("Output")

    # ---- creating entities ----
    weather: Entity = weathersim.Function(function=lambda time: random.uniform(0.0, 1000.0))
    pvs: list[Entity] = pvsim.PV.create(50, area=10, latitude=53.14, efficiency=0.5, el_tilt=32.0, az_tilt=0.0)
    grid: Entity = gridsim.Grid(network_function="create_cigre_network_lv") # this will create a grid based on cigre LV network using pandapower's built in function
    output: Entity = outputsim.Dict() # will store the simulation results

    # getting all LV buses and external grid connection from the grid entity
    lv_buses: list[Entity] = []
    ext_grid: None | Entity = None

    for entity in grid.children:
        if entity.type == "Bus" and entity.extra_info["nominal voltage [kV]"] == 0.4:
            lv_buses.append(entity)
        elif entity.type == "ExternalGrid":
            ext_grid = entity

    if ext_grid is None or len(lv_buses) == 0:
        raise RuntimeError("No external grid or LV buses found in grid")

    # ---- connecting entities' inputs and outputs ----

    # each pv gets its weather data (Direct normal irradiance value) from the weather entity
    for pv in pvs:
        world.connect(weather, pv, ("value", "DNI[W/m2]"))

    # connect the pv's outputted power (P[MW]) randomly to all available LV buses' power input (P_gen[MW])
    mosaik.util.connect_randomly(
        world,
        pvs,
        lv_buses,
        ("P[MW]", "P_gen[MW]"),
    )

    # connect external grid connection's power output to the sim results output entity
    # so that we can see how PV system influences the power levels of the external grid
    world.connect(ext_grid, output, "P[MW]", "Q[MVar]")

    # ---- run the simulation and get (gathered) simulation results ----
    world.run(until=3600)
    result: dict = outputsim.get_dict(output.eid) # type: ignore (underlying lib issue)
    print("\nSimulation Results:")
    pprint(result)
