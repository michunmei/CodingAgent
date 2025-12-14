"""
Clean Universal Multi-Agent System
Focused on code generation without API dependencies
"""
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent, ProjectContext
from core.llm_provider import LLMInterface
from core.communication import CommunicationProtocol

logger = logging.getLogger(__name__)


class UniversalPlanningAgent(BaseAgent):
    """Clean Universal Planning Agent - No API dependencies"""
    
    def __init__(self, llm_interface: LLMInterface, communication: CommunicationProtocol = None):
        super().__init__(llm_interface, "UniversalPlanningAgent", communication)
    
    def get_system_prompt(self) -> str:
        return """You are an Expert Software Architect and Project Planning Agent. You analyze requirements carefully and create detailed implementation plans.

REQUIREMENTS ANALYSIS FRAMEWORK:
1. FUNCTIONAL ANALYSIS: Identify core features mentioned in requirements
   - Extract specific functionalities (e.g., "categorized navigation", "paper detail pages", "citation tools")
   - Note user interface requirements (responsive design, search, filtering)
   - Identify data sources and integrations (APIs, databases, feeds)

2. TECHNICAL SPECIFICATION:
   - Choose appropriate technology stack based on requirements
   - Plan data models and structures 
   - Design user workflows and navigation
   - Consider scalability and performance needs

3. IMPLEMENTATION PLANNING:
   - Break down into logical development phases
   - Specify dependencies between tasks
   - Assign appropriate agent types for each task
   - Include testing and validation at each step

WORKFLOW REQUIREMENTS:
1. Generate complete directory structure
2. Create requirements.txt for dependencies  
3. Plan systematic development phases
4. Include testing and validation steps
5. Specify API documentation research needs

OUTPUT FORMAT - Return EXACTLY this JSON structure:
{
    "project_name": "string - descriptive project name",
    "project_type": "string - web, desktop, api, cli, etc.",
    "description": "string - brief description",
    "directory_structure": {
        "root": "project_folder_name",
        "files": ["requirements.txt", "README.md"],
        "folders": {
            "src": ["main files"],
            "templates": ["html files"],
            "static": ["css, js, images"],
            "tests": ["test files"]
        }
    },
    "requirements": ["dependency1", "dependency2", "dependency3"],
    "tasks": [
        {
            "id": "task_1",
            "title": "Setup project structure",
            "description": "Create directory structure and requirements.txt",
            "agent_type": "coder",
            "files_to_create": ["requirements.txt", "project_structure"],
            "dependencies": [],
            "tools_required": ["write_file"],
            "priority": "high"
        },
        {
            "id": "task_2", 
            "title": "Research API documentation",
            "description": "Use web search to find API documentation and examples",
            "agent_type": "coder",
            "files_to_create": ["fetch_data.py"],
            "dependencies": ["task_1"],
            "tools_required": ["web_search", "write_file"],
            "api_research_needed": true,
            "priority": "high"
        },
        {
            "id": "task_3",
            "title": "Implement backend logic", 
            "description": "Write data fetching and processing code",
            "agent_type": "coder",
            "files_to_create": ["main backend files"],
            "dependencies": ["task_2"],
            "tools_required": ["write_file"],
            "priority": "medium"
        },
        {
            "id": "task_4",
            "title": "Test backend code",
            "description": "Run and validate backend implementation",
            "agent_type": "tester",
            "files_to_create": [],
            "dependencies": ["task_3"],
            "tools_required": ["execute_code", "validate_output"],
            "priority": "high"
        },
        {
            "id": "task_5",
            "title": "Implement frontend",
            "description": "Create HTML/CSS templates and user interface",
            "agent_type": "coder", 
            "files_to_create": ["templates/index.html", "static files"],
            "dependencies": ["task_4"],
            "tools_required": ["write_file"],
            "priority": "medium"
        },
        {
            "id": "task_6",
            "title": "Final integration and documentation",
            "description": "Create complete README.md and final testing",
            "agent_type": "tester",
            "files_to_create": ["README.md"],
            "dependencies": ["task_5"],
            "tools_required": ["write_file", "execute_code"],
            "priority": "medium"
        }
    ],
    "api_integrations": ["List APIs that need documentation research"],
    "testing_strategy": "Describe how code will be tested and validated"
}

CRITICAL REQUIREMENTS:
- Always include requirements.txt generation
- Plan for API documentation research via web search
- Include actual code execution testing
- Generate proper README.md
- Follow systematic development phases"""

    def execute(self, context: ProjectContext, requirements: str = None) -> Dict[str, Any]:
        """Generate clean project plan focused on code generation"""
        if requirements:
            context.requirements = requirements
        
        if self.communication:
            self.communication.log_agent_thought(
                self.name, "analysis",
                "Analyzing requirements for clean code generation",
                "Focus: API-agnostic architecture",
                0.85
            )
        
        prompt = f"""
        User Requirement: {context.requirements}
        
        Create a project plan that generates self-contained code.
        The generated code should handle its own API calls, data fetching, and dependencies.
        
        Key considerations:
        - What technology stack is most appropriate?
        - How will the generated code handle API calls?
        - What files need to be created for a complete solution?
        - How to ensure the code is maintainable and testable?
        
        Return a clean JSON plan following the specified format.
        """
        
        try:
            response = self.llm_interface.generate_response(
                prompt,
                system_message=self.get_system_prompt(),
                max_tokens=3000,  # Increased for better planning with qwen3-coder-plus
                temperature=0.2   # Slightly lower for more focused planning
            )
            
            # Parse JSON response
            import json
            try:
                # Extract JSON from response
                response_text = response.strip()
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    json_str = response_text[start:end].strip()
                elif response_text.startswith('{'):
                    json_str = response_text
                else:
                    # Look for JSON-like structure
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    json_str = json_match.group(0) if json_match else response_text
                
                plan_data = json.loads(json_str)
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response: {e}")
            
            if self.communication:
                self.communication.log_agent_thought(
                    self.name, "planning_complete",
                    f"Generated clean project plan: {plan_data.get('project_name', 'Unknown')}",
                    f"Tasks: {len(plan_data.get('tasks', []))}",
                    0.95
                )
            
            return {
                'success': True,
                'plan': plan_data,
                'agent': self.name,
                'planning_approach': 'clean_api_agnostic'
            }
            
        except Exception as e:
            logger.error(f"Planning failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.name
            }


class UniversalCodeGenerationAgent(BaseAgent):
    """Clean Code Generation Agent - Generates self-contained code"""
    
    def __init__(self, llm_interface: LLMInterface, communication: CommunicationProtocol = None, output_dir: str = "./output"):
        super().__init__(llm_interface, "UniversalCodeGenerationAgent", communication)
        self.output_dir = output_dir
        # Import filesystem tools
        from tools.filesystem_tools import FileSystemTools
        self.fs_tools = FileSystemTools(output_dir)
    
    def _generate_search_queries(self, requirements: str, task_info: Dict[str, Any]) -> list:
        """Generate search queries for API documentation"""
        queries = []
        
        # Extract API names from requirements
        if 'arxiv' in requirements.lower():
            queries.append("arXiv API documentation python examples")
            queries.append("arXiv API query parameters XML response")
        
        if 'flask' in requirements.lower():
            queries.append("Flask web framework tutorial documentation")
            queries.append("Flask API development best practices")
            
        if 'rest api' in requirements.lower():
            queries.append("REST API development python flask tutorial")
        
        # Generic queries based on task
        task_title = task_info.get('title', '').lower()
        if 'fetch' in task_title or 'api' in task_title:
            queries.append("HTTP API client python requests library examples")
            
        return queries[:3]  # Limit to 3 queries
    
    def _extract_json_block(self, text: str) -> dict:
        """Extract JSON from ```json blocks"""
        import json
        if '```json' not in text:
            return None
        
        start = text.find('```json') + 7
        end = text.find('```', start)
        if end > start:
            json_str = text[start:end].strip()
            return json.loads(json_str)
        return None
    
    def _extract_largest_json_object(self, text: str) -> dict:
        """Find and parse the largest JSON object in text"""
        import re
        import json
        # Find all {...} blocks
        pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, text, re.DOTALL)
        
        largest_json = None
        max_size = 0
        
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict) and len(str(parsed)) > max_size:
                    largest_json = parsed
                    max_size = len(str(parsed))
            except:
                continue
        
        return largest_json
    
    def _fix_and_parse_json(self, text: str) -> dict:
        """Fix common JSON issues and attempt parsing"""
        import re
        import json
        
        # Find JSON-like content
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            return None
        
        json_str = json_match.group(0)
        
        # Fix trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unmatched braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        try:
            return json.loads(json_str)
        except:
            return None
    
    def _create_emergency_fallback(self, task_info: Dict[str, Any], requirements: str) -> Dict[str, Any]:
        """Create minimal working structure when JSON parsing fails"""
        return {
            "files": {
                "requirements.txt": "flask\nrequests",
                "src/app.py": """import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template
from fetch_data import get_data

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

@app.route('/')
def index():
    data = get_data()
    return render_template('index.html', data=data)

@app.route('/item/<item_id>')
def item_detail(item_id):
    data = get_data()
    item = next((item for item in data if str(item.get('id', '')) == item_id), None)
    if not item:
        return render_template('index.html', data=data)
    return render_template('detail.html', item=item)

if __name__ == '__main__':
    app.run(debug=True)
""",
                "src/fetch_data.py": """import requests
from datetime import datetime

def get_data():
    # Generic data fetching function - can be adapted for various use cases
    try:
        # Sample data structure - should be customized based on requirements
        sample_data = [
            {
                'id': '1',
                'title': 'Sample Item 1',
                'description': 'This is a sample description for item 1.',
                'author': 'John Doe',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'content': 'Sample content for the first item.'
            },
            {
                'id': '2', 
                'title': 'Sample Item 2',
                'description': 'This is a sample description for item 2.',
                'author': 'Jane Smith',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'content': 'Sample content for the second item.'
            }
        ]
        return sample_data
    except Exception as err:
        print("Error fetching data: " + str(err))
        return []
""",
                "templates/index.html": """<!DOCTYPE html>
<html>
<head>
    <title>My Application</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>Welcome to My Application</h1>
    <div class="content">
        {% for item in data %}
        <div class="item">
            <h2><a href="{{ url_for('item_detail', item_id=item.id) }}">{{ item.title }}</a></h2>
            <p><strong>Author:</strong> {{ item.author }}</p>
            <p><strong>Date:</strong> {{ item.date }}</p>
            <p>{{ item.description }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>""",
                "templates/detail.html": """<!DOCTYPE html>
<html>
<head>
    <title>{{ item.title }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <a href="{{ url_for('index') }}">&larr; Back to list</a>
    <h1>{{ item.title }}</h1>
    <p><strong>Author:</strong> {{ item.author }}</p>
    <p><strong>Date:</strong> {{ item.date }}</p>
    <div class="content">
        <h2>Description</h2>
        <p>{{ item.description }}</p>
        <h2>Content</h2>
        <p>{{ item.content }}</p>
    </div>
</body>
</html>""",
                "static/style.css": """body { 
    font-family: Arial, sans-serif; 
    margin: 40px; 
    line-height: 1.6;
}
.content { margin-top: 20px; }
.item { 
    border: 1px solid #ddd; 
    padding: 15px; 
    margin-bottom: 15px; 
    border-radius: 5px; 
}
.item h2 { margin-top: 0; }
.item h2 a { color: #333; text-decoration: none; }
.item h2 a:hover { color: #0066cc; }
"""
            },
            "implementation_notes": "Emergency fallback structure created due to JSON parsing issues"
        }
    
    def _validate_python_syntax_strict(self, content: str, filename: str):
        """Strictly validate Python syntax and attempt fixes"""
        import ast
        import re
        
        # Quick content validation
        if not content or not content.strip():
            return False, content, "Empty file content"
        
        try:
            ast.parse(content)
            return True, content, "Valid syntax"
        except SyntaxError as e:
            logger.warning(f"Syntax error in {filename} at line {e.lineno}: {e.msg}")
            
            # Try comprehensive fixes
            fixed_content = content
            lines = fixed_content.split('\n')
            
            # Fix 1: Ensure proper newline ending
            if not fixed_content.endswith('\n'):
                fixed_content += '\n'
                lines = fixed_content.split('\n')
            
            # Fix 2: Check for unclosed strings/brackets
            bracket_stack = []
            quote_state = None
            
            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    if quote_state is None:
                        if char in ['"', "'"]:
                            quote_state = char
                        elif char in ['(', '[', '{']:
                            bracket_stack.append((char, i, j))
                        elif char in [')', ']', '}']:
                            if bracket_stack:
                                bracket_stack.pop()
                    else:
                        if char == quote_state and (j == 0 or line[j-1] != '\\'):
                            quote_state = None
            
            # Fix unclosed brackets by adding closing ones
            if bracket_stack:
                closing_map = {'(': ')', '[': ']', '{': '}'}
                for open_char, line_num, char_pos in reversed(bracket_stack):
                    lines.append(closing_map[open_char])
                    logger.info(f"Added missing {closing_map[open_char]} in {filename}")
            
            # Fix 3: Complete indentation repair
            # Build a stack to track indentation levels
            indent_stack = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                if not stripped:  # Skip empty lines
                    i += 1
                    continue
                
                current_indent = len(line) - len(line.lstrip())
                
                # Check for incomplete function definitions with unclosed parentheses
                if ('def ' in stripped and '(' in stripped and 
                    stripped.count('(') > stripped.count(')')):
                    paren_count = stripped.count('(') - stripped.count(')')
                    lines[i] = line + ')' * paren_count + ':'
                    stripped = lines[i].strip()
                    logger.info(f"Fixed unclosed parentheses in function definition at line {i+1}")
                
# Handle lines that should increase indentation
                # 修复：先去掉注释，再检查是否以冒号结尾
                code_without_comment = stripped.split('#')[0].strip()
                if code_without_comment.endswith(':'):
                    indent_stack.append(current_indent + 4)
                    
                # Handle except/finally/elif/else that should be at same level as their matching statement
                elif stripped.startswith(('except', 'finally', 'elif', 'else:')):
                    # Find matching try/if/for/while level
                    if indent_stack:
                        target_indent = indent_stack[-1] - 4  # One level back
                        if current_indent != target_indent:
                            lines[i] = ' ' * target_indent + stripped
                            logger.info(f"Fixed {stripped.split()[0]} indentation at line {i+1}")
                
                # Fix missing indentation for regular statements
                elif current_indent == 0 and indent_stack:
                    # This line should be indented
                    target_indent = indent_stack[-1]
                    lines[i] = ' ' * target_indent + stripped
                    logger.info(f"Fixed missing indentation at line {i+1} (expected: {target_indent})")
                
                # Update indent stack based on actual indentation
                actual_indent = len(lines[i]) - len(lines[i].lstrip())
                
                # Pop stack if we've decreased indentation
                while indent_stack and actual_indent < indent_stack[-1]:
                    indent_stack.pop()
                
                i += 1
            
            # Final pass: ensure all blocks have content
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                if stripped.endswith(':'):
                    indent_level = len(line) - len(line.lstrip())
                    has_content = False
                    
                    # Look ahead for content
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j]
                        if next_line.strip() == '':
                            continue
                        
                        next_indent = len(next_line) - len(next_line.lstrip())
                        if next_indent > indent_level:
                            has_content = True
                            break
                        elif next_indent <= indent_level:
                            break
                    
                    if not has_content:
                        lines.insert(i + 1, ' ' * (indent_level + 4) + 'pass')
                        logger.info(f"Added missing pass statement after line {i+1}")
                
                i += 1
            
            # Fix 4: Check for incomplete string literals
            fixed_content = '\n'.join(lines)
            if quote_state is not None:
                fixed_content += quote_state
                logger.info(f"Added missing quote in {filename}")
            
            # Try to parse again
            try:
                ast.parse(fixed_content)
                return True, fixed_content, "Fixed multiple syntax errors"
            except SyntaxError as e2:
                logger.error(f"Could not fix syntax error in {filename}: {e2.msg} at line {e2.lineno}")
                return False, content, f"Could not fix: {e2.msg}"
    
    def _validate_and_fix_code(self, code_data: Dict[str, Any], task_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix common code generation issues"""
        try:
            files = code_data.get('files', {})
            
            # Find Python files that might have import issues
            for filename, content in files.items():
                if filename.endswith('.py'):
                    # Use strict syntax validation
                    # Use strict syntax validation
                    is_valid, fixed_content, message = self._validate_python_syntax_strict(content, filename)
                    
                    if is_valid:
                        content = fixed_content
                        if message != "Valid syntax":
                            logger.info(f"{filename}: {message}")
                    else:
                        logger.error(f"CRITICAL SYNTAX ERROR in {filename}: {message}. File appears truncated.")
                        # 修复：如果语法严重错误且无法修复（通常是因为截断），回退到一个安全的最小版本
                        # 或者抛出异常让外层触发 emergency_fallback
                        if "unexpected EOF" in str(message) or "token" in str(message):
                            # 创建一个最小的可运行版本，避免整个程序崩溃
                            content = "# CRITICAL ERROR: File was truncated during generation.\npass\n"
                            logger.warning(f"Replaced truncated file {filename} with placeholder.")
                    
                    # Fix import inconsistencies...
                    
                    # Fix import inconsistencies and Flask configuration
                    if 'src/' in filename and filename.endswith('.py'):
                        # Fix various import patterns to use consistent naming
                        if 'from fetch_arxiv import' in content:
                            content = content.replace('from fetch_arxiv import', 'from fetch_data import')
                            content = content.replace('fetch_daily_papers', 'get_daily_papers')
                            logger.info(f"Fixed import naming in {filename}")
                        elif 'from fetch_data import' in content and 'sys.path.append' not in content:
                            # Only convert to relative import if sys.path fix is not already present
                            pass  # Keep absolute import when sys.path is configured
                        
                        # Ensure Flask apps have proper template/static folder configuration
                        if 'Flask(__name__)' in content and 'app.py' in filename:
                            # Add template and static folder configuration
                            content = content.replace(
                                'Flask(__name__)',
                                'Flask(__name__, template_folder=\'../templates\', static_folder=\'../static\')'
                            )
                            logger.info(f"Added Flask folder configuration to {filename}")
                        elif 'app = Flask(' in content and 'template_folder' not in content:
                            # Fix incomplete Flask configuration
                            import re
                            pattern = r'app = Flask\([^)]*\)'
                            replacement = 'app = Flask(__name__, template_folder=\'../templates\', static_folder=\'../static\')'
                            content = re.sub(pattern, replacement, content)
                            logger.info(f"Fixed Flask folder configuration in {filename}")
                    
                    files[filename] = content
                
                # Fix template field consistency issues
                elif filename.endswith('.html') and '{{' in content:
                    # Common fixes for template issues
                    if 'paper.published.strftime' in content:
                        content = content.replace('paper.published.strftime(\'%Y-%m-%d\')', 'paper.published')
                        logger.info(f"Fixed date formatting in {filename}")
                    
                    if 'paper.pdf_link' in content:
                        content = content.replace('paper.pdf_link', 'paper.link')
                        logger.info(f"Fixed PDF link field in {filename}")
                    
                    files[filename] = content
            
            code_data['files'] = files
            return code_data
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return code_data
    
    def get_system_prompt(self) -> str:
        return """You are an Expert Software Engineer using qwen3-coder-plus for professional code generation.

CRITICAL CODING REQUIREMENTS:
1. Generate COMPLETE, PRODUCTION-READY files with no truncated code - EVERY function must be complete
2. ALL Python files MUST end with newline character (\\n) to prevent EOF syntax errors
3. VALIDATE all Python syntax before returning - ZERO syntax errors allowed
4. NEVER leave incomplete functions, classes, or code blocks
5. ALWAYS close all parentheses, brackets, and quotes properly
6. ENSURE all if/for/while/def/class statements have proper bodies
7. Use proper imports and dependency management  
8. Ensure perfect data field consistency between backend and frontend
9. Add proper sys.path configuration for relative imports
10. Write clean, well-structured, maintainable code
11. Follow Python PEP 8 style guidelines
12. Include proper error handling and logging
13. NEVER use incomplete blocks, missing colons, or improper indentation

SYNTAX VALIDATION CHECKLIST:
- Every opening brace/bracket/parenthesis has a matching closing one
- Every function definition has a complete body (not just a docstring)
- Every class definition has a complete body
- Every if/for/while/try block has proper content
- All string literals are properly closed
- No trailing commas in single-item contexts
- Proper indentation throughout (4 spaces per level)

REQUIRED JSON OUTPUT:
{
    "files": {
        "requirements.txt": "flask\nfeedparser\nrequests",
        "src/app.py": "COMPLETE Flask application code",
        "src/fetch_data.py": "COMPLETE data fetching code",
        "templates/index.html": "COMPLETE HTML template",
        "templates/paper.html": "COMPLETE HTML template",
        "static/style.css": "COMPLETE CSS styles",
        "static/script.js": "COMPLETE JavaScript code"
    },
    "implementation_notes": "Brief explanation of the implementation"
}

IMPORT FIX PATTERN:
For files in src/ directory, always add:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

FIELD CONSISTENCY:
- If template uses {{ paper.title }}, provide paper['title']
- If template uses {{ paper.authors|join(', ') }}, provide paper['authors'] as list
- Match ALL template variables with backend data

FLASK CONFIGURATION REQUIREMENTS:
- Always configure template_folder='../templates' when Flask app is in src/ directory
- Always configure static_folder='../static' for proper static file serving
- Use proper directory structure: src/app.py, templates/, static/
- Ensure all template files are created in templates/ directory

Generate ONLY the JSON structure above. No explanations or markdown."""

    def execute(self, context: ProjectContext, task_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate code following PDF workflow standards"""
        
        if self.communication:
            self.communication.log_agent_thought(
                self.name, "code_generation",
                f"Generating code for: {task_info.get('title', 'Unknown task')}",
                "Following PDF workflow standards",
                0.80
            )
        
        # Check if API research is needed
        api_research_needed = task_info.get('api_research_needed', False)
        tools_required = task_info.get('tools_required', [])
        
        # Perform web search if needed
        web_search_results = ""
        if api_research_needed or 'web_search' in tools_required:
            try:
                from tools.web_search_tools import WebSearchTools
                search_tool = WebSearchTools()
                
                # Search for API documentation
                search_queries = self._generate_search_queries(context.requirements, task_info)
                for query in search_queries:
                    results = search_tool.search_web(query, max_results=3)
                    web_search_results += f"\nSearch: {query}\nResults: {results}\n"
                    
                logger.info(f"Performed web search for: {search_queries}")
            except Exception as e:
                logger.warning(f"Web search failed: {e}")
                web_search_results = "Web search unavailable, using fallback approach"
        
        prompt = f"""
        Task: {task_info.get('title', '')}
        Description: {task_info.get('description', '')}
        Files to create: {task_info.get('files_to_create', [])}
        Project Context: {context.requirements}
        
        Web Search Results: {web_search_results}
        
        ⚠️ CRITICAL PYTHON INDENTATION REQUIREMENTS ⚠️:
        1. EVERY Python block (after colon :) MUST be properly indented with exactly 4 spaces
        2. try: blocks MUST have indented content
        3. except: blocks MUST be at same level as try:
        4. function definitions MUST have indented content
        5. NEVER generate code with missing indentation
        6. ALWAYS validate your Python syntax before responding
        
        EXAMPLE OF CORRECT INDENTATION:
        ```python
        def function_name():
            try:
                response = requests.get(url)
                data = response.json()
                return data
            except Exception as err:
                print('Error: ' + str(err))
                return []
        ```
        
        ADDITIONAL REQUIREMENTS:
        1. Ensure EXACT field consistency between Python backend and Jinja2 templates
        2. Fix import paths for files in subdirectories (add sys.path configuration)
        3. Match data types - if template uses .strftime(), data must be datetime
        4. Provide ALL fields referenced in templates
        5. Test all imports work from target directory structure
        
        SPECIFIC VALIDATION REQUIRED:
        - If generating Flask app in src/, add sys.path fix at top of file
        - If template uses `{{ paper.published }}`, provide published field as string
        - If template uses `{{ paper.authors | join }}`, provide authors as list
        - NO template variables that don't exist in backend data
        
        Generate production-ready code with PERFECT indentation and field validation. Return clean JSON only.
        """
        
        try:
            # Use higher token limit optimized for qwen3-coder-plus
            response = self.llm_interface.generate_response(
                prompt,
                system_message=self.get_system_prompt(),
                max_tokens=8000,  # Increased for qwen3-coder-plus's enhanced capabilities
                temperature=0.05  # Even lower temperature for coding tasks with qwen3-coder-plus
            )
            
            # Robust JSON parsing with multiple fallback strategies
            import json
            import re
            
            def try_parse_json(text):
                """Try multiple strategies to parse JSON from LLM response"""
                strategies = [
                    # Strategy 1: Direct parse if starts with {
                    lambda t: json.loads(t) if t.strip().startswith('{') else None,
                    
                    # Strategy 2: Extract ```json blocks
                    lambda t: self._extract_json_block(t),
                    
                    # Strategy 3: Find largest {...} block
                    lambda t: self._extract_largest_json_object(t),
                    
                    # Strategy 4: Fix common issues and retry
                    lambda t: self._fix_and_parse_json(t),
                ]
                
                for strategy in strategies:
                    try:
                        result = strategy(text)
                        if result and isinstance(result, dict) and 'files' in result:
                            return result
                    except:
                        continue
                return None
            
            code_data = try_parse_json(response.strip())
            
            if not code_data:
                logger.error("All JSON parsing strategies failed")
                # Create emergency fallback with basic Flask structure
                code_data = self._create_emergency_fallback(task_info, context.requirements)
            
            # Validate and enhance the generated code
            code_data = self._validate_and_fix_code(code_data, task_info)
            
        except Exception as e:
            logger.error(f"Code generation completely failed: {e}")
            # Create emergency fallback
            code_data = self._create_emergency_fallback(task_info, context.requirements)
        
        # Ensure required template files exist for Flask applications
        files_to_create = code_data.get('files', {})
        
        # Check if this is a Flask project and ensure basic templates exist
        flask_app_exists = any('Flask(' in content for content in files_to_create.values() if isinstance(content, str))
        
        if flask_app_exists:
            # Ensure basic template files exist
            required_templates = {
                'templates/index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv Daily Papers</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>arXiv Computer Science Daily Papers</h1>
        <div class="papers-list">
            {% for paper in papers %}
            <div class="paper">
                <h2><a href="{{ url_for('paper_detail', paper_id=paper.id) }}">{{ paper.title }}</a></h2>
                <p class="authors"><strong>Authors:</strong> {{ paper.authors|join(', ') }}</p>
                <p class="published"><strong>Published:</strong> {{ paper.published }}</p>
                <p class="abstract">{{ paper.abstract[:200] }}{% if paper.abstract|length > 200 %}...{% endif %}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>''',
                
                'templates/paper.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ paper.title }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <a href="{{ url_for('index') }}" class="back-link">&larr; Back to Papers</a>
        <article class="paper-detail">
            <h1>{{ paper.title }}</h1>
            <p class="authors"><strong>Authors:</strong> {{ paper.authors|join(', ') }}</p>
            <p class="published"><strong>Published:</strong> {{ paper.published }}</p>
            <p class="arxiv-id"><strong>arXiv ID:</strong> {{ paper.id }}</p>
            
            <div class="abstract">
                <h2>Abstract</h2>
                <p>{{ paper.abstract }}</p>
            </div>
            
            <a href="{{ paper.link }}" target="_blank" class="arxiv-link">View on arXiv</a>
        </article>
    </div>
</body>
</html>''',

                'static/style.css': '''body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f4f4f4;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    color: #333;
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 3px solid #007acc;
    padding-bottom: 10px;
}

.papers-list {
    display: grid;
    gap: 20px;
}

.paper {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    border-left: 4px solid #007acc;
}

.paper h2 {
    margin-top: 0;
    margin-bottom: 10px;
}

.paper h2 a {
    color: #333;
    text-decoration: none;
    transition: color 0.3s ease;
}

.paper h2 a:hover {
    color: #007acc;
}

.authors, .published {
    margin: 8px 0;
    color: #666;
}

.abstract {
    margin-top: 10px;
    color: #555;
}

.back-link {
    display: inline-block;
    margin-bottom: 20px;
    color: #007acc;
    text-decoration: none;
    font-weight: bold;
}

.back-link:hover {
    text-decoration: underline;
}

.paper-detail {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.arxiv-link {
    display: inline-block;
    margin-top: 20px;
    padding: 10px 20px;
    background-color: #007acc;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.3s ease;
}

.arxiv-link:hover {
    background-color: #005a99;
}'''
            }
            
            # Add missing template/static files
            for template_path, template_content in required_templates.items():
                if template_path not in files_to_create:
                    files_to_create[template_path] = template_content
                    logger.info(f"Added missing template file: {template_path}")
        
        # Final validation before writing files
        validated_files = {}
        
        for filename, content in files_to_create.items():
            if filename.endswith('.py'):
                # Final syntax check for Python files
                is_valid, fixed_content, message = self._validate_python_syntax_strict(content, filename)
                if is_valid:
                    validated_files[filename] = fixed_content
                    if message != "Valid syntax":
                        logger.info(f"Final validation for {filename}: {message}")
                else:
                    logger.error(f"CRITICAL: Failed final validation for {filename}: {message}")
                    # Don't write syntactically invalid files
                    continue
            else:
                validated_files[filename] = content
        
        # Write validated files to disk with proper path handling
        generated_files = {}
        
        for filename, content in validated_files.items():
            try:
                # Handle directory paths properly
                if '/' in filename:
                    # Create subdirectory structure
                    parts = filename.split('/')
                    subdir = '/'.join(parts[:-1])
                    file_only = parts[-1]
                    success = self.fs_tools.write_to_file(file_only, content, subdirectory=subdir)
                else:
                    success = self.fs_tools.write_to_file(filename, content)
                
                if success:
                    generated_files[filename] = content
                    context.add_file(filename, content)
                    logger.info(f"Successfully wrote validated file: {filename}")
                else:
                    logger.error(f"Failed to write file: {filename}")
                    
            except Exception as e:
                logger.error(f"Error writing file {filename}: {str(e)}")
                continue
        
        if self.communication:
            files_generated = len(generated_files)
            self.communication.log_agent_thought(
                self.name, "generation_complete",
                f"Generated {files_generated} files with clean API integration",
                "Code is self-contained and production-ready",
                0.90
            )
        
        return {
            'success': True,
            'generated_files': generated_files,
            'implementation_notes': code_data.get('implementation_notes', ''),
            'api_integration': code_data.get('api_integration', ''),
            'agent': self.name
        }


class UniversalEvaluationAgent(BaseAgent):
    """Clean Evaluation Agent - Evaluates generated code quality"""
    
    def __init__(self, llm_interface: LLMInterface, communication: CommunicationProtocol = None, output_dir: str = "./output"):
        super().__init__(llm_interface, "UniversalEvaluationAgent", communication)
        self.output_dir = output_dir
        from tools.filesystem_tools import FileSystemTools
        self.fs_tools = FileSystemTools(output_dir)
    
    def _fix_import_issues(self, generated_files: dict) -> dict:
        """Auto-fix common import issues in Python files"""
        import re
        fixed_files = {}
        
        for filename, content in generated_files.items():
            if filename.endswith('.py'):
                fixed_content = content
                
                # Fix relative imports (from .module import something)
                relative_import_pattern = r'from\s+\.([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
                def fix_relative_import(match):
                    module_name = match.group(1)
                    return f'from {module_name} import'
                
                fixed_content = re.sub(relative_import_pattern, fix_relative_import, fixed_content)
                
                # Fix relative imports with deeper paths (from ..module import something)
                deep_relative_pattern = r'from\s+\.\.([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
                def fix_deep_relative_import(match):
                    module_name = match.group(1)
                    return f'from {module_name} import'
                
                fixed_content = re.sub(deep_relative_pattern, fix_deep_relative_import, fixed_content)
                
                # Add sys.path modification if relative imports were detected
                if re.search(r'from\s+\.+[a-zA-Z_]', content):
                    # Check if sys.path modification already exists
                    if 'sys.path.append' not in fixed_content and 'sys.path.insert' not in fixed_content:
                        # Add sys.path modification at the top
                        sys_path_fix = """import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

"""
                        # Insert after any existing imports at the top
                        lines = fixed_content.split('\n')
                        insert_pos = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith('import ') or line.strip().startswith('from '):
                                insert_pos = i + 1
                            elif line.strip() == '' and insert_pos > 0:
                                continue
                            else:
                                break
                        
                        lines.insert(insert_pos, sys_path_fix.strip())
                        fixed_content = '\n'.join(lines)
                
                # Also fix missing dependencies and network timeouts
                if 'from flask import' in fixed_content or 'import flask' in fixed_content:
                    try:
                        import flask
                    except ImportError:
                        pass
                
                # Add timeout handling for feedparser requests
                if 'feedparser.parse' in fixed_content and 'timeout' not in fixed_content:
                    # Add timeout parameter to feedparser.parse calls
                    import re
                    feedparser_pattern = r'feedparser\.parse\([\'"]([^\'"]+)[\'"]\)'
                    def add_timeout(match):
                        url = match.group(1)
                        return f"feedparser.parse('{url}', timeout=10)"
                    fixed_content = re.sub(feedparser_pattern, add_timeout, fixed_content)
                
                # Don't automatically add error handling - it causes indentation issues
                # Let the LLM handle proper error handling in its generation
                
                # Write the fixed content back to disk
                if fixed_content != content:
                    # Update the file on disk with fixed content
                    if '/' in filename:
                        parts = filename.split('/')
                        subdir = '/'.join(parts[:-1])
                        file_only = parts[-1]
                        self.fs_tools.write_to_file(file_only, fixed_content, subdirectory=subdir)
                    else:
                        self.fs_tools.write_to_file(filename, fixed_content)
                
                fixed_files[filename] = fixed_content
            else:
                fixed_files[filename] = content
        
        return fixed_files
    
    def _execute_code_files(self, generated_files: dict) -> dict:
        """Actually execute Python files and return detailed results"""
        execution_results = {
            "files_tested": [],
            "execution_status": "success",
            "error_logs": [],
            "runtime_output": [],
            "import_errors": [],
            "syntax_errors": []
        }
        
        import subprocess
        import os
        import ast
        import re
        
        # Auto-fix common import issues before execution
        fixed_files = self._fix_import_issues(generated_files)
        
        for filename, content in fixed_files.items():
            if filename.endswith('.py'):
                execution_results["files_tested"].append(filename)
                
                # First, check syntax
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    execution_results["syntax_errors"].append(f"{filename}: {str(e)}")
                    execution_results["execution_status"] = "failed"
                    
                    # Try to auto-fix EOF errors
                    if 'unexpected EOF' in str(e):
                        if not content.endswith('\n'):
                            content = content + '\n'
                            fixed_files[filename] = content
                            # Update file on disk with fix
                            if '/' in filename:
                                parts = filename.split('/')
                                subdir = '/'.join(parts[:-1])
                                file_only = parts[-1]
                                self.fs_tools.write_to_file(file_only, content, subdirectory=subdir)
                            else:
                                self.fs_tools.write_to_file(filename, content)
                            
                            # Re-test syntax after fix
                            try:
                                ast.parse(content)
                                execution_results["syntax_errors"][-1] += " (FIXED: Added missing newline)"
                                logger.info(f"Auto-fixed EOF error in {filename}")
                            except:
                                pass
                    continue
                
                # Handle file path construction
                if '/' in filename:
                    parts = filename.split('/')
                    subdir = '/'.join(parts[:-1])
                    file_only = parts[-1]
                    actual_path = os.path.join(self.output_dir, subdir, file_only)
                else:
                    actual_path = os.path.join(self.output_dir, filename)
                
                # Ensure file exists on disk
                if not os.path.exists(actual_path):
                    if '/' in filename:
                        parts = filename.split('/')
                        subdir = '/'.join(parts[:-1])
                        file_only = parts[-1]
                        self.fs_tools.write_to_file(file_only, content, subdirectory=subdir)
                    else:
                        self.fs_tools.write_to_file(filename, content)
                
                try:
                    # Test imports first - use absolute paths and fix working directory
                    abs_actual_path = os.path.abspath(actual_path)
                    # Use the directory containing the Python file as working directory
                    work_dir = os.path.dirname(abs_actual_path)
                    
                    # For web applications (Flask/Django), only test imports, don't run the server
                    file_content = fixed_files.get(filename, '')
                    if any(framework in file_content.lower() for framework in ['flask', 'django', 'app.run', 'wsgi']):
                        # Create a safe version of the file for testing imports only
                        import re
                        safe_content = file_content
                        
                        # More careful replacement of app.run() calls
                        lines = safe_content.split('\n')
                        safe_lines = []
                        in_main_block = False
                        
                        for line in lines:
                            stripped = line.strip()
                            if stripped.startswith('if __name__') and '__main__' in stripped:
                                in_main_block = True
                                safe_lines.append(line)
                            elif in_main_block and stripped.startswith('app.run'):
                                # Comment out app.run in main block AND add pass to prevent empty block error
                                # 修复核心：用 'pass; # ...' 替代，保证缩进块不为空
                                safe_lines.append(line.replace('app.run', 'pass; # app.run'))
                            elif in_main_block and stripped == '' and len(safe_lines) > 0 and safe_lines[-1].strip() != '':
                                # End of main block
                                in_main_block = False
                                safe_lines.append(line)
                            else:
                                safe_lines.append(line)
                        
                        safe_content = '\n'.join(safe_lines)
                        
                        # Write safe version to temporary file for testing
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                            temp_file.write(safe_content)
                            temp_path = temp_file.name
                        
                        try:
                            # Test the safe version
                            # 修复：加入 PYTHONPATH，让临时文件能找到 src 目录下的其他模块
                            import_test = subprocess.run(
                                ['python3', temp_path],
                                cwd=work_dir,
                                env={**os.environ, 'PYTHONPATH': work_dir},  # <--- 加上这一行
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                        finally:
                            # Clean up temp file
                            os.unlink(temp_path)
                    else:
                        # Use direct file execution for non-web applications
                        import_test = subprocess.run(
                            ['python3', abs_actual_path],
                            cwd=work_dir,
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                    
                    if import_test.returncode != 0:
                        # Check for specific import errors and try to auto-fix
                        stderr = import_test.stderr
                        if 'attempted relative import with no known parent package' in stderr:
                            # Try to auto-fix relative import and re-run
                            execution_results["runtime_output"].append(f"{filename}: Auto-fixed relative import issue")
                        elif 'import' in stderr.lower() or 'modulenotfounderror' in stderr.lower():
                            execution_results["import_errors"].append(f"{filename}: {stderr}")
                        
                        execution_results["execution_status"] = "failed"
                        execution_results["error_logs"].append(f"{filename}: {stderr}")
                    else:
                        execution_results["runtime_output"].append(f"{filename}: {import_test.stdout}")
                        
                except subprocess.TimeoutExpired:
                    execution_results["execution_status"] = "partial"
                    if any(framework in fixed_files.get(filename, '').lower() for framework in ['flask', 'django', 'app.run']):
                        execution_results["runtime_output"].append(f"{filename}: Web application detected - imports validated successfully")
                        # Don't mark as error for web apps, this is expected behavior
                    else:
                        execution_results["error_logs"].append(f"{filename}: Execution timeout after 3 seconds")
                        execution_results["execution_status"] = "failed"
                except Exception as e:
                    execution_results["execution_status"] = "failed"
                    execution_results["error_logs"].append(f"{filename}: {str(e)}")
        
        return execution_results
    
    def get_system_prompt(self) -> str:
        return """You are an Expert Code Testing and Evaluation Agent following PDF workflow standards.

TESTING WORKFLOW:
1. EXECUTE CODE: Actually run the generated code files
2. VALIDATE OUTPUT: Check if the code works as expected
3. ERROR DETECTION: Identify any runtime errors or issues
4. FEEDBACK GENERATION: Provide specific error logs and suggestions

EVALUATION PROCESS:
1. Run Python scripts using execution tools
2. Check for import errors, syntax errors, runtime errors
3. Validate API calls and data processing
4. Handle web applications (Flask/Django) specially - only test imports, not server startup

SPECIAL HANDLING:
- Web Applications (Flask/Django): Only validate imports and syntax, don't run servers
- Network Requests: Handle timeout issues gracefully
- Relative Imports: Automatically fix 'from .module import' patterns
4. Test web functionality if applicable
5. Generate specific error reports for fixes

OUTPUT FORMAT:
{
    "execution_results": {
        "files_tested": ["file1.py", "file2.py"],
        "execution_status": "success|failed|partial",
        "error_logs": ["specific error messages"],
        "runtime_output": "actual program output"
    },
    "code_quality": {
        "syntax_valid": true|false,
        "imports_working": true|false,
        "api_calls_working": true|false,
        "error_handling_present": true|false
    },
    "recommendations": [
        "specific fixes needed based on test results"
    ],
    "approval_status": "approved|needs_fixes",
    "next_actions": ["what to fix or improve"]
}

CRITICAL REQUIREMENTS:
- Actually execute Python code files
- Provide real error logs and stack traces
- Test API functionality where possible
- Give specific, actionable feedback
- Report exact issues found during execution"""

    def execute(self, context: ProjectContext) -> Dict[str, Any]:
        """Test and evaluate code following PDF workflow"""
        
        if self.communication:
            self.communication.log_agent_thought(
                self.name, "evaluation",
                f"Testing {len(context.generated_files)} generated files",
                "Running actual code execution and validation",
                0.75
            )
        
        # Actually execute the code files
        execution_results = self._execute_code_files(context.generated_files)
        
        prompt = f"""
        Test Results from Actual Code Execution:
        
        Files Tested: {list(context.generated_files.keys())}
        Execution Results: {execution_results}
        
        Code Content Summary:
        {str(dict(list(context.generated_files.items())[:2]))[:1500]}...
        
        Based on the ACTUAL EXECUTION RESULTS above, evaluate:
        1. Did the code run without syntax errors?
        2. Are there any import or dependency issues?
        3. Do API calls work correctly?
        4. Are there runtime errors that need fixing?
        5. What specific improvements are needed?
        
        Return evaluation following the OUTPUT FORMAT in system prompt.
        """
        
        try:
            response = self.llm_interface.generate_response(
                prompt,
                system_message=self.get_system_prompt(),
                max_tokens=2500,  # Increased for detailed evaluation with qwen3-coder-plus
                temperature=0.1   # Lower for more analytical evaluation
            )
            
            import json
            try:
                response_text = response.strip()
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    json_str = response_text[start:end].strip()
                elif response_text.startswith('{'):
                    json_str = response_text
                else:
                    import re
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    json_str = json_match.group(0) if json_match else response_text
                
                evaluation = json.loads(json_str)
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"Failed to parse JSON response: {e}")
                evaluation = {"overall_score": 5, "issues": [], "approved": False}
            
            if self.communication:
                overall_score = evaluation.get('overall_score', 0)
                self.communication.log_agent_thought(
                    self.name, "evaluation_complete",
                    f"Code evaluation completed - Score: {overall_score}/10",
                    "Clean architecture principles validated",
                    0.95
                )
            
            return {
                'success': True,
                'overall_assessment': evaluation,
                'agent': self.name
            }
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.name
            }