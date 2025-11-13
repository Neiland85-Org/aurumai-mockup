"""
Asset Entity - Generic asset (alias for Machine for now)

In the future, this could represent a broader concept including
production lines, systems, or logical groupings of machines.
"""

from .machine import Machine

# For now, Asset is an alias for Machine
# This provides flexibility for future domain expansion
Asset = Machine
