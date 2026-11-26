"""S3-SOP 接口桩：未接通，调用即报错。"""

import pytest

from src.s3_sop_stub import S3SOPNotConnected, S3SOPStub


def test_put_raises_not_connected():
    with pytest.raises(S3SOPNotConnected, match="未接通"):
        S3SOPStub().put_object("bucket", "key", b"data")


def test_get_raises_not_connected():
    with pytest.raises(S3SOPNotConnected, match="未接通"):
        S3SOPStub().get_object("bucket", "key")
