from typing import Any, Dict, List, Optional
from framework.im.message import IMMessage
from framework.ioc.container import DependencyContainer
from framework.workflow.core.block import Block
from framework.workflow.core.workflow.input_output import Input, Output
from framework.memory.memory_manager import MemoryManager
from framework.memory.registry import ScopeRegistry, ComposerRegistry, DecomposerRegistry
from framework.llm.format.response import LLMChatResponse

class ChatMemoryQuery(Block):
    def __init__(self, container: DependencyContainer, scope_type: Optional[str] = None):
        inputs = {"msg": Input("msg", IMMessage, "Input message")}
        outputs = {"memory_content": Output("memory_content", str, "memory messages")}
        super().__init__("chat_memory_query", inputs, outputs)
        
        self.memory_manager = container.resolve(MemoryManager)
        
        # 如果没有指定作用域类型，使用配置中的默认值
        if scope_type is None:
            scope_type = self.memory_manager.config.default_scope
            
        # 获取作用域实例
        scope_registry = container.resolve(ScopeRegistry)
        self.scope = scope_registry.get_scope(scope_type)
        
        # 获取解析器实例
        decomposer_registry = container.resolve(DecomposerRegistry)
        self.decomposer = decomposer_registry.get_decomposer("default")

    def execute(self, msg: IMMessage) -> Dict[str, Any]:
        entries = self.memory_manager.query(self.scope, msg.sender)
        memory_content = self.decomposer.decompose(entries)
        return {"memory_content": memory_content}

class ChatMemoryStore(Block):
    def __init__(self, container: DependencyContainer, scope_type: str = None):
        inputs = {
            "user_msg": Input("user_msg", IMMessage, "User message"),
            "llm_resp": Input("llm_resp", LLMChatResponse, "LLM response message")
        }
        outputs = {}
        super().__init__("chat_memory_store", inputs, outputs)
        
        self.memory_manager = container.resolve(MemoryManager)
        
        # 如果没有指定作用域类型，使用配置中的默认值
        if scope_type is None:
            scope_type = self.memory_manager.config.default_scope
            
        # 获取作用域实例
        scope_registry = container.resolve(ScopeRegistry)
        self.scope = scope_registry.get_scope(scope_type)
        
        # 获取组合器实例
        composer_registry = container.resolve(ComposerRegistry)
        self.composer = composer_registry.get_composer("default")

    def execute(self, user_msg: IMMessage, llm_resp: LLMChatResponse) -> Dict[str, Any]:
        # 存储用户消息
        user_entry = self.composer.compose(user_msg)
        self.memory_manager.store(self.scope, user_entry)
        
        # 存储LLM响应
        llm_entry = self.composer.compose(llm_resp)
        self.memory_manager.store(self.scope, llm_entry)
        
        return {} 