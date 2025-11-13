from .api_async import (
    AsyncSmartWaterApi, 
)
from .api_sync import (
    SmartWaterApi, 
    SmartWaterApiFlag,
)
from .data import (
    SmartWaterConnectError, 
    SmartWaterAuthError, 
    SmartWaterDataError, 
    SmartWaterError, 
)

# for unit tests
from .data import (
    LoginMethod,
)


# https://github.com/python-trio/unasync
# https://spwoodcock.dev/blog/2025-02-python-dry-async/