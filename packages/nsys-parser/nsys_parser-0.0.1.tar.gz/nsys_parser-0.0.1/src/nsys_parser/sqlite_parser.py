import sqlite3
import torch

from typing import Optional
from os import path


def dict_factory(cursor, row):
    fields = [col[0] for col in cursor.description]
    return dict(zip(fields, row))


def init_conn(
    filepath: str,
) -> tuple[Optional[sqlite3.Connection], Optional[sqlite3.Cursor]]:
    if not path.exists(filepath):
        return None, None
    conn = sqlite3.connect(filepath)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    return conn, cur


def get_device_name(db: sqlite3.Cursor) -> str:
    names = [
        d["name"] for d in db.execute("SELECT name FROM TARGET_INFO_GPU").fetchall()
    ]
    assert len(names) == 1
    return names[0]


def get_strs_dict(db: sqlite3.Cursor) -> dict[str, int]:
    return {
        d["value"]: d["id"]
        for d in db.execute("SELECT id, value FROM StringIds").fetchall()
    }


def get_proc_stream(db: sqlite3.Cursor, io: str) -> str:
    cmd = "SELECT filenameId, contentId FROM ProcessStreams"
    ds = db.execute(cmd).fetchall()
    for d in ds:
        cmd = "SELECT value FROM StringIds WHERE id = ?"
        filename = db.execute(cmd, (d["filenameId"],)).fetchone()["value"]
        if io in filename:
            content = db.execute(cmd, (d["contentId"],)).fetchone()["value"]
            return content

    return None


def get_nvtx_event_cmd(
    id: int,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    global_tid: Optional[int] = None,
) -> str:
    query_cmd = "SELECT * FROM NVTX_EVENTS WHERE textId = ?"
    param = (id,)
    if start_time is not None:
        query_cmd += " AND start >= ?"
        param += (start_time,)
    if end_time is not None:
        query_cmd += " AND end <= ?"
        param += (end_time,)
    if global_tid is not None:
        query_cmd += " AND globalTid == ?"
        param += (global_tid,)
    return query_cmd, param


def get_nvtx_event(
    db: sqlite3.Cursor,
    id: int,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    global_tid: Optional[int] = None,
) -> dict:
    query_cmd, param = get_nvtx_event_cmd(id, start_time, end_time, global_tid)
    return db.execute(query_cmd, param).fetchone()


def get_nvtx_events(
    db: sqlite3.Cursor,
    id: int,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    global_tid: Optional[int] = None,
) -> list[dict]:
    query_cmd, param = get_nvtx_event_cmd(id, start_time, end_time, global_tid)
    return db.execute(query_cmd, param).fetchall()


def get_cuda_api_events(
    db: sqlite3.Cursor,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    global_tid: Optional[int] = None,
) -> list[dict]:
    query_cmd = "SELECT * FROM CUPTI_ACTIVITY_KIND_RUNTIME"
    param = ()
    if start_time is not None or end_time is not None or global_tid is not None:
        query_cmd += " WHERE"
        if start_time is not None:
            query_cmd += " start >= ?"
            param += (start_time,)
        if end_time is not None:
            query_cmd += "AND end <= ?" if start_time is not None else " end <= ?"
            param += (end_time,)
        if global_tid is not None:
            query_cmd += "AND globalTid == ?" if (start_time is not None or end_time is not None) else " globalTid == ?"
            param += (global_tid,)

    return db.execute(query_cmd, param).fetchall()


def get_cuda_kernel_event(
    db: sqlite3.Cursor,
    correlationId: int,
    global_pid: Optional[int] = None,
) -> dict:
    query_cmd = "SELECT * FROM CUPTI_ACTIVITY_KIND_KERNEL WHERE correlationId = ?"
    param = (correlationId,)
    if global_pid is not None:
        query_cmd += " AND globalPid == ?"
        param += (global_pid,)
    return db.execute(query_cmd, param).fetchone()


def get_cuda_graph_event(
    db: sqlite3.Cursor,
    correlationId: int,
    global_pid: Optional[int] = None,
) -> Optional[dict]:
    query_cmd = "SELECT * FROM CUPTI_ACTIVITY_KIND_GRAPH_TRACE WHERE correlationId = ?"
    param = (correlationId,)
    if global_pid is not None:
        query_cmd += " AND globalPid == ?"
        param += (global_pid,)
    return db.execute(query_cmd, param).fetchone()


def get_metric_dict(db: sqlite3.Cursor) -> dict[str, int]:
    return {
        d["metricName"]: d["metricId"]
        for d in db.execute(
            "SELECT metricId, metricName FROM TARGET_INFO_GPU_METRICS"
        ).fetchall()
    }


def get_gpu_metric(
    db: sqlite3.Cursor, metric_id: int, rng: Optional[tuple[int, int]] = None
) -> tuple[torch.Tensor, torch.Tensor]:
    query_cmd = "SELECT timestamp, value FROM GPU_METRICS WHERE metricId = ?"
    param = (metric_id,)
    if rng is not None:
        query_cmd += " AND timestamp BETWEEN ? and ?"
        param = (metric_id, rng[0], rng[1])
    result = db.execute(query_cmd, param).fetchall()
    metrics = torch.tensor([d["value"] for d in result], device="cpu")
    timestamps = torch.tensor([d["timestamp"] for d in result], device="cpu")
    return metrics, timestamps
