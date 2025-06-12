from enum import Enum

class KubernetesRole(Enum):
    NONE = None
    CONTROL_PLANE = "control-plane"
    WORKER = "worker"
