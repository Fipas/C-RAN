from docplex.mp.model import Model
from docplex.util.environment import get_environment
import net_data


class CRANNode(net_data.Node):
    def __init__(self, node, is_ru, is_cu):
        self.is_ru = bool(is_ru)
        self.is_cu = bool(is_cu)
        super().__init__(node.node_id, node.node_type)


class CRANFlow:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.flows = []

    def add_flow(self, flow):
        self.flows.append(flow)


class CRANSolution:
    def __init__(self):
        self.nodes = []
        self.rus = []
        self.flow_sets = []
        self.base_stations = []
        self.cu = None

    def add_node(self, node):
        self.nodes.append(node)
        if node.is_cu:
            self.cu = node
        elif node.is_ru:
            self.rus.append(node)
        else:
            self.base_stations.append(node)

    def get_base_stations(self):
        return self.base_stations

    def get_nodes(self):
        return self.nodes

    def get_rus(self):
        return self.rus
    
    def get_cu(self):
        return self.cu

    def add_flow_set(self, flow_set):
        self.flow_sets.append(flow_set)

    def get_flow_set(self, source, target):
        return list(filter(lambda x: x.source == source and x.target == target, self.flow_sets))[0]

    def save_expran_file(self):
        pass


class CRANModel:
    def __init__(self, topology):
        self.topology = topology
        self.mdl = self.build_model()
        self.solution = None
        self.solved = False

    def get_solution(self):
        if self.solved:
            return self.solution
        
        self.solution = self.solve()
        self.solved = True
        return self.solution

    def build_model(self):
        mdl = Model(name='CRAN', log_output=True)
        #mdl.parameters.benders.strategy = 3

        x = mdl.binary_var_dict(keys=(node for node in self.topology.get_base_stations()), name='x')
        y = mdl.binary_var_dict(keys=(node for node in self.topology.get_base_stations()), name='y')
        r = mdl.continuous_var_dict(keys=(path for path in self.topology.get_paths()), lb=0, name='r')

        mdl.maximize(mdl.sum(x))

        # Choose one CU
        mdl.add_constraint(mdl.sum(y) == 1)

        # If node is CU, can't be RU
        for node in self.topology.get_base_stations():
            mdl.add_constraint(x[node] <= (1 - y[node]))

        # Satisfy bandwidth demands
        for a in self.topology.get_nodes():
            for b in self.topology.get_nodes():
                if a.is_base_station() and b.is_base_station():
                    mdl.add_constraint(
                        mdl.sum(r[path] for path in self.topology.paths[b.get_id()][a.get_id()]) >= 
                        x[a] * y[b] * 2500)

        # Link capacity constraint
        #for link in self.topology.get_links():
        #    mdl.add_constraint(mdl.sum(r[path] * int(link in path.links) 
        #        for path in self.topology.get_paths()) <=
        #        link.capacity)


        mdl.print_information()
        self.x = x
        self.y = y
        self.r = r
        return mdl
    
    def solve(self):
        self.solved = True
        if self.mdl.solve():
            self.mdl.print_solution()
            self.mdl.report()

            cran_solution = CRANSolution()

            r_values = self.mdl.solution.get_value_dict(self.r)
            x_values = self.mdl.solution.get_value_dict(self.x)
            y_values = self.mdl.solution.get_value_dict(self.y)

            for node in self.topology.get_base_stations():
                is_ru = bool(int(round(x_values[node])))
                is_cu = bool(int(round(y_values[node])))
                cran_solution.add_node(CRANNode(node, is_ru, is_cu))

            flows = 0

            for node in cran_solution.rus:
                flow_set = CRANFlow(cran_solution.cu, node)
                for path in self.topology.paths[cran_solution.cu.get_id()][node.get_id()]:
                    value = round(r_values[path])
                    if value > 0:
                        flow = net_data.Flow(flows, path, value)
                        flows += 1
                        flow_set.add_flow(flow)
                
                cran_solution.add_flow_set(flow_set)

            self.solution = cran_solution
            return cran_solution
        else:
            return None

                

if __name__ == '__main__':
    cran_model = CRANModel(net_data.Topology('top_base_file.json'))
    cran_model.solve()