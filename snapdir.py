# MIT License
# 
# Copyright (c) 2025 Paul Tiffany
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#!/usr/bin/env python3
"""
Enhanced Directory Snapshot Tool for AI Coding Assistants

A powerful tool to create structured snapshots of directory trees optimized for
AI coding assistants like Claude Code, OpenAI Codex, and Google CLI.

Features:
- Smart binary file detection and handling
- Configurable size limits and depth controls
- Progress tracking for large operations
- Symlink detection and handling
- Token counting for AI context optimization
- Multiple output formats (JSON, markdown, XML)
- Configuration file support
- Comprehensive filtering options
- Project structure analysis
"""

import os
import json
import argparse
import re
import sys
import hashlib
import mimetypes
import configparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import time

# Initialize mimetypes
mimetypes.init()

@dataclass
class FileMetadata:
    """Metadata for a file entry."""
    name: str
    type: str
    path: str
    size: int
    modified_time: str
    encoding: Optional[str] = None
    mime_type: Optional[str] = None
    hash_sha256: Optional[str] = None
    lines: Optional[int] = None
    tokens_estimate: Optional[int] = None

@dataclass
class DirectoryStats:
    """Statistics for the directory snapshot."""
    total_files: int = 0
    total_directories: int = 0
    total_size: int = 0
    text_files: int = 0
    binary_files: int = 0
    symlinks: int = 0
    errors: int = 0
    estimated_tokens: int = 0

class ProgressTracker:
    """Thread-safe progress tracker for large operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.last_update = 0
        
    def update(self, increment: int = 1):
        with self.lock:
            self.current += increment
            now = time.time()
            # Update every 0.5 seconds or on completion
            if now - self.last_update > 0.5 or self.current >= self.total:
                self.last_update = now
                elapsed = now - self.start_time
                if self.current > 0:
                    eta = (elapsed / self.current) * (self.total - self.current)
                    percentage = (self.current / self.total) * 100
                    print(f"\r{self.description}: {self.current}/{self.total} ({percentage:.1f}%) - ETA: {eta:.1f}s", 
                          end='', flush=True)
                    
    def complete(self):
        elapsed = time.time() - self.start_time
        print(f"\r{self.description}: {self.current}/{self.total} (100%) - Completed in {elapsed:.1f}s")

class EnhancedSnapdir:
    """Enhanced directory snapshot tool optimized for AI coding assistants."""
    
    # Enhanced default exclusions with AI-specific patterns
    DEFAULT_EXCLUDE_DIRS = {
        "__pycache__", ".pytest_cache", "venv", ".venv", "env", ".env",
        ".git", ".svn", ".hg", ".bzr",
        "node_modules", "bower_components", ".npm", ".yarn",
        "dist", "build", "out", "target", "bin", "obj",
        ".idea", ".vscode", ".vs", ".settings",
        "pylantern.egg-info", "*.egg-info",
        "SRV", "tmp", "temp", ".tmp", ".temp",
        ".DS_Store", "Thumbs.db",
        ".cache", ".mypy_cache", ".coverage",
        "logs", "log", "*.log"
    }
    
    DEFAULT_EXCLUDE_FILES = {
        ".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib",
        ".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm",
        ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".ico",
        ".mp3", ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".db", ".sqlite", ".sqlite3",
        ".lock", ".pid", ".tmp", ".temp", ".bak", ".orig", ".swp",
        ".DS_Store", "Thumbs.db", "desktop.ini"
    }
    
    # AI-friendly file extensions (prioritized for inclusion)
    AI_FRIENDLY_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".cc", ".cxx",
        ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
        ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
        ".xml", ".md", ".rst", ".txt", ".log",
        ".sql", ".graphql", ".proto", ".thrift",
        ".dockerfile", ".dockerignore", ".gitignore", ".gitattributes",
        ".makefile", ".cmake", ".gradle", ".maven", ".sbt"
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.stats = DirectoryStats()
        
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file if provided."""
        default_config = {
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'max_depth': 50,
            'max_tokens_per_file': 100000,
            'show_progress': True,
            'include_hash': False,
            'include_token_count': True,
            'binary_detection_bytes': 8192,
            'follow_symlinks': False,
            'ai_optimized': True
        }
        
        if not config_file or not os.path.exists(config_file):
            return default_config
            
        try:
            parser = configparser.ConfigParser()
            parser.read(config_file)
            
            if 'snapdir' in parser:
                section = parser['snapdir']
                for key, value in section.items():
                    if key in default_config:
                        # Convert to appropriate type
                        if isinstance(default_config[key], bool):
                            default_config[key] = section.getboolean(key)
                        elif isinstance(default_config[key], int):
                            default_config[key] = section.getint(key)
                        else:
                            default_config[key] = value
                            
        except Exception as e:
            print(f"Warning: Error loading config file: {e}")
            
        return default_config
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Detect if a file is binary by checking for null bytes."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(self.config['binary_detection_bytes'])
                return b'\x00' in chunk
        except Exception:
            return True
    
    def _estimate_tokens(self, content: str) -> int:
        """Estimate token count for AI context planning."""
        # Rough estimation: ~4 characters per token for code
        # This is a heuristic, actual tokenization depends on the model
        return len(content) // 4
    
    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA256 hash of file content."""
        if not self.config['include_hash']:
            return None
            
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def _should_include_path(self, path: str, include_pattern: Optional[re.Pattern], 
                           exclude_pattern: Optional[re.Pattern]) -> bool:
        """Determine if a path should be included based on patterns."""
        # Apply exclusion pattern first
        if exclude_pattern and exclude_pattern.search(path):
            return False
            
        # Apply inclusion pattern
        if include_pattern and not include_pattern.search(path):
            return False
            
        return True
    
    def _count_files_recursive(self, root_path: str, include_pattern: Optional[re.Pattern], 
                              exclude_pattern: Optional[re.Pattern]) -> int:
        """Count total files for progress tracking."""
        count = 0
        try:
            for root, dirs, files in os.walk(root_path, followlinks=self.config['follow_symlinks']):
                # Filter directories in-place
                dirs[:] = [d for d in dirs if not any(d.startswith(pattern.rstrip('*')) 
                          for pattern in self.DEFAULT_EXCLUDE_DIRS)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, start=os.path.dirname(root_path))
                    
                    if self._should_include_path(rel_path, include_pattern, exclude_pattern):
                        count += 1
                        
        except Exception as e:
            print(f"Warning: Error counting files: {e}")
            
        return count
    
    def _process_file(self, file_path: str, relative_path: str) -> Dict:
        """Process a single file and return its metadata and content."""
        try:
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            
            # Skip files that are too large
            if file_size > self.config['max_file_size']:
                self.stats.errors += 1
                return {
                    "name": os.path.basename(file_path),
                    "type": "file",
                    "path": relative_path,
                    "size": file_size,
                    "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "source": f"[File too large: {file_size:,} bytes, max: {self.config['max_file_size']:,}]",
                    "error": "file_too_large"
                }
            
            # Detect if file is binary
            is_binary = self._is_binary_file(file_path)
            mime_type, encoding = mimetypes.guess_type(file_path)
            
            if is_binary:
                self.stats.binary_files += 1
                return {
                    "name": os.path.basename(file_path),
                    "type": "file",
                    "path": relative_path,
                    "size": file_size,
                    "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "mime_type": mime_type,
                    "source": "[Binary file - content not included]",
                    "is_binary": True,
                    "hash_sha256": self._get_file_hash(file_path)
                }
            
            # Read text file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                # Estimate tokens and line count
                lines = content.count('\n') + 1 if content else 0
                tokens = self._estimate_tokens(content) if self.config['include_token_count'] else None
                
                # Skip files with too many tokens for AI context
                if tokens and tokens > self.config['max_tokens_per_file']:
                    content = f"[File too large for AI context: ~{tokens:,} tokens, max: {self.config['max_tokens_per_file']:,}]"
                    
                self.stats.text_files += 1
                if tokens:
                    self.stats.estimated_tokens += tokens
                
                file_data = {
                    "name": os.path.basename(file_path),
                    "type": "file",
                    "path": relative_path,
                    "size": file_size,
                    "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "mime_type": mime_type,
                    "encoding": encoding,
                    "lines": lines,
                    "source": content,
                    "is_binary": False
                }
                
                if tokens:
                    file_data["tokens_estimate"] = tokens
                    
                if self.config['include_hash']:
                    file_data["hash_sha256"] = self._get_file_hash(file_path)
                
                return file_data
                
            except Exception as e:
                self.stats.errors += 1
                return {
                    "name": os.path.basename(file_path),
                    "type": "file",
                    "path": relative_path,
                    "size": file_size,
                    "modified_time": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    "source": f"[Error reading file: {str(e)}]",
                    "error": str(e)
                }
                
        except Exception as e:
            self.stats.errors += 1
            return {
                "name": os.path.basename(file_path),
                "type": "file",
                "path": relative_path,
                "source": f"[Error accessing file: {str(e)}]",
                "error": str(e)
            }
    
    def build_tree(self, root_path: str, include_regex: Optional[str] = None, 
                   exclude_regex: Optional[str] = None, current_depth: int = 0) -> Dict:
        """Build a comprehensive directory tree snapshot."""
        
        # Check depth limit
        if current_depth > self.config['max_depth']:
            return {
                "name": os.path.basename(root_path),
                "type": "directory",
                "path": os.path.relpath(root_path, start=os.path.dirname(root_path)),
                "error": f"Max depth exceeded ({self.config['max_depth']})"
            }
        
        # Compile regex patterns
        include_pattern = re.compile(include_regex) if include_regex else None
        exclude_pattern = re.compile(exclude_regex) if exclude_regex else None
        
        tree = {
            "name": os.path.basename(root_path),
            "type": "directory",
            "path": os.path.relpath(root_path, start=os.path.dirname(root_path)),
            "children": []
        }
        
        try:
            items = sorted(os.listdir(root_path))
            
            for item_name in items:
                item_path = os.path.join(root_path, item_name)
                relative_path = os.path.relpath(item_path, start=os.path.dirname(root_path))
                
                # Handle symlinks
                if os.path.islink(item_path):
                    self.stats.symlinks += 1
                    if not self.config['follow_symlinks']:
                        continue
                
                # Apply default exclusions
                if os.path.isdir(item_path):
                    if any(item_name.startswith(pattern.rstrip('*')) 
                          for pattern in self.DEFAULT_EXCLUDE_DIRS):
                        continue
                else:
                    if any(item_name.endswith(ext) for ext in self.DEFAULT_EXCLUDE_FILES):
                        continue
                
                # Apply regex filters
                if not self._should_include_path(relative_path, include_pattern, exclude_pattern):
                    continue
                
                if os.path.isdir(item_path):
                    self.stats.total_directories += 1
                    subtree = self.build_tree(item_path, include_regex, exclude_regex, current_depth + 1)
                    tree["children"].append(subtree)
                    
                elif os.path.isfile(item_path):
                    self.stats.total_files += 1
                    file_data = self._process_file(item_path, relative_path)
                    tree["children"].append(file_data)
                    
                    # Update progress if enabled
                    if hasattr(self, 'progress') and self.progress:
                        self.progress.update()
                        
        except Exception as e:
            print(f"Error processing directory {root_path}: {e}")
            tree["error"] = str(e)
            self.stats.errors += 1
            
        return tree
    
    def generate_snapshot(self, root_path: str, include_regex: Optional[str] = None, 
                         exclude_regex: Optional[str] = None) -> Dict:
        """Generate a complete snapshot with metadata and statistics."""
        
        if not os.path.isdir(root_path):
            raise ValueError(f"Root path '{root_path}' is not a valid directory")
        
        # Initialize progress tracking
        if self.config['show_progress']:
            include_pattern = re.compile(include_regex) if include_regex else None
            exclude_pattern = re.compile(exclude_regex) if exclude_regex else None
            total_files = self._count_files_recursive(root_path, include_pattern, exclude_pattern)
            
            if total_files > 0:
                self.progress = ProgressTracker(total_files, "Processing files")
            else:
                self.progress = None
        else:
            self.progress = None
        
        # Build the tree
        tree = self.build_tree(root_path, include_regex, exclude_regex)
        
        # Complete progress tracking
        if self.progress:
            self.progress.complete()
            print()  # New line after progress
        
        # Generate comprehensive snapshot
        snapshot = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "root_path": os.path.abspath(root_path),
                "tool_version": "2.0.0",
                "config": self.config,
                "filters": {
                    "include_regex": include_regex,
                    "exclude_regex": exclude_regex
                }
            },
            "statistics": asdict(self.stats),
            "tree": tree
        }
        
        return snapshot
    
    def export_markdown(self, snapshot: Dict) -> str:
        """Export snapshot as markdown format for AI assistants."""
        md = []
        md.append("# Directory Snapshot")
        md.append(f"Generated: {snapshot['metadata']['generated_at']}")
        md.append(f"Root: `{snapshot['metadata']['root_path']}`")
        md.append('')
        
        # Statistics
        stats = snapshot['statistics']
        md.append("## Statistics")
        md.append(f"- **Files**: {stats['total_files']:,} ({stats['text_files']:,} text, {stats['binary_files']:,} binary)")
        md.append(f"- **Directories**: {stats['total_directories']:,}")
        md.append(f"- **Total Size**: {stats['total_size']:,} bytes")
        md.append(f"- **Estimated Tokens**: {stats['estimated_tokens']:,}")
        if stats['errors'] > 0:
            md.append(f"- **Errors**: {stats['errors']}")
        md.append('')
        
        # File tree
        md.append("## File Tree")
        md.append("```")
        md.extend(self._tree_to_text(snapshot['tree']))
        md.append("```")
        md.append('')
        
        # File contents
        md.append("## File Contents")
        md.extend(self._extract_file_contents_md(snapshot['tree']))
        
        return '\n'.join(md)
    
    def _tree_to_text(self, tree: Dict, prefix: str = "", is_last: bool = True) -> List[str]:
        """Convert tree structure to text representation."""
        lines = []
        
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{tree['name']}")
        
        if tree['type'] == 'directory' and 'children' in tree:
            extension = "    " if is_last else "│   "
            children = tree['children']
            
            for i, child in enumerate(children):
                child_is_last = i == len(children) - 1
                lines.extend(self._tree_to_text(child, prefix + extension, child_is_last))
                
        return lines
    
    def _extract_file_contents_md(self, tree: Dict) -> List[str]:
        """Extract file contents in markdown format."""
        md = []
        
        if tree['type'] == 'file' and 'source' in tree:
            if not tree.get('is_binary', False) and not tree['source'].startswith('['):
                ext = os.path.splitext(tree['name'])[1].lower()
                lang = self._get_language_for_extension(ext)
                
                md.append(f"### {tree['path']}")
                if tree.get('tokens_estimate'):
                    md.append(f"*Estimated tokens: {tree['tokens_estimate']:,}*")
                md.append('')
                md.append(f"```{lang}")
                md.append(tree['source'])
                md.append("```")
                md.append('')
                
        elif tree['type'] == 'directory' and 'children' in tree:
            for child in tree['children']:
                md.extend(self._extract_file_contents_md(child))
                
        return md
    
    def _get_language_for_extension(self, ext: str) -> str:
        """Get language identifier for syntax highlighting."""
        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'jsx', '.tsx': 'tsx', '.java': 'java',
            '.c': 'c', '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.h': 'c', '.hpp': 'cpp', '.cs': 'csharp',
            '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
            '.php': 'php', '.swift': 'swift', '.kt': 'kotlin',
            '.scala': 'scala', '.sh': 'bash', '.bash': 'bash',
            '.zsh': 'zsh', '.fish': 'fish', '.ps1': 'powershell',
            '.html': 'html', '.htm': 'html', '.css': 'css',
            '.scss': 'scss', '.sass': 'sass', '.less': 'less',
            '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
            '.toml': 'toml', '.ini': 'ini', '.cfg': 'ini',
            '.xml': 'xml', '.md': 'markdown', '.sql': 'sql',
            '.dockerfile': 'dockerfile', '.makefile': 'makefile'
        }
        return lang_map.get(ext, 'text')

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced Directory Snapshot Tool for AI Coding Assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic snapshot
  python snapdir.py /path/to/project

  # With filters and custom output
  python snapdir.py /path/to/project -i "\.py$" -e "test_.*" -o snapshot.json -p

  # Generate markdown for AI
  python snapdir.py /path/to/project --format markdown -o README.md

  # Use configuration file
  python snapdir.py /path/to/project --config snapdir.conf

  # AI-optimized snapshot with token limits
  python snapdir.py /path/to/project --max-tokens 50000 --ai-optimized
        """
    )
    
    parser.add_argument("root_path", type=str, help="Root directory to snapshot")
    parser.add_argument("-o", "--output", type=str, help="Output file path")
    parser.add_argument("-p", "--pretty", action="store_true", help="Pretty print JSON output")
    parser.add_argument("-i", "--include", type=str, help="Include regex pattern")
    parser.add_argument("-e", "--exclude", type=str, help="Exclude regex pattern")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", 
                       help="Output format (default: json)")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--max-size", type=int, help="Maximum file size in bytes")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens per file")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress tracking")
    parser.add_argument("--include-hash", action="store_true", help="Include SHA256 hashes")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symbolic links")
    parser.add_argument("--ai-optimized", action="store_true", help="Optimize for AI context")
    
    args = parser.parse_args()
    
    try:
        # Create enhanced snapdir instance
        snapdir = EnhancedSnapdir(args.config)
        
        # Override config with command line arguments
        if args.max_size:
            snapdir.config['max_file_size'] = args.max_size
        if args.max_tokens:
            snapdir.config['max_tokens_per_file'] = args.max_tokens
        if args.no_progress:
            snapdir.config['show_progress'] = False
        if args.include_hash:
            snapdir.config['include_hash'] = True
        if args.follow_symlinks:
            snapdir.config['follow_symlinks'] = True
        if args.ai_optimized:
            snapdir.config['ai_optimized'] = True
        
        # Generate snapshot
        snapshot = snapdir.generate_snapshot(args.root_path, args.include, args.exclude)
        
        # Format output
        if args.format == "markdown":
            output = snapdir.export_markdown(snapshot)
        else:
            if args.pretty:
                output = json.dumps(snapshot, indent=2, ensure_ascii=False)
            else:
                output = json.dumps(snapshot, separators=(',', ':'), ensure_ascii=False)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Snapshot written to '{args.output}'")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
