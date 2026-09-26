import os
from pathlib import Path
from typing import List, Dict, Any

class RepoLoader:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        # Faltu build directories aur hidden folders ignore karein
        self.ignored_dirs = {'.git', 'target', 'node_modules', 'build', '.idea', '.mvn', 'bin', 'out'}
        # Sirf source code aur configuration files process karein
        self.allowed_extensions = {
            '.java', '.py', '.js', '.ts',
            '.md', '.yml', '.yaml', '.xml', '.json'
        }
        self.max_file_size = 1 * 1024 * 1024  # 1MB safety limit per file

    def load_repository_files(self) -> List[Dict[str, Any]]:
        """
        Recursively walks the repository, filtering out ignored directories,
        and reads the content of allowed files.
        """
        if not self.repo_path.exists() or not self.repo_path.is_dir():
            raise FileNotFoundError(f"Repository path does not exist: {self.repo_path}")

        collected_files = []

        for root, dirs, files in os.walk(self.repo_path):
            # os.walk ko modify karein taaki wo ignored_dirs ke andar na jaye (Performance boost)
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]

            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()

                if ext in self.allowed_extensions:
                    # Skip files larger than 1MB to prevent memory exhaustion
                    if file_path.stat().st_size > self.max_file_size:
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Qdrant metadata ke liye relative path zaroori hai
                        relative_path = str(file_path.relative_to(self.repo_path))

                        collected_files.append({
                            "file_path": relative_path,
                            "extension": ext,
                            "content": content
                        })
                    except Exception as e:
                        print(f"Warning: Failed to read {file_path}. Reason: {e}")

        return collected_files