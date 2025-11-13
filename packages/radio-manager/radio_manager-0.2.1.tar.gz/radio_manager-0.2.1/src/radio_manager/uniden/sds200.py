"""Uniden SDS200 scanner implementation."""

import time
import random
import serial
import socket
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from ..base import Radio
from .rtsp import RTSPClient, RTPReceiver, AudioPlayer

logger = logging.getLogger(__name__)


class SDS200(Radio):
    """
    Uniden SDS200 digital scanning receiver.

    Supports both serial (USB) and network (UDP/IP) connections.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SDS200 scanner.

        Config options:
            - ser_port: Serial port (e.g., '/dev/ttyACM0')
            - baudrate: Serial baudrate (default: 115200)
            - host: IP address for network connection
            - port: UDP port (default: 50536)
            - timeout: Communication timeout (default: 0.5 seconds)
        """
        super().__init__(config)
        self.model = "SDS200"

        # Connection settings
        self.ser_port = config.get('ser_port')
        self.baudrate = config.get('baudrate', 115200)
        self.host = config.get('host')
        self.port = config.get('port', 50536)
        self.timeout = config.get('timeout', 0.5)

        # Determine connection type
        if self.host:
            self.connection_type = "network"
        elif self.ser_port:
            self.connection_type = "serial"
        else:
            raise ValueError(
                "Must provide either 'host' or 'ser_port' in config"
            )

        self._serial_conn: Optional[serial.Serial] = None
        self._volume: Optional[int] = None
        self._squelch: Optional[int] = None

    def connect(self) -> bool:
        """Connect to the scanner."""
        if self.connection_type == "serial":
            try:
                self._serial_conn = serial.Serial(
                    port=self.ser_port,
                    baudrate=self.baudrate,
                    timeout=self.timeout
                )
                self.connected = True
                logger.debug(f"Connected to {self.ser_port}")
                return True
            except serial.SerialException as e:
                logger.error(f"Failed to connect: {e}")
                self.connected = False
                return False
        else:
            # Network is connectionless (UDP)
            self.connected = True
            logger.debug(f"Ready for network communication with {self.host}:{self.port}")
            return True

    def disconnect(self) -> bool:
        """Disconnect from the scanner."""
        if self._serial_conn and self._serial_conn.is_open:
            self._serial_conn.close()
            logger.debug("Disconnected from serial port")
        self.connected = False
        return True

    def send_command(self, command: str) -> str:
        """Send a command and return the response."""
        if not self.connected:
            raise RuntimeError("Not connected to scanner")

        if self.connection_type == "serial":
            return self._send_serial(command)
        else:
            return self._send_network(command)

    def _send_serial(self, command: str) -> str:
        """Send command via serial."""
        if not self._serial_conn:
            raise RuntimeError("Serial connection not established")

        # Flush input buffer
        self._serial_conn.reset_input_buffer()

        # Send command
        cmd = (command + '\r').encode('latin-1')
        self._serial_conn.write(cmd)

        # Wait for data
        time.sleep(0.05)

        # Read until silent
        buffer = b''
        while True:
            bytes_waiting = self._serial_conn.in_waiting
            if bytes_waiting > 0:
                buffer += self._serial_conn.read(bytes_waiting)
            else:
                time.sleep(0.1)
                if self._serial_conn.in_waiting == 0:
                    break

        # Decode and clean
        response = buffer.decode('latin-1').rstrip('\r')
        return response.replace('\r', '\n').replace('\n\n', '\n').strip()

    def _send_network(self, command: str) -> str:
        """Send command via UDP."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)

            # Send command
            cmd = (command + '\r').encode('latin-1')
            sock.sendto(cmd, (self.host, self.port))

            # Receive response
            data, _ = sock.recvfrom(2048)
            response = data.decode('latin-1').rstrip('\r')
            return response.replace('\r', '\n').replace('\n\n', '\n').strip()

    def get_status(self) -> Dict[str, Any]:
        """Get current scanner status."""
        response = self.send_command("GSI")

        return {
            'model': self.model,
            'connected': self.connected,
            'connection_type': self.connection_type,
            'channel': self._parse_channel(response),
            'raw_response': response
        }

    def _parse_channel(self, response: str) -> str:
        """Parse channel information from XML response."""
        try:
            # Find XML in response
            xml_start = response.find('<?xml')
            if xml_start == -1:
                return "No XML data"

            xml_data = response[xml_start:]
            root = ET.fromstring(xml_data)

            # Check mute status
            property_elem = root.find('.//Property')
            if property_elem is not None and property_elem.get('Mute') == "Mute":
                return "Muted"

            # Get department
            dept = root.find('.//Department')
            dept_name = dept.get('Name') if dept is not None else "Unknown"

            # Get channel name (conventional frequency or talkgroup)
            conv_freq = root.find('.//ConvFrequency')
            tgid = root.find('.//TGID')

            if conv_freq is not None:
                return f"{dept_name} - {conv_freq.get('Name')}"
            elif tgid is not None:
                return f"{dept_name} - {tgid.get('Name')}"
            else:
                return f"{dept_name} - Unknown"

        except Exception as e:
            logger.error(f"Failed to parse channel: {e}")
            return "Parse error"

    def parse_TGID(self, xml) -> str:
        """
        Extract the numeric ID from the scanner's data
        """
        tgid_only = xml

        return tgid_only

    def get_reception_info(self) -> Dict[str, str]:
        """
        Get current reception information.

        Returns dict with:
            - frequency: Current frequency (if receiving)
            - site: Site name (if receiving)
            - group: Department/Group name (if receiving)
            - channel: Channel name or "No Signal"
        """
        response = self.send_command("GSI")

        try:
            # Find XML in response
            xml_start = response.find('<?xml')
            if xml_start == -1:
                return {
                    'frequency': '',
                    'site': '',
                    'group': '',
                    'channel': 'No Signal',
                }

            xml_data = response[xml_start:]
            root = ET.fromstring(xml_data)

            # Check mute status
            property_elem = root.find('.//Property')
            if (property_elem is not None and
                    property_elem.get('Mute') == "Mute"):
                return {
                    'frequency': '',
                    'site': '',
                    'group': '',
                    'channel': 'No Signal',
                }

            # Get system name (site)
            system_elem = root.find('.//System')
            site = (system_elem.get('Name')
                    if system_elem is not None else '')

            # Get department (group)
            dept_elem = root.find('.//Department')
            group = (dept_elem.get('Name')
                     if dept_elem is not None else '')

            # Get frequency and channel name
            conv_freq = root.find('.//ConvFrequency')
            tgid = root.find('.//TGID')

            if conv_freq is not None:
                # Conventional frequency but it
                # still could be a digital channel
                name = conv_freq.get('Name', '')

                freq = conv_freq.get('Freq', '')
                # Strip leading zeros and blanks from frequency
                freq = freq.lstrip()
                freq = freq.lstrip('0') or '0'

                # Check for a TGID (ie, as in the
                # case of monitoring a single
                # channel of a DMR system)
                # and use that information
                # Examples:
                # "TGID None" for truly conventional
                # "TGID 123456" for a Talkgroup
                TGID = conv_freq.get('TGID', '').removeprefix("TGID ")

                if TGID != "None":  # Note: String comparison!
                    freq = TGID

            elif tgid is not None:
                # Trunked system - get frequency from TGID
                freq = tgid.get('TGID', '')
                # Strip leading zeros and blanks from frequency
                freq = freq.lstrip()
                freq = freq.lstrip('0') or '0'
                name = tgid.get('Name', '')
            else:
                # No active reception
                return {
                    'freq': '',
                    'site': '',
                    'group': '',
                    'name': 'No Signal',
                }

            return {
                'freq': freq,
                'site': site,
                'group': group,
                'name': name,
            }

        except Exception as e:
            logger.error(f"Failed to parse reception info: {e}")
            return {
                'frequency': '',
                'site': '',
                'group': '',
                'channel': 'No Signal',
            }

    @property
    def volume(self) -> int:
        """Get current volume (0-29)."""
        if self._volume is None:
            response = self.send_command("VOL")
            # Parse volume from response
            # Format: "VOL,XX" where XX is volume
            try:
                self._volume = int(response.split(',')[1])
            except (IndexError, ValueError):
                self._volume = 0
        return self._volume

    @volume.setter
    def volume(self, level: int) -> None:
        """Set volume (0-29)."""
        if not 0 <= level <= 29:
            raise ValueError(f"Volume must be 0-29, got {level}")

        self.send_command(f"VOL,{level}")
        self._volume = level

    @property
    def squelch(self) -> int:
        """Get current squelch level."""
        if self._squelch is None:
            response = self.send_command("SQL")
            # Parse squelch from response
            # Format: "SQL,XX" where XX is squelch level
            try:
                self._squelch = int(response.split(',')[1])
            except (IndexError, ValueError):
                self._squelch = 0
        return self._squelch

    @squelch.setter
    def squelch(self, level: int) -> None:
        """Set squelch level."""
        if level < 0:
            raise ValueError(f"Squelch must be non-negative, got {level}")

        self.send_command(f"SQL,{level}")
        self._squelch = level

    def set_frequency(self, frequency: float) -> bool:
        """Set frequency (not implemented for SDS200)."""
        raise NotImplementedError("SDS200 is a scanner, use systems/channels")

    def reboot(self) -> bool:
        """Reboot the scanner."""
        logger.info("Rebooting scanner...")
        self.send_command("MSM,1")
        time.sleep(25)  # Wait for reboot

        try:
            self.send_command("GSI")
            logger.info("Scanner rebooted successfully")
            return True
        except Exception as e:
            logger.error(f"Scanner did not respond after reboot: {e}")
            return False

    def stream_audio(self, callback=None) -> None:
        """
        Stream audio from scanner via RTSP.

        Only works with network connection. If callback is provided, it will be
        called with each audio packet. Otherwise, audio is played to speakers.

        Args:
            callback: Optional function(ulaw_data: bytes) to handle audio packets.
                     If None, audio is played via PyAudio.

        Raises:
            RuntimeError: If using serial connection (RTSP requires network)
        """
        if self.connection_type != "network":
            raise RuntimeError("RTSP audio streaming requires network connection")

        client_rtp_port = random.randint(40000, 50000)

        rtsp = RTSPClient(self.host)
        rtp = RTPReceiver(client_rtp_port)
        audio = AudioPlayer() if not callback else None

        # RTSP handshake
        try:
            rtsp.connect()
            logger.info("Connected to RTSP server")
        except Exception as e:
            logger.error(f"RTSP connection failed: {e}")
            logger.info("Attempting scanner reboot...")
            self.reboot()
            rtsp.connect()
            logger.info("Reconnected after reboot")

        if not rtsp.options():
            raise RuntimeError("RTSP OPTIONS failed")

        if not rtsp.describe():
            raise RuntimeError("RTSP DESCRIBE failed")

        if not rtsp.setup(client_rtp_port):
            raise RuntimeError("RTSP SETUP failed")

        try:
            # Start RTP receiver
            rtp.start()

            if not rtsp.play():
                raise RuntimeError("RTSP PLAY failed")

            logger.info("Audio streaming started - Press Ctrl+C to stop")

            # Start audio playback if not using callback
            if audio:
                audio.start(sample_rate=8000, channels=1)

            packet_count = 0
            while rtp.running:
                audio_data = rtp.receive()

                if audio_data:
                    if callback:
                        callback(audio_data)
                    elif audio:
                        audio.play(audio_data)

                    packet_count += 1

                    # Scanner stops after ~7500 packets
                    if packet_count > 7000:
                        logger.info(f"Reached packet limit: {packet_count}")
                        break

        except KeyboardInterrupt:
            logger.info("Stopping audio stream...")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
        finally:
            rtp.stop()
            if audio:
                audio.stop()
            rtsp.teardown()
