import httpx
from ..types.common import MerchantVersionResponse
from ..version import check_version, MERCHANT_PROTOCOL_VERSION
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class MerchantClient:
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.httpx_client = httpx.Client()
        try:
            server_config = self.get_config()
        except ValidationError as e:
            raise ValueError(f"Backend returned an unexpected /config response: {e}") from e
        if not check_version(server_config.version, MERCHANT_PROTOCOL_VERSION):
             logger.warning(f"Server version: {server_config.version} and Client version: {MERCHANT_PROTOCOL_VERSION} are incompatible")
    
    def get_config(self):
        r = self.httpx_client.get(f'{self.base_url}/config').raise_for_status()
        v = MerchantVersionResponse.model_validate(r.json())
        return v

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.httpx_client.close()