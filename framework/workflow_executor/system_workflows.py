from framework.workflow_executor.workflow_registry import WorkflowRegistry
from framework.workflows.game.factory import GameWorkflowFactory
from framework.workflows.system.factory import SystemWorkflowFactory
from framework.workflows.default.factory import DefaultWorkflowFactory

def register_system_workflows(registry: WorkflowRegistry):
    """注册系统自带的工作流"""
    
    # 游戏相关工作流
    registry.register("game", "dice", GameWorkflowFactory.create_dice_workflow)
    registry.register("game", "gacha", GameWorkflowFactory.create_gacha_workflow)
    
    # 系统相关工作流
    registry.register("system", "help", SystemWorkflowFactory.create_help_workflow)
    registry.register("system", "admin", SystemWorkflowFactory.create_help_workflow)  # 暂时用help代替
    registry.register("system", "status", SystemWorkflowFactory.create_help_workflow)  # 暂时用help代替
    registry.register("system", "settings", SystemWorkflowFactory.create_help_workflow)  # 暂时用help代替
    
    # 聊天相关工作流
    registry.register("chat", "normal", DefaultWorkflowFactory.create_workflow)
    registry.register("chat", "creative", DefaultWorkflowFactory.create_workflow)  # 暂时用默认的
    registry.register("chat", "roleplay", DefaultWorkflowFactory.create_workflow)  # 暂时用默认的 