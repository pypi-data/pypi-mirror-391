"""api.py: API for Smart Water Technology data retrieval."""

import asyncio
import base64
import jwt
import httpx
import logging
import math
import threading

from datetime import datetime, timezone
from enum import Enum, StrEnum
from typing import Any

from google.oauth2 import credentials as oauth2
from google.cloud import firestore_v1

from .const import (
    FIREBASE_PUBLIC_API_KEY,
    FIRESTORE_URL,
    FIRESTORE_PROJECT_NAME,
    GOOGLE_APIS_LOGIN_URL,
    GOOGLE_APIS_REFRESH_URL,
    ACCESS_TOKEN_EXPIRE_MARGIN,
    CALL_CONTEXT_ASYNC,
    CALL_CONTEXT_SYNC,
    utcnow_ts,
    utcnow_dt,
)
from .data import (
    CallContext,
    LoginMethod,
    FirestoreMethod,
    SmartWaterHistoryDetail, 
    SmartWaterHistoryItem,
    SmartWaterConnectError, 
    SmartWaterAuthError, 
    SmartWaterDataError, 
    SmartWaterError, 
)
from .tasks import (
    AsyncTaskHelper,
    TaskHelper,
)


_LOGGER = logging.getLogger(__name__)


class SmartWaterApiFlag(StrEnum):
    """Extra flags to pass to Api"""
    REFRESH_HANDLER_START   = "refresh_handler_start"   # bool
    DIAGNOSTICS_COLLECT     = "diagnostics_collect"     # bool


# Smart Water API to detect device and get device info, fetch the actual data from the device, and parse it
class AsyncSmartWaterApi:

    # Constants
    CALL_CONTEXT = CALL_CONTEXT_ASYNC   # Sync/Async environment detection
    
    def __init__(self, username, password, client:httpx.AsyncClient|None = None, flags:dict = {}):
        
        # Configuration
        self._username: str = username
        self._password: str = password

        # Login data
        self._login_time: datetime|None = None
        self._login_method: LoginMethod|None = None

        self._refresh_token: str|None = None
        self._access_token: str|None = None
        self._access_exp_ts: float|None = None
        
        self._user_id: str = None

        # Automatic refresh of access token
        self._refresh_handler_start = flags.get(SmartWaterApiFlag.REFRESH_HANDLER_START, False)
        self._refresh_task = None
        self._refresh_schedule: float = 0

        # Http Client.
        self._http_client: httpx.AsyncClient = client or httpx.AsyncClient()
        self._http_client_close = False if client else True     # Do not close an external passed client

        # Firestore Clients.
        # In the async Api class we also need the sync client as not all operations are supported on async client
        # In the sync Api class this leads to assigning the same variable twice...
        self._firestore_client_async: firestore_v1.AsyncClient = None
        self._firestore_client_sync: firestore_v1.Client = None
        self._firestore_client_close = False

        self._firestore_watch_map: dict[str,Any] = {}
        self._firestore_watch_def: dict[str,dict] = {}

        # Locks to protect certain operations from being called from multiple threads
        self._login_lock = asyncio.Lock()

        # To pass diagnostics data back to our parent
        self._diag_collect: bool = flags.get(SmartWaterApiFlag.DIAGNOSTICS_COLLECT, False)
        self._diag_counters: dict[str, int] = {}
        self._diag_history: list[SmartWaterHistoryItem] = []
        self._diag_details: dict[str, SmartWaterHistoryDetail] = {}

        self._diag_durations: dict[int, int] = { n: 0 for n in range(10) }
        self._diag_methods: dict[str, int] = { m: 0 for m in FirestoreMethod }


    @property
    def profile_id(self) -> str:
        """The unique profile id. Only available after successfull login."""
        return self._user_id
    
    
    @property
    def closed(self) -> bool:
        """Returns whether the SmartWaterApi has been closed."""
        if self._http_client:
            return self._http_client.is_closed
        else:
            return True
        

    async def close(self):
        """Safely logout and close all client handles"""

        # Logout
        await self.logout()

        # Cleanup
        if self._http_client is not None and self._http_client_close:
            await self._http_client.aclose()
            self._http_client = None

        # In the async Api class we also needed the sync client as not all operations are supported on async client
        # In the sync Api class this leads to checking the same variable twice...
        if self._firestore_client_async is not None and self._firestore_client_close:
            self._firestore_client_async.close()
            self._firestore_client_async = None

        if self._firestore_client_sync is not None and self._firestore_client_close:
            self._firestore_client_sync.close()
            self._firestore_client_sync = None


    async def login(self):
        """
        Login to Smart Water Technology servers.
        Guards for calls from multiple threads.
        """

        # Only one thread at a time can check the tokens and do subsequent login if needed.
        # Once one thread is done, the next thread can then check the (new) token.
        async with self._login_lock:
            await self._login()


    async def _login(self):
        """Login to Google Apis by trying each of the possible login methods"""        

        # First try to keep using the access token
        # Next, try to refresh that token.
        # Finally try the Google APIs login method
        error = None
        methods = [LoginMethod.ACCESS_TOKEN, LoginMethod.REFRESH_TOKEN, LoginMethod.GOOGLE_APIS]
        for method in methods:
            try:
                match method:
                    case LoginMethod.ACCESS_TOKEN:
                        # Try to keep using the Access Token
                        success = await self._login_access_token()

                    case LoginMethod.REFRESH_TOKEN:
                        # Try to refresh the token
                        success = await self._login_refresh_token()

                    case LoginMethod.GOOGLE_APIS:
                        # Try to do a new login with username+password
                        success = await self._login_google_apis()

                    case _:
                        success = False

                if success:
                    # if we reached this point then a login method succeeded
                    return 
            
            except Exception as ex:
                _LOGGER.debug(str(ex))
                error = ex

                # Clear any previous login tokens before trying the next method
                await self._logout(context="login", method=method)

        # if we reached this point then all methods failed.
        if error:
            raise error
        

    async def _login_access_token(self) -> bool:
        """Inspect whether the access token is still valid"""

        if self._access_token is None or self._access_exp_ts is None:
            # No acces-token to check; silently continue to the next login method (token refresh)
            return False

        # inspect the exp field inside the access_token
        if self._access_exp_ts - ACCESS_TOKEN_EXPIRE_MARGIN < utcnow_ts():
            _LOGGER.debug(f"Access-Token expired")
            return False    # silently continue to the next login method (token refresh)

        # Re-use this access token
        dt = utcnow_dt()
        context = f"login access_token reuse"
        token = {
            "access_token": self._access_token,
            "access_expire": datetime.fromtimestamp(self._access_exp_ts, timezone.utc)
        }
        self._add_diagnostics(dt, context, None, None, token)

        # _LOGGER.debug(f"Reuse the access-token")
        return True


    async def _login_refresh_token(self) -> bool:
        """Attempty to refresh the access token"""

        if not self._refresh_token:
            # No refresh-token; silently continue to the next login method
            return False
        
        # Don't bother to check the contents of the refresh token, 
        # just attempt to request a new access token via the refresh token
        _LOGGER.debug(f"Try refresh the access-token")

        result = await self._http_request(
            context = f"login access_token refresh",
            request = {
                "method": "POST",
                "url": GOOGLE_APIS_REFRESH_URL,
                "params": {
                    "key": base64.b64encode(FIREBASE_PUBLIC_API_KEY, b'-_').rstrip(b'=').decode('ascii'),
                },
                "json": {
                    "grantType": "refresh_token",
                    "refreshToken": self._refresh_token or "",
                },
            },
        )

        # Store access-token in variable so it will be added as Authorization header in calls to Smart Water servers
        self._user_id = result.get('user_id', None)
        self._refresh_token = result.get('refresh_token')
        self._access_token = result.get('access_token')
        self._access_exp_ts = self._get_expire(self._access_token)

        if not self._access_token or not self._refresh_token:
            error = f"No tokens found in response from token refresh"
            _LOGGER.debug(error)    # logged as warning after last retry
            raise SmartWaterAuthError(error)
        
        # The refresh of the tokens succeeded. Schedule the next refresh
        self._login_time = utcnow_dt()

        _LOGGER.info(f"Refreshed the access-token")
        return await self._login_finalize()


    async def _login_google_apis(self) -> bool:
        """Login via Google-Apis"""

        _LOGGER.debug(f"Try login via Google-Apis for '{self._username}'")

        result = await self._http_request(
            context = f"login Google-Apis",
            request = {
                "method": "POST",
                "url": GOOGLE_APIS_LOGIN_URL,
                "params": {
                    "key": base64.b64encode(FIREBASE_PUBLIC_API_KEY, b'-_').rstrip(b'=').decode('ascii'),
                },
                "json": {
                    "email": self._username,
                    "password": self._password,
                    "returnSecureToken": True,
                    "clientType": "CLIENT_TYPE_ANDROID"
                },
            },            
        )

        self._refresh_token = result.get('refreshToken')
        self._access_token = result.get('idToken')
        self._access_exp_ts = self._get_expire(self._access_token)

        self._user_id = result.get('localId')

        if not self._access_token:
            error = f"No tokens found in response from login"
            _LOGGER.debug(error)    # logged as warning after last retry
            raise SmartWaterAuthError(error)

        # if we reach this point then the token was OK
        self._login_time = utcnow_dt()
        self._login_method = LoginMethod.GOOGLE_APIS

        _LOGGER.info(f"Login succeeded")
        return await self._login_finalize()


    async def _login_finalize(self) -> bool:
        """Common functionality that needs to be performed regardless of the type of login"""

        # Schedule the next refresh of the access token
        self._refresh_schedule = self._access_exp_ts - ACCESS_TOKEN_EXPIRE_MARGIN

        # If needed, start our login_refresh_handler thread
        if self._refresh_handler_start and self._refresh_task is None:
            self._refresh_task = AsyncTaskHelper()
            await self._refresh_task.start(self._login_refresh_handler)

        # In the async Api class we also need the sync client as not all operations are supported on async client
        # In the sync Api class this leads to assigning the same variable twice...
        if self._firestore_client_async is not None and self._firestore_client_close:
            self._firestore_client_async.close()
            self._firestore_client_async = None

        if self._firestore_client_sync is not None and self._firestore_client_close:
            self._firestore_client_sync.close()
            self._firestore_client_sync = None

        credentials = oauth2.Credentials(token=self._access_token, refresh_token=self._refresh_token)

        self._firestore_client_async = firestore_v1.AsyncClient(
            project = FIRESTORE_PROJECT_NAME,
            credentials = credentials
        )
        self._firestore_client_sync = firestore_v1.Client(
            project = FIRESTORE_PROJECT_NAME,
            credentials = credentials
        )
        self._firestore_client_close = True

        # Re-register any callbacks
        for watch_def in self._firestore_watch_def.values():
            context = watch_def.get("context")
            request = watch_def.get("request")
            callback = watch_def.get("callback")
       
            await self._firestore_request(context, request, callback)

        return True


    async def _login_refresh_handler(self) -> bool:
        """
        Parallel task that will refresh the access token when scheduled.
        """
        _LOGGER.debug(f"Token refresh handler started")

        while not self._refresh_task.is_stop_requested():
            try:
                # Wait until access token is almost expired, or wait at least 1 minute
                exp_timestamp = self._refresh_schedule or 0
                now_timestamp = utcnow_ts()
                delay_seconds = max(math.ceil(exp_timestamp - now_timestamp), 60)

                if await self._refresh_task.wait_for_stop(timeout = delay_seconds):
                    # Stop event detected
                    pass
                else:
                    # Reuse access token, refresh it, or re-login
                    await self.login()

            except Exception as ex:
                _LOGGER.debug(f"Token refresh handler caught exception: {ex}")
        
        _LOGGER.debug(f"Token refresh handler stopped")
        return True


    async def logout(self):
        """Logout"""

        # Only one thread at a time can check token and do subsequent login or logout if needed.
        # Once one thread is done, the next thread can then check the (new) token.
        async with self._login_lock:
            await self._logout(context="", method=None)

            # Stop token refresh_handler
            if self._refresh_task is not None:
                await self._refresh_task.stop()
                self._refresh_task = None


    async def _logout(self, context: str, method: LoginMethod|None = None):
        """Internal logout handler"""

        # Note: do not call 'async with self._login_lock' here.
        # It will result in a deadlock as login calls _logout from within its lock

        # Sanitize parameters
        context = context.lower() if context else ""

        # Reduce amount of tracing to only when we are actually logged-in.
        if self._login_time and method not in [LoginMethod.ACCESS_TOKEN]:
           _LOGGER.debug(f"Logout")

        # Instead of closing we will simply forget all tokens. The result is that on a next
        # request, the client will act like it is a new one.
        self._access_token = None
        self._access_exp_ts = None

        # Do not clear refresh token when called in a 'login' context and when we were 
        # only checking the access_token
        if not (context.startswith("login") and method in [LoginMethod.ACCESS_TOKEN]):
            self._refresh_token = None
            self._refresh_timestamp = 0

        # Do not clear login_method when called in a 'login' context, as it interferes with 
        # the loop iterating all login methods.
        if not context.startswith("login"):
            self._login_method = None
            self._login_time = None


    def _get_expire(self, token: str|None) -> float:
        """Return the exp field from the token"""
        try:
            payload = jwt.decode(jwt=token, options={"verify_signature": False})
            
            return float(payload.get("exp", 0))
        except:            
            return float(0)


    async def fetch_profile(self):
        """
        Get user profile
        """
        await self.login()

        _LOGGER.debug(f"Retrieve profile for user '{self._username}' ({self._user_id})")
        return await self._firestore_request(
            context = f"profile {self._user_id}",
            request = {
                "method": FirestoreMethod.DOCUMENT,
                "path": f"profiles/{self._user_id}",
            },
        )
    

    async def on_profile(self, callback):
        """
        Register a callback function that will fire:
        - Once initially
        - On each change of the profile
        """
        await self.login()

        _LOGGER.info(f"Register watch on profile for user '{self._username}' ({self._user_id})")
        return await self._firestore_request(
            context = f"watch {self._user_id}",
            request = {
                "method": FirestoreMethod.WATCH,
                "path": f"profiles/{self._user_id}",
            },
            callback = callback,
        )


    async def fetch_gateway(self, gateway_id: str):
        """
        Get gatweway
        """
        await self.login()

        _LOGGER.debug(f"Retrieve gateway '{gateway_id}'")
        return await self._firestore_request(
            context = f"gateway {gateway_id}",
            request = {
                "method": "FirestoreDoc",
                "path": f"gateways/{gateway_id}",
            },
        )


    async def fetch_gateways(self):
        """
        Get all available gateways
        """
        await self.login()

        _LOGGER.debug(f"Retrieve all gateways for user '{self._username}' ({self._user_id})")
        return await self._firestore_request(
            context = f"gateways {self._user_id}",
            request = {
                "method": FirestoreMethod.COLLECTION,
                "path": f"gateways",
                "where": {
                    "field_path": f"members.{self._user_id}.enabled",
                    "op_string": "==",
                    "value": True,
                },
                "order": {
                    "field_path": "__name__",
                    "direction": "ASCENDING",
                },
            },
        )


    async def on_gateway(self, gateway_id: str, callback):
        """
        Register a callback function that will fire:
        - Once initially
        - On each change of the gateway
        """
        await self.login()

        _LOGGER.info(f"Register watch on gateway '{gateway_id}'")
        return await self._firestore_request(
            context = f"watch {gateway_id}",
            request = {
                "method": FirestoreMethod.WATCH,
                "path": f"gateways/{gateway_id}",
            },
            callback = callback,
        )


    async def fetch_device(self, device_id: str):
        """
        Get device (tank or pump)
        """
        await self.login()

        _LOGGER.debug(f"Retrieve device '{device_id}'")
        return await self._firestore_request(
            context = f"device {device_id}",
            request = {
                "method": "FirestoreDoc",
                "path": f"devices/{device_id}",
            },
        )


    async def fetch_devices(self, gateway_id: str):
        """
        Get all available devices for a gatweway
        """
        await self.login()

        _LOGGER.debug(f"Retrieve all devices for gateway '{gateway_id}'")
        return await self._firestore_request(
            context = f"devices {gateway_id}",
            request = {
                "method": FirestoreMethod.COLLECTION,
                "path": f"devices",
                "where": {
                    "field_path": f"gatewayId",
                    "op_string": "==",
                    "value": gateway_id,
                },
                "order": {
                    "field_path": "__name__",
                    "direction": "ASCENDING",
                },
            },
        )


    async def on_device(self, device_id: str, callback):
        """
        Register a callback function that will fire:
        - Once initially
        - On each change of the gateway
        """
        await self.login()

        _LOGGER.info(f"Register watch on device '{device_id}'")
        return await self._firestore_request(
            context = f"watch {device_id}",
            request = {
                "method": FirestoreMethod.WATCH,
                "path": f"devices/{device_id}",
            },
            callback = callback,
        )


    async def _http_request(self, context, request):
        """
        GET or POST a request for JSON data

        Only used for login and token refresh
        """

        # Perform the request
        dt = utcnow_dt()
        response = None
        flags = request.get("flags", {})
        try:
            rsp = await self._http_client.request(
                method = request["method"], 
                url = request["url"],
                params = request.get("params", None), 
                data = request.get("data", None), 
                json = request.get("json", None), 
                headers = request.get("headers", None),
                follow_redirects = flags.get("redirects", True)
            )

            # Remember actual requests and response params, used for diagnostics
            request["headers"] = rsp.request.headers
            response = {
                "success": rsp.is_success,
                "status": f"{rsp.status_code} {rsp.reason_phrase}",
                "headers": rsp.headers,
                "elapsed": round((utcnow_dt() - dt).total_seconds(), 1),
            }
            if rsp.is_success and rsp.headers.get('content-type','').startswith('application/json'):
                response["json"] = rsp.json()
            else:
                response["text"] = rsp.text

        except Exception as ex:
            error = f"Unable to perform request, got exception '{str(ex)}' while trying to reach {request["url"]}"
            _LOGGER.debug(error)

            # Force a logout to so next login will be a real login, not a token reuse
            await self._logout(context)
            raise SmartWaterConnectError(error)

        # Save the diagnostics if requested
        self._add_diagnostics(dt, context, request, response)
        
        # Check response
        if not response["success"]:
            error = f"Unable to perform request, got response {response["status"]} while trying to reach {request["url"]}"
            _LOGGER.debug(error)

            # Force a logout to so next login will be a real login, not a token reuse
            await self._logout(context)
            if "401" in response["status"]:
                raise SmartWaterAuthError(error)
            else:
                raise SmartWaterConnectError(error)
        
        if flags.get("redirects",None) == False and response['status'].startswith("302"):
            return response["headers"].get("location", '')

        elif "text" in response:
            return response["text"]
        
        elif "json" in response:
            return response["json"]
        
        else:
            return None
    

    async def _firestore_request(self, context: str, request: dict, callback=None):
        """Firestore document, collection or watch request"""
        
        # Perform the request
        dt = utcnow_dt()
        response = {}
        try:
            if request["method"] == FirestoreMethod.DOCUMENT:
                # Get the snapshot for this document ref and convert it to a dict
                doc_ref = self._firestore_client_async.document(request["path"])
                doc_snap = await doc_ref.get()

                doc_json = doc_snap.to_dict()

                response = {
                    "id": doc_snap.id,
                    "created": doc_snap.create_time,
                    "updated": doc_snap.update_time,
                    "elapsed": round((utcnow_dt() - dt).total_seconds(), 1),
                    "json": doc_json,
                }

            elif request["method"] == FirestoreMethod.COLLECTION:
                # Query for the requested documents and convert result into a map of id to dict
                coll_ref = self._firestore_client_async.collection(request["path"])

                if "where" in request:
                    r_where = request["where"]
                    f_filter = firestore_v1.FieldFilter(
                                    field_path = r_where.get("field_path"), 
                                    op_string = r_where.get("op_string", "=="), 
                                    value = r_where.get("value", None)
                    )
                    coll_ref = coll_ref.where(filter = f_filter)

                if "order" in request:
                    r_order = request["order"]
                    if r_order.get("direction") == "DESCENDING":
                        f_direction = firestore_v1.types.query.StructuredQuery.Direction.DESCENDING
                    else:
                        f_direction = firestore_v1.types.query.StructuredQuery.Direction.ASCENDING

                    coll_ref = coll_ref.order_by(
                                    field_path = r_order.get("field_path"), 
                                    direction = f_direction
                    )

                # Result is a list of document snapshots
                # Convert into a mapping from id to dict
                coll_snap = await coll_ref.get()
                
                response = {
                    "items": { item.id: item.to_dict() for item in coll_snap },
                    "elapsed": round((utcnow_dt() - dt).total_seconds(), 1),
                }

            elif request["method"] == FirestoreMethod.WATCH:
                # Start a watcher for changes to a document
                doc_path = request["path"]
                doc_ref = self._firestore_client_sync.document(doc_path)
                
                # Helper functions to process the result before we return it to the outer callback
                def watcher_callback(doc_snapshot, changes, read_time):
                    for doc_snap in doc_snapshot:
                        dt = utcnow_dt()
                        context = f"snapshot {doc_snap.id}"
                        request = {
                            "method": FirestoreMethod.SNAPSHOT,
                            "path": doc_path,
                        }
                        response = {
                            "id": doc_snap.id,
                            "created": doc_snap.create_time,
                            "updated": doc_snap.update_time,
                            "json": doc_snap.to_dict(),
                        }
                        self._add_diagnostics(dt, context, request, response)

                        callback(doc_snap.id, doc_snap.to_dict())

                # Register the snapshot callback and remember it so we can discard it on close
                # Also remember the original parameters so we can re-register when credentials are refreshed
                self._firestore_watch_map[doc_path] = doc_ref.on_snapshot(watcher_callback)
                self._firestore_watch_def[doc_path] = {
                    "context": context,
                    "request": request,
                    "callback": callback,
                }

                response = {
                    "elapsed": round((utcnow_dt() - dt).total_seconds(), 1),
                }
            else:
                raise NotImplementedError(f"FirestoreMethod '{request["method"]}'")
            
        except Exception as ex:
            error = f"Unable to perform request, got exception '{str(ex)}' while trying to reach {request["method"]} '{request["path"]}'"
            _LOGGER.debug(error)

            # Force a logout to so next login will be a real login, not a token reuse
            await self._logout(context)
            raise SmartWaterConnectError(error)
        
        # Save the diagnostics if requested
        self._add_diagnostics(dt, context, request, response)
        
        if "json" in response:
            return response["json"]
        elif "items" in response:
            return response["items"]
        else:
            return None


    def _add_diagnostics(self, dt: datetime, context: str, request: dict|None, response: dict|None, token: dict|None = None):
        """Gather diagnostics"""

        if not self._diag_collect:
            return

        method = request.get("method", "unknown") if request is not None else None
        method = method.replace("GET", "HttpGet").replace("POST", "HttpPost") if method is not None else None

        duration = response.get("elapsed", None) if response is not None else None
        duration = round(duration, 0) if duration is not None else None
        
        history_item = SmartWaterHistoryItem.create(dt, context, request, response, token)
        history_detail = SmartWaterHistoryDetail.create(dt, context, request, response, token)

        # Call durations
        if duration is not None:
            if duration in self._diag_durations:
                self._diag_durations[duration] += 1
            else:
                self._diag_durations[duration] = 1

        # Call method
        if method is not None:
            if method in self._diag_methods:
                self._diag_methods[method] += 1
            else:
                self._diag_methods[method] = 1

        # Call counters
        if context in self._diag_counters:
            self._diag_counters[context] += 1
        else:
            self._diag_counters[context] = 1

        # Call history        
        self._diag_history.append(history_item)
        while len(self._diag_history) > 64:
            self._diag_history.pop(0)

        # Call details
        self._diag_details[context] = history_detail


    async def get_diagnostics(self) -> dict[str, Any]:
        """Return the gathered diagnostics"""

        data = {
            "login_time": self._login_time,
            "login_method": self._login_method,
        }

        calls_total = sum([ n for key, n in self._diag_counters.items() ]) or 1
        calls_counter = { key: n for key, n in self._diag_counters.items() }
        calls_percent = { key: round(100.0 * n / calls_total, 2) for key, n in calls_counter.items() }

        durations_total = sum(self._diag_durations.values()) or 1
        durations_counter = dict(sorted(self._diag_durations.items()))
        durations_percent = { key: round(100.0 * n / durations_total, 2) for key, n in durations_counter.items() }

        methods_total = sum(self._diag_methods.values()) or 1
        methods_counter = dict(sorted(self._diag_methods.items()))
        methods_percent = { key: round(100.0 * n / methods_total, 2) for key, n in methods_counter.items() }
        
        return {
            "data": data,
            "diagnostics": {
                "dt": utcnow_dt(),
                "durations": {
                    "counter": durations_counter,
                    "percent": durations_percent,
                },
                "methods": {
                    "counter": methods_counter,
                    "percent": methods_percent,
                },
                "calls": {
                    "counter": calls_counter,
                    "percent": calls_percent,
                },
            },
            "history": self._diag_history,
            "details": self._diag_details,
        }
