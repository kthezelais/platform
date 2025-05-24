import libvirt
from controllers.pool_controller import get_pool
from controllers.network_controller import get_network
from settings import \
    DEFAULT_VM_NAME, \
    LIBVIRT_PERMISSION, \
    NETWORK_NAME


conn = libvirt.open(f"qemu:///{LIBVIRT_PERMISSION}")
print(conn.listStoragePools())
print(conn.listAllStoragePools(), end="\n\n")


try:
    conn.listAllDomains()[0].destroy()
except:
    pass

try:
    pool_img = get_pool(conn, "images")

    pool_img.destroy()
    pool_img.undefine()
except:
    pass

try:
    pool_vm = get_pool(conn, DEFAULT_VM_NAME)

    pool_vm.destroy()
    pool_vm.undefine()
except:
    pass

try:
    network = get_network(conn, NETWORK_NAME)

    network.destroy()
    network.undefine()
except:
    pass


print(conn.listStoragePools())
print(conn.listAllStoragePools(), end="\n\n")
