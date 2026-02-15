from datetime import datetime
from typing import Literal, Optional, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..core.logger import logger


router = APIRouter()


class ClientErrorEvent(BaseModel):
    level: Literal["error", "warning", "info"] = "error"
    message: str = Field(..., min_length=1, max_length=4000)
    source: Optional[str] = Field(default="web")
    component: Optional[str] = Field(default=None, max_length=200)
    trace_id: Optional[str] = Field(default=None, max_length=100)
    page_url: Optional[str] = Field(default=None, max_length=2000)
    user_agent: Optional[str] = Field(default=None, max_length=2000)
    stack: Optional[str] = Field(default=None, max_length=12000)
    context: Optional[dict[str, Any]] = None
    timestamp: Optional[str] = None


@router.post("/client-errors", response_model=dict)
async def report_client_error(event: ClientErrorEvent):
    event_time = event.timestamp or datetime.utcnow().isoformat()
    tags = {
        "kind": "client_error",
        "level": event.level,
        "source": event.source or "web",
        "component": event.component or "unknown",
        "trace_id": event.trace_id or "none",
    }

    summary = (
        f"[CLIENT-ERROR] level={tags['level']} source={tags['source']} "
        f"component={tags['component']} trace_id={tags['trace_id']} "
        f"message={event.message}"
    )

    detail = {
        "timestamp": event_time,
        "page_url": event.page_url,
        "user_agent": event.user_agent,
        "stack": event.stack,
        "context": event.context,
    }

    if event.level == "error":
        logger.error(summary)
    elif event.level == "warning":
        logger.warning(summary)
    else:
        logger.info(summary)

    logger.info(f"[CLIENT-ERROR-DETAIL] {detail}")

    return {
        "success": True,
        "message": "client error received",
        "received_at": event_time,
    }

