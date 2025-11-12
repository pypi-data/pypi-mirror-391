"""
Export Models - 导出数据模型

定义文档导出的数据结构
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path


class ExportFormat(Enum):
    """导出格式"""
    MARKDOWN = "markdown"   # Markdown 格式
    HTML = "html"          # HTML 格式
    JSON = "json"          # JSON 格式
    ARCHIVE = "archive"    # 完整文档包 (zip)


@dataclass
class ExportOptions:
    """导出选项"""
    # 格式选项
    format: ExportFormat = ExportFormat.MARKDOWN

    # 内容选项
    include_metadata: bool = True        # 包含元数据
    include_stage_outputs: bool = True   # 包含阶段输出
    include_memories: bool = True        # 包含记忆
    include_gate_results: bool = True    # 包含质量门结果
    include_templates: bool = False      # 包含原始模板
    include_transitions: bool = False    # 包含状态转换历史

    # 输出选项
    output_dir: Optional[Path] = None    # 输出目录
    single_file: bool = True             # 单文件输出（默认改为 True）
    create_index: bool = True            # 创建索引文件

    # 样式选项
    add_toc: bool = True                 # 添加目录
    add_timestamps: bool = True          # 添加时间戳
    add_statistics: bool = True          # 添加统计信息

    # 过滤选项
    stage_filter: Optional[List[str]] = None  # 阶段过滤器（只导出指定阶段）

    # 自定义选项
    custom_template: Optional[Path] = None  # 自定义模板路径
    metadata: Dict[str, Any] = field(default_factory=dict)  # 自定义元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'format': self.format.value,
            'include_metadata': self.include_metadata,
            'include_stage_outputs': self.include_stage_outputs,
            'include_memories': self.include_memories,
            'include_gate_results': self.include_gate_results,
            'include_templates': self.include_templates,
            'include_transitions': self.include_transitions,
            'output_dir': str(self.output_dir) if self.output_dir else None,
            'single_file': self.single_file,
            'create_index': self.create_index,
            'add_toc': self.add_toc,
            'add_timestamps': self.add_timestamps,
            'add_statistics': self.add_statistics,
            'stage_filter': self.stage_filter,
            'custom_template': str(self.custom_template) if self.custom_template else None,
            'metadata': self.metadata
        }


@dataclass
class ExportResult:
    """导出结果"""
    success: bool                        # 是否成功
    output_path: Optional[Path] = None   # 输出路径
    files_created: List[Path] = field(default_factory=list)  # 创建的文件列表
    error: Optional[str] = None          # 错误信息
    message: Optional[str] = None        # 消息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'output_path': str(self.output_path) if self.output_path else None,
            'files_created': [str(f) for f in self.files_created],
            'error': self.error,
            'message': self.message,
            'metadata': self.metadata
        }
