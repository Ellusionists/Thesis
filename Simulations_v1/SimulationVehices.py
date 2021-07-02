## Simulation for different routes generated when # of vehicles is changed for a constant demand.

#imports
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from latlong_vrp import append_list_as_row, update_file, makefile, plotgraph,update_fixed
import sys
import pandas as pd
import time
import math



def create_data_model(count):
    """Stores the data for the problem."""
    # matrix_data = pd.read_csv(''.join([filepath,'site_latlong.csv']), index_col="SAP_ID")
    matrix_data = pd.read_csv('newdata.csv')
    matrix = matrix_data.values.tolist()
    data = {}
    data['distance_matrix'] = []
    for i in matrix:   
        data['distance_matrix'].append(i)
    #data['vehicle_capacities'] = [100, 100, 100, 100,100]
    data['num_vehicles'] = 10
    data['depot'] = 0
    data['demands'] = []
    for i in range (count):
        data['demands'].append(1)
    
    num = math.ceil(count/data['num_vehicles'] + 2)
    print(num)
    data['vehicle_capacities'] = []
    for i in range (data['num_vehicles']):
        data['vehicle_capacities'].append(num)
        
    #data['vehicle_capacities'] = [20,20, 20, 20,20,20,20,20,20,20]
    return data





# ---------------------------------------------------------------------------

# Methods to add dimensions to routes; dimensions represent quantities
# accumulated at nodes along the routes. They represent quantities such as
# weights or volumes carried along the route, or distance or times.
# Quantities at a node are represented by "cumul" variables and the increase
# or decrease of quantities between nodes are represented by "transit"
# variables. These variables are linked as follows:

# if j == next(i), cumul(j) = cumul(i) + transit(i) + slack(i)
# where slack is a positive slack variable (can represent waiting times for
# a time dimension).

def demand_callback(from_index):
    """Returns the demand of the node."""
    # Convert from routing variable Index to demands NodeIndex.
    from_node = manager.IndexToNode(from_index)
    return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
    demand_callback)
    routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,  # null capacity slack
    data['vehicle_capacities'],  # vehicle maximum capacities
    True,  # start cumul to zero
    'Capacity')



def vehicle_demand_initialiser(count):
    import random
    vehicle_demands = []
    for i in range(count):
        vehicle_demands.append(round(random.uniform(0.05, 0.95), 3))
    
    with open('data_model_demand.txt', 'w') as f:
        for demand in vehicle_demands:
            f.write(str(demand) +'\n')
        f.close()