"""
Code Execution tools for testing and validation in Multi-Agent Collaborative System
"""
import subprocess
import os
import tempfile
import shutil
import logging
import signal
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class ExecutionResult:
    """Result of code execution"""
    def __init__(self, success: bool, stdout: str = "", stderr: str = "", 
                 return_code: int = 0, execution_time: float = 0.0):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.execution_time = execution_time

class CodeExecutionTool:
    """Safe code execution tool for testing and validation"""
    
    def __init__(self, working_directory: str = None, timeout: int = 30):
        """
        Initialize code execution tool
        
        Args:
            working_directory: Directory to execute commands in
            timeout: Maximum execution time in seconds
        """
        self.working_directory = Path(working_directory) if working_directory else Path.cwd()
        self.timeout = timeout
        self.allowed_commands = {
            # Development tools
            'python', 'python3', 'node', 'npm', 'pip', 'pip3',
            # Web server testing
            'curl', 'wget', 'http-server', 'python -m http.server',
            # File operations
            'ls', 'cat', 'head', 'tail', 'find', 'grep',
            # Version control
            'git',
            # Build tools
            'make', 'cmake', 'gcc', 'g++',
            # Package managers
            'apt-get', 'brew', 'yum',
            # Testing tools
            'pytest', 'jest', 'mocha', 'phpunit',
            # Linting tools
            'eslint', 'pylint', 'flake8', 'black'
        }
        self.blocked_commands = {
            # System control
            'sudo', 'su', 'chmod +x', 'chown',
            # Network/system access
            'ssh', 'scp', 'rsync', 'nc', 'netcat',
            # Process control
            'kill', 'killall', 'pkill',
            # System modification
            'rm -rf /', 'mkfs', 'fdisk',
            # Service control
            'systemctl', 'service', 'init.d'
        }
        
        logger.info(f"CodeExecutionTool initialized with working directory: {self.working_directory}")
    
    def is_command_safe(self, command: str) -> bool:
        """
        Check if command is safe to execute
        
        Args:
            command: Command string to check
            
        Returns:
            True if command is safe to execute
        """
        command_lower = command.lower().strip()
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                logger.warning(f"Blocked unsafe command: {command}")
                return False
        
        # Extract the main command (first word)
        main_command = command_lower.split()[0]
        
        # For Python commands, allow more flexibility
        if main_command in ['python', 'python3']:
            # Block dangerous Python operations
            dangerous_python = ['import os', 'os.system', 'subprocess', 'eval(', 'exec(']
            for danger in dangerous_python:
                if danger in command_lower:
                    logger.warning(f"Blocked dangerous Python command: {command}")
                    return False
            return True
        
        # Check if main command is in allowed list
        return main_command in self.allowed_commands
    
    def execute_command(self, command: str, working_dir: str = None) -> ExecutionResult:
        """
        Execute a shell command safely
        
        Args:
            command: Command to execute
            working_dir: Optional working directory override
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        
        if not self.is_command_safe(command):
            return ExecutionResult(
                success=False,
                stderr=f"Command blocked for safety: {command}",
                return_code=-1
            )
        
        work_dir = Path(working_dir) if working_dir else self.working_directory
        
        try:
            logger.info(f"Executing command: {command}")
            logger.debug(f"Working directory: {work_dir}")
            
            # Ensure working directory exists
            work_dir.mkdir(parents=True, exist_ok=True)
            
            # Execute command with timeout
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(work_dir),
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                return_code = process.returncode
                
                execution_time = time.time() - start_time
                
                result = ExecutionResult(
                    success=return_code == 0,
                    stdout=stdout,
                    stderr=stderr,
                    return_code=return_code,
                    execution_time=execution_time
                )
                
                logger.info(f"Command completed with return code: {return_code}")
                if stdout:
                    logger.debug(f"STDOUT: {stdout[:500]}...")
                if stderr:
                    logger.debug(f"STDERR: {stderr[:500]}...")
                
                return result
                
            except subprocess.TimeoutExpired:
                # Kill the process group
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                
                process.wait()
                
                return ExecutionResult(
                    success=False,
                    stderr=f"Command timed out after {self.timeout} seconds",
                    return_code=-1,
                    execution_time=self.timeout
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {str(e)}")
            return ExecutionResult(
                success=False,
                stderr=f"Execution error: {str(e)}",
                return_code=-1,
                execution_time=execution_time
            )
    
    def execute_python_code(self, code: str, filename: str = "temp_script.py") -> ExecutionResult:
        """
        Execute Python code safely in a temporary file
        
        Args:
            code: Python code to execute
            filename: Temporary filename for the code
            
        Returns:
            ExecutionResult with execution details
        """
        temp_dir = tempfile.mkdtemp()
        temp_file = Path(temp_dir) / filename
        
        try:
            # Write code to temporary file
            temp_file.write_text(code, encoding='utf-8')
            
            # Execute the Python file
            command = f"python3 {temp_file}"
            result = self.execute_command(command, working_dir=temp_dir)
            
            return result
            
        except Exception as e:
            logger.error(f"Python code execution failed: {str(e)}")
            return ExecutionResult(
                success=False,
                stderr=f"Python execution error: {str(e)}",
                return_code=-1
            )
        finally:
            # Clean up temporary files
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {str(e)}")
    
    def test_web_server(self, file_path: str, port: int = 8000, test_duration: int = 5) -> ExecutionResult:
        """
        Start a web server and test if it's working
        
        Args:
            file_path: Path to HTML file or directory to serve
            port: Port to serve on
            test_duration: How long to test the server
            
        Returns:
            ExecutionResult with test results
        """
        file_path = Path(file_path)
        
        if file_path.is_file():
            work_dir = file_path.parent
        else:
            work_dir = file_path
        
        server_process = None
        try:
            # Start HTTP server
            command = f"python3 -m http.server {port}"
            logger.info(f"Starting web server on port {port}")
            
            server_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(work_dir),
                text=True
            )
            
            # Wait a moment for server to start
            time.sleep(2)
            
            # Test if server is responding
            test_command = f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}"
            test_result = self.execute_command(test_command)
            
            # Let server run for test duration
            time.sleep(test_duration)
            
            # Terminate server
            server_process.terminate()
            server_process.wait()
            
            if test_result.success and "200" in test_result.stdout:
                return ExecutionResult(
                    success=True,
                    stdout=f"Web server started successfully on port {port}",
                    execution_time=test_duration + 2
                )
            else:
                return ExecutionResult(
                    success=False,
                    stderr=f"Web server failed to respond properly: {test_result.stdout}",
                    execution_time=test_duration + 2
                )
                
        except Exception as e:
            if server_process:
                server_process.terminate()
            
            logger.error(f"Web server test failed: {str(e)}")
            return ExecutionResult(
                success=False,
                stderr=f"Web server test error: {str(e)}",
                return_code=-1
            )
    
    def validate_html(self, file_path: str) -> ExecutionResult:
        """
        Validate HTML file syntax
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            ExecutionResult with validation results
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return ExecutionResult(
                    success=False,
                    stderr=f"HTML file not found: {file_path}"
                )
            
            # Simple HTML validation using Python
            validation_code = f'''
import re
import sys

def validate_html(filepath):
    try:
        with open(r"{file_path}", 'r', encoding='utf-8') as f:
            content = f.read()
        
        errors = []
        
        # Check for basic HTML structure
        if not re.search(r'<!DOCTYPE html>', content, re.IGNORECASE):
            errors.append("Missing DOCTYPE declaration")
        
        if not re.search(r'<html.*?>', content, re.IGNORECASE):
            errors.append("Missing HTML tag")
        
        if not re.search(r'<head.*?>', content, re.IGNORECASE):
            errors.append("Missing HEAD tag")
        
        if not re.search(r'<body.*?>', content, re.IGNORECASE):
            errors.append("Missing BODY tag")
        
        # Check for unclosed tags (basic check)
        tags = re.findall(r'<(/?)(\w+)(?:[^>]*?)/?>', content)
        tag_stack = []
        
        for is_closing, tag_name in tags:
            tag_name = tag_name.lower()
            if tag_name in ['meta', 'link', 'br', 'hr', 'img', 'input']:
                continue  # Self-closing tags
                
            if is_closing == '/':
                if tag_stack and tag_stack[-1] == tag_name:
                    tag_stack.pop()
                else:
                    errors.append(f"Mismatched closing tag: {tag_name}")
            else:
                tag_stack.append(tag_name)
        
        if tag_stack:
            errors.append(f"Unclosed tags: {{', '.join(tag_stack)}}")
        
        if errors:
            print("HTML Validation Errors:")
            for error in errors:
                print(f"  - {{error}}")
            sys.exit(1)
        else:
            print("HTML validation passed")
            sys.exit(0)
            
    except Exception as e:
        print(f"Validation error: {{str(e)}}")
        sys.exit(1)

validate_html(r"{file_path}")
'''
            
            return self.execute_python_code(validation_code, "html_validator.py")
            
        except Exception as e:
            logger.error(f"HTML validation failed: {str(e)}")
            return ExecutionResult(
                success=False,
                stderr=f"HTML validation error: {str(e)}",
                return_code=-1
            )
    
    def run_tests(self, test_directory: str, test_framework: str = "pytest") -> ExecutionResult:
        """
        Run tests in a directory
        
        Args:
            test_directory: Directory containing tests
            test_framework: Test framework to use (pytest, jest, etc.)
            
        Returns:
            ExecutionResult with test results
        """
        test_dir = Path(test_directory)
        
        if not test_dir.exists():
            return ExecutionResult(
                success=False,
                stderr=f"Test directory not found: {test_directory}"
            )
        
        if test_framework == "pytest":
            command = "python3 -m pytest -v"
        elif test_framework == "jest":
            command = "npm test"
        else:
            command = test_framework
        
        return self.execute_command(command, working_dir=str(test_dir))
    
    def check_syntax(self, file_path: str, language: str = None) -> ExecutionResult:
        """
        Check syntax of a code file
        
        Args:
            file_path: Path to code file
            language: Programming language (auto-detected if None)
            
        Returns:
            ExecutionResult with syntax check results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ExecutionResult(
                success=False,
                stderr=f"File not found: {file_path}"
            )
        
        # Auto-detect language
        if not language:
            extension = file_path.suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json'
            }
            language = language_map.get(extension, 'unknown')
        
        if language == 'python':
            command = f"python3 -m py_compile {file_path}"
        elif language == 'javascript':
            command = f"node --check {file_path}"
        elif language == 'html':
            return self.validate_html(str(file_path))
        elif language == 'json':
            # JSON syntax check using Python
            check_code = f'''
import json
try:
    with open(r"{file_path}", 'r') as f:
        json.load(f)
    print("JSON syntax is valid")
except json.JSONDecodeError as e:
    print(f"JSON syntax error: {{e}}")
    exit(1)
'''
            return self.execute_python_code(check_code, "json_checker.py")
        else:
            return ExecutionResult(
                success=False,
                stderr=f"Syntax checking not supported for language: {language}"
            )
        
        return self.execute_command(command)