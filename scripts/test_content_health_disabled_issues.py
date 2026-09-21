"""Exercise the real workflow shell with the repository Issues feature disabled."""
import os
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def test_disabled_issues_keeps_report_without_calling_issue_api(tmp_path):
    workflow = yaml.safe_load((ROOT / '.github/workflows/content-health.yml').read_text())
    step = next(s for s in workflow['jobs']['scan']['steps']
                if s.get('name') == 'Update the single tracking issue')
    gh = tmp_path / 'gh'
    gh.write_text('#!/bin/sh\nif [ "$1" = api ]; then echo false; exit 0; fi\necho "unexpected issue API call" >&2\nexit 99\n')
    gh.chmod(0o755)
    result = subprocess.run(['bash', '-e', '-c', step['run']], text=True, capture_output=True,
                            env={**os.environ, 'PATH': f'{tmp_path}:' + os.environ['PATH'],
                                 'REPOSITORY': 'example/repo', 'MODE': 'weekly'})
    assert result.returncode == 0, result.stderr
    assert 'Issues are disabled' in result.stdout
    # Skipping notification must never disable the actual failure gate.
    final = next(s for s in workflow['jobs']['scan']['steps']
                 if s.get('name') == 'Fail only on hard findings')
    failed = subprocess.run(['bash', '-e', '-c', final['run']],
                            env={**os.environ, 'SUMMARY_EXIT': '1'})
    assert failed.returncode != 0
