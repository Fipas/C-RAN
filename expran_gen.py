import net_data
import cran_model
import flow_model
import random
import copy
import expran_adapter


base_topology = net_data.Topology('top_base_file.json')
cran_model = cran_model.CRANModel(base_topology)
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



    
    



