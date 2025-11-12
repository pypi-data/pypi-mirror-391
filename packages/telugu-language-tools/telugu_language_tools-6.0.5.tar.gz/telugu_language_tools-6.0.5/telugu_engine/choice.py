"""
Simple choice selection module for CLI interaction.
"""

from typing import List, Optional


def choose(options: List[str]) -> Optional[str]:
    """
    Select an option from a list (non-interactive mode).

    For non-interactive environments, returns the first option.
    In interactive environments, this would prompt the user.

    Args:
        options: List of options to choose from

    Returns:
        Selected option or None
    """
    # For now, return first option (non-interactive)
    # In a full implementation, this would use input() to get user choice
    if not options:
        return None

    return options[0]
