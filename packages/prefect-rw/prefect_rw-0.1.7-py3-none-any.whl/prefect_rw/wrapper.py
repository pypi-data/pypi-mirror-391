from pathlib import Path
from typing import Any, Literal

from prefect import deploy as _deploy
from prefect import flow
from prefect.deployments.runner import RunnerDeployment

from prefect_rw import RemoteStorageDir, RemoteStorageScript

_deployments = []


def _wrap_dep(
    name: str,
    path: str,
    function_name: str,
    mode: Literal["script", "dir"],
    work_pool_name: str,
    parameters: dict[str, Any] | None,
    concurrency_limit: int,
    **kwargs: dict[str, Any],
) -> RunnerDeployment:
    if not kwargs:
        kwargs = {}
    path = path if path.startswith(r"\\") else ("file://" + path)
    match mode:
        case "script":
            storage = RemoteStorageScript(path)
        case "dir":
            storage = RemoteStorageDir(path)
        case _:
            raise ValueError
    p = Path(path)

    return flow.from_source(
        storage,
        f"{p.name}:{function_name}",
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
    function_name: str,
    mode: Literal["script", "dir"],
    work_pool_name: str = "main",
    parameters: dict[str, Any] | None = None,
    concurrency_limit: int = 2,
    **kwargs: dict[str, Any],
) -> None:
    dep = _wrap_dep(name, path, function_name, mode, work_pool_name, parameters, concurrency_limit, **kwargs)
    _deployments.append(dep)


def deploy_one(
    name: str,
    path: str,
    function_name: str,
    mode: Literal["script", "dir"],
    work_pool_name: str = "main",
    parameters: dict[str, Any] | None = None,
    concurrency_limit: int = 2,
    **kwargs: dict[str, Any],
) -> None:
    dep = _wrap_dep(name, path, function_name, mode, work_pool_name, parameters, concurrency_limit, **kwargs)
    dep.apply(work_pool_name=work_pool_name)


def deploy_all(work_pool_name: str) -> None:
    _deploy(*_deployments, work_pool_name=work_pool_name, ignore_warnings=True)
