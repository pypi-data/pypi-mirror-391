# SPDX-License-Identifier: PROPRIETARY
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import logging
import time
import uuid

import pyarrow as pa
import pytest
import ray

import geneva
from geneva.cluster import K8sConfigMethod
from geneva.cluster.builder import GenevaClusterBuilder
from geneva.manifest.mgr import GenevaManifest
from geneva.runners.ray.raycluster import ClusterStatus, RayCluster
from geneva.utils import dt_now_utc

_LOG = logging.getLogger(__name__)


# use a random version to force checkpoint to invalidate
@geneva.udf(num_cpus=1, version=uuid.uuid4().hex)
def plus_one(a: int) -> int:
    return a + 1


SIZE = 1024


def test_get_imported(
    geneva_test_bucket: str,
    standard_cluster: RayCluster,
) -> None:
    from geneva.runners.ray.pipeline import get_imported

    geneva.connect(geneva_test_bucket)
    with standard_cluster:
        pkgs = ray.get(get_imported.remote())
        for pkg, ver in sorted(pkgs.items()):
            _LOG.info(f"{pkg}=={ver}")


def test_ray_add_column_pipeline(
    geneva_test_bucket: str,
    standard_cluster: RayCluster,
) -> None:
    conn = geneva.connect(geneva_test_bucket)
    table_name = uuid.uuid4().hex
    table = conn.create_table(
        table_name,
        pa.Table.from_pydict({"a": pa.array(range(SIZE))}),
    )
    with standard_cluster:
        table.add_columns(
            {"b": plus_one},  # type: ignore[arg-type]
            batch_size=32,
            concurrency=2,
            intra_applier_concurrency=2,
        )
        table.backfill("b")

    assert table.to_arrow() == pa.Table.from_pydict(
        {"a": pa.array(range(SIZE)), "b": pa.array(range(1, SIZE + 1))}
    )
    conn.drop_table(table_name)


@pytest.mark.timeout(600)
def test_ray_add_column_pipeline_backfill_async(
    geneva_test_bucket: str,
    standard_cluster: RayCluster,
) -> None:
    conn = geneva.connect(geneva_test_bucket)
    table_name = uuid.uuid4().hex
    table = conn.create_table(
        table_name,
        pa.Table.from_pydict({"a": pa.array(range(SIZE))}),
    )
    with standard_cluster:
        table.add_columns(
            {"b": plus_one},  # type: ignore[arg-type]
            batch_size=32,
            concurrency=8,
            intra_applier_concurrency=8,
        )
        fut = table.backfill_async("b")
        while not fut.done():
            time.sleep(1)
        table.checkout_latest()

        time.sleep(10)  # todo: why is this needed?
        _LOG.info("FUT pbars: %s", fut._pbars)  # type: ignore[attr-defined]
        # there should be 4 pbars - geneva, checkpointed, ready to commit and committed
        assert len(fut._pbars) == 4  # type: ignore[attr-defined]

        cs = ClusterStatus()
        cs.get_status()
        assert cs.pbar_k8s is not None
        assert cs.pbar_kuberay is not None

    assert table.to_arrow() == pa.Table.from_pydict(
        {"a": pa.array(range(SIZE)), "b": pa.array(range(1, SIZE + 1))}
    )
    conn.drop_table(table_name)


def test_ray_add_column_pipeline_cpu_only_pool(
    geneva_test_bucket: str,
    standard_cluster: RayCluster,
) -> None:
    conn = geneva.connect(geneva_test_bucket)
    table_name = uuid.uuid4().hex
    table = conn.create_table(
        table_name,
        pa.Table.from_pydict({"a": pa.array(range(SIZE))}),
    )
    with standard_cluster:
        table.add_columns(
            {"b": plus_one},  # type: ignore[arg-type]
            batch_size=32,
            concurrency=4,
            use_cpu_only_pool=True,
        )
        table.backfill("b")

    assert table.to_arrow() == pa.Table.from_pydict(
        {"a": pa.array(range(SIZE)), "b": pa.array(range(1, SIZE + 1))}
    )
    conn.drop_table(table_name)


def test_backfill_multiple_fragments_with_context(
    geneva_test_bucket: str,
    slug: str | None,
    geneva_k8s_service_account: str,
    k8s_namespace: str,
    head_node_selector: dict,
    worker_node_selector: dict,
    region: str,
    k8s_config_method: K8sConfigMethod,
    manifest: str | None,
) -> None:
    adds = 10
    rows_per_add = 10

    db = geneva.connect(geneva_test_bucket)
    table_name = uuid.uuid4().hex
    data = pa.Table.from_pydict({"a": pa.array(range(rows_per_add))})
    table = db.create_table(table_name, data)
    for _ in range(adds):
        # split adds to create many fragments
        data = pa.Table.from_pydict({"a": pa.array(range(rows_per_add))})
        table.add(data)

    cluster_name = "add-column-context"
    cluster_name += f"-{dt_now_utc().strftime('%Y-%m-%d-%H-%M')}-{slug}"
    manifest_name = f"test-manifest-{slug}"

    success = False
    try:
        cluster = (
            GenevaClusterBuilder()
            .name(cluster_name)
            .namespace(k8s_namespace)
            .config_method(k8s_config_method)
            .aws_config(region=region, role_name="geneva-client-role")
            .head_group(
                service_account=geneva_k8s_service_account,
                node_selector=head_node_selector,
                # cpus=2, memory="4Gi", num_gpus=0 use defaults
            )
            .add_cpu_worker_group(
                service_account=geneva_k8s_service_account,
                node_selector=worker_node_selector,
                # cpus=4, memory="8Gi" use defaults
            )
            .add_cpu_worker_group(
                service_account=geneva_k8s_service_account,
                node_selector=worker_node_selector,
                # cpus=4, memory="8Gi" use defaults
            )
            .build()
        )

        db.define_cluster(cluster_name, cluster)

        if manifest:
            # saved manifest provided via --manifest arg
            manifest_name = manifest
        else:
            db.define_manifest(
                manifest_name,
                GenevaManifest(
                    manifest_name,
                    delete_local_zips=True,
                    skip_site_packages=False,
                    pip=["lancedb", "geneva"],
                    py_modules=["./"],
                ),
            )

        with db.context(
            cluster=cluster_name, manifest=manifest_name, log_to_driver=False
        ):
            table.add_columns(
                {"b": plus_one},  # type: ignore[arg-type]
            )
            table.backfill("b")

            jobs = db._history.list_jobs(table_name, None)
            _LOG.info(f"{jobs=}")
            assert len(jobs) == 1, "expected a job record"
            assert jobs[0].status == "DONE"
            assert jobs[0].table_name == table_name
            assert jobs[0].job_type == "BACKFILL"
            assert jobs[0].metrics, "expected metrics"
            assert jobs[0].events, "expected events"

            success = True

        assert success, "pipeline failed"

    finally:
        db.delete_cluster(cluster_name)
        db.drop_table(table_name)
        if not manifest:
            db.delete_manifest(manifest_name)
