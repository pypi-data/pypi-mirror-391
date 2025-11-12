"""
AceFlow MCP Server Configuration Management
统一配置管理，支持多传输模式和环境变量配置
"""

import os
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServerConfig:
    """AceFlow MCP Server配置类"""
    
    # 传输层配置
    transport: str = "auto"  # stdio, http, streamable-http, auto
    host: str = "0.0.0.0"  # 监听所有接口
    port: int = 8000
    
    # HTTP特定配置
    enable_https: bool = False
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    
    # 性能配置
    max_connections: int = 100
    request_timeout: int = 30
    keepalive_timeout: int = 60
    
    # 工作目录配置
    working_directory: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    debug: bool = False
    
    # 安全配置
    allowed_origins: list = None
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]  # 默认允许所有源
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """从环境变量创建配置"""
        return cls(
            transport=os.getenv('ACEFLOW_TRANSPORT', 'auto'),
            host=os.getenv('ACEFLOW_HOST', '0.0.0.0'),  # 默认监听所有接口
            port=int(os.getenv('ACEFLOW_PORT', '8000')),
            
            enable_https=os.getenv('ACEFLOW_ENABLE_HTTPS', 'false').lower() == 'true',
            cert_file=os.getenv('ACEFLOW_CERT_FILE'),
            key_file=os.getenv('ACEFLOW_KEY_FILE'),
            
            max_connections=int(os.getenv('ACEFLOW_MAX_CONNECTIONS', '100')),
            request_timeout=int(os.getenv('ACEFLOW_REQUEST_TIMEOUT', '30')),
            keepalive_timeout=int(os.getenv('ACEFLOW_KEEPALIVE_TIMEOUT', '60')),
            
            working_directory=os.getenv('ACEFLOW_WORKING_DIRECTORY'),
            
            log_level=os.getenv('ACEFLOW_LOG_LEVEL', 'INFO'),
            debug=os.getenv('ACEFLOW_DEBUG', 'false').lower() == 'true',
            
            allowed_origins=os.getenv('ACEFLOW_ALLOWED_ORIGINS', '*').split(','),
            api_key=os.getenv('ACEFLOW_API_KEY'),
        )
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> 'ServerConfig':
        """从配置文件创建配置"""
        import yaml
        
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def detect_transport_mode(self) -> str:
        """智能检测传输模式"""
        if self.transport != "auto":
            return self.transport
        
        # 检测运行环境
        if os.getenv('MCP_STDIO_MODE'):
            return "stdio"
        
        # 检测Docker环境
        if os.path.exists('/.dockerenv') or os.getenv('KUBERNETES_SERVICE_HOST'):
            return "streamable-http"
        
        # 检测是否有HTTP相关参数
        if self.host != "localhost" or self.port != 8000:
            return "streamable-http"
        
        # 默认stdio模式
        return "stdio"
    
    def get_work_dir(self) -> str:
        """获取工作目录"""
        if self.working_directory:
            return self.working_directory
        
        # 智能检测工作目录
        candidates = [
            os.getenv('MCP_CWD'),
            os.getenv('CLIENT_CWD'),
            os.getenv('VSCODE_CWD'),
            os.getenv('CURSOR_CWD'),
            os.getenv('PWD'),
            os.getenv('INIT_CWD'),
            os.getcwd()
        ]
        
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        
        return os.getcwd()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'transport': self.transport,
            'host': self.host,
            'port': self.port,
            'enable_https': self.enable_https,
            'cert_file': self.cert_file,
            'key_file': self.key_file,
            'max_connections': self.max_connections,
            'request_timeout': self.request_timeout,
            'keepalive_timeout': self.keepalive_timeout,
            'working_directory': self.working_directory,
            'log_level': self.log_level,
            'debug': self.debug,
            'allowed_origins': self.allowed_origins,
            'api_key': self.api_key,
        }
    
    def validate(self) -> bool:
        """验证配置有效性"""
        if self.transport not in ['stdio', 'http', 'streamable-http', 'sse', 'auto']:
            raise ValueError(f"不支持的传输模式: {self.transport}")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"端口范围无效: {self.port}")
        
        if self.enable_https and (not self.cert_file or not self.key_file):
            raise ValueError("启用HTTPS需要同时提供cert_file和key_file")
        
        if self.cert_file and not Path(self.cert_file).exists():
            raise FileNotFoundError(f"证书文件不存在: {self.cert_file}")
        
        if self.key_file and not Path(self.key_file).exists():
            raise FileNotFoundError(f"密钥文件不存在: {self.key_file}")
        
        return True


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config: Optional[ServerConfig] = None
    
    @property
    def config(self) -> ServerConfig:
        """获取配置实例"""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def load_config(self) -> ServerConfig:
        """加载配置"""
        if self.config_file and Path(self.config_file).exists():
            # 从配置文件加载
            config = ServerConfig.from_file(self.config_file)
        else:
            # 从环境变量加载
            config = ServerConfig.from_env()
        
        # 验证配置
        config.validate()
        
        return config
    
    def reload_config(self) -> ServerConfig:
        """重新加载配置"""
        self._config = None
        return self.config
    
    def save_config(self, config_file: Optional[str] = None) -> None:
        """保存配置到文件"""
        import yaml
        
        file_path = config_file or self.config_file or 'aceflow-config.yaml'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config.to_dict(), f, default_flow_style=False, allow_unicode=True)


# 全局配置实例
_config_manager: Optional[ConfigManager] = None


def get_config() -> ServerConfig:
    """获取全局配置实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.config


def init_config(config_file: Optional[str] = None) -> ServerConfig:
    """初始化配置管理器"""
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager.config