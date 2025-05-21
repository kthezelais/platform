import libvirt
import subprocess, crypt
from pathlib import Path
from settings import \
    RESOURCES_PATH, \
    DEFAULT_USERNAME, \
    DEFAULT_PASSWORD, \
    DEFAULT_VM_NAME, \
    VM_DIR


def create_cloud_init_disk(
        vm_name: str,
        login_user: str = DEFAULT_USERNAME,
        login_pass: str = DEFAULT_PASSWORD) -> Path:
    # Generate user-data/meta-data in vm_dir
    vm_dir = Path(f"{VM_DIR}/{vm_name}")
    try:
        # Setup user-data / meta-data
        with open(f"{RESOURCES_PATH}/cloud-init-tpl/user-data.yaml", "r") as file:
            salt = crypt.mksalt(crypt.METHOD_SHA512)
            user_data = file.read().format(username=login_user, password=crypt.crypt(login_pass, salt))

        # Create user-data file
        with open(f"{vm_dir}/user-data.yaml", "w") as file:
            file.write(user_data)

        # Create meta-data file
        with open(f"{vm_dir}/meta-data.yaml", "w") as file:
            pass
    except Exception as e:
        print(f"Couldn't create VM directory '{vm_dir}': {e}")
        exit(1)

    try:
        # Create cloud-init iso from user-data file
        subprocess.run(["cloud-localds", f"{vm_dir}/seed.iso", f"{vm_dir}/user-data.yaml", f"{vm_dir}/meta-data.yaml"])
    except subprocess.CalledProcessError as e:
        print(e)


def create_volume(
        storage_pool: libvirt.virStoragePool,
        vm_name: str,
        base_img: Path) -> libvirt.virStorageVol:
    # Create Volume
    with open(f"{RESOURCES_PATH}/volume.xml", "r") as file:
        volume_xml = file.read().format(volume_name=f"{vm_name}.qcow2", base_img=f"{base_img}")
    return storage_pool.createXML(volume_xml, 0)


def create_virtual_machine(
        conn: libvirt.virConnect,
        volume: libvirt.virStorageVol,
        network: libvirt.virNetwork,
        name:str = DEFAULT_VM_NAME,
        vcpu:int = 1,
        memory:int = 1) -> libvirt.virDomain:
    # Load VM XML configuration
    with open(f"{RESOURCES_PATH}/virtual_machine.xml", "r") as file:
        vm_xml = file.read().format(
            name=name,
            memory=memory,
            vcpu=vcpu,
            vm_disk_path=volume.path(),
            bridge_name=network.bridgeName(),
            cloud_init_iso=f"{Path(volume.path()).parent}/seed.iso"
        )
    return conn.createXML(vm_xml)


def delete_vm_by_name(conn:libvirt.virConnect, name:str) -> libvirt.virDomain:
    # Loop over all existing VMs
    for vm in conn.listAllDomains():
        if vm.name() == name:
            # Return the deleted VM
            return delete_vm(vm)
    
    print(f"VirtualMachine '{name}' not found.\n")
    return None


def delete_vm(vm:libvirt.virDomain):
    # Try to stop and delete VM
    try:
        vm.XMLDesc()
        vm.reset()
        vm.destroy()
    except libvirt.libvirtError:
        print(f"VirtualMachine '{vm.name()}' not found.\n")

    print(f"VirtualMachine '{vm.name()}' successfully destroyed.\n")
    return vm
