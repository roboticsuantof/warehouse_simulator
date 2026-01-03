"""
Environment package for the Warehouse competition.
"""

from gymnasium.envs.registration import register

__version__ = "0.1.0"
__author__ = 'Angel Ayala'


register(
    id='envs/WarehouseEnv-v0',
    entry_point='envs:WarehouseEnvContinuous',
)

