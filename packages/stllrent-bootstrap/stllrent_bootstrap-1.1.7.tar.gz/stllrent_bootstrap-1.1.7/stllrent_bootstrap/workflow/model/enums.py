from enum import Enum
 
class TaskStatus(str, Enum):
    """Define os possíveis status de uma Task."""
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    REJECTED = "REJECTED"
    FAILURE = "FAILURE" # TODO: Em futuras versões, diferenciar falha de negócio (REJECTED) de falha de sistema.

class WorkflowStatus(str, Enum):
    """Define os possíveis status de um Workflow."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
