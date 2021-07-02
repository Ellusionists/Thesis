from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from latlong_vrp import append_list_as_row, update_file, makefile, plotgraph,update_fixed
import sys
import pandas as pd
import time
import math

start_time = time.time()


filepath = r'/Users/adityagoel/Documents/Thesis/Vrp-CurrentProgress/'
update_file(filepath)
sitepositions = pd.read_csv(''.join([filepath, 'site_position.csv']))
count   = len(sitepositions)
sapids = sitepositions['SAP_ID'].tolist()
    

# position = pd.read_csv(''.join([filepath,'site_position.csv']), index_col="SAP_ID")
# latlongs = dict( (sap_id,(position.loc[sap_id, 'LONGITUDE'], position.loc[sap_id, 'LATITUDE'] )) for sap_id in sapids) 
# cel = ['SAP_ID']

# for i in latlongs :
#     cel.append(i)

# append_list_as_row(''.join([filepath,'site_latlong.csv']), cel)
# append_list_as_row(''.join([filepath,'site_time.csv']), cel)


# makefile(latlongs,filepath)



def create_data_model(count):
    """Stores the data for the problem."""
    matrix_data = pd.read_csv(''.join([filepath,'site_latlong.csv']), index_col="SAP_ID")
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


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    total_distance = 0
    total_load = 0
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        sap_index = []
        
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} -> '.format(node_index)
            sap_index.append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        plan_output += ' {0} \n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        sap_index.append(manager.IndexToNode(index))
        print(plan_output)
        for z in sap_index:
            print(sapids[z],end=" -> ")
        print("\n")
        total_distance += route_distance
        total_load += route_load
        with open('result.txt', 'a') as f:
            print(plan_output, file=f)
            for z in sap_index:
                print(sapids[z],end=" -> ",file=f)
            print("\n",file = f)

        max_route_distance = max(route_distance, max_route_distance)

    print('Maximum of the route distances: {}'.format(max_route_distance))    
    print('Total distance of all routes: {}'.format(total_distance))
    #print('Total load of all routes: {}'.format(total_load))


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_data_model(count)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # Add Capacity constraint.
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
    # distance_dimension = routing.GetDimensionOrDie(Capacity)
    # distance_dimension.SetGlobalSpanCostCoefficient(10000)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


if __name__ == '__main__':
    main()
    print("-- %s seconds ---" % (time.time() - start_time))
    