from pathlib import Path
from typing import TYPE_CHECKING, Any

from prefect.logging import get_logger

from prefect_rw.rw_storage import RemoteStorageDir, RemoteStorageScript

if TYPE_CHECKING:
    import logging

deployment_logger: "logging.Logger" = get_logger("deployment")


async def pull_dir_from_remote_storage(path: str, **settings: Any) -> dict[str, Any]:  # noqa: ANN401
    """Pull code from a remote storage location into the current working directory."""
    storage = RemoteStorageDir(path, **settings)

    await storage.pull_code()

    directory = str(storage.destination.relative_to(Path.cwd()))
    deployment_logger.info(f"Pulled code from {path!r} into {directory!r}")  # noqa: G004
    return {"directory": directory}


async def pull_script_from_remote_storage(path: str, **settings: Any) -> dict[str, Any]:  # noqa: ANN401
    """Pull code from a remote storage location into the current working directory."""
    storage = RemoteStorageScript(path, **settings)

    await storage.pull_code()

    directory = str(storage.destination)
    deployment_logger.info(f"Pulled code from {path!r} into {storage.destination!r}")  # noqa: G004
    return {"directory": directory, "dir": storage.destination.name}
