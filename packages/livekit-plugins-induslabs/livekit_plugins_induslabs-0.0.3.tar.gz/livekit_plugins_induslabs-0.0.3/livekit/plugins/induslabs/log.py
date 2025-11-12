"""Logging utilities for the IndusLabs plugin.

This module exposes a module-level :data:`logger` instance that is used
throughout the TTS and STT implementations.  Having a dedicated logger
allows users to configure log levels for this plugin independently of
other parts of their application.
"""

import logging

#: Logger for the IndusLabs plugin
logger = logging.getLogger(__name__)
