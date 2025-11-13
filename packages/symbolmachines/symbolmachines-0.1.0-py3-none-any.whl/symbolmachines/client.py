import requests
from typing import Optional, Dict, Any


class Symbol:
    """
    Main Symbol Machines SDK client.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.symbol.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url

        self.memory = {
            "inject": {"create": self._create_inject},
            "save": {"create": self._create_save},
        }

    # -------------------------
    # Internal HTTP wrapper
    # -------------------------
    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if not response.ok:
            raise Exception(f"SymbolMachines API Error {response.status_code}: {response.text}")

        # return JSON or empty dict
        try:
            return response.json()
        except ValueError:
            return {}

    # -------------------------
    # Public Methods
    # -------------------------
    def _create_inject(self, input: str) -> Dict[str, Any]:
        return self._post("/memory/inject", {"input": input})

    def _create_save(self, output: str) -> None:
        self._post("/memory/save", {"output": output})
