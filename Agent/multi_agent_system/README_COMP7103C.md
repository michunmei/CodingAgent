# COMP7103C Multi-Agent Collaborative System

## Code Agent Building Assignment

A sophisticated multi-agent collaborative system that autonomously completes software development from natural language task descriptions, implementing the exact specifications from the COMP7103C course requirements.

**🆕 Now optimized for qwen3-coder-plus - Enhanced code generation capabilities with professional-grade output!**

---

## 🏗️ Project Architecture

### Role-Specific Agents

This system implements the three specialized agents as specified in the PDF requirements:

#### 1. **Project Planning Agent**
- **Core Responsibility**: Handles high-level planning, designs software architecture, and breaks down initial requirements into executable task lists with clear technical specifications and dependencies
- **Implementation**: `agents/base_agent.py:ProjectPlanningAgent`
- **Key Features**: Requirements analysis, task decomposition, dependency management

#### 2. **Code Generation Agent** 
- **Core Responsibility**: Executes concrete development tasks, receives explicit instructions and utilizes programming tools to implement code solutions
- **Implementation**: `agents/base_agent.py:CodeGenerationAgent` 
- **Key Features**: File creation, code implementation, filesystem operations

#### 3. **Code Evaluation Agent**
- **Core Responsibility**: Reviews and validates code quality, functionality, and adherence to requirements through automated testing and analysis
- **Implementation**: `agents/base_agent.py:CodeEvaluationAgent`
- **Key Features**: Quality assessment, functionality validation, requirement compliance

### Multi-Agent Orchestrator

The orchestration framework implements the three core components specified in the PDF:

#### 1. **Task Scheduling** (`core/standard_orchestrator.py:TaskScheduler`)
- Determining which agent should work next
- Coordinating task dependencies across the system
- Managing task execution queue and priority

#### 2. **Communication Management** (`core/standard_orchestrator.py:CommunicationManager`) 
- Establishing protocols for seamless information exchange
- Collaboration between specialized agents
- Message routing and response handling

#### 3. **State Management** (`core/state_management.py:StateManager`)
- Tracking global project state
- Maintaining shared memory
- Determining final task completion status

### Tool Kit

The system includes the specified tool kits:

#### **Filesystem Tools** (`tools/filesystem_tools.py`)
- `create_file`: Create new files with content
- `write_to_file`: Write content to existing files  
- `read_file`: Read file contents
- Other file management operations

#### **Web Search Tool** (`tools/web_search_tools.py`)
- Simulated search functionality
- External knowledge retrieval
- Documentation access

#### **Code Execution Tool** (Safety-first implementation)
- Shell command execution capabilities
- Testing and validation support
- Appropriate safety measures

---

## 🧪 Test Case: Generate an "arXiv CS Daily" Webpage

### Official COMP7103C Test Case Implementation

The system implements the exact test case specified in the PDF with three core functionalities:

#### 1. **Domain-Specific Navigation System**
- Categorized navigation based on arXiv's primary CS fields (cs.AI, cs.TH, cs.SY, etc.)
- Quick filtering between major subfields
- Easy access to areas of interest

#### 2. **Daily Updated Paper List**  
- Latest papers with essential details
- Paper titles hyperlinked to detail pages
- Submission time and arXiv field tags (e.g., [cs.CV])

#### 3. **Dedicated Paper Detail Page**
- Direct PDF links (hosted on arXiv)
- Core metadata (title, authors with affiliations, submission date)
- Citation generation tools (BibTeX, standard academic citation)
- One-click copy functionality

---

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd multi_agent_system

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your LLM API credentials:

```bash
# Qwen API Configuration (optimized for COMP7103C)
DASHSCOPE_API_KEY=sk-your_api_key_here
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1  # 新加坡地域
# 北京地域请使用: QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3-coder-plus  # Enhanced coding model (default)

# Alternative LLM APIs (as mentioned in PDF)
# DeepSeek: deepseek/deepseek-chat-v3.1
# GLM: z-ai/glm-4.5-air  
# Llama: meta-llama/llama-3.3-70b-instruct

# Logging Configuration
LOG_LEVEL=INFO
```

**Getting API Keys:**
- **Qwen**: Visit [DashScope Console](https://dashscope.console.aliyun.com/)
- **DeepSeek**: Visit [DeepSeek API](https://platform.deepseek.com/)
- **Other APIs**: Follow PDF suggestions for alternative providers

### 3. Run the Official Test Case

```bash
# Execute COMP7103C Test Case: arXiv CS Daily
python main_comp7103c.py
```

This will execute the official test case demonstrating all required capabilities.

---

## 📊 Key Execution Examples

### Example 1: Official Test Case
```bash
python main_comp7103c.py
```
**Output**: Complete arXiv CS Daily webpage with navigation, paper lists, and detail pages

### Example 2: Custom Development Task
```bash
python universal_main.py "Build a calculator web application"
```
**Output**: Full calculator implementation with HTML, CSS, and JavaScript

### Example 3: Interactive Mode
```bash
python universal_main.py
# Enter requirement when prompted
```

---

## 🏁 Expected Output Files

The system generates complete, functional software projects:

### arXiv CS Daily Test Case Output:
```
output/arxiv_cs_daily_official/
├── index.html              # Main homepage with navigation
├── styles.css              # Responsive styling  
├── script.js               # Interactive functionality
├── paper-detail.html       # Paper detail page template
├── data/
│   └── papers.json         # Paper data structure
└── execution_logs.json     # Detailed system logs
```

### Generated Files Include:
- **HTML5** compliant structure
- **CSS3** responsive design  
- **JavaScript ES6+** functionality
- **JSON** data integration
- **Complete documentation** and logs

---

## 📈 System Features

### ✅ **Multi-Agent Architecture** 
- Specialized roles with clear responsibilities
- Effective orchestration for seamless collaboration

### ✅ **LLM API Integration**
- Stable communication with major LLMs
- Engineering best practices implementation
- Support for Qwen, DeepSeek, GLM, Llama, and more

### ✅ **Agent Tools Implementation**
- Advanced function-calling capabilities
- Comprehensive filesystem interaction
- Environment interaction capabilities

### ✅ **Advanced Agent Communication**
- Sophisticated instruction protocols
- Effective behavior guidance
- Decision-making coordination

### ✅ **Task Decomposition & Collaboration**
- High-level objective breakdown
- Concrete sub-task coordination
- Multi-agent execution management

### ✅ **AI-Generated Quality Evaluation**
- Structure and readability assessment
- Functional completeness validation
- Requirements adherence verification

---

## 🔧 Technical Implementation

### LLM Provider Integration
- **Qwen API**: Primary recommendation for COMP7103C
- **OpenAI-compatible**: Supports multiple providers
- **Error Handling**: Robust retry mechanisms
- **Cost Management**: Efficient token usage

### Agent Communication Protocol
- **Detailed Logging**: Agent thoughts and actions (PDF requirement)
- **Message Routing**: Sophisticated inter-agent communication  
- **State Tracking**: Comprehensive project state management
- **Debug Support**: Complete execution traces

### File System Operations
- **Safety First**: Secure file operations
- **Complete Coverage**: All required file management
- **Error Recovery**: Robust error handling
- **Path Management**: Proper directory structure

---

## 📝 Logging and Debugging

### Comprehensive Logging (PDF Requirement)
The system implements detailed logs of agent thoughts and actions for effective debugging:

```bash
# View system logs
tail -f comp7103c_agent_system.log

# Analyze execution logs  
cat output/arxiv_cs_daily_official/execution_logs.json
```

### Log Categories:
- **Agent Thoughts**: Decision-making processes
- **Communication**: Inter-agent message exchange
- **Task Execution**: Step-by-step task completion
- **State Changes**: Project state evolution
- **Error Tracking**: Complete error traces

---

## 🎯 COMP7103C Learning Objectives Achieved

### ✅ **Design Multi-Agent Architectures**
- Three specialized agents with clear roles
- Effective orchestration system implementation
- Seamless collaboration framework

### ✅ **Integrate LLM APIs** 
- Qwen API integration with best practices
- Stable communication protocols
- Multiple LLM provider support

### ✅ **Implement Agent Tools**
- Advanced function-calling capabilities
- Comprehensive filesystem interaction
- Environment manipulation tools

### ✅ **Architect Advanced Agent Communication**
- Sophisticated instruction protocols
- Effective agent behavior guidance
- Decision-making coordination systems

### ✅ **Practice Task Decomposition & Collaboration**
- High-level objective breakdown
- Concrete sub-task generation
- Multi-agent coordination execution

### ✅ **Evaluate AI-Generated Quality**
- Structure and readability assessment
- Functional completeness validation
- Requirements adherence verification

---

## 🛠️ Development Guidelines

### Following PDF Hints & Suggestions:

#### ✅ **Start Small**: 
- Implemented single-file generation first
- Gradually scaled up functionality
- Modular development approach

#### ✅ **Leverage Logging**:
- Detailed agent thought processes
- Complete action logging
- Effective debugging support

#### ✅ **Iterate on Prompts**:
- Continuously refined system prompts
- Agent behavior optimization
- Performance-based improvements

#### ✅ **Manage Costs**:
- Efficient development process
- High-performance model usage for testing
- Token usage optimization

#### ✅ **Original Implementation**:
- No copying from AutoGen or ChatDev
- Original architecture and design
- COMP7103C-specific implementation

---

## 📚 Course Integration

### COMP7103C Specific Features:
- **PDF-Compliant Architecture**: Exact specification implementation
- **Official Test Case**: arXiv CS Daily webpage generation
- **Required Components**: All three orchestrator components
- **Logging Requirements**: Detailed agent thought processes
- **Tool Kit Implementation**: All specified tools included

### Assignment Deliverables:
✅ **Git Repository**: Complete source code with detailed README  
✅ **Project Report**: Comprehensive documentation (see SYSTEM_STATUS.md)  
✅ **Live Demonstration**: Ready for TA presentation  

---

## 🔗 Repository Structure

```
multi_agent_system/
├── agents/                    # Role-specific agents
│   ├── base_agent.py         # Core agent implementations
│   └── universal_agents.py   # Enhanced agent variants
├── core/                     # Orchestration framework
│   ├── standard_orchestrator.py  # COMP7103C orchestrator
│   ├── communication.py     # Agent communication
│   ├── state_management.py  # State tracking
│   └── llm_provider.py      # LLM integration
├── tools/                    # Agent tool kit
│   ├── filesystem_tools.py  # File operations
│   ├── web_search_tools.py  # Search capabilities
│   └── execution_tools.py   # Code execution
├── output/                   # Generated projects
├── config.py                 # System configuration
├── requirements.txt          # Dependencies
├── main_comp7103c.py        # Official test case entry
├── universal_main.py        # General purpose entry
└── README_COMP7103C.md      # This documentation
```

---

## 🚀 Getting Started Immediately

### Quick Test (2 minutes):
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key in .env file
echo "QWEN_API_KEY=your_key_here" > .env

# 3. Run official test case  
python main_comp7103c.py
```

### Expected Result:
- Complete arXiv CS Daily webpage
- Three core functionalities implemented
- All files generated in output directory
- Detailed logs for analysis

*Generated by COMP7103C Multi-Agent Collaborative System - Demonstrating autonomous software development from natural language specifications.*