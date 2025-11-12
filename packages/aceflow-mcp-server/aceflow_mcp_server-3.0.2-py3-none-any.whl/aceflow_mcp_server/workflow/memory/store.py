"""
Memory Store - 记忆存储

提供记忆的持久化存储功能
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from .models import Memory, MemoryType, MemoryPriority, MemoryQuery


class MemoryStore:
    """记忆存储 - 负责记忆的持久化"""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        初始化记忆存储

        Args:
            storage_path: 存储文件路径，默认为 .aceflow/workflow_memory.json
        """
        if storage_path is None:
            storage_path = Path.cwd() / ".aceflow" / "workflow_memory.json"

        self.storage_path = storage_path
        self.memories: Dict[str, Memory] = {}  # memory_id -> Memory
        self._load()

    def add(self, memory: Memory) -> bool:
        """
        添加记忆

        Args:
            memory: 记忆对象

        Returns:
            是否成功
        """
        self.memories[memory.memory_id] = memory
        return self._save()

    def get(self, memory_id: str) -> Optional[Memory]:
        """
        获取记忆

        Args:
            memory_id: 记忆ID

        Returns:
            记忆对象或 None
        """
        memory = self.memories.get(memory_id)
        if memory:
            memory.access()
            self._save()  # 保存访问更新
        return memory

    def update(self, memory: Memory) -> bool:
        """
        更新记忆

        Args:
            memory: 记忆对象

        Returns:
            是否成功
        """
        if memory.memory_id in self.memories:
            self.memories[memory.memory_id] = memory
            return self._save()
        return False

    def delete(self, memory_id: str) -> bool:
        """
        删除记忆

        Args:
            memory_id: 记忆ID

        Returns:
            是否成功
        """
        if memory_id in self.memories:
            del self.memories[memory_id]
            return self._save()
        return False

    def query(self, query: MemoryQuery) -> List[Memory]:
        """
        查询记忆

        Args:
            query: 查询条件

        Returns:
            匹配的记忆列表
        """
        # 过滤匹配的记忆
        matched = [
            memory for memory in self.memories.values()
            if query.matches(memory)
        ]

        # 排序
        if query.sort_by == "created_at":
            matched.sort(key=lambda m: m.created_at, reverse=query.sort_desc)
        elif query.sort_by == "accessed_at":
            matched.sort(key=lambda m: m.accessed_at, reverse=query.sort_desc)
        elif query.sort_by == "access_count":
            matched.sort(key=lambda m: m.access_count, reverse=query.sort_desc)
        elif query.sort_by == "priority":
            priority_order = {
                MemoryPriority.LOW: 0,
                MemoryPriority.MEDIUM: 1,
                MemoryPriority.HIGH: 2,
                MemoryPriority.CRITICAL: 3
            }
            matched.sort(
                key=lambda m: priority_order[m.priority],
                reverse=query.sort_desc
            )

        # 限制数量
        if query.limit and query.limit > 0:
            matched = matched[:query.limit]

        # 标记访问
        for memory in matched:
            memory.access()

        self._save()  # 保存访问更新
        return matched

    def get_all(self) -> List[Memory]:
        """获取所有记忆"""
        return list(self.memories.values())

    def get_by_iteration(self, iteration_id: str) -> List[Memory]:
        """获取某个迭代的所有记忆"""
        query = MemoryQuery(iteration_id=iteration_id)
        return self.query(query)

    def get_by_stage(self, iteration_id: str, stage_id: str) -> List[Memory]:
        """获取某个阶段的所有记忆"""
        query = MemoryQuery(iteration_id=iteration_id, stage_id=stage_id)
        return self.query(query)

    def get_by_type(self, memory_type: MemoryType, limit: Optional[int] = None) -> List[Memory]:
        """获取某个类型的所有记忆"""
        query = MemoryQuery(types=[memory_type], limit=limit)
        return self.query(query)

    def search(self, text: str, limit: Optional[int] = 10) -> List[Memory]:
        """
        文本搜索

        Args:
            text: 搜索文本
            limit: 结果数量限制

        Returns:
            匹配的记忆列表
        """
        query = MemoryQuery(search_text=text, limit=limit)
        return self.query(query)

    # === 清理操作 ===

    def cleanup_old_memories(self, days: int = 90,
                            keep_critical: bool = True) -> int:
        """
        清理旧记忆

        Args:
            days: 保留最近多少天的记忆
            keep_critical: 是否保留关键记忆

        Returns:
            清理的数量
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        original_count = len(self.memories)

        # 过滤要保留的记忆
        to_keep = {}
        for memory_id, memory in self.memories.items():
            # 保留最近的记忆
            if memory.created_at > cutoff_date:
                to_keep[memory_id] = memory
                continue

            # 保留关键记忆
            if keep_critical and memory.priority == MemoryPriority.CRITICAL:
                to_keep[memory_id] = memory
                continue

            # 保留最近访问的记忆
            if memory.accessed_at > cutoff_date:
                to_keep[memory_id] = memory
                continue

        self.memories = to_keep
        cleaned_count = original_count - len(self.memories)

        if cleaned_count > 0:
            self._save()

        return cleaned_count

    def cleanup_by_priority(self, keep_count: int = 1000) -> int:
        """
        按优先级清理，保留指定数量的记忆

        Args:
            keep_count: 保留的记忆数量

        Returns:
            清理的数量
        """
        if len(self.memories) <= keep_count:
            return 0

        original_count = len(self.memories)

        # 按优先级和访问时间排序
        priority_order = {
            MemoryPriority.CRITICAL: 4,
            MemoryPriority.HIGH: 3,
            MemoryPriority.MEDIUM: 2,
            MemoryPriority.LOW: 1
        }

        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: (
                priority_order[m.priority],
                m.accessed_at
            ),
            reverse=True
        )

        # 保留前 keep_count 个
        to_keep = {m.memory_id: m for m in sorted_memories[:keep_count]}
        self.memories = to_keep

        cleaned_count = original_count - len(self.memories)
        if cleaned_count > 0:
            self._save()

        return cleaned_count

    # === 统计信息 ===

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.memories:
            return {
                'total': 0,
                'by_type': {},
                'by_priority': {},
                'by_mode': {}
            }

        # 按类型统计
        by_type = {}
        for memory in self.memories.values():
            type_key = memory.type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

        # 按优先级统计
        by_priority = {}
        for memory in self.memories.values():
            priority_key = memory.priority.value
            by_priority[priority_key] = by_priority.get(priority_key, 0) + 1

        # 按模式统计
        by_mode = {}
        for memory in self.memories.values():
            if memory.mode:
                by_mode[memory.mode] = by_mode.get(memory.mode, 0) + 1

        return {
            'total': len(self.memories),
            'by_type': by_type,
            'by_priority': by_priority,
            'by_mode': by_mode,
            'storage_path': str(self.storage_path)
        }

    # === 持久化 ===

    def _load(self):
        """从文件加载记忆"""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.memories = {}
            for memory_data in data:
                memory = Memory.from_dict(memory_data)
                self.memories[memory.memory_id] = memory

        except Exception as e:
            print(f"警告: 加载记忆失败: {e}")
            self.memories = {}

    def _save(self) -> bool:
        """保存记忆到文件"""
        try:
            # 确保目录存在
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            # 转换为字典列表
            data = [memory.to_dict() for memory in self.memories.values()]

            # 写入文件
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"警告: 保存记忆失败: {e}")
            return False

    def export_to_json(self, export_path: Path) -> bool:
        """
        导出记忆到 JSON 文件

        Args:
            export_path: 导出文件路径

        Returns:
            是否成功
        """
        try:
            data = [memory.to_dict() for memory in self.memories.values()]

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def import_from_json(self, import_path: Path,
                        merge: bool = False) -> int:
        """
        从 JSON 文件导入记忆

        Args:
            import_path: 导入文件路径
            merge: 是否合并 (False 则覆盖)

        Returns:
            导入的记忆数量
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not merge:
                self.memories = {}

            imported_count = 0
            for memory_data in data:
                memory = Memory.from_dict(memory_data)
                self.memories[memory.memory_id] = memory
                imported_count += 1

            self._save()
            return imported_count

        except Exception as e:
            print(f"导入失败: {e}")
            return 0
