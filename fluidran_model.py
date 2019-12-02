import json
import net_data

class FlowSet:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.flows = []

    def add_flow(self, flow):
        self.flows.append(flow)


class Solution:
    def __init__(self):
        self.flow_sets = []
        self.forwarding_nodes = []
        self.base_stations = []
        self.central_unit = None
        self.flow_sets = []

    def add_node(self, node):
        if node.is_central_unit():
            self.central_unit = node
        elif node.is_base_station():
            self.base_stations.append(node)
        else:
            self.forwarding_nodes.append(node)

    def make_flow_sets(self):
        for node in self.base_stations:
            self.flow_sets.append(FlowSet(self.central_unit, node))

    def get_flow_set(self, source, target):
        if isinstance(source, int):
            return list(filter(lambda x: x.source.get_id() == source and 
                    x.target.get_id() == target, self.flow_sets))[0]
        else:
            return list(filter(lambda x: x.source == source and 
                    x.target == target, self.flow_sets))[0]

    def get_base_stations(self):
        return self.base_stations
    
    def get_central_unit(self):
        return self.central_unit

    def get_forwarding_nodes(self):
        return self.forwarding_nodes

    def add_flow_set(self, flow_set):
        self.flow_sets.append(flow_set)

    def load_from_file(self, topology, filename):
        with open(filename) as json_file:
            data = json.load(json_file)

            for node in topology.get_nodes():
                self.add_node(node)

            self.make_flow_sets()

            flow_id = 1
            for flow in data['flows']:
                path = flow['path']
                value = float(flow['value'])
                f_source = int(path['source'])
                f_target = int(path['target'])
                link_list = []
                for link in path['seq']:
                    source = int(link[0])
                    target = int(link[1])
                    link_list.append((min(source, target), max(source, target)))
                
                topology_path = topology.get_path_by_links(link_list)

                if topology_path == None:
                    print('Failed to find path for flow')
                    exit()

                self.get_flow_set(f_source, f_target).add_flow(net_data.Flow(flow_id, topology_path, value))
                
