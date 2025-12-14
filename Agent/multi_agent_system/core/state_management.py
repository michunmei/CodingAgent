"""
Standard State Management for Multi-Agent Collaborative System
COMP7103C Compliant - Tracking global project state, maintaining shared memory, and determining final task completion status
"""
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class AgentState(Enum):
    """Agent state enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class Task:
    """Task representation with dependencies and constraints"""
    id: str
    title: str
    description: str
    agent_type: str  # Which type of agent should handle this
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # in minutes
    max_duration: Optional[int] = None  # maximum allowed duration
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    files_to_create: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    validation_criteria: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "agent_type": self.agent_type,
            "priority": self.priority.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            "max_duration": self.max_duration,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "error_info": self.error_info,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "files_to_create": self.files_to_create,
            "tools_required": self.tools_required,
            "validation_criteria": self.validation_criteria,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        task = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            agent_type=data["agent_type"],
            priority=TaskPriority(data.get("priority", TaskPriority.NORMAL.value)),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            dependencies=data.get("dependencies", []),
            estimated_duration=data.get("estimated_duration"),
            max_duration=data.get("max_duration"),
            created_at=datetime.fromisoformat(data["created_at"]),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            files_to_create=data.get("files_to_create", []),
            tools_required=data.get("tools_required", []),
            validation_criteria=data.get("validation_criteria", {}),
            metadata=data.get("metadata", {})
        )
        
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        task.assigned_agent = data.get("assigned_agent")
        task.result = data.get("result")
        task.error_info = data.get("error_info")
        
        return task

@dataclass
class AgentInfo:
    """Agent information and state"""
    name: str
    agent_type: str
    state: AgentState = AgentState.IDLE
    current_task: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    active_tasks: Set[str] = field(default_factory=set)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return (self.state == AgentState.IDLE and 
                len(self.active_tasks) < self.max_concurrent_tasks)
    
    def get_utilization(self) -> float:
        """Get agent utilization percentage"""
        return len(self.active_tasks) / self.max_concurrent_tasks

class ProjectState:
    """Global project state management"""
    
    def __init__(self, project_name: str = ""):
        self.project_name = project_name
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.phase = "initialization"  # initialization, planning, development, testing, completion
        self.overall_progress = 0.0  # 0.0 to 1.0
        self.shared_memory: Dict[str, Any] = {}
        self.file_registry: Dict[str, Dict[str, Any]] = {}  # filename -> metadata
        self.generated_artifacts: List[str] = []
        self.quality_metrics: Dict[str, Any] = {}
        self.lock = threading.Lock()
        
        logger.info(f"ProjectState initialized for: {project_name}")
    
    def update_phase(self, new_phase: str) -> None:
        """Update project phase"""
        with self.lock:
            old_phase = self.phase
            self.phase = new_phase
            self.last_updated = datetime.now()
            logger.info(f"Project phase changed: {old_phase} -> {new_phase}")
    
    def update_progress(self, progress: float) -> None:
        """Update overall project progress"""
        with self.lock:
            self.overall_progress = max(0.0, min(1.0, progress))
            self.last_updated = datetime.now()
            logger.info(f"Project progress updated: {self.overall_progress:.2%}")
    
    def set_shared_data(self, key: str, value: Any) -> None:
        """Set shared data between agents"""
        with self.lock:
            self.shared_memory[key] = value
            self.last_updated = datetime.now()
            logger.debug(f"Shared data set: {key}")
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """Get shared data"""
        with self.lock:
            return self.shared_memory.get(key, default)
    
    def register_file(self, filename: str, metadata: Dict[str, Any]) -> None:
        """Register a generated file"""
        with self.lock:
            self.file_registry[filename] = {
                **metadata,
                "registered_at": datetime.now().isoformat()
            }
            if filename not in self.generated_artifacts:
                self.generated_artifacts.append(filename)
            self.last_updated = datetime.now()
            logger.info(f"File registered: {filename}")
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get project summary"""
        with self.lock:
            return {
                "project_name": self.project_name,
                "created_at": self.created_at.isoformat(),
                "last_updated": self.last_updated.isoformat(),
                "phase": self.phase,
                "progress": self.overall_progress,
                "total_files": len(self.file_registry),
                "generated_artifacts": len(self.generated_artifacts),
                "shared_data_keys": list(self.shared_memory.keys()),
                "quality_metrics": self.quality_metrics
            }

class TaskScheduler:
    """Advanced task scheduler with dependency resolution and agent allocation"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, AgentInfo] = {}
        self.project_state = ProjectState()
        self.task_queue: List[str] = []  # Task IDs in execution order
        self.dependency_graph: Dict[str, Set[str]] = {}  # task_id -> dependencies
        self.reverse_dependencies: Dict[str, Set[str]] = {}  # task_id -> dependents
        self.lock = threading.Lock()
        
        logger.info("TaskScheduler initialized")
    
    def register_agent(self, name: str, agent_type: str, capabilities: List[str] = None,
                      max_concurrent_tasks: int = 1) -> None:
        """Register an agent with the scheduler"""
        with self.lock:
            self.agents[name] = AgentInfo(
                name=name,
                agent_type=agent_type,
                capabilities=capabilities or [],
                max_concurrent_tasks=max_concurrent_tasks
            )
            logger.info(f"Agent registered: {name} ({agent_type})")
    
    def add_task(self, task: Task) -> str:
        """Add a task to the scheduler"""
        with self.lock:
            self.tasks[task.id] = task
            self.dependency_graph[task.id] = set(task.dependencies)
            
            # Update reverse dependencies
            for dep_id in task.dependencies:
                if dep_id not in self.reverse_dependencies:
                    self.reverse_dependencies[dep_id] = set()
                self.reverse_dependencies[dep_id].add(task.id)
            
            # Update task status based on dependencies
            self._update_task_status(task.id)
            
            logger.info(f"Task added: {task.id} - {task.title}")
            return task.id
    
    def create_task_from_plan_item(self, plan_item: Dict[str, Any]) -> Task:
        """Create a task from a plan item"""
        task_id = plan_item.get("id", str(uuid.uuid4()))
        
        # Determine agent type from task content
        agent_type = self._determine_agent_type(plan_item)
        
        task = Task(
            id=task_id,
            title=plan_item.get("title", "Unknown Task"),
            description=plan_item.get("description", ""),
            agent_type=agent_type,
            dependencies=plan_item.get("dependencies", []),
            estimated_duration=self._parse_estimated_effort(plan_item.get("estimated_effort")),
            files_to_create=plan_item.get("files_to_create", []),
            tools_required=self._determine_required_tools(plan_item),
            validation_criteria=self._extract_validation_criteria(plan_item),
            metadata={"source": "project_plan", "plan_item": plan_item}
        )
        
        return task
    
    def get_next_task(self, agent_name: str) -> Optional[Task]:
        """Get the next task for a specific agent"""
        with self.lock:
            if agent_name not in self.agents:
                logger.warning(f"Agent '{agent_name}' not found in registered agents")
                return None
            
            agent = self.agents[agent_name]
            logger.debug(f"Checking agent '{agent_name}' availability: {agent.is_available()}")
            
            if not agent.is_available():
                return None
            
            # Find ready tasks that match agent capabilities
            ready_tasks = [
                task for task in self.tasks.values()
                if (task.status == TaskStatus.READY and
                    task.agent_type == agent.agent_type and
                    self._can_agent_handle_task(agent, task))
            ]
            
            logger.info(f"Found {len(ready_tasks)} ready tasks for agent '{agent_name}' of type '{agent.agent_type}'")
            logger.debug(f"Total tasks: {len(self.tasks)}")
            
            # Debug: log task statuses and types
            for task_id, task in self.tasks.items():
                logger.debug(f"Task {task_id}: status={task.status.value}, agent_type={task.agent_type}")
            
            if not ready_tasks:
                return None
            
            # Sort by priority and creation time
            ready_tasks.sort(key=lambda t: (-t.priority.value, t.created_at))
            
            selected_task = ready_tasks[0]
            self._assign_task_to_agent(selected_task.id, agent_name)
            
            return selected_task
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark a task as completed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # Update agent state
            if task.assigned_agent and task.assigned_agent in self.agents:
                agent = self.agents[task.assigned_agent]
                agent.state = AgentState.IDLE
                agent.current_task = None
                agent.active_tasks.discard(task_id)
                agent.completed_tasks.append(task_id)
                agent.last_activity = datetime.now()
            
            # Check for dependent tasks that can now be ready
            self._update_dependent_tasks(task_id)
            
            # Register generated files
            if task.result and "generated_files" in task.result:
                for filename in task.result["generated_files"]:
                    self.project_state.register_file(filename, {
                        "task_id": task_id,
                        "agent": task.assigned_agent,
                        "file_type": self._determine_file_type(filename)
                    })
            
            logger.info(f"Task completed: {task_id}")
            return True
    
    def fail_task(self, task_id: str, error_info: Dict[str, Any]) -> bool:
        """Mark a task as failed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.retry_count += 1
            task.error_info = error_info
            
            if task.retry_count < task.max_retries:
                # Reset for retry
                task.status = TaskStatus.READY
                task.assigned_agent = None
                logger.warning(f"Task retry {task.retry_count}/{task.max_retries}: {task_id}")
            else:
                # Mark as permanently failed
                task.status = TaskStatus.FAILED
                
                # Update agent state
                if task.assigned_agent and task.assigned_agent in self.agents:
                    agent = self.agents[task.assigned_agent]
                    agent.state = AgentState.IDLE
                    agent.current_task = None
                    agent.active_tasks.discard(task_id)
                    agent.failed_tasks.append(task_id)
                
                logger.error(f"Task failed permanently: {task_id}")
            
            return True
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get overall project status"""
        with self.lock:
            total_tasks = len(self.tasks)
            completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
            in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
            
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0
            self.project_state.update_progress(progress)
            
            return {
                "project_summary": self.project_state.get_project_summary(),
                "task_statistics": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks,
                    "in_progress": in_progress_tasks,
                    "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
                    "ready": len([t for t in self.tasks.values() if t.status == TaskStatus.READY]),
                    "blocked": len([t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED])
                },
                "agent_statistics": {
                    "total_agents": len(self.agents),
                    "active_agents": len([a for a in self.agents.values() if a.state == AgentState.BUSY]),
                    "idle_agents": len([a for a in self.agents.values() if a.state == AgentState.IDLE]),
                    "agent_utilization": {
                        name: agent.get_utilization()
                        for name, agent in self.agents.items()
                    }
                },
                "overall_progress": progress
            }
    
    def _update_task_status(self, task_id: str) -> None:
        """Update task status based on dependencies"""
        task = self.tasks[task_id]
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return
        
        # Check if all dependencies are completed
        all_deps_completed = all(
            dep_id in self.tasks and self.tasks[dep_id].status == TaskStatus.COMPLETED
            for dep_id in task.dependencies
        )
        
        if all_deps_completed:
            task.status = TaskStatus.READY
        elif any(dep_id in self.tasks and self.tasks[dep_id].status == TaskStatus.FAILED 
                for dep_id in task.dependencies):
            task.status = TaskStatus.BLOCKED
        else:
            task.status = TaskStatus.PENDING
    
    def _update_dependent_tasks(self, completed_task_id: str) -> None:
        """Update tasks that depend on the completed task"""
        if completed_task_id in self.reverse_dependencies:
            for dependent_id in self.reverse_dependencies[completed_task_id]:
                self._update_task_status(dependent_id)
    
    def _assign_task_to_agent(self, task_id: str, agent_name: str) -> None:
        """Assign a task to an agent"""
        task = self.tasks[task_id]
        agent = self.agents[agent_name]
        
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent = agent_name
        task.started_at = datetime.now()
        
        agent.state = AgentState.BUSY
        agent.current_task = task_id
        agent.active_tasks.add(task_id)
        agent.last_activity = datetime.now()
        
        logger.info(f"Task assigned: {task_id} -> {agent_name}")
    
    def _can_agent_handle_task(self, agent: AgentInfo, task: Task) -> bool:
        """Check if an agent can handle a specific task"""
        # Basic type matching
        if task.agent_type != agent.agent_type:
            return False
        
        # Check capabilities if specified
        if task.tools_required:
            agent_tools = set(agent.capabilities)
            required_tools = set(task.tools_required)
            if not required_tools.issubset(agent_tools):
                return False
        
        return True
    
    def _determine_agent_type(self, plan_item: Dict[str, Any]) -> str:
        """Determine which agent type should handle a task"""
        title = plan_item.get("title", "").lower()
        description = plan_item.get("description", "").lower()
        
        # Only pure planning/design tasks should go to ProjectPlanningAgent
        # Implementation tasks (even if they involve architecture) go to CodeGenerationAgent
        if any(keyword in title or keyword in description 
               for keyword in ["review", "test", "validate", "check", "quality", "qa"]):
            return "CodeEvaluationAgent"
        else:
            # All implementation tasks go to CodeGenerationAgent
            return "CodeGenerationAgent"
    
    def _parse_estimated_effort(self, effort_str: str) -> Optional[int]:
        """Parse estimated effort string to minutes"""
        if not effort_str:
            return None
        
        effort_str = effort_str.lower()
        if "hour" in effort_str:
            try:
                hours = float(effort_str.split("hour")[0].strip())
                return int(hours * 60)
            except:
                pass
        elif "min" in effort_str:
            try:
                minutes = float(effort_str.split("min")[0].strip())
                return int(minutes)
            except:
                pass
        
        return None
    
    def _determine_required_tools(self, plan_item: Dict[str, Any]) -> List[str]:
        """Determine required tools from plan item"""
        tools = []
        
        files_to_create = plan_item.get("files_to_create", [])
        for filename in files_to_create:
            ext = Path(filename).suffix.lower()
            if ext in [".py"]:
                tools.append("python")
            elif ext in [".js", ".ts"]:
                tools.append("javascript")
            elif ext in [".html", ".css"]:
                tools.append("web_development")
        
        description = plan_item.get("description", "").lower()
        if "test" in description:
            tools.append("testing")
        if "server" in description:
            tools.append("web_server")
        
        return tools
    
    def _extract_validation_criteria(self, plan_item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract validation criteria from plan item"""
        criteria = {}
        
        if plan_item.get("files_to_create"):
            criteria["files_required"] = plan_item["files_to_create"]
        
        description = plan_item.get("description", "")
        if "responsive" in description.lower():
            criteria["responsive_design"] = True
        if "test" in description.lower():
            criteria["needs_testing"] = True
        
        return criteria
    
    def _determine_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        ext = Path(filename).suffix.lower()
        
        type_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".md": "markdown"
        }
        
        return type_map.get(ext, "unknown")


class StateManager:
    """
    State Management: Tracking global project state, maintaining shared memory, 
    and determining final task completion status
    
    COMP7103C Compliant implementation
    """
    
    def __init__(self):
        self.global_state = {}
        self.state_history = []
        self.task_states = {}
        self.shared_memory = {}
        logger.info("StateManager initialized")
    
    def set_global_state(self, key: str, value: Any):
        """Set a global state variable"""
        old_value = self.global_state.get(key)
        self.global_state[key] = value
        
        # Log state change
        change_record = {
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'change_type': 'global_state'
        }
        self.state_history.append(change_record)
        logger.debug(f"Global state updated: {key} = {value}")
    
    def get_global_state(self, key: str, default=None):
        """Get a global state variable"""
        return self.global_state.get(key, default)
    
    def update_task_status(self, task_id: str, status: str, details: Dict[str, Any] = None):
        """Update task status in state management"""
        if task_id not in self.task_states:
            self.task_states[task_id] = {}
        
        old_status = self.task_states[task_id].get('status')
        self.task_states[task_id].update({
            'status': status,
            'updated_at': datetime.now().isoformat(),
            'details': details or {}
        })
        
        # Log task state change
        change_record = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'old_status': old_status,
            'new_status': status,
            'change_type': 'task_state'
        }
        self.state_history.append(change_record)
        logger.info(f"Task {task_id} status updated: {old_status} -> {status}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current task status"""
        return self.task_states.get(task_id, {})
    
    def set_shared_memory(self, key: str, value: Any):
        """Set shared memory for inter-agent communication"""
        self.shared_memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        logger.debug(f"Shared memory updated: {key}")
    
    def get_shared_memory(self, key: str, default=None):
        """Get shared memory value"""
        memory_item = self.shared_memory.get(key)
        if memory_item:
            return memory_item['value']
        return default
    
    def get_all_states(self) -> Dict[str, Any]:
        """Get complete state snapshot"""
        return {
            'global_state': self.global_state,
            'task_states': self.task_states,
            'shared_memory': {k: v['value'] for k, v in self.shared_memory.items()},
            'state_timestamp': datetime.now().isoformat()
        }
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get complete state change history"""
        return self.state_history
    
    def determine_completion_status(self) -> Dict[str, Any]:
        """Determine final task completion status"""
        total_tasks = len(self.task_states)
        if total_tasks == 0:
            return {'status': 'no_tasks', 'completion_rate': 0.0}
        
        completed_tasks = len([
            task for task in self.task_states.values() 
            if task.get('status') == 'completed'
        ])
        
        failed_tasks = len([
            task for task in self.task_states.values()
            if task.get('status') == 'failed'
        ])
        
        completion_rate = completed_tasks / total_tasks
        
        if completion_rate == 1.0:
            final_status = 'fully_completed'
        elif completion_rate >= 0.8:
            final_status = 'mostly_completed'
        elif completion_rate >= 0.5:
            final_status = 'partially_completed'
        else:
            final_status = 'minimal_completion'
        
        return {
            'status': final_status,
            'completion_rate': completion_rate,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': completed_tasks / max(total_tasks, 1)
        }