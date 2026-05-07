import pytest
import copy
from src.app import app, activities


# Store the initial state of activities
_initial_activities = copy.deepcopy(activities)


@pytest.fixture(scope="function")
def reset_activities():
    """Reset the activities dict to its initial state before each test."""
    # Setup: Deep copy the initial state back into the global activities dict
    activities.clear()
    activities.update(copy.deepcopy(_initial_activities))
    yield
    # Teardown: Clean up after test
    activities.clear()
    activities.update(copy.deepcopy(_initial_activities))
