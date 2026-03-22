"""Async HTTP client wrapping the backend REST API."""
import httpx
import config


class APIClient:
    def __init__(self):
        self.base = config.BACKEND_URL
        self.device = config.DEVICE_ID
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base, timeout=10.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_status(self) -> dict | None:
        c = await self._get_client()
        try:
            r = await c.get(f'/api/devices/{self.device}/status')
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def trigger_feed(self, portion: int = 50) -> dict | None:
        c = await self._get_client()
        try:
            r = await c.post(f'/api/devices/{self.device}/feed', json={'portion': portion})
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def get_schedule(self) -> dict | None:
        c = await self._get_client()
        try:
            r = await c.get(f'/api/devices/{self.device}/schedule')
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def update_schedule(self, times: list[str]) -> dict | None:
        c = await self._get_client()
        try:
            r = await c.post(f'/api/devices/{self.device}/schedule', json={'times': times})
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def get_settings(self) -> dict | None:
        c = await self._get_client()
        try:
            r = await c.get(f'/api/devices/{self.device}/settings')
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def update_settings(self, settings: dict) -> dict | None:
        c = await self._get_client()
        try:
            r = await c.post(f'/api/devices/{self.device}/settings', json=settings)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def get_events(self, limit: int = 10, event_type: str | None = None) -> list | None:
        c = await self._get_client()
        params = {'limit': limit}
        if event_type:
            params['type'] = event_type
        try:
            r = await c.get(f'/api/devices/{self.device}/events', params=params)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def get_stats(self, period: str = 'day') -> dict | None:
        c = await self._get_client()
        try:
            r = await c.get(f'/api/devices/{self.device}/stats', params={'period': period})
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    async def get_telemetry(self, period: str = '24h', limit: int = 100) -> list | None:
        c = await self._get_client()
        try:
            r = await c.get(f'/api/devices/{self.device}/telemetry', params={'period': period, 'limit': limit})
            r.raise_for_status()
            return r.json()
        except Exception:
            return None


api = APIClient()
