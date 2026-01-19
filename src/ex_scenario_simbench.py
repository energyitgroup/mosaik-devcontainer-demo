# Example Mosaik scenario simulation
# - Using a simbench network (mosaik-pandapower built in function for fetching the network)
# - Output is saved in HDF5 format

import warnings
import mosaik
import mosaik.util

# The underlying simbench library has warnings about deprecation, which we ignore:
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

SIM_CONFIG: mosaik.SimConfig = {
    "hdf5": {"python": "mosaik_hdf5:MosaikHdf5"},
    "Grid": {"python": "mosaik_components.pandapower:Simulator"},
}

SIMULATION_DURATION = (24 * 3600) * 1 # seconds, 1 day

# World simulation loop
with mosaik.World(SIM_CONFIG) as world:

    # Start simulators
    db = world.start("hdf5", step_size=900, duration=SIMULATION_DURATION)
    pp = world.start("Grid", step_size=900) # 15 min intervals

    grid = pp.Grid(simbench="1-LV-rural2--0-sw")
    hdf5 = db.Database(filename="simresults_ex_scenario_simbench.hdf5")

    bus_entities = []
    load_entities = []
    staticgen_entities = []
    line_entities = []
    externalgrid_entities = [] # only one in the case of simbench ID "1-LV-rural3--0-sw"

    for entity in grid.children:
        match entity.type:
            case "Bus":
                bus_entities.append(entity)
            case "Load":
                load_entities.append(entity)
            case "StaticGen":
                staticgen_entities.append(entity)
            case "Line":
                line_entities.append(entity)
            case "ExternalGrid":
                externalgrid_entities.append(entity)
            case _:
                print("An unknown grid entity type was found: {}".format(entity.type))

    mosaik.util.connect_many_to_one(world, bus_entities, hdf5, "P[MW]", "Q[MVar]", "Vm[pu]", "Va[deg]")
    mosaik.util.connect_many_to_one(world, load_entities, hdf5, "P[MW]", "Q[MVar]")
    mosaik.util.connect_many_to_one(world, staticgen_entities, hdf5, "P[MW]", "Q[MVar]")
    mosaik.util.connect_many_to_one(world, line_entities, hdf5, "I[kA]", "loading[%]")
    mosaik.util.connect_many_to_one(world, externalgrid_entities, hdf5, "P[MW]", "Q[MVar]")

    world.run(until=SIMULATION_DURATION)
