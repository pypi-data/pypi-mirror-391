"""
RTSP/RTP implementation for Uniden scanner audio streaming.

This module provides a custom RTSP client for streaming audio from Uniden scanners.
The scanner's RTSP implementation is non-standard (see docs/uniden/RTSP_QUIRKS.md).
"""

import os
import sys
import socket
import struct
import contextlib
import logging

logger = logging.getLogger(__name__)

# Redirect stderr to suppress ALSA/JACK warnings
# These warnings come from the C library level, so we need to suppress stderr
@contextlib.contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output"""
    stderr_fd = sys.stderr.fileno()
    with os.fdopen(os.dup(stderr_fd), 'w') as old_stderr:
        with open(os.devnull, 'w') as devnull:
            os.dup2(devnull.fileno(), stderr_fd)
        try:
            yield
        finally:
            os.dup2(old_stderr.fileno(), stderr_fd)


# Lazy import of pyaudio - only import when audio is actually used
def _import_pyaudio():
    """Lazy import of pyaudio to avoid requiring it at integration load time."""
    try:
        with suppress_stderr():
            import pyaudio
            return pyaudio
    except ImportError:
        logger.error("pyaudio not available - audio streaming will not work")
        raise RuntimeError(
            "PyAudio is required for audio streaming. "
            "Install with: pip install pyaudio"
        )


RTSP_PORT = 554
RTP_BUFFER_SIZE = 2048

# G.711 u-law decoding table
# This is a standard u-law to linear PCM conversion
ULAW_TO_LINEAR = [
    -32124, -31100, -30076, -29052, -28028, -27004, -25980, -24956,
    -23932, -22908, -21884, -20860, -19836, -18812, -17788, -16764,
    -15996, -15484, -14972, -14460, -13948, -13436, -12924, -12412,
    -11900, -11388, -10876, -10364, -9852, -9340, -8828, -8316,
    -7932, -7676, -7420, -7164, -6908, -6652, -6396, -6140,
    -5884, -5628, -5372, -5116, -4860, -4604, -4348, -4092,
    -3900, -3772, -3644, -3516, -3388, -3260, -3132, -3004,
    -2876, -2748, -2620, -2492, -2364, -2236, -2108, -1980,
    -1884, -1820, -1756, -1692, -1628, -1564, -1500, -1436,
    -1372, -1308, -1244, -1180, -1116, -1052, -988, -924,
    -876, -844, -812, -780, -748, -716, -684, -652,
    -620, -588, -556, -524, -492, -460, -428, -396,
    -372, -356, -340, -324, -308, -292, -276, -260,
    -244, -228, -212, -196, -180, -164, -148, -132,
    -120, -112, -104, -96, -88, -80, -72, -64,
    -56, -48, -40, -32, -24, -16, -8, 0,
    32124, 31100, 30076, 29052, 28028, 27004, 25980, 24956,
    23932, 22908, 21884, 20860, 19836, 18812, 17788, 16764,
    15996, 15484, 14972, 14460, 13948, 13436, 12924, 12412,
    11900, 11388, 10876, 10364, 9852, 9340, 8828, 8316,
    7932, 7676, 7420, 7164, 6908, 6652, 6396, 6140,
    5884, 5628, 5372, 5116, 4860, 4604, 4348, 4092,
    3900, 3772, 3644, 3516, 3388, 3260, 3132, 3004,
    2876, 2748, 2620, 2492, 2364, 2236, 2108, 1980,
    1884, 1820, 1756, 1692, 1628, 1564, 1500, 1436,
    1372, 1308, 1244, 1180, 1116, 1052, 988, 924,
    876, 844, 812, 780, 748, 716, 684, 652,
    620, 588, 556, 524, 492, 460, 428, 396,
    372, 356, 340, 324, 308, 292, 276, 260,
    244, 228, 212, 196, 180, 164, 148, 132,
    120, 112, 104, 96, 88, 80, 72, 64,
    56, 48, 40, 32, 24, 16, 8, 0
]


def ulaw_to_pcm(ulaw_data):
    """
    Convert G.711 u-law data to 16-bit linear PCM.

    Args:
        ulaw_data: Bytes of u-law encoded audio

    Returns:
        Bytes of 16-bit signed PCM audio (little-endian)
    """
    pcm_data = bytearray(len(ulaw_data) * 2)
    for i, byte in enumerate(ulaw_data):
        sample = ULAW_TO_LINEAR[byte]
        # Pack as 16-bit signed integer (little-endian)
        pcm_data[i * 2] = sample & 0xFF
        pcm_data[i * 2 + 1] = (sample >> 8) & 0xFF
    return bytes(pcm_data)


class RTSPClient:
    """
    Custom RTSP client for Uniden scanner.

    The Uniden scanner's RTSP implementation has several quirks that differ
    from the standard RTSP specification. See docs/uniden/RTSP_QUIRKS.md
    for detailed documentation.
    """

    def __init__(self, host, path='/au:scanner.au'):
        """
        Initialize RTSP client.

        Args:
            host: Scanner IP address
            path: RTSP path (default: '/au:scanner.au')
        """
        self.host = host
        self.path = path
        self.url = f"rtsp://{host}{path}"
        self.cseq = 0
        self.session = None
        self.server_port = None
        self.client_port = None
        self.sock = None

    def _send_request(self, method, url=None, extra_headers=None):
        """
        Send an RTSP request and receive response.

        Args:
            method: RTSP method (OPTIONS, DESCRIBE, SETUP, PLAY, TEARDOWN)
            url: URL to use (defaults to self.url)
            extra_headers: Dict of additional headers to include

        Returns:
            Response string
        """
        self.cseq += 1

        # Use provided URL or default to self.url
        if url is None:
            url = self.url

        # Build request
        request = f"{method} {url} RTSP/1.0\r\n"
        request += f"CSeq: {self.cseq}\r\n"
        request += "User-Agent: Python RTSP Client\r\n"

        if self.session:
            request += f"Session: {self.session}\r\n"

        if extra_headers:
            for key, value in extra_headers.items():
                request += f"{key}: {value}\r\n"

        request += "\r\n"

        # Send request
        self.sock.sendall(request.encode('utf-8'))

        # Receive response
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            response += chunk

        return response.decode('utf-8', errors='ignore')

    def connect(self):
        """Connect to RTSP server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.connect((self.host, RTSP_PORT))
        logger.debug(f"Connected to RTSP server at {self.host}:{RTSP_PORT}")

    def options(self):
        """
        Send OPTIONS request.

        Returns:
            True if successful, False otherwise
        """
        response = self._send_request("OPTIONS")
        if "200 OK" in response:
            logger.debug("OPTIONS request successful")
            return True
        logger.error(f"OPTIONS request failed: {response}")
        return False

    def describe(self):
        """
        Send DESCRIBE request.

        Returns:
            True if successful, False otherwise
        """
        headers = {"Accept": "application/sdp"}
        response = self._send_request("DESCRIBE", None, headers)

        if "200 OK" in response:
            logger.debug("DESCRIBE request successful")
            return True
        logger.error(f"DESCRIBE request failed: {response}")
        return False

    def setup(self, client_port):
        """
        Send SETUP request.

        This is where the scanner's RTSP implementation diverges significantly
        from the standard. See docs/uniden/RTSP_QUIRKS.md for details.

        Args:
            client_port: RTP port for receiving audio

        Returns:
            True if successful, False otherwise
        """
        self.client_port = client_port

        # Use the exact transport format the scanner expects
        transport = "RTP/AVP;unicast;"
        transport += f"client_port={client_port}"
        transport += f"-{client_port + 1}"

        headers = {"Transport": transport}

        # SETUP URL should be: rtsp://IP/path/trackID=1 (no port in URL)
        setup_url = f"rtsp://{self.host}{self.path}/trackID=1"
        response = self._send_request("SETUP", setup_url, headers)

        if "200 OK" in response:
            # Extract session ID
            for line in response.split('\r\n'):
                if line.startswith('Session:'):
                    self.session = line.split(':')[1].strip().split(';')[0]
                    logger.debug(f"Got session ID: {self.session}")

                if line.startswith('Transport:'):
                    # Extract server_port
                    parts = line.split(';')
                    for part in parts:
                        if 'server_port' in part:
                            self.server_port = int(part.split('=')[1])
                            logger.debug(f"Got server port: {self.server_port}")

            return True
        else:
            logger.error(f"SETUP request failed: {response}")
            return False

    def play(self):
        """
        Send PLAY request to start audio streaming.

        Returns:
            True if successful, False otherwise
        """
        headers = {"Range": "npt=0.000-"}
        response = self._send_request("PLAY", f"{self.url}/", headers)

        if "200 OK" in response:
            logger.debug("PLAY request successful - audio streaming started")
            return True
        logger.error(f"PLAY request failed: {response}")
        return False

    def teardown(self):
        """
        Send TEARDOWN request to stop streaming and clean up.
        """
        response = None
        try:
            response = self._send_request("TEARDOWN", f"{self.url}/")
            logger.debug("TEARDOWN request sent")
        except Exception as e:
            logger.warning(f"TEARDOWN error: {e}: {response}")
        finally:
            if self.sock:
                self.sock.close()
                self.sock = None


class RTPReceiver:
    """
    RTP receiver for audio stream.

    Receives RTP packets containing G.711 u-law encoded audio.
    """

    def __init__(self, port):
        """
        Initialize RTP receiver.

        Args:
            port: UDP port to listen on
        """
        self.port = port
        self.sock = None
        self.running = False

    def start(self):
        """Start receiving RTP packets."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.settimeout(1.0)
        self.running = True
        logger.debug(f"RTP receiver started on port {self.port}")

    def receive(self):
        """
        Receive one RTP packet.

        Returns:
            Audio payload bytes (G.711 u-law), or None if no data
        """
        try:
            data, addr = self.sock.recvfrom(RTP_BUFFER_SIZE)

            # Parse RTP header (12 bytes minimum)
            if len(data) < 12:
                return None

            # RTP header format:
            # 0: V(2), P(1), X(1), CC(4)
            # 1: M(1), PT(7)
            # 2-3: Sequence number
            # 4-7: Timestamp
            # 8-11: SSRC

            header = struct.unpack('!BBHII', data[:12])
            payload_type = header[1] & 0x7F

            # G.711 u-law is typically payload type 0
            if payload_type != 0:
                logger.debug(f"Unexpected payload type: {payload_type}")
                return None

            # Extract audio payload (skip RTP header)
            audio_payload = data[12:]

            return audio_payload

        except socket.timeout:
            return None
        except Exception as e:
            logger.debug(f"RTP receive error: {e}")
            return None

    def stop(self):
        """Stop receiving."""
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None
        logger.debug("RTP receiver stopped")


class AudioPlayer:
    """
    Audio player using PyAudio.

    Plays G.711 u-law audio from the scanner through the default audio device.
    """

    def __init__(self):
        """Initialize audio player."""
        self.pyaudio = _import_pyaudio()
        if self.pyaudio:
            with suppress_stderr():
                self.pa = self.pyaudio.PyAudio()
        else:
            self.pa = None
        self.stream = None

    def start(self, sample_rate=8000, channels=1):
        """
        Start audio playback stream.

        Args:
            sample_rate: Sample rate in Hz (default: 8000)
            channels: Number of channels (default: 1 for mono)
        """
        if not self.pa or not self.pyaudio:
            logger.error("Cannot start audio - pyaudio not available")
            return
        with suppress_stderr():
            self.stream = self.pa.open(
                format=self.pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                output=True,
                frames_per_buffer=160
            )
        logger.debug(f"Audio player started: {sample_rate}Hz, {channels} channel(s)")

    def play(self, ulaw_data):
        """
        Play G.711 u-law audio data.

        Args:
            ulaw_data: Bytes of u-law encoded audio
        """
        if not self.stream:
            return

        # Convert G.711 u-law to linear PCM
        try:
            pcm_data = ulaw_to_pcm(ulaw_data)
            self.stream.write(pcm_data)
        except Exception as e:
            logger.debug(f"Skipping packet: {e}")
            pass  # Skip bad packets

    def stop(self):
        """Stop playback and clean up."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.pa:
            self.pa.terminate()
            self.pa = None
        logger.debug("Audio player stopped")
