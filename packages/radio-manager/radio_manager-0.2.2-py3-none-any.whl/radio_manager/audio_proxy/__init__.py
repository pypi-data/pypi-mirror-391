"""
Audio proxy for streaming scanner audio over HTTP.

This module provides an HTTP audio proxy that converts the Uniden scanner's
non-standard RTSP stream to a standard HTTP/WAV stream that works in web
browsers and Home Assistant.
"""

from .proxy import AudioProxyServer, start_audio_proxy

__all__ = ['AudioProxyServer', 'start_audio_proxy']
