from datetime import datetime
import logging

from dataclasses import dataclass
from enum import Enum, StrEnum

from .const import (
    CALL_CONTEXT_SYNC,
    CALL_CONTEXT_ASYNC,
)

_LOGGER = logging.getLogger(__name__)


class CallContext(StrEnum):
    SYNC = CALL_CONTEXT_SYNC
    ASYNC = CALL_CONTEXT_ASYNC

class LoginMethod(StrEnum):
    ACCESS_TOKEN = 'Access-Token'
    REFRESH_TOKEN = 'Refresh-Token'
    GOOGLE_APIS = 'Google-Apis'

class FirestoreMethod(StrEnum):
    DOCUMENT = "FirestoreDoc"
    COLLECTION = "FirestoreColl"
    WATCH = "FirestoreWatch"
    SNAPSHOT = "FirestoreSnapshot"


class SmartWaterError(Exception):
    """Exception to indicate generic error failure."""    
    
class SmartWaterConnectError(SmartWaterError):
    """Exception to indicate authentication failure."""

class SmartWaterAuthError(SmartWaterError):
    """Exception to indicate authentication or authorization failure."""

class SmartWaterDataError(SmartWaterError):
    """Exception to indicate generic data failure."""  


@dataclass
class SmartWaterHistoryItem:
    dt: datetime
    op: str
    rsp: str|None = None
 
    @staticmethod
    def create(dt: datetime, context: str , request: dict|None, response: dict|None, token: dict|None) -> 'SmartWaterHistoryItem':
        item = SmartWaterHistoryItem( 
            dt = dt, 
            op = context,
        )

        # If possible, add a summary of the response status and json res and code
        if response:
            rsp_parts = []
            if "status_code" in response:
                rsp_parts.append(response["status_code"])
            if "status" in response:
                rsp_parts.append(response["status"])
            
            item.rsp = ', '.join(rsp_parts)

        return item


@dataclass
class SmartWaterHistoryDetail:
    dt: datetime
    req: dict|None
    rsp: dict|None
    token: dict|None

    @staticmethod
    def create(dt: datetime, context: str , request: dict|None, response: dict|None, token: dict|None) -> 'SmartWaterHistoryDetail':
        detail = SmartWaterHistoryDetail(
            dt = dt, 
            req = request,
            rsp = response,
            token = token,
        )
        return detail


class SmartWaterDictFactory:
    @staticmethod
    def exclude_none_values(x):
        """
        Usage:
          item = SmartWaterHistoryItem(...)
          item_as_dict = asdict(item, dict_factory=SmartWaterDictFactory.exclude_none_values)
        """
        return { k: v for (k, v) in x if v is not None }

