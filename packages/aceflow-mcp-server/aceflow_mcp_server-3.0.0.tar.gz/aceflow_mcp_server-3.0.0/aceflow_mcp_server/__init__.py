"""
AceFlow MCP Server
AI-协作增强版MCP服务器，支持双向AI-MCP数据交换的智能开发工作流服务器

Features:
- 支持MCP 2025 Streamable HTTP协议
- 支持传统stdio传输模式
- 智能工作目录检测
- Docker容器化部署
- 多客户端并发支持
- 断线重连和会话恢复
"""

__version__ = "2.2.0"
__author__ = "AceFlow Team"
__email__ = "team@aceflow.dev"
__license__ = "MIT"

from typing import Optional
import logging

# 设置日志
logger = logging.getLogger(__name__)

# 导入核心模块 (使用try-except避免导入错误)
try:
    from .tools import AceFlowTools
    from .config import ServerConfig, get_config
    from .mcp_stdio_server import MCPStdioServer
    from .mcp_http_server import MCPHTTPServer  
    from .unified_server import UnifiedMCPServer
    
    # 导出公共API
    __all__ = [
        "__version__",
        "__author__", 
        "__email__",
        "__license__",
        "AceFlowTools",
        "ServerConfig",
        "get_config", 
        "MCPStdioServer",
        "MCPHTTPServer",
        "UnifiedMCPServer",
        "create_server",
        "run_server"
    ]
    
    def create_server(
        transport: str = "auto",
        host: str = "localhost", 
        port: int = 8000,
        config: Optional[ServerConfig] = None
    ) -> UnifiedMCPServer:
        """
        创建MCP服务器实例
        
        Args:
            transport: 传输模式 (auto, stdio, streamable-http)
            host: HTTP模式监听主机
            port: HTTP模式监听端口  
            config: 服务器配置
            
        Returns:
            服务器实例
        """
        if config is None:
            config = ServerConfig(
                transport=transport,
                host=host,
                port=port
            )
        
        return UnifiedMCPServer(config)


    async def run_server(
        transport: str = "auto",
        host: str = "localhost",
        port: int = 8000,
        config: Optional[ServerConfig] = None
    ) -> None:
        """
        运行MCP服务器
        
        Args:
            transport: 传输模式 (auto, stdio, streamable-http)
            host: HTTP模式监听主机
            port: HTTP模式监听端口
            config: 服务器配置
        """
        server = create_server(transport, host, port, config)
        await server.run()

except ImportError as e:
    logger.warning(f"部分模块导入失败，回退到基础功能: {e}")
    __all__ = ["__version__", "__author__", "__email__", "__license__"]


# 版本兼容性检查
def check_version_compatibility():
    """检查版本兼容性"""
    import sys
    
    if sys.version_info < (3, 8):
        raise RuntimeError("AceFlow MCP Server requires Python 3.8 or higher")
    
    logger.debug(f"AceFlow MCP Server v{__version__} initialized")


# 初始化时检查版本
check_version_compatibility()