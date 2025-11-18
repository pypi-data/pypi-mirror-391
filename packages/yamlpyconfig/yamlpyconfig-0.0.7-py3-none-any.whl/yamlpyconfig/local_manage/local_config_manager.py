import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

from yamlpyconfig.utils import ExpressionHelper
from yamlpyconfig.local_manage import LocalConfigLoader
from yamlpyconfig.utils import ConfigMerge

logger = logging.getLogger(__name__)

class LocalConfigManager:
    """
    Local configuration manager.
    默认获取 config_dir / application.yaml 以及 config_dir / application-{profile}.yaml 的本地文件配置。
    其中 profile 的获取逻辑是：
    1. 首先获取APP_PROFILE作为环境变量的值，如果存在返回
    2. 然后获取SPRING_PROFILES_ACTIVE座位环境变量的值，如果存在返回
    3. 最后获取application.yaml配置文件中的profile的配置，如果存在则返回
    如果以上三处都未获取到有效的profile，则不再尝试获取application-{profile}.yaml的配置。
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize local config manager.

        Args:
            config_dir: Directory containing config files. Defaults to current working directory.
        """
        self.config_dir = Path(config_dir) if config_dir else Path.cwd()

    def load_config(self) -> Dict[str, Any]:
            """Load local configuration.

            Args:
                profile: Profile to load. Defaults to None.

            Returns:
                A dictionary with the loaded configuration.
            """
            config: dict[str, Any] = LocalConfigLoader(self.config_dir).load_local_yaml("application")
            ExpressionHelper.resolve_config(config)

            profile = self._detect_profile(config)
            if profile:
                logger.info(f"Using profile: {profile}")
                config_profile = LocalConfigLoader(self.config_dir).load_local_yaml(f"application-{profile}")
                ConfigMerge.deep_merge(config, config_profile, False)
            ExpressionHelper.resolve_config(config)
            return config

    @staticmethod
    def _detect_profile(config) -> Optional[str]:
        """Detect profile from environment or config files."""
        # Check environment variable
        env_profile = os.getenv('APP_PROFILE', os.getenv('SPRING_PROFILES_ACTIVE'))
        if env_profile:
            return env_profile
        # Try to extract from local loader
        if "profile" in config:
            return config["profile"]
        return None