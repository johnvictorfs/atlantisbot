from typing import Dict, Any

import aiohttp


class ApiService:
    def __init__(self, base_url: str, path: str, api_token: str):
        self.base_url = base_url
        self.path = path

        headers = {'authorization': api_token}
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(headers=headers)

    @property
    def url(self) -> str:
        return f"{self.base_url}/{self.path}/"

    def object_url(self, pk: int) -> str:
        return f"{self.base_url}/{self.path}/{pk}/"

    async def search(self, query: str):
        response = await self.session.get(f"{self.url}?search={query}")
        return await response.json()

    async def get_one(self, pk: int):
        """Get one Object from API by pk"""
        response = await self.session.get(self.object_url(pk))
        return await response.json()

    async def get_all(self):
        """Get all Objects from that type from API"""
        response = await self.session.get(self.url)
        return await response.json()

    async def delete(self, pk: int):
        """Delete one Object by pk"""
        response = await self.session.delete(self.object_url(pk))
        return await response.json()

    async def update(self, pk: int, data: Dict[str, Any]):
        """Update one Object by pk"""
        response = await self.session.put(self.object_url(pk), data=data)
        return await response.json()

    async def create(self, data: Dict[str, Any]):
        """Create one Object with the data passed"""
        response = await self.session.post(self.url, data=data)
        return await response.json()


discord = ApiService(base_url='https://rsatlantis.tk', path='discord', api_token='')


class BotApi:
    def __init__(self, base_url: str, api_token: str):
        self.discord_users = ApiService(base_url=base_url, path='atlantisbot/api/users', api_token=api_token)
        self.users = ApiService(base_url=base_url, path='api/users', api_token=api_token)
        self.amigo_secreto = ApiService(base_url=base_url, path='atlantisbot/api/amigosecreto', api_token=api_token)
        self.amigo_secreto_status = ApiService(base_url=base_url, path='atlantisbot/api/amigosecreto_status', api_token=api_token)
        self.disabled_commands = ApiService(base_url=base_url, path='atlantisbot/api/disabled_commands', api_token=api_token)
        self.ingame_names = ApiService(base_url=base_url, path='atlantisbot/api/ingame_names', api_token=api_token)
