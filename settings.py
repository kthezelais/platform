import os
from pathlib import Path

# Directories
WORK_DIR = Path('/var/lib/libvirt/images/.platform')
RESOURCES_PATH = f"{os.getcwd()}/resources"
IMG_DIR = Path(f'{WORK_DIR}/images')
VM_DIR = Path(f'{WORK_DIR}/virtualmachines')

# Network bridge name
NETWORK_NAME = "vm-network"
LIBVIRT_PERMISSION = "system"

# Default config
DEFAULT_VM_NAME    = "vm-test"
DEFAULT_USERNAME   = "ubuntu"
DEFAULT_PASSWORD   = "ubuntu"
DEFAULT_OS_VARIANT = "ubuntu24.04"
