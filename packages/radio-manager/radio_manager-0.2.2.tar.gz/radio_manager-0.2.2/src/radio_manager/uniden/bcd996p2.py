"""Uniden BCD996P2 scanner implementation."""

import serial
import logging
from typing import Dict, Any, Optional
from ..base import Radio

logger = logging.getLogger(__name__)


class BCD996P2(Radio):
    """
    Uniden BCD996P2 digital/analog scanning receiver.

    Serial connection only (no network support).
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BCD996P2 scanner.

        Config options:
            - ser_port: Serial port (e.g., '/dev/ttyACM1')
            - baudrate: Serial baudrate (default: 115200)
            - timeout: Communication timeout (default: 0.5 seconds)
        """
        super().__init__(config)
        self.model = "BCD996P2"

        # Connection settings (serial only)
        self.ser_port = config.get('ser_port')
        if not self.ser_port:
            raise ValueError("BCD996P2 requires 'ser_port' in config")

        self.baudrate = config.get('baudrate', 115200)
        self.timeout = config.get('timeout', 0.5)

        self.firmware_version: Optional[str] = None
        self.scanner_mode: Optional[str] = None  # PRG or EPG

    def connect(self) -> bool:
        """
        Connect to the scanner.

        BCD996P2 opens/closes serial port per command, so this just validates
        the connection is possible.
        """
        try:
            # Set connected temporarily to allow send_command to work
            self.connected = True

            # Test connection by getting firmware version
            self.firmware_version = self.get_firmware_version()
            logger.debug(
                f"Connected to BCD996P2 on {self.ser_port},"
                f" FW: {self.firmware_version}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from scanner and exit remote mode."""
        if self.connected:
            try:
                # Exit programming/remote mode
                # When we EPG, the scanner ends up in a hold mode,
                # so, consider that when reimplementing this
                # self.send_command("EPG")

                # Adding this may or may not make sense
                # For example, if disconnect is called
                # after KEY,H,P (hold), then we'd
                # be silly to start scanning again.
                # Maybe only "connect()" for
                #   Programming?
                #   Commands that require EPG?
                # self.send_command("KEY,S,P")
                logger.debug("Exited remote mode")
            except Exception as e:
                logger.warning(f"Failed to exit remote mode: {e}")

        self.connected = False
        logger.debug("Disconnected from scanner")
        return True

    def send_command(self, command: str) -> str:
        """
        Send command and return response.

        BCD996P2 opens/closes connection per command.
        """
        if not self.connected:
            raise RuntimeError("Not connected to scanner")

        try:
            # Open serial connection
            with serial.Serial(
                port=self.ser_port,
                baudrate=self.baudrate,
                timeout=self.timeout
            ) as ser:
                # Send command with carriage return
                cmd = (command + '\r').encode('latin-1')
                ser.write(cmd)

                # Read response until carriage return
                response = ser.read_until(b'\r')
                return response.decode('latin-1').rstrip('\r')

        except serial.SerialException as e:
            raise RuntimeError(f"Serial communication failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current scanner status."""
        # Get model info
        model_info = self.send_command("MDL")

        # Get scanner mode (PRG or EPG)
        # self.scanner_mode = self.send_command("PRG")

        return {
            'model': self.model,
            'firmware': self.firmware_version,
            'scanner_mode': self.scanner_mode,
            'model_info': model_info,
            'connected': self.connected
        }

    def get_firmware_version(self) -> str:
        """Get firmware version."""
        response = self.send_command("VER")
        # Response format: "VER,version"
        try:
            return response.split(',')[1]
        except IndexError:
            return response

    @property
    def volume(self) -> int:
        """Get current volume."""
        response = self.send_command("VOL")
        # Response format: "VOL,XX"
        try:
            return int(response.split(',')[1])
        except (IndexError, ValueError):
            return 0

    @volume.setter
    def volume(self, level: int) -> None:
        """Set volume (0-15 for BCD996P2)."""
        if not 0 <= level <= 15:
            raise ValueError(f"Volume must be 0-15 for BCD996P2, got {level}")

        self.send_command(f"VOL,{level}")

    @property
    def squelch(self) -> int:
        """Get current squelch level."""
        response = self.send_command("SQL")
        # Response format: "SQL,XX"
        try:
            return int(response.split(',')[1])
        except (IndexError, ValueError):
            return 0

    @squelch.setter
    def squelch(self, level: int) -> None:
        """Set squelch level."""
        if level < 0:
            raise ValueError(f"Squelch must be non-negative, got {level}")

        self.send_command(f"SQL,{level}")

    def set_frequency(self, frequency: float) -> bool:
        """Set frequency (not implemented for BCD996P2)."""
        raise NotImplementedError(
            "BCD996P2 is a scanner, use systems/channels"
        )

    def set_mode(self, mode: str) -> bool:
        """
        Set scanner mode.

        Args:
            mode: Either 'PRG' (programming) or 'EPG' (scanning)
        """
        if mode not in ['PRG', 'EPG']:
            raise ValueError(f"Mode must be 'PRG' or 'EPG', got '{mode}'")

        self.scanner_mode = mode
        logger.info(f"Set scanner mode to {mode}")
        return True

    def get_reception_info(self) -> Dict[str, str]:
        """
        Get current reception information.

        Returns dict with:
            - frequency: Current frequency (if receiving)
            - site: Site name (if receiving)
            - group: Group name (if receiving)
            - name: Channel name or "No Signal"
        """
        response = self.send_command("GLG")
        # Response format: GLG,freq,unknown,unknown,unknown,
        #                  unknown,site,group,channel,...
        fields = response.split(',')

        # Check if scanner is receiving (field 1 not empty)
        if len(fields) > 1 and fields[1].strip():
            # Get frequency and strip leading zeros
            freq = fields[1] if len(fields) > 1 else ''
            freq = freq.lstrip('0') or '0'  # Keep at least one '0'

            return {
                'freq': freq,
                'site': fields[5] if len(fields) > 5 else '',
                'group': fields[6] if len(fields) > 6 else '',
                'name': fields[7] if len(fields) > 7 else '',
            }
        else:
            # Not receiving
            return {
                'name': '',
                'site': '',
                'group': '',
                'freq': 'No Signal',
            }
