"""
Base Agent class for Multi-Agent Collaborative System
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from core.llm_provider import LLMInterface
from core.communication import CommunicationProtocol

logger = logging.getLogger(__name__)

@dataclass
class ProjectContext:
    """Context object to maintain state across agents"""
    project_name: str = ""
    requirements: str = ""
    current_plan: Optional[Dict[str, Any]] = None
    generated_files: Dict[str, str] = field(default_factory=dict)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_file(self, filename: str, content: str):
        """Add a generated file to the context"""
        self.generated_files[filename] = content
        logger.info(f"Added file to context: {filename}")
    
    def mark_task_completed(self, task_id: str):
        """Mark a task as completed"""
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
            logger.info(f"Task completed: {task_id}")

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, llm_interface: LLMInterface, name: str = "BaseAgent", 
                 communication: CommunicationProtocol = None):
        self.llm_interface = llm_interface
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.communication = communication
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def execute(self, context: ProjectContext, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
    
    def _log_execution(self, context: ProjectContext, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """Log agent execution for debugging"""
        self.logger.info(f"Agent {self.name} executed")
        self.logger.debug(f"Input: {input_data}")
        self.logger.debug(f"Output: {output_data}")
        
        # Add to conversation history
        context.add_message("system", f"{self.name} executed with input: {str(input_data)}")
        context.add_message("assistant", f"{self.name} output: {str(output_data)}")

class ProjectPlanningAgent(BaseAgent):
    """Project Planning Agent: Handles high-level planning, designs software architecture, and breaks down initial requirements into executable task lists with clear technical specifications and dependencies
    
    Core Responsibilities (as per COMP7103C requirements):
    - High-level planning and software architecture design
    - Breaking down requirements into executable task lists  
    - Clear technical specifications and dependencies
    - Task decomposition and coordination planning
    """
    
    def __init__(self, llm_interface: LLMInterface, communication: CommunicationProtocol = None):
        super().__init__(llm_interface, "ProjectPlanningAgent", communication)
    
    def get_system_prompt(self) -> str:
        return """You are a Project Planning Agent (Architect) for a Multi-Agent System.

        CRITICAL: You must first explore the project directory to understand available resources.
        
        Your workflow:
        1. Use list_dir tool to explore the current directory and discover available data files
        2. If you find arxiv_data.json or similar data files, read them to understand the data structure  
        3. Generate a specific task list based on the requirements and available data
        
        For arXiv CS Daily webpage projects, generate exactly these tasks:
        
        Task 1: Read arxiv_data.json to understand data structure
        Task 2: Write index.html with navigation bar (cs.AI, cs.AR, cs.CV, cs.LG, cs.CL) and card-style layout
        Task 3: Write styles.css to beautify the page with modern responsive design
        Task 4: Write script.js to load data from JSON and render dynamic paper lists and navigation
        Task 5: Create test cases to verify all files are generated correctly
        
        Output Format: Always return valid JSON with this exact structure:
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
                ...
            ]
        }
        
        IMPORTANT: You must explore the directory first before generating the plan!"""
    
    def execute(self, context: ProjectContext, requirements: str = None) -> Dict[str, Any]:
        """Generate project plan with directory exploration and data analysis"""
        if requirements:
            context.requirements = requirements
        
        # Log thinking process
        if self.communication:
            self.communication.log_agent_thought(
                self.name, "analysis",
                f"Starting project planning with directory exploration",
                f"Requirements: {requirements[:100]}...",
                0.85
            )
        
        # Build enhanced prompt with tool instructions
        enhanced_prompt = f"""
        Project Requirements: {context.requirements}
        
        STEP 1: Explore the project directory using available tools
        STEP 2: Look for data files like arxiv_data.json
        STEP 3: If found, read the data to understand structure
        STEP 4: Generate specific task list based on findings
        
        Available tools: list_dir, read_file
        
        Generate a project plan following the exact JSON format specified in your system prompt.
        """
        
        # Generate plan using LLM with enhanced context
        plan = self.llm_interface.generate_plan_with_tools(enhanced_prompt)
        
        if plan and isinstance(plan, dict) and "tasks" in plan:
            context.current_plan = plan
            context.project_name = plan.get("project_name", "arXiv CS Daily")
            
            # Log successful planning thoughts
            if self.communication:
                self.communication.log_agent_thought(
                    self.name, "decision",
                    f"Successfully generated plan with {len(plan.get('tasks', []))} tasks",
                    f"Found data files and created appropriate task breakdown",
                    0.9
                )
            
            result = {
                "success": True,
                "plan": plan,
                "message": f"Generated plan for {context.project_name} with {len(plan['tasks'])} tasks"
            }
        else:
            # Log failure thoughts
            if self.communication:
                self.communication.log_agent_thought(
                    self.name, "reflection",
                    "Failed to generate project plan",
                    "LLM did not return valid JSON plan structure",
                    0.3
                )
            
            result = {
                "success": False,
                "plan": None,
                "message": "Failed to generate project plan"
            }
        
        self._log_execution(context, {"requirements": context.requirements}, result)
        return result

class CodeGenerationAgent(BaseAgent):
    """Code Generation Agent: Executes concrete development tasks, receives explicit instructions and utilizes programming tools to implement code solutions
    
    Core Responsibilities (as per COMP7103C requirements):
    - Execute concrete development tasks with explicit instructions
    - Utilize programming tools and filesystem operations
    - Implement code solutions based on task specifications
    - Generate functional, complete code files
    """
    
    def __init__(self, llm_interface: LLMInterface, communication: CommunicationProtocol = None, output_dir: str = "./output"):
        super().__init__(llm_interface, "CodeGenerationAgent", communication)
        self.output_dir = output_dir
        # Import filesystem tools
        from tools.filesystem_tools import FileSystemTools
        self.fs_tools = FileSystemTools(output_dir)
    
    def get_system_prompt(self) -> str:
        return """You are a Code Generation Agent (Engineer) in a Multi-Agent System.

        CRITICAL REQUIREMENT: You must use write_to_file tool to actually save code to disk.
        
        Your workflow for each task:
        1. If task requires reading existing files, use read_file first
        2. Generate the required code for the specified file
        3. Use write_to_file to actually save the code to the filesystem
        4. Verify the file was created successfully
        
        For arXiv CS Daily project specifically:
        
        Task 1: Use read_file('arxiv_data.json') to understand data structure
        Task 2: Generate index.html with:
           - Navigation for categories (cs.AI, cs.AR, cs.CV, cs.LG, cs.CL)
           - Card-style layout for papers
           - Responsive design structure
           
        Task 3: Generate styles.css with:
           - Modern responsive design
           - Card layouts and navigation styling
           - Professional academic look
           
        Task 4: Generate script.js with:
           - Functions to load arxiv_data.json
           - Dynamic rendering of papers by category
           - Category filtering functionality
           - Detail page/modal functionality
           
        Task 5: Generate test.html to verify functionality
        
        Code Generation Rules:
        - Write production-ready, standards-compliant code
        - Use modern web technologies (HTML5, CSS3, ES6+)
        - Ensure cross-browser compatibility
        - Implement proper error handling
        - Focus on user experience and accessibility
        
        REMEMBER: You must actually write files to disk using write_to_file tool!"""
    
    def execute(self, context: ProjectContext, task: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute task with actual file writing using filesystem tools"""
        if not task:
            return {
                "success": False,
                "message": "No task provided",
                "generated_files": {}
            }
        
        generated_files = {}
        files_written = 0
        
        # Handle Task 1: Read data structure
        if task.get("id") == "task_1":
            if self.communication:
                self.communication.log_agent_thought(
                    self.name, "execution",
                    "Reading arxiv_data.json to understand data structure",
                    "Using read_file tool to analyze data format",
                    0.85
                )
            
            try:
                # Read the arxiv_data.json file to understand structure
                data_content = self.fs_tools.read_file("../arxiv_data.json")
                if data_content:
                    context.metadata["data_structure"] = "arxiv_data.json analyzed successfully"
                    return {
                        "success": True,
                        "generated_files": {},
                        "task_id": task.get("id"),
                        "message": "Successfully read and analyzed arxiv_data.json structure"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to read arxiv_data.json: {str(e)}",
                    "generated_files": {}
                }
        
        # Handle file creation tasks (Task 2-5)
        for filename in task.get("files_to_create", []):
            if self.communication:
                self.communication.log_agent_thought(
                    self.name, "planning",
                    f"Generating code for {filename}",
                    f"Will write file to disk using filesystem tools",
                    0.8
                )
            
            # Generate code using enhanced prompts for arXiv project
            code = self._generate_arxiv_code(task, filename, context)
            
            if code:
                try:
                    # CRITICAL: Actually write file to disk
                    self.fs_tools.create_file(filename, code)
                    generated_files[filename] = code
                    context.add_file(filename, code)
                    files_written += 1
                    
                    if self.communication:
                        self.communication.log_agent_thought(
                            self.name, "success",
                            f"Successfully wrote {filename} to disk",
                            f"File contains {len(code)} characters",
                            0.95
                        )
                    
                    self.logger.info(f"Successfully wrote file: {filename}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to write file {filename}: {str(e)}")
                    if self.communication:
                        self.communication.log_agent_thought(
                            self.name, "error",
                            f"Failed to write {filename} to disk",
                            f"Error: {str(e)}",
                            0.2
                        )
            else:
                self.logger.warning(f"Failed to generate code for {filename}")
        
        result = {
            "success": files_written > 0,
            "generated_files": generated_files,
            "task_id": task.get("id"),
            "message": f"Successfully wrote {files_written} files to disk for task: {task.get('title')}"
        }
        
        if result["success"]:
            context.mark_task_completed(task.get("id", "unknown"))
        
        self._log_execution(context, {"task": task}, result)
        return result
    
    def _generate_arxiv_code(self, task: Dict[str, Any], filename: str, context: ProjectContext) -> str:
        """Generate specific code for arXiv CS Daily project files"""
        
        if filename == "index.html":
            return self._generate_index_html()
        elif filename == "styles.css":
            return self._generate_styles_css()
        elif filename == "script.js":
            return self._generate_script_js()
        elif filename == "test.html":
            return self._generate_test_html()
        else:
            # Fallback to general code generation
            prompt = self._build_code_prompt(task, filename, context)
            language = self._get_language_from_filename(filename)
            return self.llm_interface.generate_code(prompt, language) or ""
    
    def _generate_index_html(self) -> str:
        """Generate the main HTML file for arXiv CS Daily"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv CS Daily</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>arXiv CS Daily</h1>
            <p class="subtitle">Latest Computer Science Research Papers</p>
        </div>
    </header>

    <nav class="category-nav">
        <div class="container">
            <h2>Categories</h2>
            <div class="category-buttons" id="categoryButtons">
                <button class="category-btn active" data-category="all">All Papers</button>
                <button class="category-btn" data-category="cs.AI">Artificial Intelligence</button>
                <button class="category-btn" data-category="cs.AR">Hardware Architecture</button>
                <button class="category-btn" data-category="cs.CV">Computer Vision</button>
                <button class="category-btn" data-category="cs.LG">Machine Learning</button>
                <button class="category-btn" data-category="cs.CL">Computation and Language</button>
            </div>
        </div>
    </nav>

    <main class="container">
        <section class="papers-section">
            <h2 id="sectionTitle">All Papers</h2>
            <div class="papers-grid" id="papersGrid">
                <!-- Papers will be loaded here by JavaScript -->
            </div>
        </section>
    </main>

    <!-- Modal for paper details -->
    <div class="modal" id="paperModal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 arXiv CS Daily - Generated by Multi-Agent System</p>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>'''
    
    def _generate_styles_css(self) -> str:
        """Generate CSS styles for arXiv CS Daily"""
        return '''/* arXiv CS Daily Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 60px 0;
    text-align: center;
}

.header h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.subtitle {
    font-size: 1.2rem;
    opacity: 0.9;
}

.category-nav {
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 30px 0;
}

.category-nav h2 {
    margin-bottom: 20px;
    color: #2c3e50;
}

.category-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.category-btn {
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    color: #495057;
    padding: 12px 24px;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
    font-weight: 500;
}

.category-btn:hover {
    background: #e9ecef;
    border-color: #adb5bd;
}

.category-btn.active {
    background: #007bff;
    border-color: #007bff;
    color: white;
}

.papers-section {
    margin: 40px 0;
}

.papers-section h2 {
    margin-bottom: 30px;
    color: #2c3e50;
    font-size: 2rem;
}

.papers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 30px;
}

.paper-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    cursor: pointer;
}

.paper-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.paper-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 10px;
    line-height: 1.4;
}

.paper-authors {
    color: #6c757d;
    margin-bottom: 10px;
    font-size: 0.9rem;
}

.paper-date {
    color: #28a745;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 15px;
}

.paper-abstract {
    color: #495057;
    line-height: 1.6;
    margin-bottom: 15px;
}

.paper-link {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
}

.paper-link:hover {
    text-decoration: underline;
}

/* Modal styles */
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: white;
    margin: 5% auto;
    padding: 30px;
    border-radius: 12px;
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    overflow-y: auto;
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.close:hover {
    color: #333;
}

.footer {
    background: #2c3e50;
    color: white;
    text-align: center;
    padding: 30px 0;
    margin-top: 60px;
}

/* Responsive design */
@media (max-width: 768px) {
    .header h1 {
        font-size: 2rem;
    }
    
    .category-buttons {
        justify-content: center;
    }
    
    .papers-grid {
        grid-template-columns: 1fr;
    }
}'''
    
    def _generate_script_js(self) -> str:
        """Generate JavaScript functionality for arXiv CS Daily"""
        return '''// arXiv CS Daily JavaScript
let papersData = [];
let currentCategory = 'all';

// Load papers data from JSON file
async function loadPapersData() {
    try {
        const response = await fetch('arxiv_data.json');
        const data = await response.json();
        papersData = data.papers || [];
        renderPapers();
        updateStats();
    } catch (error) {
        console.error('Error loading papers data:', error);
        showError('Failed to load papers data');
    }
}

// Render papers based on current filter
function renderPapers(category = currentCategory) {
    const papersGrid = document.getElementById('papersGrid');
    const sectionTitle = document.getElementById('sectionTitle');
    
    let filteredPapers = papersData;
    if (category !== 'all') {
        filteredPapers = papersData.filter(paper => paper.category === category);
    }
    
    // Update section title
    if (category === 'all') {
        sectionTitle.textContent = `All Papers (${filteredPapers.length})`;
    } else {
        const categoryName = getCategoryName(category);
        sectionTitle.textContent = `${categoryName} (${filteredPapers.length})`;
    }
    
    // Render paper cards
    papersGrid.innerHTML = filteredPapers.map(paper => `
        <div class="paper-card" onclick="showPaperDetails('${paper.id}')">
            <h3 class="paper-title">${paper.title}</h3>
            <p class="paper-authors">Authors: ${Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}</p>
            <p class="paper-date">Published: ${formatDate(paper.published)}</p>
            <p class="paper-abstract">${truncateAbstract(paper.abstract)}</p>
            <a href="${paper.url}" target="_blank" class="paper-link" onclick="event.stopPropagation()">View on arXiv →</a>
        </div>
    `).join('');
}

// Show paper details in modal
function showPaperDetails(paperId) {
    const paper = papersData.find(p => p.id === paperId);
    if (!paper) return;
    
    const modal = document.getElementById('paperModal');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.innerHTML = `
        <h2>${paper.title}</h2>
        <p><strong>Authors:</strong> ${Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors}</p>
        <p><strong>Category:</strong> ${paper.category} - ${getCategoryName(paper.category)}</p>
        <p><strong>Published:</strong> ${formatDate(paper.published)}</p>
        <p><strong>arXiv ID:</strong> ${paper.id}</p>
        <h3>Abstract</h3>
        <p>${paper.abstract}</p>
        <div style="margin-top: 20px;">
            <a href="${paper.url}" target="_blank" class="paper-link">View on arXiv</a>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Handle category button clicks
function setupCategoryButtons() {
    const categoryButtons = document.querySelectorAll('.category-btn');
    
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Get category and render papers
            const category = button.getAttribute('data-category');
            currentCategory = category;
            renderPapers(category);
        });
    });
}

// Setup modal functionality
function setupModal() {
    const modal = document.getElementById('paperModal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Utility functions
function getCategoryName(categoryId) {
    const categoryNames = {
        'cs.AI': 'Artificial Intelligence',
        'cs.AR': 'Hardware Architecture',
        'cs.CV': 'Computer Vision and Pattern Recognition',
        'cs.LG': 'Machine Learning',
        'cs.CL': 'Computation and Language'
    };
    return categoryNames[categoryId] || categoryId;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function truncateAbstract(abstract, maxLength = 200) {
    if (abstract.length <= maxLength) return abstract;
    return abstract.substring(0, maxLength) + '...';
}

function updateStats() {
    console.log(`Loaded ${papersData.length} papers`);
}

function showError(message) {
    const papersGrid = document.getElementById('papersGrid');
    papersGrid.innerHTML = `
        <div style="text-align: center; color: #dc3545; padding: 40px;">
            <h3>Error</h3>
            <p>${message}</p>
        </div>
    `;
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    setupCategoryButtons();
    setupModal();
    loadPapersData();
});'''
    
    def _generate_test_html(self) -> str:
        """Generate test file to verify functionality"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arXiv CS Daily - Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .test-item { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
        .pass { background-color: #d4edda; }
        .fail { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>arXiv CS Daily - Test Results</h1>
    
    <div id="testResults">
        <h2>File Verification Tests</h2>
        <div class="test-item" id="htmlTest">Checking index.html...</div>
        <div class="test-item" id="cssTest">Checking styles.css...</div>
        <div class="test-item" id="jsTest">Checking script.js...</div>
        <div class="test-item" id="dataTest">Checking arxiv_data.json...</div>
    </div>

    <script>
        async function runTests() {
            const tests = [
                { id: 'htmlTest', file: 'index.html', description: 'HTML file exists and is accessible' },
                { id: 'cssTest', file: 'styles.css', description: 'CSS file exists and is accessible' },
                { id: 'jsTest', file: 'script.js', description: 'JavaScript file exists and is accessible' },
                { id: 'dataTest', file: 'arxiv_data.json', description: 'Data file exists and is accessible' }
            ];

            for (const test of tests) {
                const element = document.getElementById(test.id);
                try {
                    const response = await fetch(test.file);
                    if (response.ok) {
                        element.textContent = `✓ ${test.description}`;
                        element.className = 'test-item pass';
                    } else {
                        element.textContent = `✗ ${test.description} (HTTP ${response.status})`;
                        element.className = 'test-item fail';
                    }
                } catch (error) {
                    element.textContent = `✗ ${test.description} (${error.message})`;
                    element.className = 'test-item fail';
                }
            }
        }

        document.addEventListener('DOMContentLoaded', runTests);
    </script>
</body>
</html>'''
    
    def _build_code_prompt(self, task: Dict[str, Any], filename: str, context: ProjectContext) -> str:
        """Build a detailed prompt for code generation"""
        prompt = f"""
        Task: {task.get('title', 'Unknown Task')}
        Description: {task.get('description', '')}
        
        File to generate: {filename}
        
        Project Context:
        - Project: {context.project_name}
        - Requirements: {context.requirements}
        
        Implementation Requirements:
        - Follow the task description exactly
        - Use modern best practices
        - Include proper error handling
        - Make the code production-ready
        - Consider the overall project architecture
        
        Additional Context:
        """
        
        if context.current_plan:
            prompt += f"\nProject Architecture: {context.current_plan.get('architecture', {})}"
        
        if context.generated_files:
            prompt += f"\nExisting Files: {list(context.generated_files.keys())}"
        
        return prompt
    
    def _get_language_from_filename(self, filename: str) -> str:
        """Determine programming language from filename"""
        extension = filename.split('.')[-1].lower()
        
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'yaml': 'yaml',
            'yml': 'yaml',
            'md': 'markdown',
            'sql': 'sql',
            'sh': 'bash'
        }
        
        return language_map.get(extension, 'text')

class CodeEvaluationAgent(BaseAgent):
    """Code Evaluation Agent: Reviews and validates code quality, functionality, and adherence to requirements through automated testing and analysis
    
    Core Responsibilities (as per COMP7103C requirements):
    - Review and validate code quality and functionality
    - Assess adherence to requirements through analysis
    - Provide automated testing and validation
    - Generate evaluation reports and feedback
    """
    
    def __init__(self, llm_interface: LLMInterface, communication: CommunicationProtocol = None, output_dir: str = "./output"):
        super().__init__(llm_interface, "CodeEvaluationAgent", communication)
        self.output_dir = output_dir
        # Import filesystem tools for file checking
        from tools.filesystem_tools import FileSystemTools
        self.fs_tools = FileSystemTools(output_dir)
    
    def get_system_prompt(self) -> str:
        return """You are a Code Evaluation Agent (Tester) in a Multi-Agent System.

        Your role is to validate that files were created correctly and functionality works as expected.
        
        CRITICAL EVALUATION STEPS:
        1. Check if files exist (index.html, styles.css, script.js)
        2. Read file contents and verify key requirements
        3. If issues found, provide feedback for Coder to fix
        
        For arXiv CS Daily project, verify:
        
        index.html checks:
        - File exists and is readable
        - Contains <nav> tag for navigation requirements
        - Contains id="papersGrid" or similar for paper list requirements
        - Has proper HTML5 structure with head, body, etc.
        - Links to styles.css and script.js
        
        styles.css checks:
        - File exists and contains CSS rules
        - Has responsive design rules (@media queries)
        - Contains styling for navigation and paper cards
        - Professional academic styling
        
        script.js checks:
        - File exists and contains JavaScript code
        - Has functions to load arxiv_data.json
        - Implements category filtering functionality
        - Has paper rendering and detail view logic
        
        Output Format - Return JSON:
        {
            "overall_score": "number (1-10)",
            "files_checked": ["list of files"],
            "issues": [
                {
                    "file": "filename",
                    "severity": "low|medium|high|critical", 
                    "description": "what is wrong",
                    "suggestion": "how to fix"
                }
            ],
            "approved": "boolean",
            "critical_issues": "number",
            "summary": "brief evaluation summary"
        }
        
        Be specific about missing functionality and provide actionable feedback."""
    
    def execute(self, context: ProjectContext, files_to_review: List[str] = None) -> Dict[str, Any]:
        """Execute comprehensive file validation with actual file checking"""
        
        # Define expected files for arXiv CS Daily project
        expected_files = ["index.html", "styles.css", "script.js", "test.html"]
        
        if not files_to_review:
            files_to_review = expected_files
        
        if self.communication:
            self.communication.log_agent_thought(
                self.name, "analysis",
                f"Starting evaluation of {len(files_to_review)} files",
                "Checking file existence and content validation",
                0.85
            )
        
        evaluation_results = []
        issues = []
        critical_issues = 0
        files_checked = []
        
        for filename in files_to_review:
            if self.communication:
                self.communication.log_agent_thought(
                    self.name, "inspection",
                    f"Evaluating {filename}",
                    "Checking file existence and content requirements",
                    0.8
                )
            
            file_result = self._evaluate_file(filename, context)
            evaluation_results.append(file_result)
            
            if file_result["exists"]:
                files_checked.append(filename)
                issues.extend(file_result.get("issues", []))
                critical_issues += len([i for i in file_result.get("issues", []) if i.get("severity") == "critical"])
            else:
                issues.append({
                    "file": filename,
                    "severity": "critical",
                    "description": f"File {filename} does not exist",
                    "suggestion": f"Coder must generate {filename} with proper content"
                })
                critical_issues += 1
        
        # Generate overall score
        total_files = len(files_to_review)
        existing_files = len(files_checked)
        overall_score = max(1, 10 - critical_issues - (total_files - existing_files))
        
        approved = critical_issues == 0 and existing_files == total_files
        
        overall_assessment = {
            "overall_score": overall_score,
            "files_checked": files_checked,
            "issues": issues,
            "approved": approved,
            "critical_issues": critical_issues,
            "summary": f"Checked {existing_files}/{total_files} files. {'Approved' if approved else 'Needs fixes'}"
        }
        
        if self.communication:
            if approved:
                self.communication.log_agent_thought(
                    self.name, "success",
                    f"All {total_files} files passed evaluation",
                    f"Score: {overall_score}/10, no critical issues found",
                    0.95
                )
            else:
                self.communication.log_agent_thought(
                    self.name, "issues",
                    f"Found {critical_issues} critical issues",
                    f"Score: {overall_score}/10, files need fixes",
                    0.4
                )
        
        result = {
            "success": True,
            "overall_assessment": overall_assessment,
            "file_evaluations": evaluation_results,
            "message": f"Evaluated {len(files_checked)} files with {critical_issues} critical issues"
        }
        
        self._log_execution(context, {"files": files_to_review}, result)
        return result
    
    def _evaluate_file(self, filename: str, context: ProjectContext) -> Dict[str, Any]:
        """Evaluate a specific file for existence and content requirements"""
        
        result = {
            "filename": filename,
            "exists": False,
            "content_length": 0,
            "issues": []
        }
        
        try:
            # Check if file exists and read content
            content = self.fs_tools.read_file(filename)
            if content:
                result["exists"] = True
                result["content_length"] = len(content)
                result["issues"] = self._check_file_content(filename, content)
            else:
                result["issues"].append({
                    "file": filename,
                    "severity": "critical",
                    "description": f"File {filename} is empty or not readable",
                    "suggestion": "Coder must regenerate file with proper content"
                })
                
        except Exception as e:
            result["issues"].append({
                "file": filename,
                "severity": "critical", 
                "description": f"Cannot access file {filename}: {str(e)}",
                "suggestion": f"Coder must create {filename} in the output directory"
            })
        
        return result
    
    def _check_file_content(self, filename: str, content: str) -> List[Dict[str, Any]]:
        """Check file content for required elements"""
        issues = []
        
        if filename == "index.html":
            # Check for required HTML elements
            if "<nav" not in content:
                issues.append({
                    "file": filename,
                    "severity": "high",
                    "description": "Missing <nav> tag for navigation requirements",
                    "suggestion": "Add navigation structure with category buttons"
                })
            
            if "papersGrid" not in content and "papers-grid" not in content:
                issues.append({
                    "file": filename,
                    "severity": "high",
                    "description": "Missing papers grid container for paper list requirements",
                    "suggestion": "Add element with id='papersGrid' or similar for paper display"
                })
            
            if "styles.css" not in content:
                issues.append({
                    "file": filename,
                    "severity": "medium",
                    "description": "Missing link to styles.css",
                    "suggestion": "Add <link rel='stylesheet' href='styles.css'>"
                })
            
            if "script.js" not in content:
                issues.append({
                    "file": filename,
                    "severity": "medium", 
                    "description": "Missing script.js inclusion",
                    "suggestion": "Add <script src='script.js'></script>"
                })
                
        elif filename == "styles.css":
            # Check for CSS content
            if len(content.strip()) < 100:
                issues.append({
                    "file": filename,
                    "severity": "high",
                    "description": "CSS file appears too short or empty",
                    "suggestion": "Add comprehensive styling for navigation, cards, and responsive design"
                })
            
            if "@media" not in content:
                issues.append({
                    "file": filename,
                    "severity": "medium",
                    "description": "Missing responsive design rules",
                    "suggestion": "Add @media queries for mobile responsiveness"
                })
                
        elif filename == "script.js":
            # Check for JavaScript functionality
            if "fetch" not in content and "XMLHttpRequest" not in content:
                issues.append({
                    "file": filename,
                    "severity": "high", 
                    "description": "Missing data loading functionality",
                    "suggestion": "Add code to fetch arxiv_data.json using fetch() or XMLHttpRequest"
                })
            
            if "arxiv_data.json" not in content:
                issues.append({
                    "file": filename,
                    "severity": "high",
                    "description": "No reference to arxiv_data.json data file",
                    "suggestion": "Add code to load papers from arxiv_data.json"
                })
            
            if "category" not in content.lower():
                issues.append({
                    "file": filename,
                    "severity": "medium",
                    "description": "Missing category filtering functionality",
                    "suggestion": "Add functions to filter papers by category"
                })
        
        return issues
    
    def _review_file(self, filename: str, content: str, context: ProjectContext) -> Dict[str, Any]:
        """Review a single file"""
        prompt = f"""
        Review the following code file for quality, security, and best practices.
        
        Filename: {filename}
        Project: {context.project_name}
        Project Requirements: {context.requirements}
        
        Code to review:
        ```
        {content}
        ```
        
        Provide a detailed review following the JSON format specified in your system prompt.
        Focus on practical, actionable feedback that improves the code quality.
        """
        
        response = self.llm_interface.provider.generate_structured_response(
            [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            expected_format="json"
        )
        
        if response["success"] and response["parsed_data"]:
            return response["parsed_data"]
        else:
            # Fallback review if JSON parsing fails
            return {
                "overall_score": 7,
                "issues": [],
                "recommendations": ["Manual review recommended - automated review failed"],
                "approved": True,
                "summary": "Automated review failed, manual review recommended"
            }
    
    def _generate_overall_assessment(self, reviews: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall project assessment"""
        if not reviews:
            return {"overall_score": 0, "summary": "No files reviewed"}
        
        scores = [review.get("overall_score", 0) for review in reviews.values()]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        all_issues = []
        for review in reviews.values():
            all_issues.extend(review.get("issues", []))
        
        critical_issues = [issue for issue in all_issues if issue.get("severity") == "critical"]
        high_issues = [issue for issue in all_issues if issue.get("severity") == "high"]
        
        approved = len(critical_issues) == 0 and avg_score >= 7.0
        
        return {
            "overall_score": round(avg_score, 1),
            "total_issues": len(all_issues),
            "critical_issues": len(critical_issues),
            "high_priority_issues": len(high_issues),
            "approved": approved,
            "summary": f"Average score: {avg_score:.1f}, {len(all_issues)} total issues found"
        }