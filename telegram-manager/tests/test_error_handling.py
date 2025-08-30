import subprocess
import sys
import os

def run_script(args):
    script_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    python_executable = os.path.join(os.path.dirname(__file__), '..', '.venv', 'bin', 'python')
    process = subprocess.run([python_executable, script_path] + args, capture_output=True, text=True)
    return process

def test_read_non_existent_channel():
    process = run_script(['read', 'non_existent_channel_for_sure'])
    assert "ERROR: Failed to read from non_existent_channel_for_sure" in process.stderr
    assert process.returncode != 0
