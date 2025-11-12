"""IndusLabs plugin for LiveKit Agents.

This package exposes classes for text‑to‑speech (TTS) and
speech‑to‑text (STT) powered by the IndusLabs Voice API.  When this
module is imported it automatically registers the plugin with the
LiveKit plugin registry, allowing the framework to discover the
additional providers.

Typical usage::

    from livekit.plugins.induslabs import TTS, STT
    tts = TTS()  # reads INDUSLABS_API_KEY from the environment
    stt = STT()
    session = AgentSession(tts=tts, stt=stt, ...)

"""

from __future__ import annotations

from .tts import TTS
from .stt import STT
from .version import __version__

__all__ = ["STT", "TTS", "__version__"]

# Register this plugin with LiveKit once it is imported.  The Plugin
# base class will keep track of the package name, version and logger.
from livekit.agents import Plugin
from .log import logger


class InduslabsPlugin(Plugin):
    """Internal class used to register the IndusLabs plugin.

    Instances of :class:`~livekit.agents.plugins.Plugin` provide
    metadata about the plugin and are collected by the framework.  The
    plugin is registered when this module is imported.  Users do not
    interact with this class directly.
    """

    def __init__(self) -> None:
        super().__init__(__name__, __version__, __package__ or __name__, logger)


# Register immediately
Plugin.register_plugin(InduslabsPlugin())

# Hide non‑exported symbols from Sphinx autodoc
_module = dir()
NOT_IN_ALL = [m for m in _module if m not in __all__]

__pdoc__ = {}

for n in NOT_IN_ALL:
    __pdoc__[n] = False
