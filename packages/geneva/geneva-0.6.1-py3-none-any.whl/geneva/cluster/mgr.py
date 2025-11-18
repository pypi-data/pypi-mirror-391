# SPDX-License-Identifier: PROPRIETARY
# SPDX-FileCopyrightText: Copyright The Geneva Authors
import enum
import json
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional

import attrs
import cattrs
import pyarrow as pa
from attr import asdict

from geneva.cluster import GenevaClusterType, K8sConfigMethod
from geneva.state.manager import BaseManager
from geneva.utils import current_user, escape_sql_string, retry_lance

if TYPE_CHECKING:
    from geneva.runners.ray.raycluster import RayCluster

CLUSTER_TABLE_NAME = "geneva_clusters"

_LOG = logging.getLogger(__name__)


@attrs.define
class RayGroupConfig:
    """Configuration for Ray pods"""

    service_account: str = attrs.field()
    num_cpus: int = attrs.field()
    memory: str = attrs.field()
    image: str = attrs.field()

    # store these as json strings
    node_selector: dict[str, str] = attrs.field(metadata={"pa_type": "string"})
    labels: dict[str, str] = attrs.field(metadata={"pa_type": "string"})
    tolerations: list[dict[str, str]] = attrs.field(metadata={"pa_type": "string"})

    num_gpus: int = attrs.field(default=0)


@attrs.define
class HeadGroupConfig(RayGroupConfig):
    """Configuration for Ray Head pod"""


@attrs.define
class WorkerGroupConfig(RayGroupConfig):
    """Configuration for Ray Worker pods"""


# todo: make config map impl use this model
@attrs.define
class KubeRayConfig:
    namespace: str = attrs.field()
    head_group: HeadGroupConfig = attrs.field()
    # todo: lance bug prevents us from storing list<struct>
    #  - store as json string for now
    worker_groups: list[WorkerGroupConfig] = attrs.field(metadata={"pa_type": "string"})
    config_method: K8sConfigMethod = attrs.field(
        default=K8sConfigMethod.LOCAL, metadata={"pa_type": "string"}
    )
    use_portforwarding: bool = attrs.field(default=True)
    aws_region: Optional[str] = attrs.field(default=None)
    aws_role_name: Optional[str] = attrs.field(default=None)

    # Arbitrary kwargs to pass to ray.init()
    ray_init_kwargs: Optional[dict[str, Any]] = attrs.field(
        factory=dict, metadata={"pa_type": "string"}
    )


@attrs.define
class GenevaCluster:
    """A Geneva Cluster represents the backend compute infrastructure
    for the execution environment."""

    cluster_type: GenevaClusterType = attrs.field(metadata={"pa_type": pa.string()})
    name: str = attrs.field()
    kuberay: Optional[KubeRayConfig] = attrs.field(
        default=None,
    )
    created_at: datetime = attrs.field(
        factory=lambda: datetime.now(timezone.utc),
        metadata={"pa_type": pa.timestamp("us", tz="UTC")},
    )
    created_by: str = attrs.field(factory=current_user)

    def validate(self) -> None:
        # use attrs validation on RayCluster
        self.to_ray_cluster()

    def to_ray_cluster(self) -> "RayCluster":
        """Convert the persisted cluster definition into internal RayCluster model"""
        from geneva.runners.ray.raycluster import (
            RayCluster,
            _HeadGroupSpec,
            _WorkerGroupSpec,
        )

        c = asdict(self)
        k = c["kuberay"]
        k.pop("use_portforwarding")
        k["region"] = k.pop("aws_region")
        k["role_name"] = k.pop("aws_role_name")
        k["name"] = c["name"]
        k["config_method"] = K8sConfigMethod(k["config_method"])
        k["head_group"] = _HeadGroupSpec(**k["head_group"])
        k["worker_groups"] = [_WorkerGroupSpec(**wg) for wg in k["worker_groups"]]
        # Extract ray_init_kwargs
        ray_init_kwargs = k.pop("ray_init_kwargs", {})
        rc = RayCluster(**k, ray_init_kwargs=ray_init_kwargs)
        return rc

    def as_dict(self) -> dict:
        return attrs.asdict(
            self,
            value_serializer=lambda obj, a, v: v.value
            if isinstance(v, enum.Enum)
            else v,
        )


class ClusterConfigManager(BaseManager):
    def get_table_name(self) -> str:
        return CLUSTER_TABLE_NAME

    def get_model(self) -> Any:
        return GenevaCluster(GenevaClusterType.KUBE_RAY, "dummy")

    @retry_lance
    def upsert(self, cluster: GenevaCluster) -> None:
        val = cluster.as_dict()
        # store list<struct> as json string for now due to lance bug
        val["kuberay"]["worker_groups"] = json.dumps(val["kuberay"]["worker_groups"])

        # store maps as json strings
        hg = val["kuberay"]["head_group"]
        hg["node_selector"] = json.dumps(hg["node_selector"])
        hg["tolerations"] = json.dumps(hg["tolerations"])
        hg["labels"] = json.dumps(hg["labels"])

        # store ray_init_kwargs as json string
        # TODO: fix schema migration to re-enable ray_init_kwargs
        #  https://linear.app/lancedb/issue/GEN-185/schema-evolution-on-nested-fields
        if val["kuberay"].get("ray_init_kwargs"):
            _LOG.warning("ray_init_kwargs not yet supported - ignoring")
        del val["kuberay"]["ray_init_kwargs"]
        # val["kuberay"]["ray_init_kwargs"] = json.dumps(  # noqa: ERA001
        #    val["kuberay"]["ray_init_kwargs"] # noqa: ERA001
        # ) # noqa: ERA001

        # note: merge_insert with fails with schema errors - use delete+add for now
        self.delete(cluster.name)
        self.get_table().add([val])

    @retry_lance
    def list(self, limit: int = 1000) -> list[GenevaCluster]:
        res = self.get_table(True).search().limit(limit).to_arrow().to_pylist()
        return [_make_cluster(cluster) for cluster in res]

    @retry_lance
    def load(self, name: str) -> GenevaCluster | None:
        res = (
            self.get_table(True)
            .search()
            .where(f"name = '{escape_sql_string(name)}'")
            .limit(1)
            .to_arrow()
            .to_pylist()
        )
        if not res:
            return None
        return _make_cluster(res[0])

    @retry_lance
    def delete(self, name: str) -> None:
        self.get_table().delete(f"name = '{escape_sql_string(name)}'")


def _make_cluster(args: dict) -> GenevaCluster:
    # parse stringified json fields
    kr = args["kuberay"]
    kr["worker_groups"] = json.loads(kr["worker_groups"])
    hg = kr["head_group"]
    hg["node_selector"] = json.loads(hg["node_selector"])
    hg["labels"] = json.loads(hg["labels"])
    hg["tolerations"] = json.loads(hg["tolerations"])

    # parse ray_init_kwargs if it exists (for backwards compatibility)
    kr["ray_init_kwargs"] = json.loads(kr.get("ray_init_kwargs", "{}") or "{}")

    converter = cattrs.Converter()
    converter.register_structure_hook(
        datetime,
        lambda ts, _: datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if isinstance(ts, str)
        else ts,
    )
    res = converter.structure(args, GenevaCluster)

    return res
