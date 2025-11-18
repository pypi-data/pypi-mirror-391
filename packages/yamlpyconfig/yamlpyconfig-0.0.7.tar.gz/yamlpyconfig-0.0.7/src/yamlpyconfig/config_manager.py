import logging
from typing import Optional

from .models import AlgorithmEnum
from yamlpyconfig.config_cache import ConfigCache
from yamlpyconfig.local_manage.local_config_manager import LocalConfigManager
from yamlpyconfig.models import NacosConfig
from yamlpyconfig.nacos_manage.nacos_config_manager import NacosConfigManager
from yamlpyconfig.utils.crypto.crypto_algorithm_factory import CryptoAlgorithmFactory
from .utils.crypto import CryptoHelper

logger = logging.getLogger(__name__)
class ConfigManager:
    """
    ConfigManager is a singleton class that manages the configuration of the application.
    It provides methods to get and set configuration values.
    """
    def __init__(self, config_dir: Optional[str] = None,
                 crypto_algorithm: AlgorithmEnum|None = None, key: str = None):
        """

        :param config_dir: 本地配置文件的根目录，包含application.yaml和application-{profile}.yaml的目录
        :param crypto_algorithm: 如果配置文件中包含{encrypted}加密数据，可以配置加密算法，用来解密
        :param key: 如果是sm2则传递私钥，如果是sm4则传递对称密钥
        """

        self._base_config = LocalConfigManager(config_dir).load_config()
        self._crypto_helper = None
        if crypto_algorithm and key:
            crypto_algorithm = CryptoAlgorithmFactory.create(crypto_algorithm, key_b64=key)
            self._crypto_helper = CryptoHelper(crypto_algorithm)
        self._cache = ConfigCache(base_config=self._base_config, crypto_helper=self._crypto_helper)
        self._nacos_manager = None


    async def start(self):
        if self._nacos_manager is None:
            try:
                nacos_config: NacosConfig = NacosConfig.load_nacos_config(self._cache.get_config())
                if nacos_config:
                    self._nacos_manager = NacosConfigManager(nacos_config, cache=self._cache)
                    await self._nacos_manager.start()
            except Exception as e:
                logger.error(f"Failed to connect to Nacos: {e}", exc_info=True)

    async def __aenter__(self):
        await self.start()
        return self
    async def stop(self):
        if self._nacos_manager:
            await self._nacos_manager.stop()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def get_config(self):
        return self._cache.get_config()