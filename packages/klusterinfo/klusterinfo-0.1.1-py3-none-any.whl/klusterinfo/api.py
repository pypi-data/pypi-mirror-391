from collections import defaultdict
from dataclasses import dataclass
import pykube

from pint import UnitRegistry

from typing import Union

import os


class AllNamespaceConfig(pykube.KubeConfig):
    def __init__(self, source_config: pykube.KubeConfig):
        super().__init__(source_config.doc)

    @property
    def namespace(self) -> None:
        return None


class Converter:
    def __init__(self):
        self.ureg = UnitRegistry()
        self.ureg.load_definitions(
            os.path.join(os.path.dirname(__file__), "kubernetes_units.txt")
        )

    def __call__(self, k_unit: Union[str, int]) -> float:
        if isinstance(k_unit, int):
            return float(k_unit)
        return float(self.ureg.Quantity(k_unit))


@dataclass
class Resource:
    amount: int
    requested: int
    limit: int

    def req_pct(self) -> float:
        return (self.requested / self.amount) * 100

    def lim_pct(self) -> float:
        return (self.limit / self.amount) * 100


@dataclass
class Memory(Resource):
    def __repr__(self):
        return f"<Memory {int(self.amount / (1024 * 1024))}MB [{self.req_pct():.2f}% / {self.lim_pct():.2f}%]>"


@dataclass
class CPU(Resource):
    def __repr__(self):
        return (
            f"<CPU {self.amount} cores [{self.req_pct():.2f}% / {self.lim_pct():.2f}%]>"
        )


@dataclass
class KubeNode:
    """ An object containing metadata on a kubernetes node """

    name: str
    cpu: CPU
    memory: Memory
    max_pods: int
    cur_pods: int

    def __repr__(self):
        return f"{self.name} ({self.cur_pods}/{self.max_pods}) pods\n\t{self.cpu}\n\t{self.memory}"


class NodeInformation:
    def __init__(self):
        self.config = AllNamespaceConfig(pykube.KubeConfig.from_file("~/.kube/config"))
        self.client = pykube.HTTPClient(self.config)

    @staticmethod
    def _node_filter(node_name):
        return {"field_selector": {"spec.nodeName": node_name}}

    def get_nodes(self):
        convert_unit = Converter()
        for node in pykube.Node.objects(self.client).all():
            pods = []
            total_cpu = node.obj["status"]["allocatable"]["cpu"]
            total_memory = node.obj["status"]["allocatable"]["memory"]
            max_pods = node.obj["status"]["allocatable"]["pods"]
            cur_pods = 0

            memory = Memory(amount=convert_unit(total_memory), requested=0, limit=0)
            cpu = CPU(amount=convert_unit(total_cpu), requested=0, limit=0)

            for pod in (
                pykube.Pod.objects(self.client)
                .filter(**self._node_filter(node.name))
                .all()
            ):
                for container in pod.obj["spec"]["containers"]:
                    limits = container["resources"].get("limits", defaultdict(int))
                    requests = container["resources"].get("requests", defaultdict(int))
                    memory.requested += convert_unit(requests.get("memory", 0))
                    memory.limit += convert_unit(limits.get("memory", 0))
                    cpu.requested += convert_unit(requests.get("cpu", 0))
                    cpu.limit += convert_unit(limits.get("cpu", 0))
                cur_pods += 1
            n = KubeNode(
                name=node.name,
                cpu=cpu,
                memory=memory,
                max_pods=max_pods,
                cur_pods=cur_pods,
            )
            print(n)
