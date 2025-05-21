import libvirt
from settings import RESOURCES_PATH


def get_network(conn: libvirt.virConnect, name: str) -> libvirt.virNetwork:
    network:libvirt.virNetwork

    # Connect/Create Network Bridge
    for network in conn.listAllNetworks():
        if name == network.name(): 
            print(f"Network Bridge '{name}' found.", end="\n\n")
            return network
    
    print("Creating...\n")

    # Open Network Bridge resource definition file
    with open(f"{RESOURCES_PATH}/network.xml", "r") as file:
        network_xml = file.read().format(name=name)

    network = conn.networkDefineXML(network_xml)
    if network is None:
        raise Exception("Failed to define the Network Bridge.")
    print(f"Network Bridge {name} defined.")

    # Start the Network Bridge
    network.create()
    print(f"Network Bridge '{name}' started.")

    # Set to autostart
    network.setAutostart(1)
    print(f"Network Bridge '{name}' set to autostart.\n")

    return network


def delete_network_by_name(conn:libvirt.virConnect, name:str) -> int:
    network:libvirt.virNetwork

    # Check if Network Bridge exists
    if name not in conn.listNetworks():
        raise libvirt.libvirtError(f"Network Bridge '{name}' doesn't exist.")
    
    network = conn.networkLookupByName(name)
    return delete_network(network)


def delete_network(network:libvirt.virNetwork) -> int:
    network.destroy()
    network.undefine()
    print(f"Network Bridge '{network.name()}' successfully deleted")
    return None
