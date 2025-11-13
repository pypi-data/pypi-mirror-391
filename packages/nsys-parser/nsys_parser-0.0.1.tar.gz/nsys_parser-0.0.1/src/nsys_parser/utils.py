import enum
import inspect
import pathlib

from typing import Callable


class MetricNames(enum.StrEnum):
    GPC_CLK_FRQ = "GPC Clock Frequency [MHz]"
    SYS_CLK_FRQ = "SYS Clock Frequency [MHz]"
    GR_ACT = "GR Active [Throughput %]"
    SYNC_COMP = "Sync Compute in Flight [Throughput %]"
    ASYNC_COMP = "Async Compute in Flight [Throughput %]"
    SM_ACT = "SM Active [Throughput %]"
    SM_ISSUE = "SM Issue [Throughput %]"
    TENSOR_ACT_TP = "Tensor Active [Throughput %]"
    VTG_WARP_TP = "Vertex/Tess/Geometry Warps in Flight [Throughput %]"
    VTG_WARP_AVG = "Vertex/Tess/Geometry Warps in Flight [Avg]"
    VTG_WARP_WPC = "Vertex/Tess/Geometry Warps in Flight [Avg Warps per Cycle]"
    PIX_WARP_TP = "Pixel Warps in Flight [Throughput %]"
    PIX_WARP_AVG = "Pixel Warps in Flight [Avg]"
    PIX_WARP_WPC = "Pixel Warps in Flight [Avg Warps per Cycle]"
    COMP_WARP_TP = "Compute Warps in Flight [Throughput %]"
    COMP_WARP_AVG = "Compute Warps in Flight [Avg]"
    COMP_WARP_WPC = "Compute Warps in Flight [Avg Warps per Cycle]"
    UNALLOC_WARP_ACT_SM_TP = "Unallocated Warps in Active SMs [Throughput %]"
    UNALLOC_WARP_ACT_SM_AVG = "Unallocated Warps in Active SMs [Avg]"
    UNALLOC_WARP_ACT_SM_WPC = "Unallocated Warps in Active SMs [Avg Warps per Cycle]"
    DRAM_RD_BW = "DRAM Read Bandwidth [Throughput %]"
    DRAM_WT_BW = "DRAM Write Bandwidth [Throughput %]"
    PCIE_RX_TP = "PCIe RX Throughput [Throughput %]"
    PCIE_TX_TP = "PCIe TX Throughput [Throughput %]"
    PCIE_RD_BAR = "PCIe Read Requests to BAR1 [Requests]"
    PCIE_WT_BAR = "PCIe Write Requests to BAR1 [Requests]"


def nvtx(f: Callable) -> str:
    filename = pathlib.Path(inspect.getfile(f)).name
    lineno = str(inspect.getsourcelines(f)[1])
    func_name = f.__name__
    return f"{filename}:{lineno}({func_name})"
