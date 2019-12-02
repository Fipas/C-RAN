import json
import net_data

def mark_links(topology, filename):
    with open(filename) as json_file:
        data = json.load(json_file)

        for split in data['splits_fluidran']:
            node_id = int(split['node'])
            node_type = split['type']

            topology.get_node(node_id).set_type(node_type)


        for flow in data['flows']:
            path = flow['path']
            for link in path['seq']:
                source = int(link[0])
                target = int(link[1])
                topology.get_link(source, target).set_used(True)

