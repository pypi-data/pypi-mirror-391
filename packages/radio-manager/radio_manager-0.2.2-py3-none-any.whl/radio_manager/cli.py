"""
Command-line interface for radio-manager.

Provides commands for managing Uniden scanners including volume control,
status queries, reboot, and audio streaming.
"""

import sys
import argparse
import logging
import signal
import threading
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)

from radio_manager.uniden.sds200 import SDS200
from radio_manager.uniden.bcd996p2 import BCD996P2
from radio_manager.__version__ import __version__
from radio_manager.audio_proxy import start_audio_proxy
from radio_manager.utils.retry import with_retry, MaxRetriesExceeded

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Radio class mapping
RADIO_MODELS = {
    'SDS200': SDS200,
    'BCD996P2': BCD996P2,
}


def find_config_file() -> Optional[Path]:
    """
    Find the radios.yaml config file.

    Search order:
    1. Current directory
    2. ~/.config/radio-manager/radios.yaml
    3. /etc/radio-manager/radios.yaml

    Returns:
        Path to config file, or None if not found
    """
    search_paths = [
        Path.cwd() / 'radios.yaml',
        Path.home() / '.config' / 'radio-manager' / 'radios.yaml',
        Path('/etc/radio-manager/radios.yaml'),
    ]

    for path in search_paths:
        if path.exists():
            logger.debug(f"Found config file: {path}")
            return path

    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Optional path to config file. If not provided, searches
                    standard locations.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If config file is invalid
    """
    if config_path:
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
    else:
        config_file = find_config_file()
        if not config_file:
            raise FileNotFoundError(
                "Config file 'radios.yaml' not found. Searched:\n"
                "  - Current directory\n"
                "  - ~/.config/radio-manager/\n"
                "  - /etc/radio-manager/"
            )

    logger.debug(f"Loading config from: {config_file}")
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_radio(config: Dict[str, Any], radio_name: Optional[str] = None):
    """
    Get a radio instance from config.

    Args:
        config: Configuration dictionary
        radio_name: Name of radio to get. If None, uses default_radio
            from config.

    Returns:
        Radio instance

    Raises:
        ValueError: If radio not found or no default configured
    """
    # Get radio name (use provided or default)
    if radio_name is None:
        radio_name = config.get('default_radio')
        if not radio_name:
            raise ValueError(
                "No radio specified and no default_radio configured "
                "in radios.yaml"
            )
        logger.debug(f"Using default radio: {radio_name}")

    # Get radio config
    radios = config.get('radios', {})
    if radio_name not in radios:
        available = ', '.join(radios.keys())
        raise ValueError(
            f"Radio '{radio_name}' not found in config. Available: {available}"
        )

    radio_config = radios[radio_name]
    model = radio_config.get('model')

    if not model:
        raise ValueError(f"Radio '{radio_name}' missing 'model' in config")

    if model not in RADIO_MODELS:
        supported = ', '.join(RADIO_MODELS.keys())
        raise ValueError(
            f"Unknown model '{model}'. Supported: {supported}"
        )

    # Create radio instance
    radio_class = RADIO_MODELS[model]
    return radio_class(radio_config)


def cmd_list_radios(args):
    """List all configured radios."""
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    radios = config.get('radios', {})
    default_radio = config.get('default_radio')

    if not radios:
        print("No radios configured.")
        return 0

    print("Configured radios:")
    print()

    for name, radio_config in radios.items():
        model = radio_config.get('model', 'Unknown')
        is_default = " (default)" if name == default_radio else ""

        print(f"  {name}{is_default}")
        print(f"    Model: {model}")

        # Show connection info
        if 'host' in radio_config:
            host = radio_config['host']
            port = radio_config.get('port', 50536)
            print(f"    Connection: Network ({host}:{port})")
        elif 'ser_port' in radio_config:
            ser_port = radio_config['ser_port']
            baudrate = radio_config.get('baudrate', 115200)
            print(f"    Connection: Serial ({ser_port} @ {baudrate})")

        print()

    return 0


def cmd_set_volume(args):
    """Set radio volume."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    try:
        with radio:
            radio.volume = args.level
            print(f"Volume set to {args.level}")
            return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to set volume: {e}")
        print(f"Error: Failed to set volume - {e}")
        return 1


def cmd_get_volume(args):
    """Get current radio volume."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    try:
        with radio:
            volume = radio.volume
            print(f"Current volume: {volume}")
            return 0
    except Exception as e:
        logger.error(f"Failed to get volume: {e}")
        print(f"Error: Failed to get volume - {e}")
        return 1


def cmd_set_squelch(args):
    """Set radio squelch."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    try:
        with radio:
            radio.squelch = args.level
            print(f"Squelch set to {args.level}")
            return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to set squelch: {e}")
        print(f"Error: Failed to set squelch - {e}")
        return 1


def cmd_get_squelch(args):
    """Get current radio squelch."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    try:
        with radio:
            squelch = radio.squelch
            print(f"Current squelch: {squelch}")
            return 0
    except Exception as e:
        logger.error(f"Failed to get squelch: {e}")
        print(f"Error: Failed to get squelch - {e}")
        return 1


def cmd_status(args):
    """Get radio status."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    try:
        with radio:
            status = radio.get_status()

            print("Radio Status:")
            print(f"  Model: {status.get('model', 'Unknown')}")
            print(f"  Connected: {status.get('connected', False)}")

            # Model-specific fields
            if 'connection_type' in status:
                print(f"  Connection: {status['connection_type']}")

            if 'channel' in status:
                print(f"  Channel: {status['channel']}")

            if 'firmware' in status:
                print(f"  Firmware: {status['firmware']}")

            if 'scanner_mode' in status:
                print(f"  Scanner Mode: {status['scanner_mode']}")

            # Volume
            try:
                volume = radio.volume
                print(f"  Volume: {volume}")
            except Exception:
                pass

            return 0
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        print(f"Error: Failed to get status - {e}")
        return 1


def cmd_reboot(args):
    """Reboot the radio."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Check if radio supports reboot
    if not hasattr(radio, 'reboot'):
        print(f"Error: {radio.model} does not support reboot command")
        return 1

    # Confirm reboot unless --force
    if not args.force:
        response = input(
            f"Reboot {radio.model}? This will take about 25 seconds "
            f"[y/N]: "
        )
        if response.lower() not in ['y', 'yes']:
            print("Reboot cancelled.")
            return 0

    try:
        with radio:
            print(f"Rebooting {radio.model}...")
            success = radio.reboot()

            if success:
                print("Reboot successful!")
                return 0
            else:
                print("Reboot may have failed - scanner did not respond")
                return 1
    except Exception as e:
        logger.error(f"Failed to reboot: {e}")
        print(f"Error: Failed to reboot - {e}")
        return 1


def cmd_stream_audio(args):
    """Stream audio from radio."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Check if radio supports audio streaming
    if not hasattr(radio, 'stream_audio'):
        print(f"Error: {radio.model} does not support audio streaming")
        return 1

    try:
        with radio:
            print(f"Streaming audio from {radio.model}...")
            print("Press Ctrl+C to stop")
            radio.stream_audio()
            return 0
    except RuntimeError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nAudio stream stopped.")
        return 0
    except Exception as e:
        logger.error(f"Failed to stream audio: {e}")
        print(f"Error: Failed to stream audio - {e}")
        return 1


def cmd_raw_command(args):
    """Send a raw command to the radio."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Check if radio supports send_command
    if not hasattr(radio, 'send_command'):
        print(f"Error: {radio.model} does not support raw commands")
        return 1

    try:
        with radio:
            response = radio.send_command(args.raw_cmd)
            print(response)
            return 0
    except Exception as e:
        logger.error(f"Failed to send command: {e}")
        print(f"Error: Failed to send command - {e}")
        return 1


def cmd_reception_info(args):
    """Monitor current reception information."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Check if radio supports get_reception_info
    if not hasattr(radio, 'get_reception_info'):
        print(
            f"Error: {radio.model} does not support "
            f"reception info command"
        )
        return 1

    try:
        with radio:
            # Build display title
            if radio.name:
                title = f"Monitoring {radio.name} ({radio.model})"
            else:
                title = f"Monitoring {radio.model}"

            print(f"{title} reception...")
            print(f"Update interval: {args.interval} second(s)")
            print("Press Ctrl+C to stop\n")

            import time
            import sys
            last_info = None

            while True:
                try:
                    # Use retry utility for get_reception_info calls
                    info = with_retry(
                        lambda: radio.get_reception_info(),
                        max_retries=5,
                        backoff_base=2.0,
                        quiet_threshold=1,
                        context_name=f"{radio.name or radio.model}"
                    )

                    # Only update display if info changed
                    if info != last_info:
                        freq = info.get('freq', 'No Signal')
                        site = info.get('site', '')
                        group = info.get('group', '')
                        name = info.get('name', '')

                        # Clear previous output and move cursor to start
                        # Use ANSI escape codes
                        sys.stdout.write('\033[2J\033[H')

                        # Display info in vertical format
                        print(f"{title} reception...")
                        print(
                            f"Update interval: {args.interval} second(s)"
                        )
                        print("Press Ctrl+C to stop\n")
                        print(f"Name:      {name}")
                        print(f"Group:     {group}")
                        print(f"Site:      {site}")
                        print(f"Channel:   {freq}")

                        sys.stdout.flush()
                        last_info = info

                    time.sleep(args.interval)

                except MaxRetriesExceeded:
                    print(
                        "\n\nERROR: Maximum consecutive timeouts reached."
                        "Stopping monitoring due to persistent "
                        "connection failure."
                    )
                    return 1

                except KeyboardInterrupt:
                    print("\n\nStopped monitoring.")
                    return 0

    except Exception as e:
        logger.error(f"Failed to monitor reception: {e}")
        print(f"Error: Failed to monitor reception - {e}")
        return 1


def cmd_audio_proxy(args):
    """Start HTTP audio proxy server."""
    try:
        config = load_config(args.config)
        radio = get_radio(config, args.radio)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Get scanner IP from radio config
    radio_name = args.radio or config.get('default_radio')
    radio_config = config.get('radios', {}).get(radio_name)
    if not radio_config:
        print("Error: Could not find radio configuration")
        return 1

    scanner_ip = radio_config.get('host')
    if not scanner_ip:
        print("Error: Radio must have 'host' configured for audio proxy")
        return 1

    # Create auto-reboot callback if enabled
    auto_reboot_callback = None
    if args.auto_reboot:
        def reboot_scanner():
            """Callback to reboot the scanner"""
            with radio:
                return radio.reboot()
        auto_reboot_callback = reboot_scanner
        print(
            "Auto-reboot enabled: Scanner will be automatically "
            "rebooted on connection failures"
        )

    try:
        print(f"Starting audio proxy for {scanner_ip}...")
        server, streamer = start_audio_proxy(
            scanner_ip=scanner_ip,
            port=args.port,
            host=args.host,
            low_latency=args.low_latency,
            auto_reboot_callback=auto_reboot_callback
        )

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(
                f"\nReceived signal {signum}, "
                f"shutting down gracefully..."
            )
            streamer.stop()
            # Shutdown server in a separate thread since signal handler
            # runs in main thread which is blocked in serve_forever()
            threading.Thread(
                target=server.shutdown,
                daemon=True
            ).start()

        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # systemd stop

        try:
            print("Audio proxy started - press Ctrl+C to stop")
            print(f"Web interface: http://{args.host}:{args.port}/")
            print(f"Stream URL: http://{args.host}:{args.port}/stream")
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            streamer.stop()
            server.shutdown()
        finally:
            print("Audio proxy stopped")

        return 0
    except Exception as e:
        logger.error(f"Failed to start audio proxy: {e}")
        print(f"Error: Failed to start audio proxy - {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Manage Uniden scanners',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all configured radios
  radio-manager list-radios

  # Get status of default radio
  radio-manager status

  # Get status of specific radio
  radio-manager status --radio sds200_desk

  # Set volume
  radio-manager set-volume 15

  # Set squelch
  radio-manager set-squelch 5

  # Stream audio
  radio-manager stream-audio

  # Monitor reception information
  radio-manager reception-info
  radio-manager reception-info --interval 0.5  # Update every 0.5 seconds

  # Start HTTP audio proxy server
  radio-manager audio-proxy
  radio-manager audio-proxy --port 8765 --low-latency
  radio-manager audio-proxy --auto-reboot  # Auto-reboot on connection failures

  # Send a raw command
  radio-manager raw-command "VOL,3"
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'radio-manager {__version__}'
    )

    parser.add_argument(
        '--config', '-c',
        help='Path to config file (default: search standard locations)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to execute'
    )

    # list-radios
    subparsers.add_parser(
        'list-radios',
        help='List all configured radios'
    )

    # set-volume
    parser_set_volume = subparsers.add_parser(
        'set-volume',
        help='Set radio volume'
    )
    parser_set_volume.add_argument(
        'level',
        type=int,
        help=(
            'Volume level (range depends on model: '
            'SDS200=0-29, BCD996P2=0-15)'
        )
    )
    parser_set_volume.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # get-volume
    parser_get_volume = subparsers.add_parser(
        'get-volume',
        help='Get current radio volume'
    )
    parser_get_volume.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # set-squelch
    parser_set_squelch = subparsers.add_parser(
        'set-squelch',
        help='Set radio squelch'
    )
    parser_set_squelch.add_argument(
        'level',
        type=int,
        help='Squelch level (model-specific range)'
    )
    parser_set_squelch.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # get-squelch
    parser_get_squelch = subparsers.add_parser(
        'get-squelch',
        help='Get current radio squelch'
    )
    parser_get_squelch.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # status
    parser_status = subparsers.add_parser(
        'status',
        help='Get radio status'
    )
    parser_status.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # reboot
    parser_reboot = subparsers.add_parser(
        'reboot',
        help='Reboot the radio (SDS200 only)'
    )
    parser_reboot.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt'
    )
    parser_reboot.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # stream-audio
    parser_stream = subparsers.add_parser(
        'stream-audio',
        help='Stream audio from radio (SDS200 network only)'
    )
    parser_stream.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # raw-command
    parser_raw = subparsers.add_parser(
        'raw-command',
        help='Send a raw command to the radio'
    )
    parser_raw.add_argument(
        'raw_cmd',
        metavar='command',
        help='Raw command to send (e.g., "VOL,3")'
    )
    parser_raw.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )

    # reception-info
    parser_reception = subparsers.add_parser(
        'reception-info',
        help='Monitor current reception information'
    )
    parser_reception.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )
    parser_reception.add_argument(
        '--interval', '-i',
        type=float,
        default=1.0,
        help='Update interval in seconds (default: 1.0)'
    )

    # audio-proxy
    parser_audio_proxy = subparsers.add_parser(
        'audio-proxy',
        help='Start HTTP audio proxy server (network scanners only)'
    )
    parser_audio_proxy.add_argument(
        '--radio', '-r',
        help=(
            'Radio name (uses default_radio from config '
            'if not specified)'
        )
    )
    parser_audio_proxy.add_argument(
        '--port', '-p',
        type=int,
        default=8765,
        help='HTTP server port (default: 8765)'
    )
    parser_audio_proxy.add_argument(
        '--host',
        default='0.0.0.0',
        help='HTTP server bind address (default: 0.0.0.0)'
    )
    parser_audio_proxy.add_argument(
        '--low-latency',
        action='store_true',
        help='Enable ultra-low latency mode (2KB buffer = ~125ms)'
    )
    parser_audio_proxy.add_argument(
        '--auto-reboot',
        action='store_true',
        help=(
            'Automatically reboot scanner on RTSP connection '
            'failures (clears phantom connections)'
        )
    )

    # Parse args
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Dispatch to command handler
    if not args.command:
        parser.print_help()
        return 0

    commands = {
        'list-radios': cmd_list_radios,
        'set-volume': cmd_set_volume,
        'get-volume': cmd_get_volume,
        'set-squelch': cmd_set_squelch,
        'get-squelch': cmd_get_squelch,
        'status': cmd_status,
        'reboot': cmd_reboot,
        'stream-audio': cmd_stream_audio,
        'raw-command': cmd_raw_command,
        'reception-info': cmd_reception_info,
        'audio-proxy': cmd_audio_proxy,
    }

    handler = commands.get(args.command)
    if not handler:
        print(f"Unknown command: {args.command}")
        return 1

    return handler(args)


if __name__ == '__main__':
    sys.exit(main())
