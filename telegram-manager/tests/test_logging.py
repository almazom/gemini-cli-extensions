import subprocess
import sys
import os

def run_script(args):
    script_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
    python_executable = os.path.join(os.path.dirname(__file__), '..', '.venv', 'bin', 'python')
    process = subprocess.run([python_executable, script_path] + args, capture_output=True, text=True)
    return process

def test_logging():
    log_file = os.path.join(os.path.dirname(__file__), '..', 'telegram_manager.log')
    if os.path.exists(log_file):
        os.remove(log_file)

    process = run_script(['read', '@Bloomberg', '1'])
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        log_content = f.read()
    assert "Connecting to Telegram" in log_content
