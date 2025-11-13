import logging
from typing import Optional

from yamlpyconfig.config_cache import ConfigCache
from yamlpyconfig.local_manage.local_config_manager import LocalConfigManager
from yamlpyconfig.models import NacosConfig
from yamlpyconfig.nacos_manage.nacos_config_manager import NacosConfigManager

logger = logging.getLogger(__name__)
class ConfigManager:
    """
    ConfigManager is a singleton class that manages the configuration of the application.
    It provides methods to get and set configuration values.
    """
    def __init__(self, config_dir: Optional[str] = None):
        self._base_config = LocalConfigManager(config_dir).load_config()
        self._cache = ConfigCache(base_config=self._base_config)
        self._nacos_manager = None


    async def start(self):
        if self._nacos_manager is None:
            try:
                nacos_config: NacosConfig = NacosConfig.load_nacos_config(self._base_config)
                if nacos_config:
                    self._nacos_manager = NacosConfigManager(nacos_config, cache=self._cache)
                    await self._nacos_manager.start()
            except Exception as e:
                logger.error(f"Failed to connect to Nacos: {e}", exc_info=True)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._nacos_manager:
            await self._nacos_manager.close()

    def get_config(self):
        return self._cache.get_config()