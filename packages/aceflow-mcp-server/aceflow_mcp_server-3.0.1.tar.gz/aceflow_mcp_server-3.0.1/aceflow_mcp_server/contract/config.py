"""
Configuration management for contract management feature.

This extends the existing config.py with contract-specific configuration.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml


class ContractConfig:
    """Configuration for contract management"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize contract configuration.

        Args:
            config_path: Path to .aceflow/config.yaml, defaults to .aceflow/config.yaml in current directory
        """
        if config_path is None:
            config_path = Path.cwd() / ".aceflow" / "config.yaml"

        self.config_path = config_path
        self.config_dir = config_path.parent
        self._config: Dict[str, Any] = {}

        if config_path.exists():
            self.load()

    def load(self) -> None:
        """Load configuration from file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

    def save(self) -> None:
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)

    @property
    def project_name(self) -> Optional[str]:
        """Get project name"""
        return self._config.get('aceflow', {}).get('project', {}).get('name')

    @project_name.setter
    def project_name(self, value: str) -> None:
        """Set project name"""
        if 'aceflow' not in self._config:
            self._config['aceflow'] = {}
        if 'project' not in self._config['aceflow']:
            self._config['aceflow']['project'] = {}
        self._config['aceflow']['project']['name'] = value

    @property
    def openapi_url(self) -> Optional[str]:
        """Get OpenAPI URL"""
        return self._config.get('aceflow', {}).get('project', {}).get('openapi_url')

    @openapi_url.setter
    def openapi_url(self, value: str) -> None:
        """Set OpenAPI URL"""
        if 'aceflow' not in self._config:
            self._config['aceflow'] = {}
        if 'project' not in self._config['aceflow']:
            self._config['aceflow']['project'] = {}
        self._config['aceflow']['project']['openapi_url'] = value

    @property
    def contract_repo_url(self) -> Optional[str]:
        """Get contract repository URL"""
        return self._config.get('aceflow', {}).get('contract_repo', {}).get('url')

    @contract_repo_url.setter
    def contract_repo_url(self, value: str) -> None:
        """Set contract repository URL"""
        if 'aceflow' not in self._config:
            self._config['aceflow'] = {}
        if 'contract_repo' not in self._config['aceflow']:
            self._config['aceflow']['contract_repo'] = {}
        self._config['aceflow']['contract_repo']['url'] = value

    @property
    def contract_repo_branch(self) -> str:
        """Get contract repository branch"""
        return self._config.get('aceflow', {}).get('contract_repo', {}).get('branch', 'main')

    @property
    def contract_repo_base_path(self) -> str:
        """Get contract repository base path"""
        return self._config.get('aceflow', {}).get('contract_repo', {}).get('base_path', 'contracts/active')

    def get_feature(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Get feature configuration.

        Args:
            feature_name: Feature name

        Returns:
            Feature configuration dict or None if not found
        """
        return self._config.get('aceflow', {}).get('features', {}).get(feature_name)

    def add_feature(self, feature_name: str, config: Dict[str, Any]) -> None:
        """
        Add or update feature configuration.

        Args:
            feature_name: Feature name
            config: Feature configuration
        """
        if 'aceflow' not in self._config:
            self._config['aceflow'] = {}
        if 'features' not in self._config['aceflow']:
            self._config['aceflow']['features'] = {}
        self._config['aceflow']['features'][feature_name] = config

    def get_features(self) -> Dict[str, Any]:
        """
        Get all feature configurations.

        Returns:
            Dictionary of all features
        """
        return self._config.get('aceflow', {}).get('features', {})

    def list_features(self) -> List[str]:
        """
        List all configured features.

        Returns:
            List of feature names
        """
        return list(self._config.get('aceflow', {}).get('features', {}).keys())

    def remove_feature(self, feature_name: str) -> None:
        """
        Remove a feature configuration.

        Args:
            feature_name: Feature name to remove
        """
        features = self._config.get('aceflow', {}).get('features', {})
        if feature_name in features:
            del features[feature_name]

    @property
    def smtp_config(self) -> Optional[Dict[str, Any]]:
        """Get SMTP configuration"""
        email_config = self._config.get('aceflow', {}).get('notification', {}).get('email', {})
        if not email_config.get('enabled', False):
            return None
        return email_config.get('smtp')

    def set_smtp_config(self, host: str, port: int, user: str, password: str, from_email: str) -> None:
        """
        Set SMTP configuration.

        Args:
            host: SMTP server host
            port: SMTP server port
            user: SMTP username
            password: SMTP password (will be stored as env var reference)
            from_email: From email address
        """
        if 'aceflow' not in self._config:
            self._config['aceflow'] = {}
        if 'notification' not in self._config['aceflow']:
            self._config['aceflow']['notification'] = {}
        if 'email' not in self._config['aceflow']['notification']:
            self._config['aceflow']['notification']['email'] = {}

        self._config['aceflow']['notification']['email'] = {
            'enabled': True,
            'smtp': {
                'host': host,
                'port': port,
                'user': user,
                'password': '${SMTP_PASSWORD}',  # Use env var
                'from': from_email
            }
        }

        # Set environment variable hint
        print(f"\n⚠️  请设置环境变量: export SMTP_PASSWORD='{password}'")

    @property
    def smart_completion_enabled(self) -> bool:
        """Check if smart completion is enabled"""
        return self._config.get('aceflow', {}).get('smart_completion', {}).get('enabled', True)

    def get_completion_rules(self) -> Dict[str, Any]:
        """Get smart completion rules"""
        return self._config.get('aceflow', {}).get('smart_completion', {}).get('rules', [])
