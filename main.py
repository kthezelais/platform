import crypt
from controllers.general_controller import create_virtual_machine
from settings import \
    DEFAULT_USERNAME, \
    DEFAULT_PASSWORD


salt = crypt.mksalt(crypt.METHOD_SHA512)

create_virtual_machine(
    users=[{
        "username": DEFAULT_USERNAME,
        "password": crypt.crypt(DEFAULT_PASSWORD, salt),
        "sudo": True
    }],
    install_k8s=True
)
