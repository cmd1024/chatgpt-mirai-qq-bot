from typing import Any, Dict, List

from pydantic import BaseModel, Field

class IMConfig(BaseModel):
    enable: Dict[str, List[str]] = dict()
    configs: Dict[str, Dict[str, Any]] = Field(description="IM 的凭证配置", default=dict())

class LLMBackendConfig(BaseModel):
    enable: bool
    adapter: str
    configs: List[Dict]
    models: List[str]

class LLMConfig(BaseModel):
    backends: Dict[str, LLMBackendConfig] = dict()
    
class DefaultConfig(BaseModel):
    llm_model: str = Field(default="gemini-1.5-flash", description="默认使用的 LLM 模型名称")

class MemoryPersistenceConfig(BaseModel):
    type: str = Field(default="file", description="持久化类型: file/redis")
    file: Dict[str, Any] = Field(
        default={
            "storage_dir": "./data/memory"
        },
        description="文件持久化配置"
    )
    redis: Dict[str, Any] = Field(
        default={
            "host": "localhost",
            "port": 6379,
            "db": 0
        },
        description="Redis持久化配置"
    )

class MemoryConfig(BaseModel):
    persistence: MemoryPersistenceConfig = MemoryPersistenceConfig()
    max_entries: int = Field(default=100, description="每个作用域最大记忆条目数")
    default_scope: str = Field(default="member", description="默认作用域类型")
    
class GlobalConfig(BaseModel):
    ims: IMConfig = IMConfig()
    llms: LLMConfig = LLMConfig()
    defaults: DefaultConfig = DefaultConfig()
    memory: MemoryConfig = MemoryConfig()
