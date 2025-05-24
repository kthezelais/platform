import libvirt
from pathlib import Path
from controllers.pool_controller import get_pool
from controllers.network_controller import get_network
from controllers.image_controller import get_image_path, import_image
from controllers.domain_controller import \
    create_volume, \
    create_cloud_init_disk, \
    create_domain
from settings import \
    WORK_DIR, \
    IMG_DIR, \
    VM_DIR, \
    DEFAULT_VM_NAME, \
    DEFAULT_OS_VARIANT, \
    NETWORK_NAME, \
    LIBVIRT_PERMISSION, \
    DEFAULT_USERNAME, \
    DEFAULT_PASSWORD


def create_virtual_machine(
        vm_name: str = DEFAULT_VM_NAME,
        os_variant: str = DEFAULT_OS_VARIANT,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        network: str = NETWORK_NAME,
        vcpu: int = 2,
        memory: int = 2048
        ) -> libvirt.virDomain:
    # Check if WORK_DIR / IMG_DIR / VM_DIR exists
    if not WORK_DIR.exists() or not IMG_DIR.exists() or not VM_DIR.exists():
        raise Exception(f"WORK_DIR, IMG_DIR or VM_DIR doesn't exists.")

    # Connect to libvirt
    conn = libvirt.open(f"qemu:///{LIBVIRT_PERMISSION}")
    if conn is None:
        raise Exception(
            f"Failed to open connection to qemu:///{LIBVIRT_PERMISSION}")

    # Download base image
    import_image(
        os_variant=os_variant
    )

    # Create/Get StoragePool
    storage_pool_vm = get_pool(
        conn=conn,
        name=vm_name
    )

    # Generate user-data/meta-data
    create_cloud_init_disk(
        vm_name=vm_name,
        login_user=username,
        login_pass=password
    )

    # Create Volume
    volume_vm = create_volume(
        storage_pool=storage_pool_vm,
        vm_name=vm_name,
        base_img=get_image_path(os_variant)
    )

    # Create/Get Network
    network = get_network(
        conn=conn,
        name=network
    )

    # Create Domaine
    return create_domain(
        conn=conn,
        volume=volume_vm,
        network=network,
        name=vm_name,
        vcpu=vcpu,
        memory=memory
    )
