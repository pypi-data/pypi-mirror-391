"""Tools package initialization.

This module exports the API instance and tool initialization functions
to avoid circular import issues.
"""

from kaggle_mcp.tools.auth import init_auth_tools, api, ensure_authenticated
from kaggle_mcp.tools.competitions import init_competition_tools
from kaggle_mcp.tools.datasets import init_dataset_tools
from kaggle_mcp.tools.kernels import init_kernel_tools
from kaggle_mcp.tools.models import init_model_tools
from kaggle_mcp.tools.config import init_config_tools

__all__ = [
    'init_auth_tools',
    'init_competition_tools',
    'init_dataset_tools',
    'init_kernel_tools',
    'init_model_tools',
    'init_config_tools',
    'api',
    'ensure_authenticated',
]
