"""
Comprehensive Error Handling and Portia Agent Monitoring System
Provides real-time monitoring, error tracking, and recovery mechanisms
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import traceback
import os

from app.portia.agent_orchestrator import agent_orchestrator
from app.services.memory import memory_service


# Ensure logs directory exists
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    try:
        os.makedirs(logs_dir)
    except OSError:
        # If we can't create the directory, log to stdout only
        logs_dir = None

# Configure comprehensive logging
if logs_dir:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'newsletter_ai.log')),
            logging.StreamHandler()
        ]
    )
else:
    # Fallback to console-only logging if directory creation fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentStatus(Enum):
    """Agent status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class ErrorEvent:
    """Represents an error event"""
    timestamp: datetime
    component: str
    error_type: str
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any]
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    resolved: bool = False


@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    name: str
    status: AgentStatus
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    last_execution: Optional[datetime]
    last_error: Optional[ErrorEvent]
    health_score: float


class PortiaAgentMonitor:
    """
    Comprehensive monitoring system for Portia AI agents
    Tracks performance, errors, and provides recovery mechanisms
    """

    def __init__(self):
        self.error_events: List[ErrorEvent] = []
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.error_handlers: Dict[str, Callable] = {}
        self.is_monitoring = False
        self.max_error_history = 1000
        
        # Initialize agent metrics
        self._initialize_agent_metrics()

    def _initialize_agent_metrics(self):
        """Initialize metrics for all agents"""
        agents = [
            "research_agent",
            "writing_agent", 
            "preference_agent",
            "custom_prompt_agent",
            "mindmap_agent",
            "agent_orchestrator"
        ]
        
        for agent_name in agents:
            self.agent_metrics[agent_name] = AgentMetrics(
                name=agent_name,
                status=AgentStatus.HEALTHY,
                total_executions=0,
                successful_executions=0,
                failed_executions=0,
                average_execution_time=0.0,
                last_execution=None,
                last_error=None,
                health_score=100.0
            )

    async def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("🔍 Starting Portia Agent Monitoring System")
        self.is_monitoring = True
        
        # Start background monitoring tasks
        asyncio.create_task(self._monitor_agent_health())
        asyncio.create_task(self._cleanup_old_errors())
        
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        logger.info("🛑 Stopping Portia Agent Monitoring System")
        self.is_monitoring = False

    async def record_agent_execution(
        self,
        agent_name: str,
        execution_time: float,
        success: bool,
        context: Dict[str, Any],
        error: Optional[Exception] = None
    ):
        """Record an agent execution for monitoring"""
        if agent_name not in self.agent_metrics:
            self._initialize_agent_metrics()
        
        metrics = self.agent_metrics[agent_name]
        metrics.total_executions += 1
        metrics.last_execution = datetime.utcnow()
        
        if success:
            metrics.successful_executions += 1
            metrics.status = AgentStatus.HEALTHY
        else:
            metrics.failed_executions += 1
            
            # Record error event
            if error:
                await self._record_error(
                    component=agent_name,
                    error=error,
                    context=context,
                    severity=self._determine_error_severity(error)
                )
        
        # Update average execution time
        if metrics.total_executions > 0:
            current_avg = metrics.average_execution_time
            metrics.average_execution_time = (
                (current_avg * (metrics.total_executions - 1) + execution_time) 
                / metrics.total_executions
            )
        
        # Update health score
        metrics.health_score = self._calculate_health_score(metrics)
        
        # Update agent status based on recent performance
        metrics.status = self._determine_agent_status(metrics)

    async def _record_error(
        self,
        component: str,
        error: Exception,
        context: Dict[str, Any],
        severity: ErrorSeverity,
        user_id: Optional[str] = None
    ):
        """Record an error event"""
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            component=component,
            error_type=type(error).__name__,
            severity=severity,
            message=str(error),
            context=context,
            stack_trace=traceback.format_exc(),
            user_id=user_id
        )
        
        self.error_events.append(error_event)
        
        # Update agent metrics
        if component in self.agent_metrics:
            self.agent_metrics[component].last_error = error_event
        
        # Log error
        logger.error(f"❌ {component} error: {error_event.message}")
        
        # Store in memory for persistent tracking
        await self._store_error_in_memory(error_event)
        
        # Trigger error handler if available
        if component in self.error_handlers:
            try:
                await self.error_handlers[component](error_event)
            except Exception as handler_error:
                logger.error(f"Error handler failed for {component}: {handler_error}")
        
        # Cleanup old errors if needed
        if len(self.error_events) > self.max_error_history:
            self.error_events = self.error_events[-self.max_error_history:]

    def _determine_error_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity based on error type"""
        error_type = type(error).__name__
        
        critical_errors = [
            "ConnectionError",
            "AuthenticationError", 
            "DatabaseError",
            "OutOfMemoryError"
        ]
        
        high_errors = [
            "TimeoutError",
            "ValidationError",
            "KeyError",
            "ValueError"
        ]
        
        medium_errors = [
            "HTTPException",
            "RequestException",
            "ParseError"
        ]
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def _calculate_health_score(self, metrics: AgentMetrics) -> float:
        """Calculate health score for an agent"""
        if metrics.total_executions == 0:
            return 100.0
        
        success_rate = metrics.successful_executions / metrics.total_executions
        base_score = success_rate * 100
        
        # Penalize for recent errors
        if metrics.last_error:
            time_since_error = datetime.utcnow() - metrics.last_error.timestamp
            if time_since_error < timedelta(hours=1):
                penalty = 20
            elif time_since_error < timedelta(hours=24):
                penalty = 10
            else:
                penalty = 5
            base_score = max(0, base_score - penalty)
        
        # Penalize for slow execution times
        if metrics.average_execution_time > 60:  # 60 seconds
            base_score = max(0, base_score - 10)
        
        return round(base_score, 1)

    def _determine_agent_status(self, metrics: AgentMetrics) -> AgentStatus:
        """Determine agent status based on metrics"""
        if metrics.health_score >= 90:
            return AgentStatus.HEALTHY
        elif metrics.health_score >= 70:
            return AgentStatus.WARNING
        elif metrics.health_score >= 50:
            return AgentStatus.ERROR
        else:
            return AgentStatus.OFFLINE

    async def _store_error_in_memory(self, error_event: ErrorEvent):
        """Store error event in memory for persistence"""
        try:
            error_data = {
                "timestamp": error_event.timestamp.isoformat(),
                "component": error_event.component,
                "error_type": error_event.error_type,
                "severity": error_event.severity.value,
                "message": error_event.message,
                "context": error_event.context,
                "user_id": error_event.user_id
            }
            
            await memory_service.store_user_context(
                "system",
                f"error_{error_event.timestamp.isoformat()}",
                error_data
            )
        except Exception as e:
            logger.error(f"Failed to store error in memory: {e}")

    async def _monitor_agent_health(self):
        """Background task to monitor agent health"""
        while self.is_monitoring:
            try:
                # Check each agent's health
                for agent_name, metrics in self.agent_metrics.items():
                    if metrics.status in [AgentStatus.ERROR, AgentStatus.OFFLINE]:
                        logger.warning(f"⚠️ Agent {agent_name} is in {metrics.status.value} state")
                        
                        # Attempt recovery
                        await self._attempt_agent_recovery(agent_name)
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)

    async def _attempt_agent_recovery(self, agent_name: str):
        """Attempt to recover a failing agent"""
        logger.info(f"🔧 Attempting recovery for agent {agent_name}")
        
        try:
            # Test agent with a simple operation
            if agent_name == "research_agent":
                test_result = await agent_orchestrator.research_agent.execute_task(
                    "search_by_topics",
                    {"topics": ["test"], "days_back": 1, "max_results_per_topic": 1}
                )
            elif agent_name == "writing_agent":
                test_result = await agent_orchestrator.writing_agent.execute_task(
                    "generate_newsletter",
                    {"articles": [], "user_preferences": {}}
                )
            else:
                # Generic health check
                test_result = {"success": True}
            
            if test_result.get("success"):
                logger.info(f"✅ Agent {agent_name} recovery successful")
                self.agent_metrics[agent_name].status = AgentStatus.HEALTHY
                return True
            else:
                logger.warning(f"❌ Agent {agent_name} recovery failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Agent {agent_name} recovery attempt failed: {e}")
            return False

    async def _cleanup_old_errors(self):
        """Clean up old error events"""
        while self.is_monitoring:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                
                # Remove old errors
                self.error_events = [
                    error for error in self.error_events
                    if error.timestamp > cutoff_time
                ]
                
                logger.info(f"🧹 Cleaned up old errors, {len(self.error_events)} errors remaining")
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(3600)

    def register_error_handler(self, component: str, handler: Callable):
        """Register a custom error handler for a component"""
        self.error_handlers[component] = handler
        logger.info(f"🔧 Registered error handler for {component}")

    async def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        recent_errors = [
            {
                "timestamp": error.timestamp.isoformat(),
                "component": error.component,
                "severity": error.severity.value,
                "message": error.message,
                "resolved": error.resolved
            }
            for error in self.error_events[-10:]  # Last 10 errors
        ]
        
        agent_status = {
            name: {
                "status": metrics.status.value,
                "health_score": metrics.health_score,
                "total_executions": metrics.total_executions,
                "success_rate": (
                    metrics.successful_executions / metrics.total_executions * 100
                    if metrics.total_executions > 0 else 0
                ),
                "average_execution_time": metrics.average_execution_time,
                "last_execution": metrics.last_execution.isoformat() if metrics.last_execution else None
            }
            for name, metrics in self.agent_metrics.items()
        }
        
        # Calculate overall system health
        avg_health = sum(m.health_score for m in self.agent_metrics.values()) / len(self.agent_metrics)
        
        return {
            "system_health": {
                "overall_score": round(avg_health, 1),
                "status": "healthy" if avg_health >= 90 else "warning" if avg_health >= 70 else "critical",
                "monitoring_active": self.is_monitoring
            },
            "agents": agent_status,
            "recent_errors": recent_errors,
            "error_summary": {
                "total_errors_24h": len([
                    e for e in self.error_events 
                    if e.timestamp > datetime.utcnow() - timedelta(days=1)
                ]),
                "critical_errors": len([
                    e for e in self.error_events 
                    if e.severity == ErrorSeverity.CRITICAL and not e.resolved
                ]),
                "unresolved_errors": len([
                    e for e in self.error_events 
                    if not e.resolved
                ])
            }
        }

    async def resolve_error(self, error_index: int) -> bool:
        """Mark an error as resolved"""
        try:
            if 0 <= error_index < len(self.error_events):
                self.error_events[error_index].resolved = True
                logger.info(f"✅ Marked error {error_index} as resolved")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve error: {e}")
            return False

    async def get_agent_performance_report(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed performance report for a specific agent"""
        if agent_name not in self.agent_metrics:
            return None
        
        metrics = self.agent_metrics[agent_name]
        
        # Get recent errors for this agent
        agent_errors = [
            {
                "timestamp": error.timestamp.isoformat(),
                "severity": error.severity.value,
                "message": error.message,
                "context": error.context
            }
            for error in self.error_events
            if error.component == agent_name and error.timestamp > datetime.utcnow() - timedelta(days=7)
        ]
        
        return {
            "agent_name": agent_name,
            "current_status": metrics.status.value,
            "health_score": metrics.health_score,
            "performance": {
                "total_executions": metrics.total_executions,
                "successful_executions": metrics.successful_executions,
                "failed_executions": metrics.failed_executions,
                "success_rate": (
                    metrics.successful_executions / metrics.total_executions * 100
                    if metrics.total_executions > 0 else 0
                ),
                "average_execution_time": metrics.average_execution_time
            },
            "recent_activity": {
                "last_execution": metrics.last_execution.isoformat() if metrics.last_execution else None,
                "last_error": {
                    "timestamp": metrics.last_error.timestamp.isoformat(),
                    "message": metrics.last_error.message,
                    "severity": metrics.last_error.severity.value
                } if metrics.last_error else None
            },
            "recent_errors": agent_errors,
            "recommendations": self._generate_agent_recommendations(metrics)
        }

    def _generate_agent_recommendations(self, metrics: AgentMetrics) -> List[str]:
        """Generate recommendations for improving agent performance"""
        recommendations = []
        
        if metrics.health_score < 70:
            recommendations.append("Agent health is below optimal - consider investigating recent errors")
        
        if metrics.average_execution_time > 30:
            recommendations.append("Average execution time is high - consider optimizing agent logic")
        
        success_rate = metrics.successful_executions / metrics.total_executions * 100 if metrics.total_executions > 0 else 0
        if success_rate < 90:
            recommendations.append("Success rate is below 90% - review error patterns and improve error handling")
        
        if metrics.last_error and datetime.utcnow() - metrics.last_error.timestamp < timedelta(hours=1):
            recommendations.append("Recent error detected - monitor closely for recurring issues")
        
        if not recommendations:
            recommendations.append("Agent is performing well - no immediate action required")
        
        return recommendations


# Global monitoring instance
portia_monitor = PortiaAgentMonitor()


# Monitoring control functions
async def start_portia_monitoring():
    """Start the global Portia monitoring system"""
    await portia_monitor.start_monitoring()


async def stop_portia_monitoring():
    """Stop the global Portia monitoring system"""
    await portia_monitor.stop_monitoring()


async def record_agent_execution(agent_name: str, execution_time: float, success: bool, context: Dict[str, Any], error: Optional[Exception] = None):
    """Record an agent execution for monitoring"""
    await portia_monitor.record_agent_execution(agent_name, execution_time, success, context, error)


async def get_monitoring_dashboard():
    """Get the monitoring dashboard data"""
    return await portia_monitor.get_monitoring_dashboard()


async def get_agent_performance_report(agent_name: str):
    """Get performance report for a specific agent"""
    return await portia_monitor.get_agent_performance_report(agent_name)