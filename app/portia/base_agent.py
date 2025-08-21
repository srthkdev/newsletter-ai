from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from portia import Portia, Plan, PlanBuilder
from app.portia.config import get_portia_client, AGENT_CONFIGS


class BaseNewsletterAgent(ABC):
    """Base class for all newsletter agents using Portia AI framework"""

    def __init__(self, agent_type: str):
        config = AGENT_CONFIGS.get(agent_type, {})
        self.name = config.get("name", "NewsletterAgent")
        self.description = config.get("description", "Newsletter AI agent")
        self.model = config.get(
            "model", "gemini-2.0-flash"
        )  # Updated default to Gemini
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)
        self.agent_type = agent_type
        self.portia_client = get_portia_client()

    @abstractmethod
    async def create_plan(self, context: Dict[str, Any]) -> Plan:
        """Create execution plan for the agent using Portia PlanBuilder"""
        pass

    @abstractmethod
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task using Portia"""
        pass

    async def run_plan(self, plan: Plan) -> Dict[str, Any]:
        """Execute a Portia plan and return results"""
        if not self.portia_client:
            return {
                "success": False,
                "error": "Portia client not initialized - check API keys",
                "agent": self.name,
            }

        try:
            plan_run = self.portia_client.run_plan(plan)
            return {
                "success": True,
                "result": plan_run.final_output,
                "plan_id": plan.id,
                "run_id": plan_run.id,
            }
        except Exception as e:
            return await self.handle_error(e, {"plan_id": plan.id})

    async def handle_error(
        self, error: Exception, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle agent execution errors"""
        return {
            "success": False,
            "error": str(error),
            "agent": self.name,
            "context": context,
            "recovery_action": "retry_with_fallback",
        }
