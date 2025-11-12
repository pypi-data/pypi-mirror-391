from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import fsspec
from prefect._internal.concurrency.api import create_call, from_async
from prefect.blocks.core import Block
from prefect.logging.loggers import get_logger
from prefect.utilities.collections import visit_collection


async def uv_sync(destination: Path, _path: Path) -> None:
    """Create a virtual environment and install dependencies."""
    init_command = ["uv", "init", "--bare", "--vcs", "none"]
    p = await from_async.wait_for_call_in_new_thread(
        create_call(subprocess.run, init_command, cwd=destination, env={**os.environ}),
    )
    p.check_returncode()
    venv_command = ["uv", "venv", "--clear", "--link-mode", "copy"]
    p = await from_async.wait_for_call_in_new_thread(
        create_call(subprocess.run, venv_command, cwd=destination, env={**os.environ}),
    )
    p.check_returncode()

    sync_command = ["uv", "sync", "--link-mode", "copy", "--active", "--script", _path.name]
    env = {**os.environ, "VIRTUAL_ENV": (destination / ".venv").as_posix()}
    p = await from_async.wait_for_call_in_new_thread(
        create_call(subprocess.run, sync_command, env=env, cwd=destination),
    )
    p.check_returncode()


class RemoteStorageScript:  # noqa: PLW1641
    """Pulls the script from a remote storage location to the local filesystem."""

    def __init__(  # noqa: D107
        self,
        path: str,
        pull_interval: int | None = 60,
        **settings: Any,  # noqa: ANN401
    ) -> None:
        self._path = Path(path)
        self._settings = settings
        self._logger = get_logger("runner.storage.remote-storage-rw-script")
        self._storage_base_path = Path(os.environ.get("_CWD", ""))
        self._pull_interval = pull_interval

    @property
    def _filesystem(self) -> fsspec.AbstractFileSystem:
        scheme, _, _, _, _ = urlsplit(self._path.as_posix())

        def replace_blocks_with_values(obj: Any) -> Any:  # noqa: ANN401
            if isinstance(obj, Block):
                if get := getattr(obj, "get", None):
                    return get()
                if hasattr(obj, "value"):
                    return obj.value  # pyright: ignore[reportAttributeAccessIssue]
                return obj.model_dump()
            return obj

        settings_with_block_values = visit_collection(
            self._settings,
            replace_blocks_with_values,
            return_data=True,
        )

        return fsspec.filesystem(scheme, **settings_with_block_values)  # pyright: ignore[reportUnknownMemberType] missing type stubs

    def set_base_path(self, path: Path) -> None:  # noqa: D102
        self._storage_base_path = path

    @property
    def pull_interval(self) -> int | None:
        """The interval at which contents from remote storage should be pulled to
        local storage. If None, remote storage will perform a one-time sync.
        """  # noqa: D205
        return self._pull_interval

    @property
    def destination(self) -> Path:
        """The local file path to pull contents from remote storage to."""
        return self._storage_base_path / self._remote_path.parent.stem

    @property
    def _remote_path(self) -> Path:
        """The remote file path to pull contents from remote storage to."""
        _, netloc, urlpath, _, _ = urlsplit(self._path.as_posix())
        return Path(netloc) / Path(urlpath.lstrip("/"))

    async def pull_code(self) -> None:
        """Pull contents from remote storage to the local filesystem."""
        self._logger.debug(
            "Pulling contents from remote storage '%s' to '%s'...",
            self._path,
            self.destination,
        )

        if not self.destination.exists():
            self.destination.mkdir(parents=True, exist_ok=True)

        remote_path = str(self._remote_path)

        try:
            await from_async.wait_for_call_in_new_thread(
                create_call(
                    self._filesystem.get,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType] missing type stubs
                    remote_path,
                    str(self.destination) + "/",
                ),
            )
        except Exception as exc:
            msg = f"Failed to pull contents from remote storage {self._path!r} to {self.destination!r}"
            raise RuntimeError(msg) from exc
        if os.environ.get("WORKER_RUNNING"):
            try:
                await uv_sync(self.destination, self._path)
            except Exception as exc:
                msg = "Failed to install dependencies"
                raise RuntimeError(msg) from exc

    def to_pull_step(self) -> dict[str, Any]:
        """Return a dictionary representation of the storage object that can be used as a deployment pull step."""

        def replace_block_with_placeholder(obj: Any) -> Any:  # noqa: ANN401
            if isinstance(obj, Block):
                return f"{{{{ {obj.get_block_placeholder()} }}}}"
            return obj

        settings_with_placeholders = visit_collection(
            self._settings,
            replace_block_with_placeholder,
            return_data=True,
        )
        return {
            "prefect_rw.pull_script_from_remote_storage": {
                "path": self._path,
                **settings_with_placeholders,
            },
        }

    def __eq__(self, __value: object, /) -> bool:
        """Equality check for runner storage objects."""
        if isinstance(__value, RemoteStorageScript):
            return self._path == __value._path and self._settings == __value._settings
        return False

    def __repr__(self) -> str:  # noqa: D105
        return f"RemoteStorageScript(path={self._path!r})"


class RemoteStorageDir:  # noqa: PLW1641
    """Pulls the script from a remote storage location to the local filesystem."""

    def __init__(  # noqa: D107
        self,
        path: str,
        pull_interval: int | None = 60,
        **settings: Any,  # noqa: ANN401
    ) -> None:
        self._path = Path(path)
        self._settings = settings
        self._logger = get_logger("runner.storage.remote-storage-rw-script")
        self._storage_base_path = Path(os.environ.get("_CWD", ""))
        self._pull_interval = pull_interval

    @property
    def _filesystem(self) -> fsspec.AbstractFileSystem:
        scheme, _, _, _, _ = urlsplit(self._path.as_posix())

        def replace_blocks_with_values(obj: Any) -> Any:  # noqa: ANN401
            if isinstance(obj, Block):
                if get := getattr(obj, "get", None):
                    return get()
                if hasattr(obj, "value"):
                    return obj.value  # pyright: ignore[reportAttributeAccessIssue]
                return obj.model_dump()
            return obj

        settings_with_block_values = visit_collection(
            self._settings,
            replace_blocks_with_values,
            return_data=True,
        )

        return fsspec.filesystem(scheme, **settings_with_block_values)  # pyright: ignore[reportUnknownMemberType] missing type stubs

    def set_base_path(self, path: Path) -> None:  # noqa: D102
        self._storage_base_path = path

    @property
    def pull_interval(self) -> int | None:
        """The interval at which contents from remote storage should be pulled to
        local storage. If None, remote storage will perform a one-time sync.
        """  # noqa: D205
        return self._pull_interval

    @property
    def destination(self) -> Path:
        """The local file path to pull contents from remote storage to."""
        return self._storage_base_path / self._remote_path.parent.stem

    @property
    def _remote_path(self) -> Path:
        """The remote file path to pull contents from remote storage to."""
        _, netloc, urlpath, _, _ = urlsplit(self._path.as_posix())
        return Path(netloc) / Path(urlpath.lstrip("/"))

    async def pull_code(self) -> None:
        """Pull contents from remote storage to the local filesystem."""
        dest = self.destination.parent
        self._logger.debug(
            "Pulling contents from remote storage '%s' to '%s'...",
            self._path,
            dest,
        )

        if not dest.exists():
            dest.mkdir(parents=True, exist_ok=True)

        remote_path = str(self._remote_path.parent)

        try:
            await from_async.wait_for_call_in_new_thread(
                create_call(
                    self._filesystem.get,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType] missing type stubs
                    remote_path,
                    str(dest) + "/",
                    recursive=True,
                ),
            )
        except Exception as exc:
            msg = f"Failed to pull contents from remote storage {self._path!r} to {dest!r}"
            raise RuntimeError(msg) from exc
        if os.environ.get("WORKER_RUNNING"):
            try:
                await uv_sync(self.destination, self._path)
            except Exception as exc:
                msg = "Failed to install dependencies"
                raise RuntimeError(msg) from exc

    def to_pull_step(self) -> dict[str, Any]:
        """Return a dictionary representation of the storage object that can be used as a deployment pull step."""

        def replace_block_with_placeholder(obj: Any) -> Any:  # noqa: ANN401
            if isinstance(obj, Block):
                return f"{{{{ {obj.get_block_placeholder()} }}}}"
            return obj

        settings_with_placeholders = visit_collection(
            self._settings,
            replace_block_with_placeholder,
            return_data=True,
        )
        return {
            "prefect_rw.pull_dir_from_remote_storage": {
                "path": self._path,
                **settings_with_placeholders,
            },
        }

    def __eq__(self, __value: object, /) -> bool:
        """Equality check for runner storage objects."""
        if isinstance(__value, RemoteStorageDir):
            return self._path == __value._path and self._settings == __value._settings
        return False

    def __repr__(self) -> str:  # noqa: D105
        return f"RemoteStorageDir(path={self._path!r})"
