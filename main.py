import libvirt
from pathlib import Path
from controllers.pool_controller import get_pool
from controllers.network_controller import get_network
from controllers.image_controller import get_image_path, import_image
from controllers.vm_controller import \
    create_volume, \
    create_cloud_init_disk, \
    create_virtual_machine
from settings import \
    WORK_DIR, \
    IMG_DIR, \
    VM_DIR, \
    DEFAULT_VM_NAME, \
    DEFAULT_OS_VARIANT, \
    NETWORK_NAME, \
    LIBVIRT_PERMISSION


# Check if WORK_DIR / IMG_DIR / VM_DIR exists
if not WORK_DIR.exists() or not IMG_DIR.exists() or not VM_DIR.exists():
    raise Exception(f"WORK_DIR, IMG_DIR or VM_DIR doesn't exists.")


# VM Configuration
NEW_VM_NAME = DEFAULT_VM_NAME
OS_VARIANT = DEFAULT_OS_VARIANT
VCPUS = 2
MEMORY = 2048
NEW_VM_DIR = Path(f"{VM_DIR}/{NEW_VM_NAME}")


# Connect to libvirt
conn = libvirt.open(f"qemu:///{LIBVIRT_PERMISSION}")
if conn is None:
    raise Exception(f"Failed to open connection to qemu:///{LIBVIRT_PERMISSION}")


# Create/Get Images StoragePool
storage_pool_img = get_pool(
    conn=conn,
    name="images"
)


# Download base image
import_image(
    os_variant=OS_VARIANT
)


# Create/Get StoragePool
storage_pool_vm = get_pool(
    conn=conn,
    name=NEW_VM_NAME
)


# Generate user-data/meta-data in NEW_VM_DIR
create_cloud_init_disk(
    vm_name=NEW_VM_NAME
)


# Create Volume
volume_vm = create_volume(
    storage_pool=storage_pool_vm,
    vm_name=NEW_VM_NAME,
    base_img=get_image_path(OS_VARIANT)
)


# Create/Get Network
network = get_network(
    conn=conn,
    name=NETWORK_NAME
)


## Create Domaine
virtual_machine = create_virtual_machine(
    conn=conn,
    volume=volume_vm,
    network=network,
    name=NEW_VM_NAME,
    vcpu=VCPUS,
    memory=MEMORY
)
