from __future__ import absolute_import, division, print_function

__metaclass__ = type

from enum import Enum
import requests


class CDORegion(Enum):
    """CDO UI endpoints (not the CDO public API)"""

    CDO_US = "defenseorchestrator.com"
    CDO_EU = "defenseorchestrator.eu"
    CDO_APJ = "www.apj.cdo.cisco.com"


class CDO:
    """Execute API calls against the CDO API"""

    def __init__(self, cdo_token: str, cdo_region: str) -> None:
        self.cdo_token = cdo_token
        self.cdo_region = CDORegion[cdo_region].value

    def _headers(self):
        """Build the required headers for CDO"""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"Python-cdo-objects",
            "Authorization": f"Bearer {self.cdo_token}",
        }

    def get(self, path: str = "", query: str = "") -> dict:
        """CDO GET operation"""
        uri = self.cdo_region if not path else f"{self.cdo_region}{path}"
        result = requests.get(url=f"https://{uri}", params=query, headers=self._headers())
        result.raise_for_status()
        if result.json():
            return result.json()


class CDOObjects(CDO):
    """Get CDO network objects using the CDO UI API (Not the Public API)"""

    def __init__(self, cdo_token, cdo_region) -> None:
        super().__init__(cdo_token, cdo_region)

    def get_objects(self, q, count=False, limit: int = 100, offset: int = 0) -> list:
        """Return CDO objects and object-groups or return the number of objects/object-groups that match the query"""
        q = q + f"&sort=name%3Aasc&limit={limit}&offset={offset}" if not count else "agg=count&" + q
        return self.get(path="/aegis/rest/v1/services/targets/objects", query=q)
