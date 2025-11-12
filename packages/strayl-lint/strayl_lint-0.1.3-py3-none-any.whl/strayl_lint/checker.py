"""API checker module - communicates with Strayl Cloud."""

import os
import requests
from typing import List, Dict, Optional
from .scanner import ApiCall


class CheckResult:
    """Result of API check."""

    def __init__(self, doc_url: str, status: str, diffs: List[Dict] = None):
        self.doc_url = doc_url
        self.status = status  # 'ok', 'warning', 'error'
        self.diffs = diffs or []

    def is_ok(self) -> bool:
        """Check if result is OK."""
        return self.status == 'ok'

    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return self.status == 'warning'

    def has_errors(self) -> bool:
        """Check if result has errors."""
        return self.status == 'error'


class ApiChecker:
    """Checks API calls against documentation."""

    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://ougtygyvcgdnytkswier.supabase.co/functions/v1"

    def check(self, calls: List[ApiCall]) -> List[CheckResult]:
        """
        Check API calls against their documentation.

        Args:
            calls: List of ApiCall objects to check

        Returns:
            List of CheckResult objects
        """
        if not calls:
            return []

        # Group calls by documentation URL
        calls_by_doc = {}
        for call in calls:
            if call.doc_url not in calls_by_doc:
                calls_by_doc[call.doc_url] = []
            calls_by_doc[call.doc_url].append(call)

        results = []

        for doc_url, doc_calls in calls_by_doc.items():
            try:
                result = self._check_single_doc(doc_url, doc_calls)
                results.append(result)
            except Exception as e:
                results.append(
                    CheckResult(
                        doc_url=doc_url,
                        status='error',
                        diffs=[{'error': str(e)}]
                    )
                )

        return results

    def _check_single_doc(self, doc_url: str, calls: List[ApiCall]) -> CheckResult:
        """
        Check calls against a single documentation URL.

        Args:
            doc_url: Documentation URL
            calls: List of calls referencing this doc

        Returns:
            CheckResult
        """
        # Prepare payload
        payload = {
            "api_key": self.api_key,
            "doc_url": doc_url,
            "calls": [call.to_dict() for call in calls]
        }

        # Make request to Strayl Cloud (with increased timeout for scraping + AI)
        response = requests.post(
            f"{self.base_url}/watchdog/check",
            json=payload,
            timeout=180  # 3 minutes: scraping (up to 100 pages) + AI processing
        )

        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")

        data = response.json()

        return CheckResult(
            doc_url=doc_url,
            status=data.get('status', 'error'),
            diffs=data.get('diffs', [])
        )

    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        Get API key from environment or config file.

        Returns:
            API key or None if not found
        """
        # Try environment variable first
        api_key = os.getenv('STRAYL_API_KEY')
        if api_key:
            return api_key

        # Try .strayl config file
        config_paths = [
            '.strayl',
            os.path.expanduser('~/.strayl'),
        ]

        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        for line in f:
                            if line.startswith('api_key'):
                                return line.split('=')[1].strip()
                except Exception:
                    continue

        return None
