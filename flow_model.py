from docplex.mp.model import Model
from docplex.util.environment import get_environment
import net_data
import cran_model
import itertools

class FlowModel:
    def __init__(self, topology, cran_solution, source, target):
        self.topology = topology
        self.cran_solution = cran_solution
        self.source = source
        self.target = target
        self.paths = []        

        for t in target:
            self.paths.append(topology.paths[self.source.get_id()][t.get_id()])
            self.paths = list(itertools.chain.from_iterable(self.paths))

        self.mdl = self.build_model()


    def build_model(self):
        mdl = Model(name='Flow model', log_output=True)
        #mdl.parameters.benders.strategy = 3

        r = mdl.continuous_var_dict(keys=(path for path in self.paths), lb=0, name='r')
        self.r = r

        mdl.maximize(mdl.sum(r))

        # Satisfy bandwidth demands
        for t in self.target:
            mdl.add_constraint(
                mdl.sum(r[path] for path in self.topology.paths[self.source.get_id()][t.get_id()]) <= 2500)

        # Link capacity constraint
        for link in self.topology.get_links():
            mdl.add_constraint(mdl.sum(r[path] * int(link in path.links) 
                for path in self.paths) <= link.capacity)

        mdl.print_information()
        return mdl
    
    def solve(self):
        if self.mdl.solve():
            self.mdl.print_solution()
            self.mdl.report()

            r_values = self.mdl.solution.get_value_dict(self.r)

            flows = 0

            s = self.source
            for t in self.target:
                flow_set = cran_model.CRANFlow(s, t)
                for path in self.topology.paths[s.get_id()][t.get_id()]:
                    value = round(r_values[path])
                    if value > 0:
                        flow = net_data.Flow(flows, path, value)
                        flows += 1
                        flow_set.add_flow(flow)
                
                self.cran_solution.add_flow_set(flow_set)

            return self.cran_solution
        else:
            return None

#flow_model = FlowModel(net_data.Topology('top_base_file.json'))
#flow_model.solve()