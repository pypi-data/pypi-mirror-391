class DeviceMetaData:
    def __init__(self, peak_fp16_tflops: float, memory_bandwidth: float, sm_count: int):
        self.PEAK_FP16_TFLOPS = peak_fp16_tflops
        self.MEMORY_BANDWIDTH = memory_bandwidth
        self.SM_COUNT = sm_count


# ref: https://images.nvidia.cn/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf
GTX4090_META_DATA = DeviceMetaData(
    peak_fp16_tflops=330.3,
    memory_bandwidth=1008,
    sm_count=128,
)
# ref: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-us-nvidia-1758950-r4-web.pdf
A100_40GB_META_DATA = DeviceMetaData(
    peak_fp16_tflops=312,
    memory_bandwidth=1555,
    sm_count=108,
)
# ref: https://www.nvidia.com/en-us/data-center/a100/
A100_80GB_META_DATA = DeviceMetaData(
    peak_fp16_tflops=312,
    memory_bandwidth=2039,
    sm_count=108,
)

_devs_meta_data = {
    "NVIDIA GeForce RTX 4090": GTX4090_META_DATA,
    "NVIDIA A100-SXM4-80GB": A100_80GB_META_DATA,
    "NVIDIA A100-SXM4-40GB": A100_40GB_META_DATA,
}


def get_dev_meta_data(name: str) -> DeviceMetaData:
    assert name in _devs_meta_data.keys()
    return _devs_meta_data[name]
