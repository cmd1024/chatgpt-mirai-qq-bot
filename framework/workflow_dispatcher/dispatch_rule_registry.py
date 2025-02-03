from typing import List
from framework.workflow_dispatcher.dispatch_rule import DispatchRule, PrefixMatchRule, KeywordMatchRule, RegexMatchRule
from framework.workflow_executor.workflow_registry import WorkflowRegistry
from framework.ioc.container import DependencyContainer
from framework.logger import get_logger
import os
from ruamel.yaml import YAML

class DispatchRuleRegistry:
    """调度规则注册表，管理调度规则的加载和注册"""
    
    def __init__(self, container: DependencyContainer):
        self.container = container
        self.workflow_registry = container.resolve(WorkflowRegistry)
        self.rules: List[DispatchRule] = []
        self.logger = get_logger("DispatchRuleRegistry")
        

    def register(self, rule: DispatchRule):
        """注册一个调度规则"""
        self.rules.append(rule)
        self.logger.info(f"Registered dispatch rule: {rule}")
        
    def load_rules(self, rules_dir: str = "data/dispatch_rules"):
        """从指定目录加载所有调度规则"""
        if not os.path.exists(rules_dir):
            os.makedirs(rules_dir)
            
        yaml = YAML(typ='safe')
        
        for file_name in os.listdir(rules_dir):
            if not file_name.endswith('.yaml'):
                continue
                
            file_path = os.path.join(rules_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules_data = yaml.load(f)
                    
                if not isinstance(rules_data, list):
                    self.logger.warning(f"Invalid rules file {file_name}, expected list of rules")
                    continue
                    
                for rule_data in rules_data:
                    rule = self._create_rule(rule_data)
                    if rule:
                        self.register(rule)
                        
            except Exception as e:
                self.logger.error(f"Failed to load rules from {file_path}: {str(e)}")
                
    def _create_rule(self, rule_data: dict) -> DispatchRule:
        """从规则数据创建调度规则实例"""
        rule_type = rule_data.get('type')
        workflow_name = rule_data.get('workflow')
        

        if not rule_type or not workflow_name:
            raise ValueError("Rule must specify 'type' and 'workflow'")
            
        # 获取工作流构建器
        workflow_builder = self.workflow_registry.get(workflow_name)
        if not workflow_builder:
            raise ValueError(f"Workflow {workflow_name} not found")
            
        # 根据规则类型创建相应的规则实例
        if rule_type == 'prefix':
            prefix = rule_data.get('prefix')
            if not prefix:
                raise ValueError("Prefix rule must specify 'prefix'")
            return PrefixMatchRule(prefix, workflow_builder)
            
        elif rule_type == 'keyword':
            keywords = rule_data.get('keywords')
            if not keywords or not isinstance(keywords, list):
                raise ValueError("Keyword rule must specify 'keywords' as list")
            return KeywordMatchRule(keywords, workflow_builder)
            
        elif rule_type == 'regex':
            pattern = rule_data.get('pattern')
            if not pattern:
                raise ValueError("Regex rule must specify 'pattern'")
            return RegexMatchRule(pattern, workflow_builder)
            
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")
            
    def get_rules(self) -> List[DispatchRule]:
        """获取所有已注册的规则"""
        return self.rules.copy() 