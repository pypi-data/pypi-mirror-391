import torch

from typing import Optional, Iterable

from . import sqlite_parser
from utils import MetricNames
from device_metadata import DeviceMetaData, get_dev_meta_data
from logger import init_logger

logger = init_logger(__name__)


class GPUGraphEvent(dict):
    def __init__(self, d: dict, parser: "NsysParser") -> None:
        super().__init__(d)
        self.__dict__ = self
        self.parser = parser

    def get_tc_active(self):
        tc_active, timestamp = self.get_gpu_metric(MetricNames.TENSOR_ACT_TP)
        return tc_active, timestamp

    def get_comp_power(self):
        return self.get_tc_active()

    def get_dram_bw(self):
        dram_rd_bw, timestamp = self.get_gpu_metric(MetricNames.DRAM_RD_BW)
        dram_wt_bw, _ = self.get_gpu_metric(MetricNames.DRAM_WT_BW)
        assert timestamp.all() == _.all()
        dram_bw = dram_rd_bw + dram_wt_bw
        return dram_bw, timestamp

    def get_gpu_metric(self, metric_name: str):
        return sqlite_parser.get_gpu_metric(
            self.parser.cur,
            self.parser.metrics_id[metric_name],
            (self.start, self.end),
        )


class Event(dict):
    def __init__(self, d: dict, parser: "NsysParser") -> None:
        super().__init__(d)
        self.__dict__ = self
        self.parser = parser

        self._cuda_start_time: Optional[int] = None
        self._cuda_end_time: Optional[int] = None
        self._cuda_api_events: Optional[list] = None

        self._global_tid: Optional[int] = None
        self._global_pid: Optional[int] = None
        self._thread_id: Optional[int] = None

        # Default globalTid, globalPid used as condition for subsequent queries
        self._global_tid_for_query: Optional[int] = None
        self._global_pid_for_query: Optional[int] = None

        # field for cuda graph, and we only support one cuda graph per event
        self._cuda_graph_event: Optional[GPUGraphEvent] = None

    def set_global_tid_for_query(self, global_tid: int):
        self._global_tid_for_query = global_tid

    def set_global_pid_for_query(self, global_pid: int):
        self._global_pid_for_query = global_pid

    def get_gpu_metric(self, metric_name: str):
        return sqlite_parser.get_gpu_metric(
            self.parser.cur,
            self.parser.metrics_id[metric_name],
            (self.cuda_start_time, self.cuda_end_time),
        )

    @property
    def cuda_api_events(self) -> list[dict]:
        if self._cuda_api_events is None:
            global_tid = (
                self._global_tid_for_query
                if self._global_tid_for_query is not None
                else self.global_tid
            )
            self._cuda_api_events = sqlite_parser.get_cuda_api_events(
                self.parser.cur, self.start, self.end, global_tid
            )
        return self._cuda_api_events

    @property
    def first_kernel_id(self):
        for e in self.cuda_api_events:
            e_id = e["correlationId"]
            global_pid = (
                self._global_pid_for_query
                if self._global_pid_for_query is not None
                else self.global_pid
            )
            kernel_event = sqlite_parser.get_cuda_kernel_event(
                self.parser.cur, e_id, global_pid
            )
            if kernel_event is not None:
                logger.debug(f'first_CUDA API event: {e}')
                logger.debug(f'first_kernel event: {kernel_event}')
                assert isinstance(e_id, int)
                return e_id

    @property
    def last_kernel_id(self):
        for e in reversed(self.cuda_api_events):
            e_id = e["correlationId"]
            global_pid = (
                self._global_pid_for_query
                if self._global_pid_for_query is not None
                else self.global_pid
            )
            kernel_event = sqlite_parser.get_cuda_kernel_event(
                self.parser.cur, e_id, global_pid
            )
            if kernel_event is not None:
                logger.debug(f'last_CUDA API event: {e}')
                logger.debug(f'last_kernel event: {kernel_event}')
                assert isinstance(e_id, int)
                return e_id

    @property
    def cuda_start_time(self):
        if self._cuda_start_time is None:
            global_pid = (
                self._global_pid_for_query
                if self._global_pid_for_query is not None
                else self.global_pid
            )
            first_kernel_event = sqlite_parser.get_cuda_kernel_event(
                self.parser.cur, self.first_kernel_id, global_pid
            )
            first_kernel_start_time = first_kernel_event["start"]
            assert isinstance(first_kernel_start_time, int)
            self._cuda_start_time = first_kernel_start_time
        return self._cuda_start_time

    @property
    def cuda_end_time(self):
        if self._cuda_end_time is None:
            global_pid = (
                self._global_pid_for_query
                if self._global_pid_for_query is not None
                else self.global_pid
            )
            last_kernel_end_time = sqlite_parser.get_cuda_kernel_event(
                self.parser.cur, self.last_kernel_id, global_pid
            )["end"]
            assert isinstance(last_kernel_end_time, int)
            self._cuda_end_time = last_kernel_end_time
        return self._cuda_end_time

    @property
    def cuda_duration(self):
        return self.cuda_end_time - self.cuda_start_time  # ns

    @property
    def cuda_graph_event(self):
        if self._cuda_graph_event is None:
            replay_event = self.parser.get_nvtx_event(
                "replay", self["start"], self["end"], self.global_tid
            )
            cuda_graph_id = replay_event.cuda_api_events[-1]["correlationId"]
            cuda_graph_event = sqlite_parser.get_cuda_graph_event(
                self.parser.cur, cuda_graph_id, self.global_pid
            )
            assert cuda_graph_event is not None
            self._cuda_graph_event = GPUGraphEvent(cuda_graph_event, self.parser)
        return self._cuda_graph_event

    @property
    def global_tid(self):
        if self._global_tid is None:
            self._global_tid = self["globalTid"]
            assert isinstance(self._global_tid, int)
        return self._global_tid

    @property
    def global_pid(self):
        if self._global_pid is None:
            self._global_pid = (self.global_tid // 0x1000_000) * 0x1000_000
        return self._global_pid

    @property
    def thread_id(self):
        if self._thread_id is None:
            self._thread_id = self.global_tid % 0x1000_000
        return self._thread_id

    def get_tc_active(self):
        tc_active, timestamp = self.get_gpu_metric(MetricNames.TENSOR_ACT_TP)
        return tc_active, timestamp

    def get_comp_power(self):
        return self.get_tc_active()

    def get_dram_bw(self):
        dram_rd_bw, timestamp = self.get_gpu_metric(MetricNames.DRAM_RD_BW)
        dram_wt_bw, _ = self.get_gpu_metric(MetricNames.DRAM_WT_BW)
        assert timestamp.all() == _.all()
        dram_bw = dram_rd_bw + dram_wt_bw
        return dram_bw, timestamp


class NsysParser:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        logger.debug(f"Connection to {db_path} establishing...")
        self.conn, self.cur = sqlite_parser.init_conn(db_path)
        assert self.conn is not None, f"{db_path} connection not found"
        assert self.cur is not None

        self.validated = self.check_validated()

        self._device_name: Optional[str] = None
        self._dev_meta_data: Optional[DeviceMetaData] = None
        self._metrics_id: Optional[dict[str, int]] = None
        self._strs_dict: Optional[dict[str, int]] = None

        # Default globalTid used as condition for subsequent queries
        self._global_tid: Optional[int] = None

    def set_global_tid_for_query(self, global_tid: int):
        self._global_tid = global_tid

    def __del__(self) -> None:
        assert self.conn is not None, f"{self.db_path} connection not found"
        assert self.cur is not None
        self.cur.close()
        self.conn.close()
        logger.info(f"Connection Closed ({self.db_path}).")

    def check_validated(self):
        stderr = sqlite_parser.get_proc_stream(self.cur, "stderr")
        if len(stderr) > 0:
            return False
        # TODO: check CUPTI_ACTIVITY_KIND_KERNEL table exists
        return True

    @property
    def device_name(self) -> str:
        if self._device_name is None:
            self._device_name = sqlite_parser.get_device_name(self.cur)
        return self._device_name

    @property
    def dev_meta_data(self) -> DeviceMetaData:
        if self._dev_meta_data is None:
            self._dev_meta_data = get_dev_meta_data(self.device_name)
        return self._dev_meta_data

    @property
    def metrics_id(self) -> dict[str, int]:
        if self._metrics_id is None:
            self._metrics_id = sqlite_parser.get_metric_dict(self.cur)
        return self._metrics_id

    @property
    def strs_dict(self) -> dict[str, int]:
        if self._strs_dict is None:
            self._strs_dict = sqlite_parser.get_strs_dict(self.cur)
        return self._strs_dict

    def get_nvtx_event(
        self,
        nvtx_name: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        global_tid: Optional[int] = None,
    ):
        query_global_tid = global_tid if global_tid is not None else self._global_tid
        if nvtx_name not in self.strs_dict:
            return None
        d = sqlite_parser.get_nvtx_event(
            self.cur, self.strs_dict[nvtx_name], start_time, end_time, query_global_tid
        )
        return Event(d, self)

    def get_nvtx_events(
        self,
        nvtx_name: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        global_tid: Optional[int] = None,
    ) -> list[Event]:
        query_global_tid = global_tid if global_tid is not None else self._global_tid
        assert nvtx_name in self.strs_dict, f"{nvtx_name} not found in {self.db_path}"
        ds = sqlite_parser.get_nvtx_events(self.cur, self.strs_dict[nvtx_name], start_time, end_time, query_global_tid)
        es = [Event(d, self) for d in ds]
        return es

    def get_dram_bw_by_range(
        self, start_time: int, end_time: int
    ):
        dram_rd_bw, timestamp = sqlite_parser.get_gpu_metric(
            self.cur, self.metrics_id[MetricNames.DRAM_RD_BW], (start_time, end_time)
        )
        dram_wt_bw, _ = sqlite_parser.get_gpu_metric(
            self.cur, self.metrics_id[MetricNames.DRAM_WT_BW], (start_time, end_time)
        )
        assert timestamp.all() == _.all()
        dram_bw = dram_rd_bw + dram_wt_bw
        return dram_bw, timestamp

    def get_comp_power_by_range(
        self, start_time: int, end_time: int
    ):
        comp_power, timestamp = sqlite_parser.get_gpu_metric(
            self.cur, self.metrics_id[MetricNames.TENSOR_ACT_TP], (start_time, end_time)
        )
        return comp_power, timestamp

    def get_events_dram_bw(
        self, events: Iterable[Event]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        bw, timestamp = zip(*[e.get_dram_bw() for e in events])
        bw = torch.cat(bw)
        timestamp = torch.cat(timestamp)
        return bw, timestamp

    def get_events_tc_active(
        self, events: Iterable[Event]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        tc_act, timestamp = zip(*[e.get_tc_active() for e in events])
        tc_act = torch.cat(tc_act)
        timestamp = torch.cat(timestamp)
        return tc_act, timestamp
