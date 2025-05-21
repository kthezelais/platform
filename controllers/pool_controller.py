import libvirt
from pathlib import Path
from settings import \
    RESOURCES_PATH, \
    IMG_DIR, \
    VM_DIR


def get_pool(conn: libvirt.virConnect, name: str) -> libvirt.virStoragePool:
    pool:libvirt.virStoragePool
    
    # Connect/Create StoragePool
    for pool in conn.listAllStoragePools():
        if name == pool.name():
            print(f"StoragePool '{name}' found.", end="\n\n")
            return pool
    
    path = Path(f"{VM_DIR}/{name}")
    if name == "images":
        path = Path(IMG_DIR)
    
    path.mkdir(parents=True, exist_ok=True)

    # Open StoragePool resource definition file
    with open(f"{RESOURCES_PATH}/storage_pool.xml", "r") as file:
        pool_xml = file.read().format(name=path.name, path=path.parent)

    print(f"StoragePool '{path.name}' doesn't seems to exist.")
    print("Creating...\n")

    pool = conn.storagePoolDefineXML(pool_xml, 0)
    if pool is None:
        raise Exception("Failed to define the StoragePool")
    print(f"StoragePool '{path.name}' defined.")

    # Build the pool (creates the directory if not already created)
    pool.build(0)
    print(f"StoragePool directory '{path.parent}/{path.name}' created.")

    # Start the pool
    pool.create()
    print(f"StoragePool '{path.name}' started.")

    # Set to autostart
    pool.setAutostart(1)
    print(f"StoragePool '{path.name}' set to autostart.\n")

    return pool


def delete_pool_by_name(conn:libvirt.virConnect, name:str) -> int:
    pool:libvirt.virStoragePool

    # Check if StoragePool exists
    if name not in conn.listStoragePools():
        raise libvirt.libvirtError(f"StoragePool '{name}' doesn't exist.")
    
    pool = conn.storagePoolLookupByName(name)
    return delete_pool(pool)


def delete_pool(pool:libvirt.virStoragePool) -> int:
    # Check if StoragePool is Volume free
    if len(pool.listVolumes()) > 0:
        raise libvirt.libvirtError(f"Can't delete StoragePool '{pool.name()}': StoragePool stores 1 or more Volumes.")
    
    # Delete StoragePool
    pool.destroy()
    pool.delete()
    pool.undefine()
    print(f"StoragePool '{pool.name()}' successfully deleted.")
    return 0
