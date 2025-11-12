"""
AceFlow MCP Unified Server Entry Point
统一服务器启动入口，支持自动模式检测和多传输协议
"""

import asyncio
import logging
import os
import sys
from typing import Optional
import click

from .config import ServerConfig, init_config
from .mcp_stdio_server import MCPStdioServer
from .mcp_http_server import MCPHTTPServer

logger = logging.getLogger(__name__)


class UnifiedMCPServer:
    """统一MCP服务器管理器"""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or init_config()
        self.server = None
        
        # 设置日志
        self._setup_logging()
        
        logger.info(f"🎯 AceFlow MCP Server v2.1.0 初始化")
        logger.info(f"📋 配置传输模式: {self.config.transport}")
        logger.info(f"📂 工作目录: {self.config.get_work_dir()}")
    
    def _setup_logging(self):
        """设置日志配置"""
        log_level = getattr(logging, self.config.log_level.upper())
        
        # 配置根日志器
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr if self._is_stdio_mode() else sys.stdout
        )
        
        # 设置特定模块的日志级别
        if self.config.debug:
            logging.getLogger('aceflow_mcp_server').setLevel(logging.DEBUG)
            logging.getLogger('uvicorn').setLevel(logging.DEBUG)
        else:
            # 生产环境下降低第三方库的日志级别
            logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
            logging.getLogger('uvicorn.error').setLevel(logging.WARNING)
    
    def _is_stdio_mode(self) -> bool:
        """判断是否为stdio模式"""
        transport = self.config.detect_transport_mode()
        return transport == "stdio"
    
    def _detect_execution_environment(self) -> dict:
        """检测执行环境"""
        env_info = {
            "is_docker": os.path.exists('/.dockerenv'),
            "is_kubernetes": bool(os.getenv('KUBERNETES_SERVICE_HOST')),
            "is_mcp_client": bool(os.getenv('MCP_STDIO_MODE')),
            "has_tty": sys.stdin.isatty(),
            "parent_process": None
        }
        
        # 尝试获取父进程信息
        try:
            import psutil
            current_process = psutil.Process()
            parent_process = current_process.parent()
            if parent_process:
                env_info["parent_process"] = parent_process.name()
        except (ImportError, Exception):
            pass
        
        return env_info
    
    def _validate_config_for_mode(self, transport: str):
        """验证配置对特定传输模式的有效性"""
        if transport in ['http', 'streamable-http', 'sse']:
            # HTTP模式需要的验证
            if self.config.port < 1 or self.config.port > 65535:
                raise ValueError(f"HTTP模式端口配置无效: {self.config.port}")
            
            if self.config.enable_https:
                if not self.config.cert_file or not self.config.key_file:
                    raise ValueError("HTTPS模式需要证书和密钥文件")
        
        elif transport == 'stdio':
            # stdio模式的验证
            if not sys.stdin.isatty() and not os.getenv('MCP_STDIO_MODE'):
                logger.warning("⚠️ stdio模式但未检测到TTY或MCP客户端环境")
    
    async def start_stdio_server(self):
        """启动stdio模式服务器"""
        logger.info("🔌 启动MCP Stdio服务器...")
        
        try:
            server = MCPStdioServer()
            await server.run()
        except KeyboardInterrupt:
            logger.info("🛑 收到中断信号，正在关闭stdio服务器...")
        except Exception as e:
            logger.error(f"❌ Stdio服务器启动失败: {e}")
            raise
    
    def start_http_server(self):
        """启动HTTP模式服务器"""
        logger.info("🌐 启动MCP HTTP服务器...")
        
        try:
            server = MCPHTTPServer(self.config)
            server.run()
        except KeyboardInterrupt:
            logger.info("🛑 收到中断信号，正在关闭HTTP服务器...")
        except Exception as e:
            logger.error(f"❌ HTTP服务器启动失败: {e}")
            raise
    
    async def run(self):
        """启动统一服务器"""
        # 检测传输模式
        transport = self.config.detect_transport_mode()
        logger.info(f"🎯 检测到传输模式: {transport}")
        
        # 验证配置
        self._validate_config_for_mode(transport)
        
        # 显示环境信息
        env_info = self._detect_execution_environment()
        logger.debug(f"🔍 执行环境: {env_info}")
        
        # 启动相应的服务器
        if transport == "stdio":
            await self.start_stdio_server()
        else:
            # HTTP系列传输模式
            self.start_http_server()


@click.command()
@click.option('--config', '-c', help='配置文件路径')
@click.option('--transport', '-t', 
              type=click.Choice(['auto', 'stdio', 'http', 'streamable-http', 'sse']),
              help='传输模式')
@click.option('--host', '-h', help='HTTP模式监听主机')
@click.option('--port', '-p', type=int, help='HTTP模式监听端口')
@click.option('--log-level', '-l',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='日志级别')
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.option('--working-directory', '-w', help='工作目录')
@click.version_option(version="2.1.0", prog_name="AceFlow MCP Server")
def main(config: Optional[str], transport: Optional[str], host: Optional[str], 
         port: Optional[int], log_level: Optional[str], debug: bool,
         working_directory: Optional[str]):
    """
    AceFlow MCP Server - AI协作增强版MCP服务器
    
    支持多种传输模式:
    - auto: 自动检测模式 (默认)
    - stdio: 标准输入输出模式
    - streamable-http: MCP 2025 Streamable HTTP模式
    - http: 传统HTTP模式
    - sse: Server-Sent Events模式
    """
    try:
        # 初始化配置
        server_config = init_config(config)
        
        # 覆盖命令行参数
        if transport:
            server_config.transport = transport
        if host:
            server_config.host = host
        if port:
            server_config.port = port
        if log_level:
            server_config.log_level = log_level
        if debug:
            server_config.debug = debug
        if working_directory:
            server_config.working_directory = working_directory
        
        # 创建并启动服务器
        server = UnifiedMCPServer(server_config)
        
        # 运行服务器
        if server_config.detect_transport_mode() == "stdio":
            # stdio模式需要异步运行
            asyncio.run(server.run())
        else:
            # HTTP模式直接运行
            asyncio.run(server.run())
            
    except KeyboardInterrupt:
        logger.info("🛑 收到键盘中断，正在退出...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 服务器启动失败: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()