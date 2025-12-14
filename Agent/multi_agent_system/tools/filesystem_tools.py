"""
Filesystem tools for file operations in Multi-Agent Collaborative System
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FileSystemTools:
    """Tools for filesystem operations"""
    
    def __init__(self, base_directory: str = "./output"):
        """
        Initialize filesystem tools
        
        Args:
            base_directory: Base directory for all file operations
        """
        self.base_directory = Path(base_directory).resolve()
        self.ensure_directory_exists(self.base_directory)
        logger.info(f"FileSystemTools initialized with base directory: {self.base_directory}")
    
    def ensure_directory_exists(self, directory_path: Path) -> bool:
        """
        Ensure a directory exists, creating it if necessary
        
        Args:
            directory_path: Path to the directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory_path}: {str(e)}")
            return False
    
    def create_file(self, filename: str, content: str, subdirectory: str = None) -> bool:
        """
        Create a file with the given content
        
        Args:
            filename: Name of the file to create
            content: Content to write to the file
            subdirectory: Optional subdirectory within base directory
            
        Returns:
            True if file was created successfully
        """
        try:
            if subdirectory:
                file_path = self.base_directory / subdirectory / filename
            else:
                file_path = self.base_directory / filename
            
            # Ensure parent directory exists
            self.ensure_directory_exists(file_path.parent)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create file {filename}: {str(e)}")
            return False
    
    def write_to_file(self, filename: str, content: str, mode: str = 'w', subdirectory: str = None) -> bool:
        """
        Write content to a file (append or overwrite)
        
        Args:
            filename: Name of the file
            content: Content to write
            mode: Write mode ('w' for overwrite, 'a' for append)
            subdirectory: Optional subdirectory
            
        Returns:
            True if write was successful
        """
        try:
            if subdirectory:
                file_path = self.base_directory / subdirectory / filename
            else:
                file_path = self.base_directory / filename
            
            # Ensure parent directory exists
            self.ensure_directory_exists(file_path.parent)
            
            # Ensure Python files end with newline to prevent EOF syntax errors
            if filename.endswith('.py') and content and not content.endswith('\n'):
                content = content + '\n'
                logger.info(f"Added missing newline to Python file: {filename}")
            
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote to file: {file_path} (mode: {mode})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write to file {filename}: {str(e)}")
            return False
    
    def read_file(self, filename: str, subdirectory: str = None) -> Optional[str]:
        """
        Read content from a file
        
        Args:
            filename: Name of the file to read
            subdirectory: Optional subdirectory
            
        Returns:
            File content as string, or None if failed
        """
        try:
            if subdirectory:
                file_path = self.base_directory / subdirectory / filename
            else:
                file_path = self.base_directory / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {filename}: {str(e)}")
            return None
    
    def list_files(self, subdirectory: str = None, pattern: str = "*") -> List[str]:
        """
        List files in a directory
        
        Args:
            subdirectory: Optional subdirectory to list
            pattern: Glob pattern to match files
            
        Returns:
            List of filenames
        """
        try:
            if subdirectory:
                directory_path = self.base_directory / subdirectory
            else:
                directory_path = self.base_directory
            
            if not directory_path.exists():
                logger.warning(f"Directory does not exist: {directory_path}")
                return []
            
            files = [f.name for f in directory_path.glob(pattern) if f.is_file()]
            logger.info(f"Listed {len(files)} files in {directory_path}")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            return []
    
    def list_directories(self, subdirectory: str = None) -> List[str]:
        """
        List subdirectories
        
        Args:
            subdirectory: Optional subdirectory to list
            
        Returns:
            List of directory names
        """
        try:
            if subdirectory:
                directory_path = self.base_directory / subdirectory
            else:
                directory_path = self.base_directory
            
            if not directory_path.exists():
                logger.warning(f"Directory does not exist: {directory_path}")
                return []
            
            directories = [d.name for d in directory_path.iterdir() if d.is_dir()]
            logger.info(f"Listed {len(directories)} directories in {directory_path}")
            return directories
            
        except Exception as e:
            logger.error(f"Failed to list directories: {str(e)}")
            return []
    
    def file_exists(self, filename: str, subdirectory: str = None) -> bool:
        """
        Check if a file exists
        
        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory
            
        Returns:
            True if file exists
        """
        try:
            if subdirectory:
                file_path = self.base_directory / subdirectory / filename
            else:
                file_path = self.base_directory / filename
            
            exists = file_path.exists() and file_path.is_file()
            logger.debug(f"File exists check: {file_path} -> {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Failed to check if file exists {filename}: {str(e)}")
            return False
    
    def delete_file(self, filename: str, subdirectory: str = None) -> bool:
        """
        Delete a file
        
        Args:
            filename: Name of the file to delete
            subdirectory: Optional subdirectory
            
        Returns:
            True if file was deleted successfully
        """
        try:
            if subdirectory:
                file_path = self.base_directory / subdirectory / filename
            else:
                file_path = self.base_directory / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {str(e)}")
            return False
    
    def create_project_structure(self, project_name: str, structure: Dict[str, Any]) -> bool:
        """
        Create a project directory structure
        
        Args:
            project_name: Name of the project directory
            structure: Dictionary describing the directory structure
            
        Returns:
            True if structure was created successfully
        """
        try:
            project_path = self.base_directory / project_name
            
            def create_structure_recursive(current_path: Path, structure_dict: Dict[str, Any]):
                for name, content in structure_dict.items():
                    item_path = current_path / name
                    
                    if isinstance(content, dict):
                        # It's a directory
                        self.ensure_directory_exists(item_path)
                        create_structure_recursive(item_path, content)
                    elif isinstance(content, str):
                        # It's a file
                        self.ensure_directory_exists(item_path.parent)
                        with open(item_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"Created file in structure: {item_path}")
            
            create_structure_recursive(project_path, structure)
            logger.info(f"Created project structure: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create project structure: {str(e)}")
            return False
    
    def save_project_metadata(self, project_name: str, metadata: Dict[str, Any]) -> bool:
        """
        Save project metadata to a JSON file
        
        Args:
            project_name: Name of the project
            metadata: Metadata dictionary to save
            
        Returns:
            True if metadata was saved successfully
        """
        try:
            metadata_file = f"{project_name}_metadata.json"
            metadata_path = self.base_directory / metadata_file
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Saved project metadata: {metadata_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project metadata: {str(e)}")
            return False
    
    def load_project_metadata(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Load project metadata from a JSON file
        
        Args:
            project_name: Name of the project
            
        Returns:
            Metadata dictionary or None if failed
        """
        try:
            metadata_file = f"{project_name}_metadata.json"
            metadata_path = self.base_directory / metadata_file
            
            if not metadata_path.exists():
                logger.warning(f"Metadata file not found: {metadata_path}")
                return None
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"Loaded project metadata: {metadata_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load project metadata: {str(e)}")
            return None
    
    def get_file_info(self, filename: str, subdirectory: str = None) -> Optional[Dict[str, Any]]:
        """
        Get file information (size, modification time, etc.)
        
        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory
            
        Returns:
            Dictionary with file information or None if failed
        """
        try:
            if subdirectory:
                file_path = self.base_directory / subdirectory / filename
            else:
                file_path = self.base_directory / filename
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            stat = file_path.stat()
            
            info = {
                "filename": filename,
                "full_path": str(file_path),
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir()
            }
            
            logger.debug(f"Got file info: {filename}")
            return info
            
        except Exception as e:
            logger.error(f"Failed to get file info for {filename}: {str(e)}")
            return None
    
    def cleanup_empty_directories(self, subdirectory: str = None) -> int:
        """
        Remove empty directories recursively
        
        Args:
            subdirectory: Optional subdirectory to clean
            
        Returns:
            Number of directories removed
        """
        try:
            if subdirectory:
                start_path = self.base_directory / subdirectory
            else:
                start_path = self.base_directory
            
            removed_count = 0
            
            # Walk the directory tree from bottom up
            for dirpath, dirnames, filenames in os.walk(start_path, topdown=False):
                if not dirnames and not filenames:
                    # Directory is empty
                    try:
                        os.rmdir(dirpath)
                        removed_count += 1
                        logger.info(f"Removed empty directory: {dirpath}")
                    except OSError:
                        # Directory might not be empty or other issues
                        pass
            
            logger.info(f"Cleaned up {removed_count} empty directories")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup empty directories: {str(e)}")
            return 0

class WebSearchTool:
    """Simulated web search tool for demonstration"""
    
    def __init__(self):
        self.search_results_cache = {}
        logger.info("WebSearchTool initialized (simulated)")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Simulate web search
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search result dictionaries
        """
        # This is a simulation - in a real implementation, you would
        # integrate with actual search APIs like Google Custom Search,
        # Bing Search API, or other search services
        
        logger.info(f"Simulated web search: {query}")
        
        if query in self.search_results_cache:
            return self.search_results_cache[query][:max_results]
        
        # Simulated results for common programming topics
        simulated_results = [
            {
                "title": f"Documentation for {query}",
                "url": f"https://docs.example.com/{query.replace(' ', '-')}",
                "description": f"Official documentation and guides for {query}"
            },
            {
                "title": f"{query} Tutorial",
                "url": f"https://tutorial.example.com/{query.replace(' ', '-')}",
                "description": f"Step-by-step tutorial for {query}"
            },
            {
                "title": f"{query} Examples",
                "url": f"https://examples.example.com/{query.replace(' ', '-')}",
                "description": f"Code examples and implementations for {query}"
            }
        ]
        
        self.search_results_cache[query] = simulated_results
        return simulated_results[:max_results]