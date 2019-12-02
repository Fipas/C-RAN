from enum import Enum
import random
import json
import networkx as nx
import itertools
import matplotlib.pyplot as plt

class NodeType(Enum):
    BaseStation = 1
    CentralUnit = 2
    Forwarding = 3

class Topology:
    def __init__(self, filename):
        self.nodes = []
        self.links = []
        self.load(filename)
        

    def load(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)

            for node in data["nodes"]:
                self.nodes.append(Node(int(node["id"])))
            
            for key in data["pos"]:
                self.get_node(int(key)).set_pos(tuple(data["pos"][key]))

            for link in data["links"]:
                from_id = int(link["from_id"])
                to_id = int(link["to_id"])
                capacity = float(link["capacity"]) * 1000
                delay = int(link["delay"])
                self.links.append(Link(from_id, to_id, capacity, delay))

                self.get_node(from_id).add_adjacent_node(self.get_node(to_id))
                self.get_node(to_id).add_adjacent_node(self.get_node(from_id))

            self.paths = {}
            for a in self.nodes:
                self.paths[a.get_id()] = {}
                for b in self.nodes:
                    self.paths[a.get_id()][b.get_id()] = []

            #self.draw_base_stations(30)
            #self.build_paths()

    def get_links(self):
        return self.links

    def reset_link_colors(self):
        for link in self.links:
            link.color = 'black'

    def get_link(self, source, target):
        #for link in self.links:
        #    print("Source: {}, Target: {}, Capacity: {}, Delay: {}".format(link.source, link.target, link.capacity, link.delay))
        return list(filter(lambda x: (x.source == source and x.target == target) or
                                    (x.target == source and x.source == target), self.links))[0]
         

    def draw_base_stations(self, percentage):
        drawn_num = 0
        num = round(len(self.nodes) * percentage / 100)

        for node in self.nodes:
            node.set_type(NodeType.Forwarding) 
    
        while drawn_num < num:
            node = random.choice(self.nodes)
            if node.get_type() != NodeType.BaseStation:
                node.set_type(NodeType.BaseStation)
                drawn_num += 1


    def build_paths(self):
        graph = nx.Graph()
        num_paths = 0

        for node in self.nodes:
            graph.add_node(node.get_id())
        
        for link in self.links:
            graph.add_edge(link.source, link.target)
        
        for a in self.nodes:
            for b in self.nodes:
                if a.is_base_station() and b.is_base_station():
                    for path in nx.all_simple_paths(graph, source=a.get_id(), target=b.get_id()):
                        #print(path)
                        nodes = []
                        links = []

                        for node in path:
                            nodes.append(self.get_node(node))

                        for i in range(1, len(path)):
                            source = path[i - 1]
                            target = path[i]
                            link = self.get_link(source, target)
                            links.append(link)

                        self.paths[a.get_id()][b.get_id()].append(Path(num_paths, nodes, links))
                        num_paths += 1


    def add_node(self, node):
        self.nodes[node.node_id] = node

    def get_node(self, node_id):
        return self.nodes[node_id]
    
    def get_nodes(self):
        return self.nodes

    def get_paths(self):
        paths = []
        for a in self.paths.keys():
            for b in self.paths.keys():
                paths.append(self.paths[a][b])

        paths = list(itertools.chain.from_iterable(paths))
        #print(paths)
        return paths

    def get_base_stations(self):
        return list(filter(lambda x: x.is_base_station(), self.nodes))

    def get_fowarding_nodes(self):
        return list(filter(lambda x: not x.is_base_station(), self.nodes))

    def get_path_by_links(self, link_list):
        sorted_link_list = list(map(lambda x: (min(x[0], x[1]), max(x[0], x[1])), link_list))
        for path in self.get_paths():
            cmp_link_list = []
            for link in path.links:
                cmp_link_list.append((min(link.source, link.target), max(link.source, link.target)))
            if sorted_link_list == cmp_link_list:
                return path

        return None

    def draw_graph(self, filename):
        graph = nx.Graph()
        color_map = []
        pos_map = {}
        edge_color = []

        for node in self.get_nodes():
            if node.is_base_station() and not node.is_central_unit():
                color_map.append('black')
            elif node.is_central_unit():
                color_map.append('blue')
            else:
                color_map.append('red')

            pos_map[node.get_id()] = list(node.get_pos())
            #print(list(node.get_pos()))
            graph.add_node(node.get_id())

        for link in self.get_links():
            graph.add_edge(link.source, link.target)
            edge_color.append(link.color)

        nx.draw(graph, with_labels=False, pos=pos_map, node_color=color_map, edge_color=edge_color)
        plt.savefig(filename, format="PNG")
        plt.cla() 
        plt.clf() 
        plt.close('all')


class Link:
    def __init__(self, source, target, capacity, delay):
        self.source = source
        self.target = target
        self.capacity = capacity
        self.delay = delay
        self.used = False
        self.color = 'black'

    
    def get_capacity(self):
        return self.capacity
    
    def set_capacity(self, capacity):
        self.capacity = capacity

    def decrease_capacity(self, value):
        self.capacity -= value

    def set_used(self, used):
        self.used = used

    def is_used(self):
        return self.used


class Flow:
    def __init__(self, flow_id, path, value):
        self.flow_id = flow_id
        self.path = path
        self.value = value


class Path:
    def __init__(self, path_id, nodes, links):
        self.path_id = path_id
        self.nodes = nodes
        self.links = links
        self.source = nodes[0]
        self.target = nodes[len(nodes) - 1]
        self.aggregate_delay = self.compute_aggregate_delay()


    def compute_aggregate_delay(self):
        delay = 0
        for link in self.links:
            delay += link.delay
        return delay
    
    def get_num_shared_links(self):
        return len(list(filter(lambda x: x.is_used(), self.links)))

    def are_links_shared(self, path):
        return len(set(self.links).intersection(path.links)) > 0

    


class Node:
    def __init__(self, node_id, node_type=NodeType.Forwarding):
        self.node_id = node_id
        self.node_type = node_type
        self.adjacent_nodes = [] 
        self.pos = ()

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def add_adjacent_node(self, node):
        self.adjacent_nodes.append(node)

    def get_adjacent_nodes(self):
        return self.adjacent_nodes

    def get_id(self):
        return self.node_id

    def get_type(self):
        return self.node_type
    
    def set_type(self, node_type):
        if isinstance(node_type, str):
            if node_type == "CU":
                node_type = NodeType.CentralUnit
            elif node_type == "RU":
                node_type = NodeType.BaseStation

        self.node_type = node_type

    def is_base_station(self):
        return self.node_type == NodeType.BaseStation or self.is_central_unit()

    def is_central_unit(self):
        return self.node_type == NodeType.CentralUnit

    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        return self.node_id == other.node_id


if __name__ == '__main__':
    t = Topology('top_base_file.json')
    for path in t.get_paths():
        pass
        #print("Id {}".format(path.path_id))
        #print(path)


