import libvirt
import time
import threading
import sys
import paramiko
from controllers.general_controller import create_virtual_machine
from settings import \
    DEFAULT_USERNAME, \
    DEFAULT_PASSWORD


def loading_animation(message: str, stop_event: threading.Event):
    animation = [
        "[       ]",
        "[=      ]",
        "[==     ]",
        "[===    ]",
        "[====   ]",
        "[=====  ]",
        "[====== ]",
        "[=======]",
        "[ ======]",
        "[  =====]",
        "[   ====]",
        "[    ===]",
        "[     ==]",
        "[      =]",
        "[       ]"
    ]
    i = 0

    while not stop_event.is_set():
        time.sleep(0.1)
        sys.stdout.write(f"\r{message} " + animation[i % len(animation)])
        sys.stdout.flush()
        i += 1
    print(f"\r{message} \033[32mOK\033[0m       ")


def wait_for_ip(domain: libvirt.virDomain, timeout: int = 120, interval: int = 2) -> str:
    stop_event = threading.Event()

    # Create and start the loading animation thread
    animation_thread = threading.Thread(target=loading_animation, args=(
        "Waiting for domain IP address", stop_event))
    animation_thread.start()

    for _ in range(timeout // interval):
        try:
            ifaces = domain.interfaceAddresses(
                libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)

            for val in ifaces.values():
                if val['addrs']:
                    for addr in val['addrs']:
                        if addr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4 and addr['addr'] != '127.0.0.1':
                            # Signal the animation thread to stop
                            stop_event.set()
                            animation_thread.join()  # Wait for the animation thread to finish
                            return addr['addr']
        except libvirt.libvirtError as e:
            pass
        time.sleep(interval)

    # Signal the animation thread to stop
    stop_event.set()
    animation_thread.join()  # Wait for the animation thread to finish
    raise TimeoutError("No IP address found for domain within timeout.")


def ssh_exec(ssh: paramiko.SSHClient, command: str) -> str:
        _, stdout, stderr = ssh.exec_command(command)
        stdout_str = stdout.read().decode()
        stderr_str = stderr.read().decode()

        with open("run.log", "a") as log:
            if stderr_str:
                log.write(stderr_str)
                return stderr_str
            log.write(stdout_str)
        return stdout_str


if __name__ == "__main__":
    start = time.perf_counter()

    # Edit or add a new user to the list
    users = [
        {
            "username": DEFAULT_USERNAME,
            "password": DEFAULT_PASSWORD,
            "sudo": True
        }
    ]

    # Disable libvirt/QEMU error message output
    libvirt.registerErrorHandler(f=lambda userdata, err: None, ctx=None)

    # Create virtual machine and define dependencies to be installed
    domain = create_virtual_machine(
        users=users,
        install_k8s=True
    )

    ip_addr = wait_for_ip(domain)

    # Print the ssh command to connect to the host
    print(f"\n\t\tssh {users[0]["username"]}@{ip_addr}", end="\n\n")

    # Connect to VM and start a cluster
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_addr, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)

    ssh_exec(ssh, f"cloud-init status --wait")
    ssh_exec(ssh, f"sudo kubeadm init --pod-network-cidr 10.224.0.0/16 --control-plane-endpoint={ip_addr}")
    kubeconfig = ssh_exec(ssh, f"sudo cat /etc/kubernetes/admin.conf")

    with open("kubeconfig", "w") as file:
        file.write(kubeconfig)

    ssh.close()
    end = time.perf_counter()
    print(f"Elapsed time: {end - start:.4f} seconds")
