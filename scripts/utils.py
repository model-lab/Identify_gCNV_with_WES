"""Reusable helper utilities for workflow scripts.

Provides simple helpers for running commands, ensuring directories, and I/O.
"""
import os
import json
import subprocess
from typing import Sequence


def ensure_parent_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def run_cmd(cmd: Sequence[str], check: bool = True) -> int:
    print('RUN:', ' '.join(cmd))
    try:
        return subprocess.check_call(list(cmd))
    except subprocess.CalledProcessError as e:
        print('Command failed with exit', e.returncode)
        if check:
            raise
        return e.returncode


def write_json(path: str, data) -> None:
    ensure_parent_dir(path)
    with open(path, 'w') as fh:
        json.dump(data, fh)


def read_json(path: str):
    with open(path) as fh:
        return json.load(fh)


def write_text(path: str, text: str) -> None:
    ensure_parent_dir(path)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
