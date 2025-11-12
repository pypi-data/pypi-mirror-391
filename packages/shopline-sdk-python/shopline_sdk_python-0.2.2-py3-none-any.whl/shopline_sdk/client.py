from typing import Optional

import aiohttp


class ShoplineAPIClient:
    def __init__(self, access_token, base_url='https://open.shopline.io/v1'):
        self.base_url = base_url.rstrip('/') + '/'
        self.access_token = access_token

    def new_session(self, headers: Optional[dict] = None, **kwargs):
        authed_headers = {'Authorization': f'Bearer {self.access_token}'}
        if headers:
            authed_headers.update(headers)
        return aiohttp.ClientSession(base_url=self.base_url, headers=authed_headers, **kwargs)
