import asyncio
import contextlib
import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import anyio
import anyio.abc
from prefect import get_client
from prefect.cli.root import app
from prefect.deployments.steps.core import run_steps
from prefect.settings import PREFECT_WORKER_HEARTBEAT_SECONDS, PREFECT_WORKER_PREFETCH_SECONDS
from prefect.utilities.processutils import (
    setup_signal_handlers_worker,
)
from prefect.workers.process import ProcessJobConfiguration, ProcessWorker, ProcessWorkerResult

if TYPE_CHECKING:
    from prefect.client.schemas.objects import FlowRun


error_msg_deployment_id = "Deployment ID not found"
error_pull_steps = "Pull steps not found - configure your deployment correctly to work with prefect_rw"
error_command = "Command not set - configure your workpool correctly to work with prefect_rw"


async def run(
    self: ProcessWorker,
    flow_run: "FlowRun",
    configuration: ProcessJobConfiguration,
    task_status: anyio.abc.TaskStatus[int] | None = None,
) -> ProcessWorkerResult:
    if task_status is None:
        task_status = anyio.TASK_STATUS_IGNORED

    working_dir_ctx = (
        tempfile.TemporaryDirectory(suffix="prefect")
        if not configuration.working_dir
        else contextlib.nullcontext(configuration.working_dir)
    )
    with working_dir_ctx as working_dir:
        if not flow_run.deployment_id:
            raise RuntimeError(error_msg_deployment_id)
        async with get_client() as client:
            deployment = await client.read_deployment(flow_run.deployment_id)
        os.environ["_CWD"] = str(working_dir)
        os.environ["WORKER_RUNNING"] = "1"
        if not deployment.pull_steps:
            raise RuntimeError(error_pull_steps)
        step_results = await run_steps(deployment.pull_steps)
        os.environ["WORKER_RUNNING"] = ""
        if not configuration.command:
            raise RuntimeError(error_command)
        configuration.command = configuration.command.format(step_results["dir"])

        process = await self._runner.execute_flow_run(
            flow_run_id=flow_run.id,
            command=configuration.command,
            cwd=Path(working_dir) / step_results["dir"],
            env=configuration.env,
            stream_output=configuration.stream_output,
            task_status=task_status,
        )

        if process is None or process.returncode is None:  # pyright: ignore[reportAttributeAccessIssue]
            msg = "Failed to start flow run process."
            raise RuntimeError(msg)

    return ProcessWorkerResult(status_code=process.returncode, identifier=str(process.pid))  # pyright: ignore[reportAttributeAccessIssue]


async def worker_start(
    worker_name: str,
    work_pool_name: str,
    work_queues: list[str] | None = None,
    limit: int | None = None,
    prefetch_seconds: int | None = None,  # pyright: ignore[reportArgumentType]
    base_job_template: str | None = None,
    *,
    run_once: bool = False,
    with_healthcheck: bool = True,
) -> None:
    ProcessWorker.run = run
    worker_process_id = os.getpid()
    setup_signal_handlers_worker(worker_process_id, "the Process worker", app.console.print)
    template_contents = None
    if base_job_template is not None:
        with open(base_job_template, encoding="utf8") as fp:  # noqa: ASYNC230
            template_contents = json.load(fp=fp)

    worker = ProcessWorker(
        name=worker_name,
        work_pool_name=work_pool_name,
        work_queues=work_queues,
        limit=limit,
        prefetch_seconds=prefetch_seconds if prefetch_seconds else int(PREFECT_WORKER_PREFETCH_SECONDS.value()),
        heartbeat_interval_seconds=int(PREFECT_WORKER_HEARTBEAT_SECONDS.value()),
        base_job_template=template_contents,
    )
    try:
        await worker.start(
            run_once=run_once,
            with_healthcheck=with_healthcheck,
            printer=app.console.print,
        )
    except asyncio.CancelledError:
        app.console.print(f"Worker {worker.name!r} stopped!", style="yellow")
