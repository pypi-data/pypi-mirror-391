from datetime import datetime
from enum import Enum
from typing import Literal

from elementary_python_sdk.core.types.base import ElementaryBaseModel


class QualityDimension(str, Enum):
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    FRESHNESS = "freshness"
    VALIDITY = "validity"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"


class TestType(str, Enum):
    __test__ = False

    DQX = "dqx"


class TestSeverity(str, Enum):
    __test__ = False

    ERROR = "ERROR"
    WARNING = "WARNING"


class TestExecutionStatus(str, Enum):
    __test__ = False

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    NO_DATA = "NO_DATA"


class Test(ElementaryBaseModel):
    kind: Literal["test"] = "test"
    name: str
    test_type: TestType
    asset_id: str
    column_name: str | None = None
    severity: TestSeverity
    config: dict | None = None
    meta: dict | None = None

    @property
    def id(self) -> str:
        return f"test.[{self.asset_id}].{self.column_name}"


class PartialTestResult(ElementaryBaseModel):
    kind: Literal["partial_test_result"] = "partial_test_result"
    test_id: str
    sub_type: str
    status: TestExecutionStatus
    column_name: str


class TestExecution(ElementaryBaseModel):
    kind: Literal["test_execution"] = "test_execution"
    test_id: str
    test_sub_unique_id: str
    column_name: str | None = None
    sub_type: str | None = None
    quality_dimension: QualityDimension | None = None
    start_time: datetime
    status: TestExecutionStatus
    failure_count: int
    description: str
    code: str | None = None
    duration_seconds: float
    exception: str | None = None
    traceback: str | None = None
