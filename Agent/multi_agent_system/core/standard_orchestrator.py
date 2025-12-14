"""
Standard Multi-Agent Orchestrator - COMP7103C Compliant
Implements the exact orchestration framework as specified in the course requirements
"""
import os
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agents.base_agent import ProjectPlanningAgent, CodeGenerationAgent, CodeEvaluationAgent, ProjectContext
from core.llm_provider import LLMInterface, QwenProvider
from core.communication import CommunicationProtocol
from core.state_management import StateManager
from tools.filesystem_tools import FileSystemTools

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Task Scheduling: Determining which agent should work next and coordinating task dependencies across the system"""
    
    def __init__(self):
        self.task_queue = []
        self.completed_tasks = []
        self.current_task = None
        
    def add_task(self, task: Dict[str, Any]):
        """Add a task to the scheduling queue"""
        task['status'] = 'pending'
        task['created_at'] = datetime.now().isoformat()
        self.task_queue.append(task)
        logger.info(f"Task added to queue: {task.get('title', 'Unknown')}")
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next executable task based on dependencies"""
        for task in self.task_queue:
            if task['status'] == 'pending':
                # Check if dependencies are satisfied
                dependencies = task.get('dependencies', [])
                dependencies_met = all(
                    dep in [t['id'] for t in self.completed_tasks] 
                    for dep in dependencies
                )
                
                if dependencies_met:
                    task['status'] = 'in_progress'
                    task['started_at'] = datetime.now().isoformat()
                    self.current_task = task
                    logger.info(f"Next task scheduled: {task.get('title', 'Unknown')}")
                    return task
        
        return None
    
    def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Mark a task as completed"""
        for task in self.task_queue:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                task['result'] = result
                self.completed_tasks.append(task)
                self.current_task = None
                logger.info(f"Task completed: {task.get('title', 'Unknown')}")
                break
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduling status"""
        pending = [t for t in self.task_queue if t['status'] == 'pending']
        in_progress = [t for t in self.task_queue if t['status'] == 'in_progress']
        
        return {
            'pending_tasks': len(pending),
            'completed_tasks': len(self.completed_tasks),
            'in_progress_tasks': len(in_progress),
            'current_task': self.current_task.get('title') if self.current_task else None
        }

class CommunicationManager:
    """Communication Management: Establishing protocols for seamless information exchange and collaboration between specialized agents"""
    
    def __init__(self):
        self.message_history = []
        self.agent_communications = {}
        
    def send_message(self, from_agent: str, to_agent: str, message: str, data: Any = None):
        """Send a message between agents"""
        comm_record = {
            'timestamp': datetime.now().isoformat(),
            'from_agent': from_agent,
            'to_agent': to_agent,
            'message': message,
            'data': data
        }
        
        self.message_history.append(comm_record)
        
        if to_agent not in self.agent_communications:
            self.agent_communications[to_agent] = []
        self.agent_communications[to_agent].append(comm_record)
        
        logger.info(f"Communication: {from_agent} -> {to_agent}: {message}")
        
    def get_messages_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific agent"""
        return self.agent_communications.get(agent_name, [])
    
    def broadcast_message(self, from_agent: str, message: str, data: Any = None):
        """Broadcast a message to all agents"""
        comm_record = {
            'timestamp': datetime.now().isoformat(),
            'from_agent': from_agent,
            'to_agent': 'ALL',
            'message': message,
            'data': data,
            'type': 'broadcast'
        }
        
        self.message_history.append(comm_record)
        logger.info(f"Broadcast from {from_agent}: {message}")

class StandardMultiAgentOrchestrator:
    """
    Standard Multi-Agent Orchestrator - COMP7103C Compliant
    
    Implements the three core components:
    - Task Scheduling: Coordinating agent execution and dependencies
    - Communication Management: Agent-to-agent information exchange
    - State Management: Global project state and memory tracking
    """
    
    def __init__(self, llm_config: Dict[str, Any], output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize core components
        self.task_scheduler = TaskScheduler()
        self.communication_manager = CommunicationManager()
        self.state_manager = StateManager()
        
        # Initialize LLM interface
        provider = QwenProvider(llm_config)
        self.llm_interface = LLMInterface(provider)
        
        # Initialize communication protocol
        self.communication_protocol = CommunicationProtocol()
        
        # Initialize specialized agents
        self.planning_agent = ProjectPlanningAgent(self.llm_interface, self.communication_protocol)
        self.code_agent = CodeGenerationAgent(self.llm_interface, self.communication_protocol, output_dir)
        self.evaluation_agent = CodeEvaluationAgent(self.llm_interface, self.communication_protocol, output_dir)
        
        # Initialize filesystem tools
        self.filesystem_tools = FileSystemTools(output_dir)
        
        logger.info("Standard Multi-Agent Orchestrator initialized with COMP7103C compliance")
    
    def execute_software_development(self, requirements: str, project_name: str = None) -> Dict[str, Any]:
        """
        Execute complete software development from natural language task descriptions
        
        Core workflow as per COMP7103C requirements:
        1. Planning Phase - Requirements analysis and task decomposition
        2. Development Phase - Code generation and implementation  
        3. Evaluation Phase - Quality validation and testing
        """
        start_time = time.time()
        
        # Initialize project context
        context = ProjectContext()
        context.requirements = requirements
        context.project_name = project_name or "Generated Project"
        
        self.state_manager.set_global_state('project_context', context)
        self.state_manager.set_global_state('project_status', 'started')
        
        logger.info(f"Starting software development: {context.project_name}")
        self.communication_manager.broadcast_message(
            "Orchestrator", 
            f"Starting project: {context.project_name}",
            {'requirements': requirements}
        )
        
        try:
            # Phase 1: Planning
            planning_result = self._execute_planning_phase(context)
            if not planning_result['success']:
                return self._create_failure_result("Planning phase failed", planning_result)
            
            # Phase 2: Development  
            development_result = self._execute_development_phase(context)
            if not development_result['success']:
                return self._create_failure_result("Development phase failed", development_result)
            
            # Phase 3: Evaluation
            evaluation_result = self._execute_evaluation_phase(context)
            
            # Final state management
            execution_time = time.time() - start_time
            self.state_manager.set_global_state('project_status', 'completed')
            self.state_manager.set_global_state('execution_time', execution_time)
            
            return self._create_success_result(context, execution_time, evaluation_result)
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            self.state_manager.set_global_state('project_status', 'failed')
            return self._create_failure_result(f"Orchestration error: {str(e)}", {})
    
    def _execute_planning_phase(self, context: ProjectContext) -> Dict[str, Any]:
        """Execute planning phase with task scheduling"""
        logger.info("=== PLANNING PHASE ===")
        
        # Communication protocol
        self.communication_manager.send_message(
            "Orchestrator", 
            "ProjectPlanningAgent",
            "Execute requirements analysis and task decomposition",
            context.requirements
        )
        
        # Execute planning agent
        planning_result = self.planning_agent.execute(context, context.requirements)
        
        if planning_result['success']:
            # Add tasks to scheduler
            plan = planning_result['plan']
            context.current_plan = plan
            
            for task in plan.get('tasks', []):
                self.task_scheduler.add_task(task)
            
            self.communication_manager.send_message(
                "ProjectPlanningAgent",
                "Orchestrator", 
                f"Planning completed with {len(plan.get('tasks', []))} tasks",
                plan
            )
            
            logger.info(f"Planning completed: {len(plan.get('tasks', []))} tasks created")
        
        return planning_result
    
    def _execute_development_phase(self, context: ProjectContext) -> Dict[str, Any]:
        """Execute development phase with task coordination"""
        logger.info("=== DEVELOPMENT PHASE ===")
        
        development_results = []
        
        # Execute tasks in dependency order
        while True:
            next_task = self.task_scheduler.get_next_task()
            if not next_task:
                break
                
            logger.info(f"Executing task: {next_task.get('title', 'Unknown')}")
            
            # Communication protocol
            self.communication_manager.send_message(
                "Orchestrator",
                "CodeGenerationAgent", 
                f"Execute task: {next_task.get('title')}",
                next_task
            )
            
            # Execute code generation
            task_result = self.code_agent.execute(context, next_task)
            development_results.append(task_result)
            
            # Update task scheduler
            self.task_scheduler.complete_task(next_task['id'], task_result)
            
            # State management update
            self.state_manager.update_task_status(next_task['id'], 'completed')
            
            if task_result['success']:
                self.communication_manager.send_message(
                    "CodeGenerationAgent",
                    "Orchestrator",
                    f"Task completed successfully: {next_task.get('title')}",
                    task_result
                )
            else:
                logger.warning(f"Task failed: {next_task.get('title')} - {task_result.get('message')}")
        
        success_count = sum(1 for r in development_results if r['success'])
        total_count = len(development_results)
        
        return {
            'success': success_count > 0,
            'completed_tasks': success_count,
            'total_tasks': total_count,
            'results': development_results
        }
    
    def _execute_evaluation_phase(self, context: ProjectContext) -> Dict[str, Any]:
        """Execute evaluation phase with quality assessment"""
        logger.info("=== EVALUATION PHASE ===")
        
        # Communication protocol
        self.communication_manager.send_message(
            "Orchestrator",
            "CodeEvaluationAgent",
            "Execute code quality validation and testing",
            list(context.generated_files.keys())
        )
        
        # Execute evaluation agent
        evaluation_result = self.evaluation_agent.execute(context)
        
        if evaluation_result['success']:
            assessment = evaluation_result['overall_assessment']
            self.communication_manager.send_message(
                "CodeEvaluationAgent",
                "Orchestrator",
                f"Evaluation completed - Score: {assessment.get('overall_score', 0)}/10",
                assessment
            )
        
        return evaluation_result
    
    def _create_success_result(self, context: ProjectContext, execution_time: float, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create successful execution result"""
        scheduler_status = self.task_scheduler.get_status()
        
        return {
            'success': True,
            'project_name': context.project_name,
            'execution_time': execution_time,
            'generated_files': dict(context.generated_files),
            'task_statistics': scheduler_status,
            'evaluation_result': evaluation_result,
            'output_directory': self.output_dir,
            'communication_history': self.communication_manager.message_history,
            'final_state': self.state_manager.get_all_states()
        }
    
    def _create_failure_result(self, error_message: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create failure result with diagnostics"""
        return {
            'success': False,
            'error': error_message,
            'details': details,
            'communication_history': self.communication_manager.message_history,
            'scheduler_status': self.task_scheduler.get_status(),
            'final_state': self.state_manager.get_all_states()
        }
    
    def get_detailed_logs(self) -> Dict[str, Any]:
        """Get comprehensive system logs for debugging and analysis"""
        return {
            'agent_thoughts': self.communication_protocol.get_all_thoughts(),
            'communication_history': self.communication_manager.message_history,
            'task_execution_log': self.task_scheduler.task_queue,
            'state_changes': self.state_manager.get_state_history(),
            'file_operations': getattr(self.filesystem_tools, 'operation_log', [])
        }
    
    def test_system_setup(self) -> bool:
        """Test all components for proper setup"""
        try:
            # Test LLM connection
            if not self.llm_interface.provider.test_connection():
                return False
                
            # Test filesystem
            test_file = os.path.join(self.output_dir, "test_file.txt")
            self.filesystem_tools.create_file("test_file.txt", "test content")
            if not os.path.exists(test_file):
                return False
            os.remove(test_file)
            
            logger.info("System setup test passed")
            return True
            
        except Exception as e:
            logger.error(f"System setup test failed: {str(e)}")
            return False