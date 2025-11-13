import aiohttp
import asyncio
import time
from enum import Enum
from typing import Optional, Any, Dict

class AuditStatus(str, Enum):
    TO_TESTS = "to-tests"
    FAILED = "failed"
    PASSED = "passed"

class Device(str, Enum):
    ALL = "all"
    DESKTOP = "desktop"
    MOBILE = "mobile"

class Language(str, Enum):
    PL = "pl"
    EN = "en"
    DE = "de"

class Sort(str, Enum):
    CREATED_AT_ASC = "created_at_asc"
    CREATED_AT_DESC = "created_at_desc"
    LAST_AUDIT_ASC = "last_audit_asc"
    LAST_AUDIT_DESC = "last_audit_desc"

class A11yCheckerClientAPIError(Exception):
    """API Error"""

class A11yCheckerClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://a11y-checker.wcag.dock.codes"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.auth_token: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "get",
        timeout: int = 300,
    ) -> Dict[str, Any]:
        if not self._session:
            self._session = aiohttp.ClientSession()

        params = params or {}
        params = {k: v for k, v in params.items() if v is not None}

        if self.api_key:
            params.setdefault("key", self.api_key)

        params["t"] = int(time.time() / 10_000)
        url = f"{self.base_url}/api/{endpoint}"

        req_headers = {"Accept": "application/json"}
        if self.auth_token:
            req_headers["Authorization"] = f"Bearer {self.auth_token}"
        if headers:
            req_headers.update(headers)

        try:
            async with asyncio.timeout(timeout):
                if method.lower() in ["get", "delete"]:
                    async with self._session.request(method.upper(), url, params=params, headers=req_headers) as res:
                        data = await res.json(content_type=None)
                else:
                    async with self._session.request(method.upper(), url, json=params, headers=req_headers) as res:
                        data = await res.json(content_type=None)

                if "detail" in data:
                    raise A11yCheckerClientAPIError(data["detail"])

                return data
        except asyncio.TimeoutError:
            raise A11yCheckerClientAPIError(f"Request to {endpoint} timed out")
        except aiohttp.ClientError as e:
            raise A11yCheckerClientAPIError(f"Request failed: {e}")

    async def scan(
        self,
        url: str,
        lang: Language = Language.EN,
        device: Device = Device.ALL,
        sync: bool = False,
        extra_data: bool = False,
        unique_key: Optional[str] = None,
        recaptcha_token: Optional[str] = None,
        key: Optional[str] = None,
    ):
        params = {
            "url": url,
            "sync": str(sync),
            "lang": lang.value,
            "extra_data": str(extra_data),
            "unique_key": unique_key,
            "recaptcha_token": recaptcha_token,
            "key": key,
        }
        if device != Device.ALL:
            params["device"] = device.value
        return await self._request("scan", params, method="get")

    async def rescan(
        self,
        uuid: str,
        lang: Language = Language.EN,
        sync: bool = False,
        extra_data: bool = False,
        recaptcha_token: Optional[str] = None,
        key: Optional[str] = None
    ):
        params = {"uuid": uuid, lang: lang.value, "sync": str(sync), "extra_data": str(extra_data), "recaptcha_token": recaptcha_token, "key": key}
        return await self._request("rescan", params, method="get")

    async def audit(
        self,
        uuid: str,
        lang: Language = Language.EN,
        extra_data: bool = False,
        key: Optional[str] = None
    ):
        params = {"uuid": uuid, 'lang': lang.value, "extra_data": str(extra_data), "key": key}
        return await self._request("audit", params, method="get")

    async def audits(
        self,
        search: str,
        page: int = 1,
        per_page: int = 10,
        sort: Sort = Sort.LAST_AUDIT_DESC,
        unique_key: Optional[str] = None,
        key: Optional[str] = None
    ):
        params = {"search": search, 'page': page, 'per_page': per_page, 'sort': sort.value, "unique_key": unique_key, "key": key}
        return await self._request("audits", params, method="get")

    async def history(
        self,
        uuid: str,
        page: int = 1,
        per_page: int = 10,
        sort: Sort = Sort.CREATED_AT_DESC,
        key: Optional[str] = None
    ):
        params = {"uuid": uuid, 'page': page, 'per_page': per_page, 'sort': sort.value, "key": key}
        return await self._request("history", params, method="get")

    async def delete_audit(self, uuid: str, key: Optional[str] = None):
        return await self._request("audit", {"uuid": uuid, "key": key}, method="delete")

    async def delete_history(self, uuid: str, key: Optional[str] = None):
        return await self._request("history", {"uuid": uuid, "key": key}, method="delete")

    async def update_audit_manual(self, uuid: str, criterion_id: int, status: AuditStatus, device: Device = Device.DESKTOP, key: Optional[str] = None):
        params = {
            "uuid": uuid,
            "criterion_id": criterion_id,
            "status": status.value,
            "device": device.value,
            "key": key,
        }
        return await self._request("audit/manual", params, method="post")

    async def user(self, key: Optional[str] = None):
        return await self._request("user", {"key": key}, method="get")
