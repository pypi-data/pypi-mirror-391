from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from smartutils.app.history.const import OpType


class HistoryCreateSchema(BaseModel):
    biz_type: str = Field(..., description="操作名，一般使用表名")
    biz_id: int = Field(..., description="操作ID，一般使用数据的主键ID")
    op_type: OpType = Field(..., description="操作类型")
    op_id: int = Field(..., description="操作人的用户ID")
    before: Optional[Dict[str, Any]] = Field(default=None, description="数据操作前")
    after: Optional[Dict[str, Any]] = Field(default=None, description="数据操作后")
    remark: Optional[str] = Field(default=None, description="备注")


class HistoryUpdateSchema(BaseModel): ...
