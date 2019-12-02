import net_data
import cran_model as cm
import flow_model
import random
import copy
import expran_adapter
import fluidran_utils
import copy
import fluidran_model

class FlowSet:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.flows = []

    def add_flow(self, flow):
        self.flows.append(flow)


def gen_cran_files():
    base_topology = net_data.Topology('top_base_file.json')
    cran_model = cm.CRANModel(base_topology)
    cran_solution = cran_model.solve()
    original_rus = copy.deepcopy(cran_solution.get_rus())
    original_cu = copy.deepcopy(cran_solution.get_cu())
    original_bs = copy.deepcopy(cran_solution.get_base_stations())
    forwarding_nodes = copy.deepcopy(base_topology.get_fowarding_nodes())
    limit = min(len(original_rus), len(original_bs))


    for i in range(limit):
        out_node = random.choice(original_rus)
        original_rus.remove(out_node)
        in_node = random.choice(original_bs)
        original_bs.remove(in_node)

        cu = cran_solution.get_cu()
        new_topology = copy.deepcopy(base_topology)

        for kept_ru in original_rus:
            flow_set = cran_solution.get_flow_set(cu, out_node)

            for flow in flow_set.flows:
                value = flow.value
                for link in flow.path.links:
                    new_topology.get_link(link.source, link.target).decrease_capacity(value)

        flow_model = flow_model.FlowModel(new_topology, cran_solution, cu, [in_node])
        flow_solution = flow_model.solve()
        
        original_rus.append(in_node)
        cran_solution.rus = original_rus
        expran_adapter.convert_cran_solution(new_topology, cran_solution, cu, original_rus, forwarding_nodes, i)
        #cran_solution.save_expran_file();


def gen_fluidran_files():
    base_topology = net_data.Topology('top_base_file.json')
    fluidran_utils.mark_links(base_topology, 'sol_fluidran.json')
    base_topology.build_paths()
    fluidran_solution = fluidran_model.Solution()
    fluidran_solution.load_from_file(base_topology, 'sol_fluidran.json')

    expran_adapter.convert_fluidran_solution(base_topology, fluidran_solution, 0)
    base_topology.draw_graph('fluidran_files/topology_0.png')

    for i in range(1, 6):
        eligible_paths = []
        base_topology.reset_link_colors()
        for a in base_topology.get_nodes():
            for b in base_topology.get_nodes():
                if a.is_central_unit() and b.is_base_station():
                    eligible_paths.extend([x for x in list(filter(lambda x: x.get_num_shared_links() == i, 
                                        base_topology.paths[a.get_id()][b.get_id()]))])
                    '''
                    for path in base_topology.paths[a.get_id()][b.get_id()]:
                        if path.get_num_shared_links() == 1:
                            print('Gotcha! 1')
                        elif path.get_num_shared_links() == 2:
                            print('Gotcha! 2')
                        elif path.get_num_shared_links() == 3:
                            print('Gotcha! 3')
                        elif path.get_num_shared_links() == 4:
                            print('Gotcha! 4')
                        elif path.get_num_shared_links() == 5:
                            print('Gotcha! 5')
                    '''

        chosen_path = random.choice(eligible_paths)
        new_sol = copy.deepcopy(fluidran_solution)
        new_sol.get_flow_set(chosen_path.source, chosen_path.target).add_flow(
            net_data.Flow(-1, chosen_path, 200))

        for link in chosen_path.links:
            link.color = 'yellow'

        expran_adapter.convert_fluidran_solution(base_topology, new_sol, i)
        base_topology.draw_graph('fluidran_files/topology_{}.png'.format(i))         
                

    

if __name__ == '__main__':
    gen_fluidran_files()