"""
LLM Provider for Qwen integration using OpenAI-compatible API
"""
import json
import re
import time
import logging
from typing import Dict, List, Optional, Any, Union
from openai import OpenAI
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class LLMResponse(BaseModel):
    """Structured LLM response"""
    content: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    model: Optional[str] = None

class QwenProvider:
    """Qwen LLM Provider using OpenAI-compatible API"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qwen provider with configuration
        
        Args:
            config: Dictionary containing API configuration
        """
        self.config = config
        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["base_url"]
        )
        self.model = config["model"]
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 4096)
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout", 60)
        
    def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        """
        Generate response using Qwen model
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for the API call
        
        Returns:
            LLMResponse object containing the response
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    timeout=self.timeout,
                    **{k: v for k, v in kwargs.items() 
                       if k not in ["temperature", "max_tokens"]}
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    usage=response.usage.dict() if response.usage else None,
                    finish_reason=response.choices[0].finish_reason,
                    model=response.model
                )
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to get response after {self.max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from Qwen response
        
        Args:
            content: Response content from Qwen
            
        Returns:
            List of dictionaries with 'language' and 'code' keys
        """
        pattern = r'```(\w*)\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        code_blocks = []
        for match in matches:
            language = match[0] if match[0] else 'text'
            code = match[1].strip()
            code_blocks.append({
                'language': language,
                'code': code
            })
        
        return code_blocks
    
    def extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from Qwen response
        
        Args:
            content: Response content from Qwen
            
        Returns:
            Parsed JSON dictionary or None if not found/invalid
        """
        # Try to find JSON in code blocks first
        code_blocks = self.extract_code_blocks(content)
        for block in code_blocks:
            if block['language'].lower() in ['json', 'javascript']:
                try:
                    return json.loads(block['code'])
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON in the content directly
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return None
    
    def generate_structured_response(
        self, 
        messages: List[Dict[str, str]], 
        expected_format: str = "json",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured response with automatic parsing
        
        Args:
            messages: List of message dictionaries
            expected_format: Expected format ('json' or 'code')
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing parsed response
        """
        response = self.generate(messages, **kwargs)
        
        result = {
            "raw_content": response.content,
            "usage": response.usage,
            "finish_reason": response.finish_reason
        }
        
        if expected_format == "json":
            parsed_json = self.extract_json(response.content)
            result["parsed_data"] = parsed_json
            result["success"] = parsed_json is not None
            
        elif expected_format == "code":
            code_blocks = self.extract_code_blocks(response.content)
            result["code_blocks"] = code_blocks
            result["success"] = len(code_blocks) > 0
            
        return result
    
    def test_connection(self) -> bool:
        """
        Test connection to Qwen API
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_messages = [
                {"role": "user", "content": "Hello, please respond with 'Connection successful'"}
            ]
            response = self.generate(test_messages)
            return "successful" in response.content.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

class LLMInterface:
    """High-level interface for LLM operations"""
    
    def __init__(self, provider: QwenProvider):
        self.provider = provider
    
    def chat(self, user_message: str, system_message: Optional[str] = None) -> str:
        """Simple chat interface"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        
        response = self.provider.generate(messages)
        return response.content
    
    def generate_response(self, prompt: str, system_message: Optional[str] = None, 
                         max_tokens: int = 4000, temperature: float = 0.3) -> str:
        """Generate response with parameters"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = self.provider.generate(messages, max_tokens=max_tokens, temperature=temperature)
        return response.content
    
    def generate_code(self, prompt: str, language: str = "python") -> Optional[str]:
        """Generate code with specific formatting"""
        system_message = f"""You are an expert {language} developer. 
        Generate clean, production-ready code based on the user's requirements.
        IMPORTANT: 
        1. Only output the code inside markdown code blocks like this:
        ```{language}
        your code here
        ```
        2. Do not include explanations unless requested.
        3. Generate complete, functional code that can be directly saved to a file."""
        
        # First try structured response
        response = self.provider.generate_structured_response(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            expected_format="code"
        )
        
        if response["success"] and response.get("code_blocks"):
            for block in response["code_blocks"]:
                if block["language"].lower() == language.lower():
                    return block["code"]
            # Return first code block if language-specific not found
            if response["code_blocks"]:
                return response["code_blocks"][0]["code"]
        
        # Fallback: try direct generation
        try:
            direct_response = self.provider.generate([
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ])
            
            if direct_response and direct_response.content:
                # Extract code from direct response
                code_blocks = self.provider.extract_code_blocks(direct_response.content)
                if code_blocks:
                    for block in code_blocks:
                        if block["language"].lower() == language.lower():
                            return block["code"]
                    return code_blocks[0]["code"]
                
                # If no code blocks found, return the content directly (might be plain code)
                content = direct_response.content.strip()
                # Remove markdown code block markers if present
                if content.startswith(f"```{language}") and content.endswith("```"):
                    return content[len(f"```{language}"):-3].strip()
                elif content.startswith("```") and content.endswith("```"):
                    lines = content.split('\n')
                    return '\n'.join(lines[1:-1]) if len(lines) > 2 else content[3:-3]
                
                return content
        
        except Exception as e:
            logger.warning(f"Fallback code generation failed: {str(e)}")
        
        return None
    
    def generate_plan(self, requirements: str) -> Optional[Dict[str, Any]]:
        """Generate project plan in JSON format"""
        system_message = """You are a senior project planning agent.
        Analyze the requirements and create a detailed project plan in JSON format.
        The JSON should have the following structure:
        {
            "project_name": "string",
            "description": "string", 
            "tasks": [
                {
                    "id": "string",
                    "title": "string",
                    "description": "string",
                    "dependencies": ["string"],
                    "estimated_effort": "string",
                    "files_to_create": ["string"]
                }
            ],
            "architecture": {
                "components": ["string"],
                "technologies": ["string"]
            }
        }"""
        
        response = self.provider.generate_structured_response(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": requirements}
            ],
            expected_format="json"
        )
        
        return response["parsed_data"] if response["success"] else None
    
    def generate_plan_with_tools(self, enhanced_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate project plan with simulated tool usage for directory exploration"""
        
        # Simulate directory exploration and file discovery
        # In a real implementation, this would use actual tools
        simulated_directory_content = ["arxiv_data.json", "main.py", "config.py", "README.md"]
        
        # Simulate reading arxiv_data.json structure
        simulated_data_structure = {
            "papers": [{"id": "str", "title": "str", "authors": "list", "category": "str"}],
            "categories": [{"id": "str", "name": "str", "description": "str"}]
        }
        
        # Build enhanced system prompt with tool simulation results
        system_message = """You are a Project Planning Agent that has just explored the directory.

        DIRECTORY EXPLORATION RESULTS:
        Found files: arxiv_data.json, main.py, config.py, README.md
        
        ARXIV_DATA.JSON STRUCTURE ANALYSIS:
        {
            "papers": [
                {
                    "id": "2412.05001",
                    "title": "Paper Title", 
                    "authors": ["Author1", "Author2"],
                    "abstract": "Abstract text",
                    "category": "cs.AI",
                    "published": "2024-12-05",
                    "url": "https://arxiv.org/abs/..."
                }
            ],
            "categories": [
                {
                    "id": "cs.AI", 
                    "name": "Artificial Intelligence",
                    "description": "AI research papers"
                }
            ]
        }
        
        Based on this exploration, generate a specific task list for building an arXiv CS Daily webpage.

        Return EXACTLY this JSON structure:
        {
            "project_name": "arXiv CS Daily",
            "tasks": [
                {
                    "id": "task_1",
                    "title": "Read Data Structure",
                    "description": "Read and analyze arxiv_data.json to understand the paper data structure",
                    "files_to_create": [],
                    "dependencies": [],
                    "tools_required": ["read_file"]
                },
                {
                    "id": "task_2", 
                    "title": "Create HTML Structure",
                    "description": "Write index.html with navigation bar for categories (cs.AI, cs.AR, cs.CV, cs.LG, cs.CL) and card-style layout for papers",
                    "files_to_create": ["index.html"],
                    "dependencies": ["task_1"],
                    "tools_required": ["write_file"]
                },
                {
                    "id": "task_3",
                    "title": "Style with CSS", 
                    "description": "Write styles.css to beautify the page with modern responsive design",
                    "files_to_create": ["styles.css"],
                    "dependencies": ["task_2"],
                    "tools_required": ["write_file"]
                },
                {
                    "id": "task_4",
                    "title": "Add JavaScript Functionality",
                    "description": "Write script.js to load data from JSON and render dynamic paper lists, category navigation, and detail pages",
                    "files_to_create": ["script.js"],
                    "dependencies": ["task_2"],
                    "tools_required": ["write_file"]
                },
                {
                    "id": "task_5",
                    "title": "Create Tests",
                    "description": "Create test cases to verify all files are generated correctly and functionality works",
                    "files_to_create": ["test.html"],
                    "dependencies": ["task_4"],
                    "tools_required": ["write_file"]
                }
            ]
        }"""
        
        response = self.provider.generate_structured_response(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": enhanced_prompt}
            ],
            expected_format="json"
        )
        
        return response["parsed_data"] if response["success"] else None
    
    def generate_universal_plan(self, enhanced_prompt: str) -> Optional[Dict[str, Any]]:
        """Generate project plan for any type of requirement"""
        
        system_message = """You are an Expert Software Architect capable of planning ANY type of software project.

        Analyze the user requirement and generate a comprehensive project plan.
        
        You can handle:
        - Web Applications (HTML/CSS/JS, React, Vue, etc.)
        - Backend APIs (Python, Node.js, Java, etc.)  
        - Desktop Applications (Electron, Python, etc.)
        - Mobile Apps (React Native, Flutter, etc.)
        - Scripts and Automation
        - Documentation Projects
        - Any other software requirement

        Return EXACTLY this JSON structure:
        {
            "project_name": "descriptive name for the project",
            "project_type": "web|desktop|mobile|api|script|documentation|other",
            "description": "brief description of what will be built",
            "tasks": [
                {
                    "id": "task_1",
                    "title": "clear task title",
                    "description": "detailed description of what needs to be done",
                    "agent_type": "coder",
                    "files_to_create": ["specific filenames to create"],
                    "dependencies": [],
                    "tools_required": ["write_file"],
                    "estimated_effort": "small|medium|large"
                },
                {
                    "id": "task_2", 
                    "title": "Review and Validate",
                    "description": "Review all generated files and validate functionality",
                    "agent_type": "reviewer",
                    "files_to_create": [],
                    "dependencies": ["task_1"],
                    "tools_required": ["read_file"],
                    "estimated_effort": "small"
                }
            ],
            "architecture": {
                "components": ["main components of the system"],
                "technologies": ["technologies/languages to use"],
                "file_structure": ["all expected output files"]
            }
        }
        
        IMPORTANT GUIDELINES:
        - Choose appropriate technologies for the requirement
        - Break work into logical, implementable tasks
        - Always include a review task at the end
        - Be specific about files to create
        - Consider dependencies between tasks
        - Make tasks actionable for a coding agent"""
        
        response = self.provider.generate_structured_response(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": enhanced_prompt}
            ],
            expected_format="json"
        )
        
        return response["parsed_data"] if response["success"] else None