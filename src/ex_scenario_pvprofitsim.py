# Example Mosaik scenario simulation
# - from Mosaik tutorial for creating a simulator https://mosaik.readthedocs.io/en/latest/tutorials/writing-a-simulator.html
# - Output is saved in CSV format

import random
import mosaik
import mosaik.util

# __________________________________________________________________
# ______________ Simulator connections configuration _______________

# Define simulators (and how to access them)
# possible connection types: 
# https://mosaik.readthedocs.io/en/latest/api_reference/mosaik.html#mosaik.AsyncWorld.sim_config
SIM_CONFIG: mosaik.SimConfig = {
    "Weather": {"python": "mosaik.basic_simulators:InputSimulator"},
    "PV": {"python": "mosaik_components.pv.pvsimulator:PVSimulator"},
    "Grid": {"python": "mosaik_components.pandapower:Simulator"},
    "Profits": {"python": "simulator_pvprofit.simulator:Simulator"},
    "CSV_writer": {"python": "mosaik_csv_writer:CSVWriter"},
}

# __________________________________________________________________
# ________________ Simulation scenario definition __________________

# create a simulation world and connect to the simulators
with mosaik.World(SIM_CONFIG) as world:

    # start each simulator with their initial parameters
    weathersim = world.start("Weather", sim_id="Weather", step_size=900)
    pvsim = world.start("PV", sim_id="PV", step_size=900, start_date="2025-01-01 12:00:00")
    gridsim = world.start("Grid", sim_id="Grid", step_size=900)
    profitssim = world.start("Profits", price=100)
    csvwritersim = world.start("CSV_writer", start_date = "2025-01-01 12:00:00", output_file="simresults_ex_scenario_pvprofitsim.csv")

    # create entities: a weather entity, which will be given an anonymous function for its output generation,
    # an array of 50 pv-entities to generate power, and finally the grid using pandapower's network creation function
    weather = weathersim.Function(function=lambda time: random.uniform(0.0, 1000.0))
    pvs = pvsim.PV.create(50, area=10, latitude=53.14, efficiency=0.5, el_tilt=32.0, az_tilt=0.0)
    grid = gridsim.Grid(network_function="create_cigre_network_lv")

    # not directly related to the simulation but for simulation results
    csv_writer = csvwritersim.CSVWriter()

    # ______________________________________________________________
    # ____________ Connecting all of the above together ____________

    # Find all the low-voltage buses in the grid as well as the external grid connection
    lv_buses = [
        entity
        for entity in grid.children
        if entity.type == "Bus" and entity.extra_info["nominal voltage [kV]"] == 0.4
    ]
    ext_grid = [entity for entity in grid.children if entity.type == "ExternalGrid"][0]

    # PV's get connected to weather (weather value to pv's direct normal irradiance):
    for pv in pvs:
        world.connect(weather, pv, ("value", "DNI[W/m2]"))

    # connect - randomly, but avoiding duplicate connections - pvs to grid:
    mosaik.util.connect_randomly(
        world,
        pvs,
        lv_buses,
        ("P[MW]", "P_gen[MW]"),
    )

    # connection of pv to external grid:
    world.connect(ext_grid, csv_writer, "P[MW]", "Q[MVar]")

    # Connecting PV's to PVProfit simulator as well as to the results
    pv_profit_eids = [f"Profit-for-{pv.eid}" for pv in pvs]
    pv_profits = profitssim.PVProfits.create(len(pv_profit_eids), eid=pv_profit_eids)
    mosaik.util.connect_zip(world, pvs, pv_profits, "P[MW]")
    mosaik.util.connect_many_to_one(world, pv_profits, csv_writer, "profit[EUR]")

    #_______________________________________________________________
    # ____________________ Running the simulation __________________

    # 1h simulation (steps in 15 mins (900s) so 4 simulation steps are run):
    world.run(until=48*3600)
