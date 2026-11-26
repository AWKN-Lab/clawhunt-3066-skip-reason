"""S3-SOP 接口桩（MOCK）：真实 S3 集成未接通。

目标接口（供后续对接时实现）：put_object(bucket, key, body) / get_object(bucket, key)。
本样品中两个方法均抛错，明确表示未接通；本样品不做任何对象存储调用，
归一化脚本只读写本地文件。
"""


class S3SOPNotConnected(RuntimeError):
    """S3-SOP 未接通时抛出的错误。"""


class S3SOPStub:
    """S3-SOP 接口桩：所有方法均未实现，调用即报错。"""

    def put_object(self, bucket: str, key: str, body: bytes) -> None:
        raise S3SOPNotConnected("S3-SOP 未接通：本样品为接口桩，不调用真实对象存储。")

    def get_object(self, bucket: str, key: str) -> bytes:
        raise S3SOPNotConnected("S3-SOP 未接通：本样品为接口桩，不调用真实对象存储。")
