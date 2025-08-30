import subprocess
import sys
import os

def run_script_with_env(args, env):
    script_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    python_executable = os.path.join(os.path.dirname(__file__), '..', '.venv', 'bin', 'python')
    process = subprocess.run([python_executable, script_path] + args, capture_output=True, text=True, env=env)
    return process

def test_short_session_string():
    env = os.environ.copy()
    env["TELEGRAM_STRING_SESSION"] = "short_string"
    process = run_script_with_env(['read', 'some_channel'], env)
    assert "ERROR: Session string appears too short" in process.stderr
    assert process.returncode != 0
