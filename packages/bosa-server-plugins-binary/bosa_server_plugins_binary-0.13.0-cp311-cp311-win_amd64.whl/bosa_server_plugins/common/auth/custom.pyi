from bosa_server_plugins.common.auth.auth import PluginAuthenticationScheme as PluginAuthenticationScheme
from typing import Any, Literal

class CustomAuthenticationScheme(PluginAuthenticationScheme):
    """Custom authentication scheme."""
    type: Literal['custom']
    config: dict[str, Any]
