"""
Memory Manager - 记忆管理器

提供记忆管理的高级功能:
- 工作流集成
- 智能召回
- 上下文关联
- 经验积累
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import hashlib

from .store import MemoryStore
from .models import Memory, MemoryType, MemoryPriority, MemoryQuery
from ..models import Stage, Iteration


class MemoryManager:
    """记忆管理器 - 提供高级记忆操作"""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        初始化记忆管理器

        Args:
            storage_path: 存储文件路径
        """
        self.store = MemoryStore(storage_path)

    # === 记忆创建 ===

    def record_stage_output(self, iteration_id: str, stage: Stage,
                           output: str, mode: str,
                           priority: MemoryPriority = MemoryPriority.HIGH) -> Memory:
        """
        记录阶段输出

        Args:
            iteration_id: 迭代ID
            stage: 阶段对象
            output: 输出内容
            mode: 工作流模式
            priority: 优先级

        Returns:
            创建的记忆对象
        """
        memory_id = self._generate_memory_id(
            f"stage_output_{iteration_id}_{stage.stage_id}"
        )

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.STAGE_OUTPUT,
            content=output,
            priority=priority,
            iteration_id=iteration_id,
            stage_id=stage.stage_id,
            mode=mode,
            tags=[stage.stage_id, stage.name, mode],
            metadata={
                'stage_name': stage.name,
                'stage_description': stage.description
            }
        )

        self.store.add(memory)
        return memory

    def record_decision(self, decision: str, context: Dict[str, Any],
                       iteration_id: Optional[str] = None,
                       stage_id: Optional[str] = None,
                       priority: MemoryPriority = MemoryPriority.HIGH) -> Memory:
        """
        记录决策

        Args:
            decision: 决策内容
            context: 决策上下文
            iteration_id: 迭代ID (可选)
            stage_id: 阶段ID (可选)
            priority: 优先级

        Returns:
            创建的记忆对象
        """
        memory_id = self._generate_memory_id(f"decision_{decision}_{datetime.now().isoformat()}")

        # 从上下文提取标签
        tags = ["决策"]
        if iteration_id:
            tags.append(iteration_id)
        if stage_id:
            tags.append(stage_id)

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.DECISION,
            content=decision,
            priority=priority,
            iteration_id=iteration_id,
            stage_id=stage_id,
            tags=tags,
            metadata=context
        )

        self.store.add(memory)
        return memory

    def record_issue(self, issue: str, severity: str,
                    iteration_id: Optional[str] = None,
                    stage_id: Optional[str] = None,
                    solution: Optional[str] = None) -> Memory:
        """
        记录问题

        Args:
            issue: 问题描述
            severity: 严重程度 (low/medium/high/critical)
            iteration_id: 迭代ID (可选)
            stage_id: 阶段ID (可选)
            solution: 解决方案 (可选)

        Returns:
            创建的记忆对象
        """
        memory_id = self._generate_memory_id(f"issue_{issue}_{datetime.now().isoformat()}")

        # 根据严重程度设置优先级
        priority_map = {
            'low': MemoryPriority.LOW,
            'medium': MemoryPriority.MEDIUM,
            'high': MemoryPriority.HIGH,
            'critical': MemoryPriority.CRITICAL
        }
        priority = priority_map.get(severity.lower(), MemoryPriority.MEDIUM)

        content = f"问题: {issue}"
        if solution:
            content += f"\n解决方案: {solution}"

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.ISSUE,
            content=content,
            priority=priority,
            iteration_id=iteration_id,
            stage_id=stage_id,
            tags=["问题", severity, stage_id or "unknown"],
            metadata={
                'severity': severity,
                'solved': solution is not None,
                'solution': solution
            }
        )

        self.store.add(memory)
        return memory

    def record_learning(self, learning: str, category: str,
                       iteration_id: Optional[str] = None,
                       applicability: str = "general") -> Memory:
        """
        记录经验教训

        Args:
            learning: 经验内容
            category: 类别 (技术/流程/团队/etc.)
            iteration_id: 迭代ID (可选)
            applicability: 适用范围 (general/specific)

        Returns:
            创建的记忆对象
        """
        memory_id = self._generate_memory_id(f"learning_{learning}_{datetime.now().isoformat()}")

        # 通用经验标记为高优先级
        priority = MemoryPriority.HIGH if applicability == "general" else MemoryPriority.MEDIUM

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.LEARNING,
            content=learning,
            priority=priority,
            iteration_id=iteration_id,
            tags=["经验", category, applicability],
            metadata={
                'category': category,
                'applicability': applicability
            }
        )

        self.store.add(memory)
        return memory

    def record_gate_result(self, gate_id: str, result: Dict[str, Any],
                          iteration_id: str, mode: str) -> Memory:
        """
        记录质量门结果

        Args:
            gate_id: 质量门ID (DG1/DG2/DG3)
            result: 质量门评估结果
            iteration_id: 迭代ID
            mode: 工作流模式

        Returns:
            创建的记忆对象
        """
        memory_id = self._generate_memory_id(f"gate_{gate_id}_{iteration_id}")

        # 提取结果信息
        gate_result = result.get('result', 'unknown')
        score = result.get('score', 0.0)

        content = f"质量门 {gate_id} 评估结果: {gate_result} (得分: {score:.2f})"

        # 根据结果设置优先级
        if gate_result == 'fail':
            priority = MemoryPriority.CRITICAL
        elif gate_result == 'warning':
            priority = MemoryPriority.HIGH
        else:
            priority = MemoryPriority.MEDIUM

        memory = Memory(
            memory_id=memory_id,
            type=MemoryType.GATE_RESULT,
            content=content,
            priority=priority,
            iteration_id=iteration_id,
            stage_id=gate_id,
            mode=mode,
            tags=[gate_id, gate_result, mode],
            metadata=result
        )

        self.store.add(memory)
        return memory

    # === 智能召回 ===

    def recall_for_stage(self, iteration_id: str, stage_id: str,
                        limit: int = 10) -> List[Memory]:
        """
        为当前阶段召回相关记忆

        Args:
            iteration_id: 迭代ID
            stage_id: 阶段ID
            limit: 返回数量

        Returns:
            相关记忆列表
        """
        relevant_memories = []

        # 1. 当前阶段的历史记忆 (from previous iterations)
        query = MemoryQuery(
            stage_id=stage_id,
            types=[MemoryType.STAGE_OUTPUT, MemoryType.ISSUE, MemoryType.LEARNING],
            limit=limit // 2
        )
        relevant_memories.extend(self.store.query(query))

        # 2. 当前迭代的前序阶段记忆
        query = MemoryQuery(
            iteration_id=iteration_id,
            types=[MemoryType.STAGE_OUTPUT, MemoryType.DECISION],
            limit=limit // 2
        )
        current_iter_memories = self.store.query(query)
        relevant_memories.extend(current_iter_memories)

        # 3. 相关的经验教训
        query = MemoryQuery(
            types=[MemoryType.LEARNING],
            tags=[stage_id],
            limit=5
        )
        relevant_memories.extend(self.store.query(query))

        # 去重并限制数量
        seen_ids = set()
        unique_memories = []
        for memory in relevant_memories:
            if memory.memory_id not in seen_ids:
                seen_ids.add(memory.memory_id)
                unique_memories.append(memory)

        return unique_memories[:limit]

    def recall_similar_issues(self, issue_description: str,
                             limit: int = 5) -> List[Memory]:
        """
        召回相似的历史问题

        Args:
            issue_description: 问题描述
            limit: 返回数量

        Returns:
            相似问题列表
        """
        query = MemoryQuery(
            types=[MemoryType.ISSUE],
            search_text=issue_description,
            limit=limit
        )

        return self.store.query(query)

    def recall_learnings(self, category: Optional[str] = None,
                        limit: int = 10) -> List[Memory]:
        """
        召回经验教训

        Args:
            category: 类别过滤 (可选)
            limit: 返回数量

        Returns:
            经验教训列表
        """
        query = MemoryQuery(
            types=[MemoryType.LEARNING],
            tags=[category] if category else None,
            limit=limit
        )

        return self.store.query(query)

    def recall_iteration_context(self, iteration_id: str) -> Dict[str, Any]:
        """
        召回完整的迭代上下文

        Args:
            iteration_id: 迭代ID

        Returns:
            迭代上下文字典
        """
        # 获取该迭代的所有记忆
        memories = self.store.get_by_iteration(iteration_id)

        # 按类型组织
        by_type = {}
        for memory in memories:
            type_key = memory.type.value
            if type_key not in by_type:
                by_type[type_key] = []
            by_type[type_key].append(memory.to_dict())

        return {
            'iteration_id': iteration_id,
            'total_memories': len(memories),
            'by_type': by_type,
            'timeline': sorted(
                [m.to_dict() for m in memories],
                key=lambda x: x['created_at']
            )
        }

    # === 工作流集成 ===

    def get_iteration_summary(self, iteration_id: str) -> Dict[str, Any]:
        """
        获取迭代总结

        Args:
            iteration_id: 迭代ID

        Returns:
            迭代总结
        """
        memories = self.store.get_by_iteration(iteration_id)

        if not memories:
            return {
                'iteration_id': iteration_id,
                'status': 'no_data',
                'summary': {}
            }

        # 统计信息
        stage_outputs = [m for m in memories if m.type == MemoryType.STAGE_OUTPUT]
        decisions = [m for m in memories if m.type == MemoryType.DECISION]
        issues = [m for m in memories if m.type == MemoryType.ISSUE]
        learnings = [m for m in memories if m.type == MemoryType.LEARNING]
        gate_results = [m for m in memories if m.type == MemoryType.GATE_RESULT]

        return {
            'iteration_id': iteration_id,
            'total_memories': len(memories),
            'stages_completed': len(set(m.stage_id for m in stage_outputs if m.stage_id)),
            'decisions_made': len(decisions),
            'issues_encountered': len(issues),
            'learnings_captured': len(learnings),
            'gates_evaluated': len(gate_results),
            'critical_issues': len([i for i in issues if i.priority == MemoryPriority.CRITICAL]),
            'mode': memories[0].mode if memories else None
        }

    # === 清理和维护 ===

    def cleanup(self, days: int = 90, keep_critical: bool = True) -> int:
        """清理旧记忆"""
        return self.store.cleanup_old_memories(days, keep_critical)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.store.get_statistics()

    # === 工具方法 ===

    def _generate_memory_id(self, base: str) -> str:
        """生成记忆ID"""
        # 使用 hash 确保 ID 唯一且可重现
        hash_obj = hashlib.md5(base.encode('utf-8'))
        return f"mem_{hash_obj.hexdigest()[:12]}"
