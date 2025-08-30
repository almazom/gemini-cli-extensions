import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import StateMachine

def test_initial_state():
    sm = StateMachine()
    assert sm.get_state() == "UNINITIALIZED"

def test_valid_transition():
    sm = StateMachine()
    sm.transition_to("INITIALIZING")
    assert sm.get_state() == "INITIALIZING"
    sm.transition_to("ACTIVE")
    assert sm.get_state() == "ACTIVE"

def test_invalid_transition():
    sm = StateMachine()
    with pytest.raises(ValueError):
        sm.transition_to("ACTIVE")
