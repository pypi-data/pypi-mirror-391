"""Code scanner for finding strayl:doc annotations."""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import ast


class ApiCall:
    """Represents an API call found in code."""

    def __init__(
        self,
        doc_url: str,
        file_path: str,
        line_number: int,
        method: Optional[str] = None,
        endpoint: Optional[str] = None,
        code_snippet: Optional[str] = None,
    ):
        self.doc_url = doc_url
        self.file_path = file_path
        self.line_number = line_number
        self.method = method
        self.endpoint = endpoint
        self.code_snippet = code_snippet

    def to_dict(self) -> Dict:
        """Convert to dictionary for API request."""
        return {
            "doc": self.doc_url,
            "file": self.file_path,
            "line": self.line_number,
            "method": self.method,
            "endpoint": self.endpoint,
            "code": self.code_snippet,
        }


class CodeScanner:
    """Scans code for strayl:doc annotations."""

    # Patterns for finding annotations
    ANNOTATION_PATTERN = re.compile(
        r'(?:#|//)\s*strayl:doc\s+(https?://[^\s]+)',
        re.IGNORECASE
    )

    # Common HTTP methods to look for
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def scan(self, extensions: List[str] = None) -> List[ApiCall]:
        """
        Scan directory for strayl:doc annotations.

        Args:
            extensions: List of file extensions to scan (e.g., ['.py', '.js'])
                       If None, scans common extensions.

        Returns:
            List of ApiCall objects found
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.java', '.rb', '.php']

        calls = []

        for ext in extensions:
            for file_path in self.root_dir.rglob(f'*{ext}'):
                # Skip common ignore patterns
                if self._should_skip(file_path):
                    continue

                try:
                    calls.extend(self._scan_file(file_path))
                except Exception as e:
                    print(f"Warning: Failed to scan {file_path}: {e}")

        return calls

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            'node_modules',
            '.git',
            '__pycache__',
            'venv',
            'env',
            'dist',
            'build',
            '.next',
            'coverage',
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _scan_file(self, file_path: Path) -> List[ApiCall]:
        """Scan a single file for annotations."""
        calls = []

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, start=1):
            match = self.ANNOTATION_PATTERN.search(line)
            if match:
                doc_url = match.group(1)

                # Try to extract API call details from following lines
                method, endpoint, code = self._extract_api_call(lines, i)

                call = ApiCall(
                    doc_url=doc_url,
                    file_path=str(file_path.relative_to(self.root_dir)),
                    line_number=i,
                    method=method,
                    endpoint=endpoint,
                    code_snippet=code,
                )
                calls.append(call)

        return calls

    def _extract_api_call(
        self,
        lines: List[str],
        annotation_line: int
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Try to extract HTTP method, endpoint, and code snippet.

        Args:
            lines: All lines from the file
            annotation_line: Line number where annotation was found (1-indexed)

        Returns:
            Tuple of (method, endpoint, code_snippet)
        """
        # Look at next few lines for API call
        method = None
        endpoint = None
        code_lines = []

        start_idx = annotation_line  # Already 1-indexed, so this is correct
        end_idx = min(start_idx + 10, len(lines))

        for i in range(start_idx, end_idx):
            line = lines[i]
            code_lines.append(line.rstrip())

            # Look for HTTP methods (be more specific to avoid false positives like "headers" matching "HEAD")
            for http_method in self.HTTP_METHODS:
                # Check for requests.method() pattern
                if re.search(rf'\brequests\.{http_method.lower()}\s*\(', line, re.IGNORECASE):
                    method = http_method
                    break
                # Check for method="METHOD" or method: "METHOD" pattern
                if re.search(rf'\bmethod\s*[:=]\s*["\']?{http_method}["\']?', line, re.IGNORECASE):
                    method = http_method
                    break

            # Try to extract URL/endpoint
            # Look for common patterns: requests.post(url), fetch(url), etc.
            # Match either full URLs (https://...) or paths starting with /
            url_match = re.search(r'["\']((https?://[^"\']+)|(/[^"\'\s]+))["\']', line)
            if url_match:
                endpoint = url_match.group(1)

            # Stop after finding meaningful code (non-empty, non-comment)
            if line.strip() and not line.strip().startswith(('#', '//')):
                if i - start_idx >= 2:  # Got at least a couple lines
                    break

        code_snippet = '\n'.join(code_lines[:5]) if code_lines else None

        return method, endpoint, code_snippet
