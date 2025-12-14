"""
COMP7103C Agent Communication Protocol - Detailed Logging for Agent Thoughts and Actions
Implements detailed logs of agent thoughts and actions for effective debugging and system analysis
"""
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages in agent communication"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    INFORMATION_SHARE = "information_share"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    COORDINATION_REQUEST = "coordination_request"
    FEEDBACK_REQUEST = "feedback_request"
    FEEDBACK_RESPONSE = "feedback_response"
    SYSTEM_NOTIFICATION = "system_notification"

class MessagePriority(Enum):
    """Priority levels for messages"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Message:
    """Communication message between agents"""
    id: str
    sender: str
    receiver: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False
    response_timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "requires_response": self.requires_response,
            "response_timeout": self.response_timeout,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            id=data["id"],
            sender=data["sender"],
            receiver=data["receiver"],
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data["priority"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            requires_response=data.get("requires_response", False),
            response_timeout=data.get("response_timeout"),
            metadata=data.get("metadata", {})
        )

@dataclass
class AgentThought:
    """Represents an agent's thought process"""
    agent_name: str
    thought_type: str  # "analysis", "planning", "decision", "reflection"
    content: str
    reasoning: str
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    related_messages: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "thought_type": self.thought_type,
            "content": self.content,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "related_messages": self.related_messages
        }

class CommunicationProtocol:
    """Advanced communication protocol for agent interaction"""
    
    def __init__(self):
        self.message_queue: List[Message] = []
        self.message_history: List[Message] = []
        self.thought_log: List[AgentThought] = []
        self.active_conversations: Dict[str, List[str]] = {}
        self.response_waiting: Dict[str, Message] = {}
        self.agent_statuses: Dict[str, Dict[str, Any]] = {}
        
        logger.info("CommunicationProtocol initialized")
    
    def generate_message_id(self) -> str:
        """Generate unique message ID"""
        return f"msg_{int(time.time() * 1000000)}"
    
    def send_message(self, sender: str, receiver: str, message_type: MessageType,
                    content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL,
                    requires_response: bool = False, response_timeout: int = None) -> str:
        """
        Send a message between agents
        
        Args:
            sender: Sender agent name
            receiver: Receiver agent name
            message_type: Type of message
            content: Message content
            priority: Message priority
            requires_response: Whether response is required
            response_timeout: Timeout for response in seconds
            
        Returns:
            Message ID
        """
        message = Message(
            id=self.generate_message_id(),
            sender=sender,
            receiver=receiver,
            message_type=message_type,
            priority=priority,
            content=content,
            requires_response=requires_response,
            response_timeout=response_timeout
        )
        
        # Add to queue (sorted by priority)
        self._insert_message_by_priority(message)
        
        # Track conversation
        conv_key = f"{sender}-{receiver}"
        if conv_key not in self.active_conversations:
            self.active_conversations[conv_key] = []
        self.active_conversations[conv_key].append(message.id)
        
        # Track response requirements
        if requires_response:
            self.response_waiting[message.id] = message
        
        logger.info(f"Message sent: {sender} -> {receiver} ({message_type.value})")
        return message.id
    
    def get_messages_for_agent(self, agent_name: str) -> List[Message]:
        """Get all pending messages for an agent"""
        messages = [msg for msg in self.message_queue if msg.receiver == agent_name]
        
        # Remove from queue and add to history
        for msg in messages:
            self.message_queue.remove(msg)
            self.message_history.append(msg)
        
        return messages
    
    def send_response(self, original_message_id: str, sender: str, content: Dict[str, Any]) -> str:
        """Send response to a message that requires response"""
        if original_message_id not in self.response_waiting:
            raise ValueError(f"No response required for message: {original_message_id}")
        
        original_message = self.response_waiting[original_message_id]
        
        response_message = Message(
            id=self.generate_message_id(),
            sender=sender,
            receiver=original_message.sender,
            message_type=MessageType.TASK_RESPONSE,
            priority=original_message.priority,
            content=content,
            metadata={"response_to": original_message_id}
        )
        
        self.message_history.append(response_message)
        del self.response_waiting[original_message_id]
        
        logger.info(f"Response sent: {sender} -> {original_message.sender}")
        return response_message.id
    
    def log_agent_thought(self, agent_name: str, thought_type: str, content: str,
                         reasoning: str, confidence: float = 0.8,
                         related_messages: List[str] = None) -> None:
        """
        Log an agent's thought process - COMP7103C Requirement
        
        Implements detailed logs of agent thoughts and actions for effective
        debugging and system analysis as specified in PDF hints & suggestions.
        
        Args:
            agent_name: Name of the agent having the thought
            thought_type: Type of thought (planning, analysis, decision, execution, etc.)
            content: The actual thought content
            reasoning: The reasoning behind this thought
            confidence: Confidence level (0.0 to 1.0)
            related_messages: IDs of related messages
        """
        thought = AgentThought(
            agent_name=agent_name,
            thought_type=thought_type,
            content=content,
            reasoning=reasoning,
            confidence=confidence,
            related_messages=related_messages or []
        )
        
        self.thought_log.append(thought)
        logger.info(f"Agent thought logged: {agent_name} - {thought_type}")
    
    def update_agent_status(self, agent_name: str, status: str, details: Dict[str, Any] = None):
        """Update agent status"""
        self.agent_statuses[agent_name] = {
            "status": status,
            "last_update": datetime.now(),
            "details": details or {}
        }
        
        # Broadcast status update
        self.send_message(
            sender=agent_name,
            receiver="ALL",
            message_type=MessageType.STATUS_UPDATE,
            content={"status": status, "details": details},
            priority=MessagePriority.LOW
        )
    
    def request_coordination(self, requester: str, task_description: str, 
                           required_agents: List[str]) -> str:
        """Request coordination between multiple agents"""
        coordination_id = f"coord_{int(time.time())}"
        
        content = {
            "coordination_id": coordination_id,
            "task_description": task_description,
            "required_agents": required_agents,
            "requester": requester
        }
        
        # Send coordination request to all required agents
        for agent in required_agents:
            self.send_message(
                sender=requester,
                receiver=agent,
                message_type=MessageType.COORDINATION_REQUEST,
                content=content,
                priority=MessagePriority.HIGH,
                requires_response=True,
                response_timeout=300
            )
        
        logger.info(f"Coordination requested: {coordination_id}")
        return coordination_id
    
    def request_feedback(self, requester: str, target_agent: str, 
                        feedback_type: str, content: Dict[str, Any]) -> str:
        """Request feedback from another agent"""
        message_id = self.send_message(
            sender=requester,
            receiver=target_agent,
            message_type=MessageType.FEEDBACK_REQUEST,
            content={
                "feedback_type": feedback_type,
                **content
            },
            priority=MessagePriority.NORMAL,
            requires_response=True,
            response_timeout=180
        )
        
        logger.info(f"Feedback requested: {requester} -> {target_agent}")
        return message_id
    
    def share_information(self, sender: str, information_type: str, data: Dict[str, Any],
                         target_agents: List[str] = None) -> List[str]:
        """Share information with other agents"""
        if target_agents is None:
            target_agents = ["ALL"]
        
        message_ids = []
        for target in target_agents:
            message_id = self.send_message(
                sender=sender,
                receiver=target,
                message_type=MessageType.INFORMATION_SHARE,
                content={
                    "information_type": information_type,
                    "data": data
                },
                priority=MessagePriority.NORMAL
            )
            message_ids.append(message_id)
        
        logger.info(f"Information shared: {sender} -> {target_agents}")
        return message_ids
    
    def report_error(self, agent_name: str, error_type: str, error_details: Dict[str, Any],
                    severity: str = "medium") -> str:
        """Report an error to the system"""
        priority_map = {
            "low": MessagePriority.LOW,
            "medium": MessagePriority.NORMAL,
            "high": MessagePriority.HIGH,
            "critical": MessagePriority.CRITICAL
        }
        
        message_id = self.send_message(
            sender=agent_name,
            receiver="SYSTEM",
            message_type=MessageType.ERROR_REPORT,
            content={
                "error_type": error_type,
                "error_details": error_details,
                "severity": severity
            },
            priority=priority_map.get(severity, MessagePriority.NORMAL)
        )
        
        logger.error(f"Error reported by {agent_name}: {error_type}")
        return message_id
    
    def get_conversation_history(self, agent1: str, agent2: str) -> List[Message]:
        """Get conversation history between two agents"""
        conv_key1 = f"{agent1}-{agent2}"
        conv_key2 = f"{agent2}-{agent1}"
        
        message_ids = []
        message_ids.extend(self.active_conversations.get(conv_key1, []))
        message_ids.extend(self.active_conversations.get(conv_key2, []))
        
        messages = [msg for msg in self.message_history if msg.id in message_ids]
        return sorted(messages, key=lambda x: x.timestamp)
    
    def get_agent_thoughts(self, agent_name: str = None, thought_type: str = None) -> List[AgentThought]:
        """Get agent thoughts filtered by agent and/or type"""
        thoughts = self.thought_log
        
        if agent_name:
            thoughts = [t for t in thoughts if t.agent_name == agent_name]
        
        if thought_type:
            thoughts = [t for t in thoughts if t.thought_type == thought_type]
        
        return sorted(thoughts, key=lambda x: x.timestamp)
    
    def get_pending_responses(self) -> Dict[str, Message]:
        """Get messages that are waiting for responses"""
        # Check for timeouts
        current_time = time.time()
        expired_messages = []
        
        for msg_id, msg in self.response_waiting.items():
            if msg.response_timeout:
                msg_time = msg.timestamp.timestamp()
                if current_time - msg_time > msg.response_timeout:
                    expired_messages.append(msg_id)
        
        # Remove expired messages
        for msg_id in expired_messages:
            del self.response_waiting[msg_id]
            logger.warning(f"Message response timeout: {msg_id}")
        
        return self.response_waiting.copy()
    
    def generate_communication_summary(self) -> Dict[str, Any]:
        """Generate summary of communication activity"""
        return {
            "total_messages": len(self.message_history),
            "pending_messages": len(self.message_queue),
            "active_conversations": len(self.active_conversations),
            "pending_responses": len(self.response_waiting),
            "total_thoughts": len(self.thought_log),
            "agent_count": len(self.agent_statuses),
            "message_types": {
                msg_type.value: len([m for m in self.message_history if m.message_type == msg_type])
                for msg_type in MessageType
            },
            "thought_types": {
                thought_type: len([t for t in self.thought_log if t.thought_type == thought_type])
                for thought_type in set([t.thought_type for t in self.thought_log])
            }
        }
    
    def _insert_message_by_priority(self, message: Message) -> None:
        """Insert message into queue based on priority"""
        priority_order = {
            MessagePriority.CRITICAL: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3
        }
        
        insert_index = 0
        for i, msg in enumerate(self.message_queue):
            if priority_order[message.priority] <= priority_order[msg.priority]:
                insert_index = i
                break
            insert_index = i + 1
        
        self.message_queue.insert(insert_index, message)
    
    def export_communication_log(self, filepath: str) -> bool:
        """Export communication log to JSON file"""
        try:
            export_data = {
                "message_history": [msg.to_dict() for msg in self.message_history],
                "thought_log": [thought.to_dict() for thought in self.thought_log],
                "agent_statuses": {
                    agent: {
                        **status,
                        "last_update": status["last_update"].isoformat()
                    }
                    for agent, status in self.agent_statuses.items()
                },
                "summary": self.generate_communication_summary(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Communication log exported to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export communication log: {str(e)}")
            return False
    
    def get_all_thoughts(self) -> List[Dict[str, Any]]:
        """Get all agent thoughts for analysis - COMP7103C requirement"""
        return [thought.to_dict() for thought in self.thought_log]
    
    def get_communication_summary(self) -> Dict[str, Any]:
        """Get comprehensive communication summary"""
        return {
            'total_messages': len(self.message_history),
            'active_conversations': len(self.active_conversations),
            'pending_responses': len(self.response_waiting),
            'total_thoughts': len(self.thought_log),
            'agent_activity': self.get_agent_activity_summary()
        }