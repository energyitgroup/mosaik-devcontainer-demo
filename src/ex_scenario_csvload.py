# Example Mosaik scenario simulation
# - CSV Feeder for Household loads with self defined Pandapower network
# - LoadProfile data is from Simbench dataset "1-LV-rural2--0-sw"
# - Output is saved to a HDF5 file

import warnings
import mosaik
import mosaik.util
import pandapower as pp

# just to avoid printing of a warning from pandas dependencies:
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

SIM_CONFIG: mosaik.SimConfig = {
    "hdf5Sim": {"python": "mosaik_hdf5:MosaikHdf5"},
    "GridSim": {"python": "mosaik_components.pandapower:Simulator"},
    "LoadSim": {"python": "mosaik_csv:CSV"}
}

SIMULATION_DURATION = (24 * 3600) * 1 # seconds, 1 day

def getNet():
    """ example network from https://www.pandapower.org/start/#a-short-introduction- """

    #create empty net
    net = pp.create_empty_network()

    #create buses
    bus1 = pp.create_bus(net, vn_kv=20., name="Bus 1")
    bus2 = pp.create_bus(net, vn_kv=0.4, name="Bus 2")
    bus3 = pp.create_bus(net, vn_kv=0.4, name="Bus 3")

    #create bus elements
    pp.create_ext_grid(net, bus=bus1, vm_pu=1.02, name="Grid Connection")

    # in our example we omit the load since we will feed load data to the bus from a CSV:
    #pp.create_load(net, bus=bus3, p_mw=0.100, q_mvar=0.05, name="Load")

    #create branch elements
    pp.create_transformer(net, hv_bus=bus1, lv_bus=bus2, std_type="0.4 MVA 20/0.4 kV", name="Trafo")
    pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=0.1, std_type="NAYY 4x50 SE", name="Line")

    return net


# World Simulation. Define your scenario and run it (with block ensures proper shutdown of all simulators):
with mosaik.World(SIM_CONFIG) as world:

    # Initialize Simulator factories:
    dbsim = world.start("hdf5Sim", step_size=900, duration=SIMULATION_DURATION)
    ppsim = world.start("GridSim", step_size=900) # 15 min intervals
    ldsim = world.start("LoadSim", sim_start="2016-01-01 00:00:00", datafile="src/data/LoadProfile.csv", type="time-based", delimiter=",")

    # Create and initialize instances of Simulators:
    grid = ppsim.Grid(net=getNet())
    hdf5 = dbsim.Database(filename="simresults_ex_scenario_csvload.hdf5")
    house = ldsim.Data.create(1)

    # pandapower objects are not directly usable for connection creation in Mosaik, 
    # so we fetch from mosaik-pandapower wrapper the "entities":
    bus_entities = []
    line_entities = []
    externalgrid_entities = [] # only one in our example from getNet()

    for entity in grid.children:
        match entity.type:
            case "Bus":
                bus_entities.append(entity)
            case "Line":
                line_entities.append(entity)
            case "ExternalGrid":
                externalgrid_entities.append(entity)
            case _:
                print("An unknown grid entity type was found: {}".format(entity.type))

    world.connect(house[0], bus_entities[2], ("H0-C_pload", "P_load[MW]"), transform=lambda relative_value: relative_value * 0.001)
    world.connect(house[0], bus_entities[2], ("H0-C_qload", "Q_load[MVar]"), transform=lambda relative_value: relative_value * 0.001)

    mosaik.util.connect_many_to_one(world, bus_entities, hdf5, "P[MW]", "Q[MVar]", "Vm[pu]", "Va[deg]")
    mosaik.util.connect_many_to_one(world, line_entities, hdf5, "I[kA]", "loading[%]")
    mosaik.util.connect_many_to_one(world, externalgrid_entities, hdf5, "P[MW]", "Q[MVar]")
    mosaik.util.connect_many_to_one(world, house, hdf5, "H0-C_pload", "H0-C_qload", transform=lambda relative_value: relative_value * 0.001)

    world.run(until=SIMULATION_DURATION)
