import asyncio
import os
import signal
from framework.config.config_loader import ConfigLoader
from framework.config.global_config import GlobalConfig
from framework.events.event_bus import EventBus
from framework.im.im_registry import IMRegistry
from framework.im.manager import IMManager
from framework.ioc.container import DependencyContainer
from framework.llm.llm_manager import LLMManager
from framework.llm.llm_registry import LLMBackendRegistry
from framework.memory.memory_adapter import MemoryAdapter
from framework.plugin_manager.plugin_loader import PluginLoader
from framework.workflow_dispatcher.workflow_dispatcher import WorkflowDispatcher
from framework.logger import get_logger
from framework.workflow_executor.block_registry import BlockRegistry
from framework.workflow_executor.system_blocks import register_system_blocks
from framework.workflow_executor.workflow_registry import WorkflowRegistry
from framework.workflow_dispatcher.dispatch_rule_registry import DispatchRuleRegistry
from framework.workflow_executor.system_workflows import register_system_workflows

logger = get_logger("Entrypoint")

# 定义优雅退出异常
class GracefulExit(SystemExit):
    code = 1

# 注册信号处理函数
def _signal_handler(*args):
    logger.warning("Interrupt signal received. Stopping application...")
    raise GracefulExit()

def init_container() -> DependencyContainer:
    container = DependencyContainer()
    container.register(DependencyContainer, container)
    
    # 注册工作流注册表
    workflow_registry = WorkflowRegistry(container)
    register_system_workflows(workflow_registry)  # 注册系统工作流
    workflow_registry.load_workflows()  # 加载自定义工作流
    container.register(WorkflowRegistry, workflow_registry)
    
    # 注册调度规则注册表
    dispatch_registry = DispatchRuleRegistry(container)
    dispatch_registry.load_rules()  # 加载调度规则
    container.register(DispatchRuleRegistry, dispatch_registry)
    
    return container

def main():
    loop = asyncio.new_event_loop()
    
    logger.info("Starting application...")
    
    # 配置文件路径
    config_path = "config.yaml"

    # 加载配置文件
    logger.info(f"Loading configuration from {config_path}")
    if os.path.exists(config_path):
        config = ConfigLoader.load_config(config_path, GlobalConfig)
        logger.info("Configuration loaded successfully")
    else:
        logger.warning(f"Configuration file {config_path} not found, using default configuration")
        logger.warning("Please create a configuration file by copying config.yaml.example to config.yaml and modify it according to your needs")
        config = GlobalConfig()
    
    container = init_container()
    
    container.register(asyncio.AbstractEventLoop, loop)
    
    container.register(EventBus, EventBus())
    
    container.register(GlobalConfig, config)
    
    container.register(BlockRegistry, BlockRegistry())
    container.register(IMRegistry, IMRegistry())
    container.register(LLMBackendRegistry, LLMBackendRegistry())
    
    im_manager = IMManager(container)
    container.register(IMManager, im_manager)
    
    llm_manager = LLMManager(container)
    container.register(LLMManager, llm_manager)
    
    plugin_loader = PluginLoader(container)
    container.register(PluginLoader, plugin_loader)
    
    workflow_dispatcher = WorkflowDispatcher(container)
    container.register(WorkflowDispatcher, workflow_dispatcher)

    memory_adapter = MemoryAdapter(container)
    container.register(MemoryAdapter, memory_adapter)

    # 注册系统 blocks
    register_system_blocks(container.resolve(BlockRegistry))
    
    # 发现并加载内部插件
    logger.info("Discovering plugins...")
    plugin_loader.discover_internal_plugins("plugins")


    # 初始化插件
    logger.info("Loading plugins")
    plugin_loader.load_plugins()
    
    # 加载模型后端配置
    logger.info("Loading LLMs")
    llm_manager.load_config()
    
    # 创建 IM 生命周期管理器
    logger.info("Starting adapters")
    im_manager.start_adapters(loop=loop)
    
    # 启动插件
    plugin_loader.start_plugins()

    # 注册信号处理函数
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        # 保持程序运行
        logger.info("Application started. Waiting for events...")
        loop.run_forever()
    except GracefulExit:
        logger.info("Graceful exit requested")
    finally:
        # 停止所有 adapter
        im_manager.stop_adapters(loop=loop)
        # 停止插件
        plugin_loader.stop_plugins()
        # 关闭事件循环
        loop.close()
        logger.info("Application stopped gracefully")

if __name__ == "__main__":
    main()