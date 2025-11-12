"""
AceFlow MCP HTTP Server Implementation
基于FastAPI实现MCP 2025 Streamable HTTP传输协议
支持多客户端并发、Server-Sent Events流式传输、断线重连
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Dict, Any, Optional, Set, AsyncGenerator
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
import uvicorn

from .config import ServerConfig, get_config
from .tools import AceFlowTools
from .mcp_output_adapter import MCPOutputAdapter
from .tool_prompts import AceFlowToolPrompts

logger = logging.getLogger(__name__)


class MCPHTTPServer:
    """MCP HTTP服务器实现类"""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or get_config()
        self.app = FastAPI(
            title="AceFlow MCP Server",
            description="AI-协作增强版MCP服务器，支持双向AI-MCP数据交换",
            version="2.1.0"
        )
        
        # 客户端会话管理
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = asyncio.Lock()
        
        # 工具和适配器实例
        self.output_adapter = MCPOutputAdapter()
        self.tools_instance = AceFlowTools(
            working_directory=self.config.get_work_dir()
        )
        
        # 设置应用
        self._setup_middleware()
        self._setup_routes()
        
        logger.info(f"🚀 MCP HTTP Server 初始化完成，工作目录: {self.config.get_work_dir()}")
    
    def _setup_middleware(self):
        """设置中间件"""
        # CORS支持
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.get("/health")
        async def health_check():
            """健康检查端点"""
            return {
                "status": "healthy",
                "version": "2.1.0",
                "transport": "streamable-http",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        @self.app.get("/mcp")
        async def mcp_get(request: Request):
            """MCP GET端点 - Server-Sent Events流式响应"""
            # 获取或创建会话
            session_id = await self._get_or_create_session(request)
            last_event_id = request.headers.get("Last-Event-ID")
            
            logger.debug(f"📡 MCP GET请求，会话ID: {session_id}, Last-Event-ID: {last_event_id}")
            
            # 创建SSE流
            return StreamingResponse(
                self._generate_sse_stream(session_id, last_event_id),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Session-ID": session_id
                }
            )
        
        @self.app.post("/mcp")
        async def mcp_post(request: Request):
            """MCP POST端点 - 同步模式，直接返回JSON-RPC响应"""
            # 解析JSON-RPC消息
            try:
                message = await request.json()
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON")

            # 验证JSON-RPC格式（在创建会话之前验证）
            if not self._validate_jsonrpc_message(message):
                raise HTTPException(status_code=400, detail="Invalid JSON-RPC message")

            # 获取会话ID（用于日志和会话管理）
            session_id = await self._get_or_create_session(request)
            logger.debug(f"📨 收到MCP消息，会话ID: {session_id}, 消息: {json.dumps(message)}")

            # 处理消息并直接返回响应（同步模式）
            try:
                response = await self._process_mcp_message(session_id, message)

                # 直接返回JSON-RPC响应
                return JSONResponse(
                    status_code=200,
                    content=response,
                    headers={"X-Session-ID": session_id}
                )
            except Exception as e:
                logger.error(f"❌ MCP消息处理错误: {e}")
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    async def _get_or_create_session(self, request: Request) -> str:
        """获取或创建客户端会话"""
        # 尝试从头部获取会话ID
        session_id = request.headers.get("X-Session-ID")
        
        if not session_id:
            # 创建新会话
            session_id = str(uuid.uuid4())
            
        async with self.session_lock:
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "created_at": datetime.now(timezone.utc),
                    "last_activity": datetime.now(timezone.utc),
                    "message_queue": asyncio.Queue(),
                    "event_id_counter": 0,
                    "client_info": {
                        "user_agent": request.headers.get("User-Agent"),
                        "remote_addr": request.client.host if request.client else None
                    }
                }
                logger.info(f"✨ 创建新MCP会话: {session_id}")
        
        return session_id
    
    def _validate_jsonrpc_message(self, message: Dict[str, Any]) -> bool:
        """验证JSON-RPC消息格式"""
        required_fields = ["jsonrpc", "method", "id"]
        
        # 检查必需字段
        for field in required_fields:
            if field not in message:
                return False
        
        # 检查版本
        if message["jsonrpc"] != "2.0":
            return False
        
        return True
    
    async def _process_mcp_message(self, session_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP消息"""
        method = message["method"]
        params = message.get("params", {})
        message_id = message["id"]
        
        logger.debug(f"🔧 处理MCP方法: {method}, 参数: {json.dumps(params)}")
        
        try:
            if method == "tools/list":
                # 列出可用工具
                tools = self._get_tool_list()
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "tools": tools
                    }
                }
            
            elif method == "tools/call":
                # 调用工具
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    raise ValueError("Missing tool name")
                
                # 执行工具调用
                result = await self._execute_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            elif method == "initialize":
                # 初始化响应
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "capabilities": {
                            "tools": {},
                            "prompts": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "AceFlow MCP Server",
                            "version": "2.1.0"
                        }
                    }
                }
            
            else:
                # 未知方法
                return {
                    "jsonrpc": "2.0",
                    "id": message_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"❌ MCP消息处理错误: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def _get_tool_list(self) -> list:
        """获取工具列表"""
        tool_definitions = AceFlowToolPrompts.get_tool_definitions()
        tools = []
        
        for tool_name, tool_def in tool_definitions.items():
            tools.append({
                "name": tool_def["name"],
                "description": tool_def["description"],
                "inputSchema": tool_def["inputSchema"]
            })
        
        return tools
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """执行工具调用"""
        try:
            # 在线程池中执行工具调用
            if tool_name == "aceflow_init":
                result = await run_in_threadpool(
                    self.tools_instance.aceflow_init,
                    mode=arguments["mode"],
                    project_name=arguments.get("project_name"),
                    directory=arguments.get("directory")
                )
            elif tool_name == "aceflow_stage":
                result = await run_in_threadpool(
                    self.tools_instance.aceflow_stage,
                    action=arguments["action"],
                    stage=arguments.get("stage")
                )
            elif tool_name == "aceflow_validate":
                result = await run_in_threadpool(
                    self.tools_instance.aceflow_validate,
                    mode=arguments.get("mode", "basic"),
                    fix=arguments.get("fix", False),
                    report=arguments.get("report", False)
                )
            elif tool_name == "aceflow_template":
                result = await run_in_threadpool(
                    self.tools_instance.aceflow_template,
                    action=arguments["action"],
                    template=arguments.get("template")
                )
            else:
                raise ValueError(f"未知工具: {tool_name}")
            
            # 使用输出适配器格式化结果
            formatted_result = self.output_adapter.convert_to_mcp_format(result)
            return formatted_result["content"][0]["text"]
            
        except Exception as e:
            logger.error(f"❌ 工具执行错误: {tool_name} - {str(e)}")
            error_response = self.output_adapter.handle_error(e)
            return error_response["content"][0]["text"]
    
    async def _queue_response(self, session_id: str, response: Dict[str, Any]):
        """将响应加入会话队列"""
        async with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session["event_id_counter"] += 1
                session["last_activity"] = datetime.now(timezone.utc)
                
                # 创建SSE事件
                event = {
                    "id": str(session["event_id_counter"]),
                    "type": "message",
                    "data": response,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                await session["message_queue"].put(event)
    
    async def _generate_sse_stream(self, session_id: str, last_event_id: Optional[str]) -> AsyncGenerator[str, None]:
        """生成Server-Sent Events流"""
        logger.debug(f"🌊 开始SSE流，会话ID: {session_id}")
        
        try:
            # 发送初始连接事件
            yield f"event: connected\\ndata: {{\"session_id\": \"{session_id}\"}}\\n\\n"
            
            # 获取会话
            async with self.session_lock:
                if session_id not in self.active_sessions:
                    logger.warning(f"⚠️ 会话不存在: {session_id}")
                    return
                
                session = self.active_sessions[session_id]
                message_queue = session["message_queue"]
            
            # 处理断线重连
            if last_event_id:
                logger.debug(f"🔄 处理断线重连，Last-Event-ID: {last_event_id}")
                # TODO: 实现消息重放逻辑
            
            # 持续发送队列中的消息
            while True:
                try:
                    # 等待消息，设置超时以发送心跳
                    event = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                    
                    # 格式化SSE事件
                    sse_data = json.dumps(event["data"])
                    yield f"id: {event['id']}\\nevent: {event['type']}\\ndata: {sse_data}\\n\\n"
                    
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield f"event: heartbeat\\ndata: {{\"timestamp\": \"{datetime.now(timezone.utc).isoformat()}\"}}\\n\\n"
                
                except Exception as e:
                    logger.error(f"❌ SSE流错误: {e}")
                    break
        
        except asyncio.CancelledError:
            logger.debug(f"🔌 SSE流被取消，会话ID: {session_id}")
        
        except Exception as e:
            logger.error(f"❌ SSE流严重错误: {e}")
        
        finally:
            logger.debug(f"🏁 SSE流结束，会话ID: {session_id}")
    
    async def cleanup_expired_sessions(self):
        """清理过期会话"""
        current_time = datetime.now(timezone.utc)
        expired_sessions = []
        
        async with self.session_lock:
            for session_id, session in self.active_sessions.items():
                # 会话超时时间：1小时
                if (current_time - session["last_activity"]).total_seconds() > 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                logger.info(f"🗑️ 清理过期会话: {session_id}")
    
    async def start_background_tasks(self):
        """启动后台任务"""
        async def cleanup_task():
            while True:
                await asyncio.sleep(300)  # 每5分钟清理一次
                await self.cleanup_expired_sessions()
        
        asyncio.create_task(cleanup_task())
    
    def run(self):
        """启动HTTP服务器"""
        logger.info(f"🚀 启动AceFlow MCP HTTP服务器")
        logger.info(f"📍 监听地址: {self.config.host}:{self.config.port}")
        logger.info(f"🔧 工作目录: {self.config.get_work_dir()}")

        # uvicorn.run will create its own event loop, so we don't need to create tasks here
        # The background cleanup will be started via lifespan events if needed

        # 启动服务器
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level.lower(),
            access_log=self.config.debug,
            ssl_keyfile=self.config.key_file,
            ssl_certfile=self.config.cert_file,
            timeout_keep_alive=self.config.keepalive_timeout,
        )


def main():
    """主函数入口"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建服务器
    server = MCPHTTPServer()

    # 输出配置信息用于调试
    logger.info("=" * 60)
    logger.info("服务器配置信息:")
    logger.info(f"  Host: {server.config.host}")
    logger.info(f"  Port: {server.config.port}")
    logger.info(f"  Transport: {server.config.transport}")
    logger.info(f"  Working Dir: {server.config.get_work_dir()}")
    logger.info(f"  Debug: {server.config.debug}")
    logger.info(f"  Log Level: {server.config.log_level}")
    logger.info("=" * 60)

    # 运行服务器
    server.run()


if __name__ == "__main__":
    main()