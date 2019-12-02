import json
import math
import shutil
import os

class VM():
  def __init__(self, vm_id, cpu, ram):
    self.vm_id = vm_id
    self.cpu = cpu
    self.ram = ram
    self.containers = []

  def add_container(self, ctn):
    self.containers.append(ctn)
    self.cpu += ctn.cpu
    self.ram += ctn.ram


class Container():
  def __init__(self, ctn_id, cpu, ram):
    self.ctn_id = ctn_id
    self.cpu = cpu
    self.ram = ram

def convert_cran_solution(topology, cran_solution, cu, rus, forwarding_nodes, file_n):
    infra = {}
    services = {}

    print("CU NUMBER {}".format(cu.get_id()))

    services["services"] = []
    flows_data = []

    infra["user"] = "John"
    infra["nodes"] = []
    infra["links"] = []

    nodes_dict = {}
    nodes_vms = {}

    link_nodes = {}
    link_nodes["linkType"] = "Nodes"
    link_nodes["Connections"] = []

    link_num = 1

    for link in topology.get_links():
        link_data = {
            "linkNumber": link_num,
            "from_node": link.source,
            "to_node": link.target,
            "delay":  float(link.delay) / 1000,
            "capacity": float(link.capacity) / 20
        }

        link_nodes["Connections"].append(link_data)
        link_num += 1

        link_data = {
            "linkNumber": link_num,
            "from_node": link.target,
            "to_node": link.source,
            "delay":  float(link.delay) / 1000,
            "capacity": float(link.capacity) / 20
        }

        #print(link_data)

        link_num += 1

    infra["links"].append(link_nodes)


    for node in forwarding_nodes:
        node_data = {
            "nodeNumber": node.get_id(),
            "nodeType": "Forwarding"
        }

        nodes_dict[node.get_id()] = node_data

    vm_num = 1
    ctn_num = 1

    node_data = {
        "nodeNumber": cu.get_id(),
        "nodeType": "MEC_Server"
    }

    nodes_dict[cu.get_id()] = node_data
    nodes_dict[cu.get_id()]["vms"] = []

    nodes_vms[cu.get_id()] = VM(vm_num, 0, 0)
    vm_num += 1


    for node in rus:
        node_data = {
            "nodeNumber": node.get_id(),
            "nodeType": "Base_Station"
        }

        nodes_dict[node.get_id()] = node_data
        nodes_dict[node.get_id()]["vms"] = []

        nodes_vms[node.get_id()] = VM(vm_num, 0, 0)
        vm_num += 1



    flow_id = 1

    s = cu
    for t in rus:     
        for flow in cran_solution.get_flow_set(s, t).flows:
            #ctn_num_source = len(nodes_vms[int(flow["path"]["source"])].containers) + 1
            #ctn_num_target = len(nodes_vms[int(flow["path"]["target"])].containers) + 1
            ctn_num_source = ctn_num
            ctn_num_target = ctn_num + 1
            ctn_num += 2

            flow_data = {
                "flowIdentifier": flow_id,
                "bandwidth": flow.value / 20,
                "nodes": list(map(lambda x: x.get_id(), flow.path.nodes)),
                "ctn_source_num": ctn_num_source,
                "ctn_target_num": ctn_num_target,
            }

            flows_data.append(flow_data)

            flow_id += 1

            nodes_vms[flow.path.source.get_id()].add_container(Container(ctn_num_source, 0.5, 512))
            nodes_vms[flow.path.target.get_id()].add_container(Container(ctn_num_target, 0.2, 512))


    for node in [cu]:
        vm = {
            "vmNumber": nodes_vms[node.get_id()].vm_id,
            "cpu": int(math.ceil(nodes_vms[node.get_id()].cpu * 1.10)),
            "ram": int(math.ceil(nodes_vms[node.get_id()].ram * 1.10)),
            "containers": []
        }

        for container in nodes_vms[node.get_id()].containers:
            ctn = {
                "ctnNumber": container.ctn_id,
                "cpu": container.cpu,
                "ram": container.ram
            }

            vm["containers"].append(ctn)

        nodes_dict[node.get_id()]["vms"].append(vm)

    for node in rus:
        vm = {
            "vmNumber": nodes_vms[node.get_id()].vm_id,
            "cpu": int(math.ceil(nodes_vms[node.get_id()].cpu * 1.10)),
            "ram": int(math.ceil(nodes_vms[node.get_id()].ram * 1.10)),
            "containers": []
        }

        for container in nodes_vms[node.get_id()].containers:
            ctn = {
                "ctnNumber": container.ctn_id,
                "cpu": container.cpu,
                "ram": container.ram
            }

            vm["containers"].append(ctn)

        nodes_dict[node.get_id()]["vms"].append(vm)

    for node in nodes_dict:
        infra["nodes"].append(nodes_dict[node])

    services["services"].append({"flows": flows_data})

    infra_file = open("cran_files/infra_{}.json".format(file_n), "w+")
    json.dump(infra, infra_file, indent=4)
    infra_file.close()

    services_file = open("cran_files/services_{}.json".format(file_n), "w+")
    json.dump(services, services_file, indent=4)
    services_file.close()


def convert_fluidran_solution(topology, sol, file_n):
    infra = {}
    services = {}
    cu = sol.get_central_unit()

    #print("CU NUMBER {}".format(sol.get_central_unit().get_id()))

    services["services"] = []
    flows_data = []

    infra["user"] = "John"
    infra["nodes"] = []
    infra["links"] = []

    nodes_dict = {}
    nodes_vms = {}

    link_nodes = {}
    link_nodes["linkType"] = "Nodes"
    link_nodes["Connections"] = []

    link_num = 1

    for link in topology.get_links():
        link_data = {
            "linkNumber": link_num,
            "from_node": link.source,
            "to_node": link.target,
            "delay":  float(link.delay) / 1000,
            "capacity": float(link.capacity) / 20
        }

        link_nodes["Connections"].append(link_data)
        link_num += 1

        link_data = {
            "linkNumber": link_num,
            "from_node": link.target,
            "to_node": link.source,
            "delay":  float(link.delay) / 1000,
            "capacity": float(link.capacity) / 20
        }

        #print(link_data)

        link_num += 1

    infra["links"].append(link_nodes)


    for node in sol.get_forwarding_nodes():
        node_data = {
            "nodeNumber": node.get_id(),
            "nodeType": "Forwarding"
        }

        nodes_dict[node.get_id()] = node_data

    vm_num = 1
    ctn_num = 1

    node_data = {
        "nodeNumber": cu.get_id(),
        "nodeType": "MEC_Server"
    }

    nodes_dict[cu.get_id()] = node_data
    nodes_dict[cu.get_id()]["vms"] = []

    nodes_vms[cu.get_id()] = VM(vm_num, 0, 0)
    vm_num += 1


    for node in sol.get_base_stations():
        node_data = {
            "nodeNumber": node.get_id(),
            "nodeType": "Base_Station"
        }

        nodes_dict[node.get_id()] = node_data
        nodes_dict[node.get_id()]["vms"] = []

        nodes_vms[node.get_id()] = VM(vm_num, 0, 0)
        vm_num += 1



    flow_id = 1

    s = cu
    for t in sol.get_base_stations():     
        for flow in sol.get_flow_set(s, t).flows:
            #ctn_num_source = len(nodes_vms[int(flow["path"]["source"])].containers) + 1
            #ctn_num_target = len(nodes_vms[int(flow["path"]["target"])].containers) + 1
            ctn_num_source = ctn_num
            ctn_num_target = ctn_num + 1
            ctn_num += 2

            flow_data = {
                "flowIdentifier": flow_id,
                "bandwidth": flow.value / 20,
                "nodes": list(map(lambda x: x.get_id(), flow.path.nodes)),
                "ctn_source_num": ctn_num_source,
                "ctn_target_num": ctn_num_target,
            }

            flows_data.append(flow_data)

            flow_id += 1

            nodes_vms[flow.path.source.get_id()].add_container(Container(ctn_num_source, 0.5, 512))
            nodes_vms[flow.path.target.get_id()].add_container(Container(ctn_num_target, 0.2, 512))


    for node in [cu]:
        vm = {
            "vmNumber": nodes_vms[node.get_id()].vm_id,
            "cpu": int(math.ceil(nodes_vms[node.get_id()].cpu * 1.10)),
            "ram": int(math.ceil(nodes_vms[node.get_id()].ram * 1.10)),
            "containers": []
        }

        for container in nodes_vms[node.get_id()].containers:
            ctn = {
                "ctnNumber": container.ctn_id,
                "cpu": container.cpu,
                "ram": container.ram
            }

            vm["containers"].append(ctn)

        nodes_dict[node.get_id()]["vms"].append(vm)

    for node in sol.get_base_stations():
        vm = {
            "vmNumber": nodes_vms[node.get_id()].vm_id,
            "cpu": int(math.ceil(nodes_vms[node.get_id()].cpu * 1.10)),
            "ram": int(math.ceil(nodes_vms[node.get_id()].ram * 1.10)),
            "containers": []
        }

        for container in nodes_vms[node.get_id()].containers:
            ctn = {
                "ctnNumber": container.ctn_id,
                "cpu": container.cpu,
                "ram": container.ram
            }

            vm["containers"].append(ctn)

        nodes_dict[node.get_id()]["vms"].append(vm)

    for node in nodes_dict:
        infra["nodes"].append(nodes_dict[node])

    services["services"].append({"flows": flows_data})

    infra_file = open("fluidran_files/infra_{}.json".format(file_n), "w+")
    json.dump(infra, infra_file, indent=4)
    infra_file.close()

    services_file = open("fluidran_files/services_{}.json".format(file_n), "w+")
    json.dump(services, services_file, indent=4)
    services_file.close()
