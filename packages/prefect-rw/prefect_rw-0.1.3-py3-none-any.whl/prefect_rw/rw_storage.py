from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import anyio
import fsspec
from prefect._internal.concurrency.api import create_call, from_async
from prefect.blocks.core import Block
from prefect.logging.loggers import get_logger
from prefect.utilities.collections import visit_collection
from prefect.utilities.processutils import run_process


class RemoteStorageDir:  # noqa: PLW1641
    """Pulls the contents of a remote storage location to the local filesystem."""

    def __init__(  # noqa: D107
        self,
        path: str,
        entrypoint: str,
        pull_interval: int | None = 60,
        **settings: Any,  # noqa: ANN401
    ) -> None:
        self.path = path
        self._settings = settings
        self._logger = get_logger("runner.storage.remote-storage-rw-dir")
        self._storage_base_path = Path.cwd()
        self._pull_interval = pull_interval
        self._entrypoint = entrypoint

    @staticmethod
    def _get_required_package_for_scheme(scheme: str) -> str | None:
        # attempt to discover the package name for the given scheme
        # from fsspec's registry
        known_implementation = fsspec.registry.get(scheme)
        if known_implementation:
            return known_implementation.__module__.split(".")[0]
        # if we don't know the implementation, try to guess it for some
        # common schemes
        if scheme == "s3":
            return "s3fs"
        if scheme in {"gs", "gcs"}:
            return "gcsfs"
        if scheme in {"abfs", "az"}:
            return "adlfs"
        return None

    @property
    def _filesystem(self) -> fsspec.AbstractFileSystem:
        scheme, _, _, _, _ = urlsplit(self.path)

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
    def entrypoint(self) -> str:
        """Path to main script with PEP723 dependencies listed."""
        return self._entrypoint

    @property
    def destination(self) -> Path:
        """The local file path to pull contents from remote storage to."""
        return self._storage_base_path / self._remote_path.stem

    @property
    def _remote_path(self) -> Path:
        """The remote file path to pull contents from remote storage to."""
        _, netloc, urlpath, _, _ = urlsplit(self.path)
        return Path(netloc) / Path(urlpath.lstrip("/"))

    async def pull_code(self) -> None:
        """Pull contents from remote storage to the local filesystem."""
        self._logger.debug(
            "Pulling contents from remote storage '%s' to '%s'...",
            self.path,
            self.destination,
        )

        if not self.destination.exists():
            self.destination.mkdir(parents=True, exist_ok=True)

        remote_path = str(self._remote_path) + "/"

        try:
            await from_async.wait_for_call_in_new_thread(
                create_call(
                    self._filesystem.get,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType] missing type stubs
                    remote_path,
                    str(self.destination),
                    recursive=True,
                ),
            )
        except Exception as exc:
            msg = f"Failed to pull contents from remote storage {self.path!r} to {self.destination!r}"
            raise RuntimeError(msg) from exc

        try:
            await self.uv_sync()
        except Exception as exc:
            msg = "Failed to install dependencies"
            raise RuntimeError(msg) from exc

    async def uv_sync(self) -> None:
        """Create a virtual environment and install dependencies."""
        venv_command = ["uv", "venv"]
        process = await run_process(
            command=venv_command,
            stream_output=True,
            task_status=anyio.TASK_STATUS_IGNORED,
            task_status_handler=lambda process: process,
            cwd=self.destination,
        )
        if process.returncode is None:
            msg = "Process exited with None return code"
            raise RuntimeError(msg)
        if process.returncode == 0:
            msg = "Process exited with error"
            raise RuntimeError(msg)

        sync_command = ["uv", "sync", "--active", "--script", self.entrypoint]
        env = {**os.environ, "VIRTUAL_ENV": str(self.destination / ".venv")}
        process = await run_process(
            command=sync_command,
            stream_output=True,
            task_status=anyio.TASK_STATUS_IGNORED,
            task_status_handler=lambda process: process,
            cwd=self.destination,
            env=env,
        )
        if process.returncode is None:
            msg = "Process exited with None return code"
            raise RuntimeError(msg)
        if process.returncode == 0:
            msg = "Process exited with error"
            raise RuntimeError(msg)

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
                "path": self.path,
                **settings_with_placeholders,
            },
        }

    def __eq__(self, __value: object, /) -> bool:
        """Equality check for runner storage objects."""
        if isinstance(__value, RemoteStorageDir):
            return self.path == __value.path and self._settings == __value._settings
        return False

    def __repr__(self) -> str:  # noqa: D105
        return f"RemoteStorageDir(path={self.path!r})"


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
        self._storage_base_path = Path(os.environ["_CWD"])
        self._pull_interval = pull_interval

    @property
    def _filesystem(self) -> fsspec.AbstractFileSystem:
        scheme, _, _, _, _ = urlsplit(str(self._path))

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
        _, netloc, urlpath, _, _ = urlsplit(str(self._path))
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
                await self.uv_sync()
            except Exception as exc:
                msg = "Failed to install dependencies"
                raise RuntimeError(msg) from exc
        # return {"tmp": str(self.destination)}

    async def uv_sync(self) -> None:
        """Create a virtual environment and install dependencies."""
        init_command = ["uv", "init", "--bare", "--vcs", "none"]
        p = await from_async.wait_for_call_in_new_thread(
            create_call(subprocess.run, init_command, cwd=self.destination, env={**os.environ}),
        )
        p.check_returncode()
        venv_command = ["uv", "venv", "--clear", "--link-mode", "copy"]
        p = await from_async.wait_for_call_in_new_thread(
            create_call(subprocess.run, venv_command, cwd=self.destination, env={**os.environ}),
        )
        p.check_returncode()

        sync_command = ["uv", "sync", "--link-mode", "copy", "--active", "--script", self._path.name]
        env = {**os.environ, "VIRTUAL_ENV": (self.destination / ".venv").as_posix()}
        p = await from_async.wait_for_call_in_new_thread(
            create_call(subprocess.run, sync_command, env=env, cwd=self.destination),
        )
        p.check_returncode()

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
