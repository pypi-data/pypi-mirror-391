from pathlib import Path
from typing import Any

from prefect import deploy as _deploy
from prefect import flow
from prefect.deployments.runner import RunnerDeployment

from prefect_rw import RemoteStorageDir, RemoteStorageScript

_deployments = []


def _wrap_dep(
    name: str,
    path: str,
    entrypoint: str,
    work_pool_name: str,
    parameters: dict[str, Any] | None,
    concurrency_limit: int,
    **kwargs: dict[str, Any],
) -> RunnerDeployment:
    if not kwargs:
        kwargs = {}
    storage = RemoteStorageScript(path) if path.endswith(".py") else RemoteStorageDir(path, entrypoint)
    p = Path(path)
    return flow.from_source(
        storage,
        f"{p.name}:{entrypoint}",
    ).to_deployment(
        name,
        work_pool_name=work_pool_name,
        parameters=parameters,
        concurrency_limit=concurrency_limit,
        **kwargs,
    )  # pyright: ignore[reportReturnType]


def add_deployment(
    name: str,
    path: str,
    entrypoint: str,
    work_pool_name: str = "main",
    parameters: dict[str, Any] | None = None,
    concurrency_limit: int = 2,
    **kwargs: dict[str, Any],
) -> None:
    dep = _wrap_dep(name, path, entrypoint, work_pool_name, parameters, concurrency_limit, **kwargs)
    _deployments.append(dep)


def deploy_one(
    name: str,
    path: str,
    entrypoint: str,
    work_pool_name: str = "main",
    parameters: dict[str, Any] | None = None,
    concurrency_limit: int = 2,
    **kwargs: dict[str, Any],
) -> None:
    dep = _wrap_dep(name, path, entrypoint, work_pool_name, parameters, concurrency_limit, **kwargs)
    dep.apply(work_pool_name=work_pool_name)


def deploy_all(work_pool_name: str) -> None:
    _deploy(*_deployments, work_pool_name=work_pool_name)
