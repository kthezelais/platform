import libvirt
from controllers.pool_controller import get_pool
from controllers.network_controller import get_network
from controllers.domain_controller import delete_domain_by_name
from settings import \
    LIBVIRT_PERMISSION, \
    NETWORK_NAME


conn = libvirt.open(f"qemu:///{LIBVIRT_PERMISSION}")
print(conn.listStoragePools())
print(conn.listAllStoragePools(), end="\n\n")


domains = []
try:
    for domain in conn.listAllDomains():
        domains.append(domain.name())
        delete_domain_by_name(conn, domain.name())
except:
    pass

try:
    pool_img = get_pool(conn, "images")

    pool_img.destroy()
    pool_img.undefine()
except:
    pass

try:
    for domain in domains:
        pool_vm = get_pool(conn, domain)

        if pool_vm.isActive():
            pool_vm.destroy()

        pool_vm.undefine()
except:
    pass

try:
    for pool in conn.listAllStoragePools():
        if pool.name() != "default":
            if pool.isActive():
                pool.destroy()

            pool.undefine()
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
