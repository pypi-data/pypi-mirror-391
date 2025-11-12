import asyncio
import ctypes
import threading
from threading import Thread

import pystray
from PIL import Image, ImageDraw
from PIL._typing import _Ink

from prefect_rw.rw_process_worker import worker_start

RUNNING_TID = None
WORKER_ARGS = {}


def create_image(width: int, height: int, color1: _Ink | None, color2: _Ink) -> Image.Image:
    """Генерит иконку квадратиками."""
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)

    return image


def raise_in_thread(tid: int, exctype: type) -> None:
    """Raise an exception in the threads with id tid."""
    # https://stackoverflow.com/a/325528
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        msg = "invalid thread id"
        raise ValueError(msg)
    if res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        msg = "PyThreadState_SetAsyncExc failed"
        raise SystemError(msg)


def w() -> None:
    asyncio.run(worker_start(**WORKER_ARGS))


def _start(_icon: pystray._base.Icon) -> None:
    """Запускает воркера."""
    global RUNNING_TID  # noqa: PLW0603
    t = Thread(target=w, daemon=True)
    t.start()
    RUNNING_TID = t.ident


def join_thread(n: int = 5) -> None:
    for _i in range(n):
        if RUNNING_TID is None:
            return
        raise_in_thread(RUNNING_TID, KeyboardInterrupt)
        t = next((t for t in threading.enumerate() if t.ident == RUNNING_TID), None)
        if t:
            print("thread is still present, joining")
            t.join(15)
            if t.is_alive():
                print("thread is still alive after join")
            else:
                break


def _stop(_icon: pystray._base.Icon) -> None:
    """Останавливает воркера."""
    join_thread()


def restart(icon: pystray._base.Icon) -> None:
    """Перезапускает воркера."""
    _stop(icon)
    _start(icon)


def stop_and_exit(icon: pystray._base.Icon) -> None:
    """Останавливает воркера и завершает приложение."""
    _stop(icon)
    icon.stop()


def main(
    worker_name: str,
    work_pool_name: str,
    limit: int = 2,
    work_queues: list[str] | None = None,
    prefetch_seconds: int | None = None,  # pyright: ignore[reportArgumentType]
    base_job_template: str | None = None,
    *,
    run_once: bool = False,
    with_healthcheck: bool = True,
) -> None:
    global WORKER_ARGS
    WORKER_ARGS = {
        "worker_name": worker_name,
        "work_pool_name": work_pool_name,
        "work_queues": work_queues,
        "limit": limit,
        "prefetch_seconds": prefetch_seconds,
        "base_job_template": base_job_template,
        "run_once": run_once,
        "with_healthcheck": with_healthcheck,
    }
    menu = pystray.Menu(
        pystray.MenuItem(text="Перезапуск", action=restart),
        pystray.MenuItem(text="Остановить и закрыть", action=stop_and_exit),
    )
    icon = pystray.Icon("prefect_worker", icon=create_image(64, 64, "red", "white"), menu=menu)

    _start(icon)

    icon.run()


if __name__ == "__main__":
    main()
