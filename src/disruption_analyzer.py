"""
This code reads the json supply chain data and creates a graph. Then,
users can use various commands to make changes to this model, and
the model will predict how those changes can affect other parts of the model.
I wrote this program to demonstrate my interest in Bloomberg and Bloomberg tech,
and to demonstrate my problem solving skills.
Author: Farhang Rouhi
"""
import json


class Node:
    """This is the node class that represents a company and stores company metadata"""
    def __init__(self, name, product, production_volume):
        """
        This is the constructor of Node class
        :param name: name or id of the company
        :param product: product of this company
        :param production_volume: production volume
        """
        self.name = name
        self.product = product
        self.production_volume = production_volume
        self.suppliers = []
        self.costumers = []
        self.production_drop = 0
        self.market_shrinkage = 0
        self.sale_drop = 0
        self.out_edge_capacity_drop = {}
        self.in_edge_capacity_drop = {}


class NodeWrapper:
    """This wrapper class is used to keep track of the depth and the path in BFS"""
    def __init__(self, node, depth=0, visited_by=None):
        """
        This is the constructor for NodeWrapper class
        :param node: the node that this class wraps
        :param depth: depth of the path to this node
        :param visited_by: which nodes have visited this node,
        and how many times (optional)
        """
        if visited_by is None:
            visited_by = {}
        self.node = node
        self.depth = depth
        self.visited_by = visited_by


def build_graph():
    """
    This function builds the graph using the json file
    :return: generated graph
    """
    file = open("../data/data.json", "r")
    data = json.load(file)
    node_dict = {}
    for id in data:
        node_dict[id] = Node(data[id]["name"], data[id]["product"], data[id]["production_volume"])
    for id in data:
        current_node = node_dict[id]
        for costumer_id in data[id]["costumers"]:
            current_node.costumers.append(node_dict[str(costumer_id)])
            current_node.out_edge_capacity_drop[node_dict[str(costumer_id)].name] = 0
        for supplier_id in data[id]["suppliers"]:
            current_node.suppliers.append(node_dict[str(supplier_id)])
            current_node.in_edge_capacity_drop[node_dict[str(supplier_id)].name] = 0
    return node_dict


def calculate_production_drop(node,reduction_factor):
    """
    This function calculates the production drop of a node
    :param node: the node that we want to update
    :param reduction_factor: by what factor we want to reduce the affect
    """
    original_supply = {}
    dropped_supply = {}
    for supplier in node.suppliers:
        if supplier.product not in original_supply:
            original_supply[supplier.product] = 0
            dropped_supply[supplier.product] = 0
        supply_volume_approximation = supplier.production_volume
        # supply_volume_approximation = supplier.production_volume / len(supplier.costumers) # Alternative approximation method
        original_supply[supplier.product] += supply_volume_approximation
        dropped_supply[supplier.product] += supply_volume_approximation * (
                (100 - node.in_edge_capacity_drop[supplier.name]) / 100)
    drops_list = []
    for key in original_supply:
        drops_list.append((1 - (dropped_supply[key] / original_supply[key])) * 100)
    node.production_drop = max(drops_list) * ((100 - reduction_factor) / 100)


def modified_bfs(start_id, node_dict, iteration_limit, depth_limit, reduction_factor):
    """
    This is a modified implementation of breadth-first search algorithm that
    follows the chains of costumers starting from a node, and determines if
    they are effected by the supply chain disruption
    :param start_id: the name of the node we want to start from (the node that was disrupted)
    :param node_dict: dictionary mapping names to node pointers
    :param iteration_limit: maximum number of traversing cycles
    :param depth_limit: maximum depth to explore
    :param reduction_factor: how much we want to reduce the affect by
    """
    queue = [NodeWrapper(node_dict[start_id])]
    while queue:
        node_wrapper = queue.pop(0)
        node = node_wrapper.node
        for costumer in node.costumers:
            if costumer.name not in node_wrapper.visited_by:
                node_wrapper.visited_by[costumer.name] = 0
            visit_count = node_wrapper.visited_by[costumer.name]
            if visit_count < iteration_limit and node_wrapper.depth < depth_limit:
                if node.production_drop > node.out_edge_capacity_drop[costumer.name]:
                    node.out_edge_capacity_drop[costumer.name] = node.production_drop
                    costumer.in_edge_capacity_drop[node.name] = node.production_drop
                    calculate_production_drop(costumer, reduction_factor)
                    costumer_wrapper = NodeWrapper(costumer, node_wrapper.depth, node_wrapper.visited_by)
                    if node.name not in costumer_wrapper.visited_by:
                        costumer_wrapper.visited_by[node.name] = 0
                    costumer_wrapper.visited_by[node.name] += 1
                    costumer_wrapper.depth += 1
                    queue.append(costumer_wrapper)


def interactive_shell(node_dict):
    """
    This function keeps reading and executing user commands.
    help prints all available commands
    :param node_dict: dictionary mapping names to node pointers
    """
    iteration_limit = 1
    depth_limit = 10
    reduction_factor = 5
    inp = input('Welcome! For available commands use "help"')
    while inp != "exit":
        splitted_inp = inp.split(" ")
        if inp == "help":
            print("remove company [company_name]\n"
                  "remove relation [supplier_name] [costumer_name]\n"
                  "reduce production [production_drop_percentage] [company_name]\n"
                  "reduce relation_capacity [capacity_drop_percentage] [supplier_name] [costumer_name]\n"
                  "shrink market [market_shrinkage_percentage] [company_name]\n"
                  "predict [company_name]\n"
                  "set iteration_limit [iteration_limit]\n"
                  "set depth_limit [depth_limit]\n"
                  "set reduction_factor [reduction_factor]\n"
                  "config\n"
                  "refresh\n"
                  "exit\n"
                  "help")
        elif inp == "refresh":
            node_dict = build_graph()
        elif splitted_inp[0] == "predict":
            if splitted_inp[1] in node_dict:
                node = node_dict[splitted_inp[1]]
                print("Company:", node.name)
                print("Production Drop:", node.production_drop)
                print("Market Shrinkage:", node.market_shrinkage)
                print("Sale Drop:", node.sale_drop)
            else:
                print("ERROR: the company is not present in the model!")
        elif "remove company" in inp:
            if splitted_inp[2] in node_dict:
                node = node_dict[splitted_inp[2]]
                node.production_drop = 100
                node.sale_drop = 100
                node.market_shrinkage = 100
                modified_bfs(splitted_inp[2], node_dict, iteration_limit, depth_limit, reduction_factor)
            else:
                print("ERROR: the company is not present in the model!")
        elif "remove relation" in inp:
            supplier = node_dict[splitted_inp[2]]
            costumer = node_dict[splitted_inp[3]]
            if costumer in supplier.costumers:
                supplier.out_edge_capacity_drop[costumer.name] = 100
                costumer.in_edge_capacity_drop[supplier.name] = 100
                calculate_production_drop(costumer, reduction_factor)
                modified_bfs(splitted_inp[3], node_dict, iteration_limit, depth_limit, reduction_factor)
            else:
                print("ERROR: the relation is not present in the model!")
        elif "reduce production" in inp:
            if splitted_inp[3] in node_dict:
                drop = float(splitted_inp[2])
                node = node_dict[splitted_inp[2]]
                node.production_drop = drop
                modified_bfs(splitted_inp[2], node_dict, iteration_limit, depth_limit, reduction_factor)
            else:
                print("ERROR: the company is not present in the model!")
        elif "reduce relation_capacity" in inp:
            supplier = node_dict[splitted_inp[3]]
            costumer = node_dict[splitted_inp[4]]
            drop = float(splitted_inp[2])
            if costumer in supplier.costumers:
                if drop>supplier.out_edge_capacity_drop[costumer.name]:
                    supplier.out_edge_capacity_drop[costumer.name] = 100
                    costumer.in_edge_capacity_drop[supplier.name] = 100
                    calculate_production_drop(costumer, reduction_factor)
                    modified_bfs(splitted_inp[4], node_dict, iteration_limit, depth_limit, reduction_factor)
            else:
                print("ERROR: the relation is not present in the model!")
        elif "set iteration_limit" in inp:
            iteration_limit = float(splitted_inp[2])
        elif "set depth_limit" in inp:
            depth_limit = float(splitted_inp[2])
        elif "set reduction_factor" in inp:
            reduction_factor = float(splitted_inp[2])
        elif "config" in inp:
            print("depth_limit",depth_limit)
            print("reduction_factor",reduction_factor)
            print("iteration_limit",iteration_limit)
        inp = input()


node_dict = build_graph()
interactive_shell(node_dict)
