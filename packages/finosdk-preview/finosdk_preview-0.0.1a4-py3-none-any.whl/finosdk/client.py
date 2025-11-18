# D:\prog\finosdk\src\finosdk\client.py
import json, os
from typing import Any, Dict, List, Optional
import requests

class APIError(Exception):
    pass

DEFAULT_BASE_URL = "https://track.finoview.com.cn/data_api/"
class Client:
    """
    轻量 HTTP 客户端
    """
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        # URL 不再从环境变量读取，只支持代码里传，或者用默认线上地址
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")

        self.timeout = timeout
        self._session = session or requests.Session()
        self._headers = {"Content-Type": "application/json"}

        # 只给 token 保留一个环境变量入口，方便用户少写一行代码
        env_token = os.getenv("FINO_API_KEY")
        tok = token or env_token
        if tok:
            self._headers["Authorization"] = f"Bearer {tok}"

    # ---------- 基础 POST ----------
    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        """
        endpoint:
          - 简写: "fac_carry" => /factor/fac_carry
          - 或完整: "factor/fac_carry" / "factor/csft_bkt_perf"
        """
        if "/" not in endpoint:
            path = f"/factor/{endpoint}"
        else:
            path = f"/{endpoint.lstrip('/')}"
        url = f"{self.base_url}{path}"

        r = self._session.post(
            url,
            data=json.dumps(payload),
            headers=self._headers,
            timeout=self.timeout,
        )
        if r.status_code != 200:
            raise APIError(f"HTTP {r.status_code}: {r.text}")
        try:
            ret = r.json()
        except Exception as e:
            raise APIError(f"Invalid JSON response: {e}\nText: {r.text}") from e

        code = ret.get("code", 500)
        if code != 200:
            raise APIError(ret.get("msg") or ret.get("message") or "API error")

        # 兼容服务端返回 data / obj 两种字段
        data = ret.get("data", None)
        if data is None:
            data = ret.get("obj", None)
        return data

    # ---------- fac_* 通用 ----------
    def _fac_generic(
        self,
        endpoint: str,
        *,
        start_date: str,
        end_date: str,
        code_list: Optional[List[str]] = None,
        factor: Optional[List[str]] = None,
        section: Optional[List[str]] = None,
    ):
        payload: Dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if code_list:
            payload["code_list"] = code_list
        if factor:
            payload["factor"] = factor
        if section:
            payload["section"] = section
        return self._post(endpoint, payload)

    def fac_carry(self, **kwargs):      return self._fac_generic("fac_carry",      **kwargs)
    def fac_trend(self, **kwargs):       return self._fac_generic("fac_trend",     **kwargs)
    def fac_position(self, **kwargs):     return self._fac_generic("fac_position",     **kwargs)
    def fac_futurespot(self, **kwargs): return self._fac_generic("fac_futurespot", **kwargs)
    def fac_value(self, **kwargs):      return self._fac_generic("fac_value",      **kwargs)
    def fac_warrant(self, **kwargs):    return self._fac_generic("fac_warrant",    **kwargs)
    def fac_volatility(self, **kwargs): return self._fac_generic("fac_volatility", **kwargs)

    # ---------- csft_* 通用 ----------
    def _csft_generic(
        self,
        endpoint: str,
        *,
        start_date: str,
        end_date: str,
        factor: Optional[List[str]] = None,
    ):
        payload: Dict[str, Any] = {"start_date": start_date, "end_date": end_date}
        # factor 不传或传 [] => 全量
        if factor:
            payload["factor"] = factor
        return self._post(endpoint, payload)

    def csft_bkt_perf(self, **kwargs):  return self._csft_generic("csft_bkt_perf",  **kwargs)
    def csft_bkt_data(self, **kwargs):  return self._csft_generic("csft_bkt_data",  **kwargs)
    def csft_bkt_dcp(self,  **kwargs):  return self._csft_generic("csft_bkt_dcp",   **kwargs)
    def csft_test_perf(self, **kwargs): return self._csft_generic("csft_test_perf", **kwargs)
    def csft_test_data(self, **kwargs): return self._csft_generic("csft_test_data", **kwargs)
    def csft_test_dcp(self,  **kwargs): return self._csft_generic("csft_test_dcp",  **kwargs)
