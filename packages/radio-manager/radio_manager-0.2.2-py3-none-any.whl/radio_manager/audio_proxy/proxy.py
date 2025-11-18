"""
HTTP Audio Proxy Server for Uniden Scanners.

Converts non-standard Uniden RTSP stream to HTTP audio stream
for browser playback.

This proxy:
1. Connects to scanner using custom RTSP client
2. Receives RTP audio packets (G.711 u-law)
3. Decodes to PCM
4. Streams as HTTP audio (WAV format)
"""

import os
import sys
import time
import random
import logging
import threading
import signal
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from typing import Optional

# Import from radio_manager
from radio_manager.uniden.rtsp import RTSPClient, RTPReceiver, ulaw_to_pcm

logger = logging.getLogger(__name__)


class AudioStreamBuffer:
    """Thread-safe circular buffer for audio data"""

    def __init__(self, max_size=64 * 1024):
        # 64KB buffer (reduced for lower latency)
        self.buffer = BytesIO()
        self.max_size = max_size
        self.lock = threading.Lock()
        self.clients = []
        # Track total bytes written (for position tracking)
        self.global_offset = 0

    def write(self, data):
        """Write audio data to buffer"""
        with self.lock:
            # If buffer too large, truncate from beginning
            current_size = self.buffer.tell()
            if current_size + len(data) > self.max_size:
                # Keep last 25% of buffer for low latency
                keep_size = int(self.max_size * 0.25)
                self.buffer.seek(current_size - keep_size)
                old_data = self.buffer.read()

                # Update global offset to account for discarded data
                self.global_offset += current_size - keep_size

                self.buffer = BytesIO()
                self.buffer.write(old_data)

            self.buffer.write(data)

    def read_from(self, position):
        """
        Read audio data from specific position.

        Position is relative to global offset.
        """
        with self.lock:
            current_pos = self.buffer.tell()
            current_global_pos = self.global_offset + current_pos

            # Convert global position to local buffer position
            local_pos = position - self.global_offset

            # Clamp to valid range
            if local_pos < 0:
                local_pos = 0
            if local_pos > current_pos:
                local_pos = current_pos

            self.buffer.seek(local_pos)
            data = self.buffer.read()
            self.buffer.seek(current_pos)
            return data, current_global_pos


class RTSPAudioStreamer:
    """Manages RTSP connection and audio streaming"""

    def __init__(self, scanner_ip, buffer, auto_reboot_callback=None):
        self.scanner_ip = scanner_ip
        self.buffer = buffer
        self.running = False
        self.thread = None
        self.rtsp_client = None
        self.rtp_receiver = None
        self.auto_reboot_callback = auto_reboot_callback
        self.connection_failures = 0
        self.suggested_reboot = False

    def start(self):
        """Start RTSP streaming thread"""
        if self.running:
            logger.warning("Streamer already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()
        logger.info("RTSP streamer started")

    def stop(self):
        """Stop RTSP streaming"""
        logger.info("Stopping RTSP streamer...")
        self.running = False

        # Cleanup first to close connections quickly
        self._cleanup()

        # Then wait for threads to finish (should be quick now)
        if self.thread and self.thread.is_alive():
            logger.info("Waiting for streaming thread...")
            self.thread.join(timeout=3)
            if self.thread.is_alive():
                logger.warning("Streaming thread did not stop in time")

        logger.info("RTSP streamer stopped")

    def _stream_loop(self):
        """Main streaming loop"""
        while self.running:
            try:
                self._connect_and_stream()
                # Reset failure count on successful connection
                self.connection_failures = 0
                self.suggested_reboot = False
            except (TimeoutError, ConnectionRefusedError, OSError) as e:
                # Connection-related errors that indicate scanner issues
                self.connection_failures += 1
                error_type = type(e).__name__
                logger.error(
                    f"RTSP connection error: {error_type} - {e} "
                    f"(attempt {self.connection_failures})"
                )
                self._cleanup()

                if self.running:
                    # After 2 failures, suggest or attempt reboot
                    if (self.connection_failures >= 2 and
                            not self.suggested_reboot):
                        self.suggested_reboot = True

                        if self.auto_reboot_callback:
                            logger.warning(
                                "Multiple connection failures detected. "
                                "Attempting automatic scanner reboot..."
                            )
                            print("\n" + "="*70)
                            print(
                                "RTSP CONNECTION FAILED - "
                                "Attempting automatic scanner reboot"
                            )
                            print("="*70)
                            print(f"Error: {error_type}")
                            print(f"Scanner: {self.scanner_ip}")
                            try:
                                self.auto_reboot_callback()
                                logger.info(
                                    "Scanner reboot initiated. "
                                    "Waiting 30 seconds for scanner "
                                    "to restart..."
                                )
                                print(
                                    "Waiting 30 seconds for scanner "
                                    "to restart..."
                                )
                                # Wait for scanner to reboot
                                for i in range(30):
                                    if not self.running:
                                        break
                                    if i % 5 == 0:
                                        print(
                                            f"  {30-i} seconds "
                                            f"remaining..."
                                        )
                                    time.sleep(1)
                                # Reset after reboot attempt
                                self.connection_failures = 0
                            except Exception as reboot_error:
                                logger.error(
                                    f"Auto-reboot failed: {reboot_error}"
                                )
                                print(f"\nAuto-reboot failed: "
                                      f"{reboot_error}")
                                print(
                                    "Please manually reboot the scanner."
                                )
                        else:
                            logger.warning(
                                "Multiple RTSP connection failures "
                                "detected!"
                            )
                            print("\n" + "="*70)
                            print(
                                "RTSP CONNECTION FAILED - "
                                "Likely a phantom connection"
                            )
                            print("="*70)
                            print(f"Scanner: {self.scanner_ip}")
                            print(f"Error: {error_type} - {e}")
                            print(f"Failures: {self.connection_failures}")
                            print(
                                "\nThe scanner may have a stuck RTSP "
                                "connection from a previous session,"
                            )
                            print(
                                "or the scanner may be "
                                "unreachable/powered off."
                            )
                            print("\nRECOMMENDED SOLUTION:")
                            print(
                                f"  1. Check scanner is powered on and "
                                f"reachable: ping {self.scanner_ip}"
                            )
                            print(f"  2. Stop this proxy (Ctrl+C)")
                            print(
                                f"  3. Reboot scanner: "
                                f"radio-manager reboot"
                            )
                            print(f"  4. Wait 25-30 seconds")
                            print(
                                f"  5. Restart proxy: "
                                f"radio-manager audio-proxy"
                            )
                            print("\nALTERNATIVE:")
                            print(
                                f"  Use --auto-reboot flag to "
                                f"automatically reboot on connection "
                                f"failure"
                            )
                            print(
                                f"  Example: "
                                f"radio-manager audio-proxy --auto-reboot"
                            )
                            print("="*70 + "\n")

                    logger.info("Reconnecting in 5 seconds...")
                    # Sleep in small intervals to allow quick shutdown
                    for _ in range(10):  # 10 iterations of 0.5s = 5 seconds
                        if not self.running:
                            break
                        time.sleep(0.5)
            except Exception as e:
                # Unexpected errors - log with traceback but don't
                # trigger reboot
                self.connection_failures += 1
                logger.error(
                    f"Unexpected streaming error: {e}",
                    exc_info=True
                )
                self._cleanup()
                if self.running:
                    logger.info("Reconnecting in 5 seconds...")
                    # Sleep in small intervals to allow quick shutdown
                    for _ in range(10):
                        if not self.running:
                            break
                        time.sleep(0.5)

    def _connect_and_stream(self):
        """Connect to scanner and stream audio"""
        logger.info(f"Connecting to scanner at {self.scanner_ip}...")

        # Random client port for RTP
        client_rtp_port = random.randint(40000, 50000)

        # Initialize RTSP client
        self.rtsp_client = RTSPClient(self.scanner_ip, path='/au:scanner.au')
        self.rtp_receiver = RTPReceiver(client_rtp_port)

        # RTSP handshake
        self.rtsp_client.connect()
        logger.info("RTSP connected")

        if not self.rtsp_client.options():
            raise Exception("RTSP OPTIONS failed")
        logger.info("RTSP OPTIONS successful")

        if not self.rtsp_client.describe():
            raise Exception("RTSP DESCRIBE failed")
        logger.info("RTSP DESCRIBE successful")

        if not self.rtsp_client.setup(client_rtp_port):
            raise Exception("RTSP SETUP failed")
        logger.info(f"RTSP SETUP successful (client port: {client_rtp_port})")

        # Start RTP receiver
        self.rtp_receiver.start()
        logger.info("RTP receiver started")

        if not self.rtsp_client.play():
            raise Exception("RTSP PLAY failed")
        logger.info("RTSP PLAY successful - streaming audio")

        # Stream audio packets
        packet_count = 0
        last_log = time.time()

        while self.running:
            # Receive RTP packet (G.711 u-law)
            # This has 1 second timeout, so loop checks self.running frequently
            ulaw_data = self.rtp_receiver.receive()

            if not self.running:
                break

            if ulaw_data:
                # Convert to PCM
                pcm_data = ulaw_to_pcm(ulaw_data)

                # Write to buffer
                self.buffer.write(pcm_data)

                packet_count += 1

                # Log progress
                if time.time() - last_log > 5:
                    logger.info(f"Streaming: {packet_count} packets received")
                    last_log = time.time()
                    packet_count = 0

    def _cleanup(self):
        """Cleanup RTSP/RTP connections"""
        try:
            # Stop RTP receiver first
            if self.rtp_receiver:
                try:
                    self.rtp_receiver.stop()
                except Exception as e:
                    logger.warning(f"RTP receiver stop error: {e}")
                finally:
                    self.rtp_receiver = None

            # Always attempt TEARDOWN to clean up server-side session
            if self.rtsp_client:
                try:
                    logger.info("Sending TEARDOWN to close RTSP session...")
                    self.rtsp_client.teardown()
                    logger.info("TEARDOWN successful")
                except Exception as e:
                    logger.warning(
                        f"TEARDOWN error (may be expected on crash): {e}"
                    )
                finally:
                    self.rtsp_client = None

            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


class AudioStreamHandler(BaseHTTPRequestHandler):
    """HTTP handler for audio streaming"""

    def log_message(self, format, *args):
        """Override to use logger"""
        logger.info(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        """Handle GET request for audio stream"""
        if self.path == '/stream.mp3' or self.path == '/stream':
            self._serve_audio_stream()
        elif self.path == '/health':
            self._serve_health()
        elif self.path == '/':
            self._serve_info()
        else:
            self.send_error(404)

    def _serve_info(self):
        """Serve info page"""
        html = """
        <html>
        <head>
            <title>Uniden Scanner Audio - Low Latency</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
                h1 { color: #4CAF50; }
                .controls { margin: 20px 0; }
                button {
                    padding: 15px 30px; font-size: 18px; cursor: pointer;
                    background: #4CAF50; color: white; border: none; border-radius: 5px;
                    margin: 5px;
                }
                button:hover { background: #45a049; }
                button:disabled { background: #666; cursor: not-allowed; }
                #status {
                    margin: 20px 0; padding: 10px; background: #333;
                    border-radius: 5px; font-family: monospace;
                }
                .info { color: #888; font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>Uniden Scanner Audio - Ultra Low Latency</h1>
            <div class="controls">
                <button id="startBtn" onclick="startAudio()">Start Audio</button>
                <button id="stopBtn" onclick="stopAudio()" disabled>Stop Audio</button>
            </div>
            <div id="status">Click Start to begin streaming...</div>
            <div class="info">
                <p>Using Web Audio API for minimal latency (~0.5-1 second)</p>
                <p>Health check: <a href="/health" style="color: #4CAF50;">/health</a></p>
                <p>Stream URL: <a href="/stream" style="color: #4CAF50;">/stream</a></p>
                <p><em>Powered by radio-manager</em></p>
            </div>

            <script>
                let audioContext = null;
                let sourceNode = null;
                let isPlaying = false;
                let audioQueue = [];
                let nextPlayTime = 0;

                async function startAudio() {
                    if (isPlaying) return;

                    document.getElementById('status').textContent = 'Initializing Web Audio...';
                    document.getElementById('startBtn').disabled = true;

                    try {
                        // Create AudioContext
                        audioContext = new (window.AudioContext || window.webkitAudioContext)({
                            sampleRate: 8000,
                            latencyHint: 'interactive'  // Lowest latency mode
                        });

                        nextPlayTime = audioContext.currentTime;
                        isPlaying = true;

                        document.getElementById('status').textContent = 'Connecting to scanner...';
                        document.getElementById('stopBtn').disabled = false;

                        // Fetch audio stream
                        const response = await fetch('/stream');
                        const reader = response.body.getReader();

                        // Skip WAV header (44 bytes)
                        let bytesRead = 0;
                        let headerSkipped = false;

                        document.getElementById('status').textContent = 'Streaming live audio...';

                        while (isPlaying) {
                            const {done, value} = await reader.read();
                            if (done) break;

                            // Skip WAV header
                            let audioData = value;
                            if (!headerSkipped) {
                                if (bytesRead + value.length > 44) {
                                    const skipBytes = 44 - bytesRead;
                                    audioData = value.slice(skipBytes);
                                    headerSkipped = true;
                                } else {
                                    bytesRead += value.length;
                                    continue;
                                }
                            }

                            // Convert PCM bytes to Float32 samples
                            const samples = new Int16Array(audioData.buffer, audioData.byteOffset, audioData.length / 2);
                            const floatSamples = new Float32Array(samples.length);
                            for (let i = 0; i < samples.length; i++) {
                                floatSamples[i] = samples[i] / 32768.0;  // Convert to -1.0 to 1.0
                            }

                            // Create audio buffer and schedule playback
                            const buffer = audioContext.createBuffer(1, floatSamples.length, 8000);
                            buffer.getChannelData(0).set(floatSamples);

                            const source = audioContext.createBufferSource();
                            source.buffer = buffer;
                            source.connect(audioContext.destination);

                            // Schedule playback with minimal latency
                            if (nextPlayTime < audioContext.currentTime) {
                                nextPlayTime = audioContext.currentTime;
                            }
                            source.start(nextPlayTime);
                            nextPlayTime += buffer.duration;
                        }

                        document.getElementById('status').textContent = 'Stream ended.';
                    } catch (error) {
                        document.getElementById('status').textContent = 'Error: ' + error.message;
                        console.error('Audio error:', error);
                    } finally {
                        stopAudio();
                    }
                }

                function stopAudio() {
                    isPlaying = false;
                    if (audioContext) {
                        audioContext.close();
                        audioContext = null;
                    }
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    if (document.getElementById('status').textContent === 'Streaming live audio...') {
                        document.getElementById('status').textContent = 'Stopped.';
                    }
                }
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def _serve_health(self):
        """Serve health check"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def _serve_audio_stream(self):
        """Stream audio to client"""
        logger.info(f"New audio client connected: {self.address_string()}")

        try:
            # Send WAV header for PCM audio with aggressive no-cache
            # headers
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header(
                'Cache-Control',
                'no-cache, no-store, must-revalidate, max-age=0'
            )
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('X-Content-Type-Options', 'nosniff')
            # Force immediate connection close when done
            self.send_header('Connection', 'close')
            self.end_headers()

            # Write WAV header (use max 32-bit value minus header size)
            # For streaming, we use a large but valid size
            max_data_size = 0xFFFFFFFF - 44  # Max size minus header
            wav_header = self._make_wav_header(
                sample_rate=8000,
                bits_per_sample=16,
                channels=1,
                data_size=max_data_size
            )
            self.wfile.write(wav_header)

            # Stream audio chunks
            buffer = self.server.audio_buffer

            # Start from beginning of current buffer to send existing
            # audio immediately. This provides better experience for
            # direct /stream access
            with buffer.lock:
                # Start from the beginning of buffered data
                # (global_offset). This sends any recently buffered
                # audio, giving immediate playback
                position = buffer.global_offset

            logger.info(
                f"Starting stream from buffer start "
                f"(offset: {buffer.global_offset})"
            )

            # Track iterations for periodic flush
            no_data_count = 0
            first_data_received = False
            bytes_sent = 0

            while True:
                # Read new audio data
                data, new_position = buffer.read_from(position)

                if data:
                    if not first_data_received:
                        logger.info(
                            f"First audio data sent: {len(data)} bytes"
                        )
                        first_data_received = True

                    # Send data immediately without chunking for lowest
                    # latency
                    self.wfile.write(data)
                    self.wfile.flush()
                    position = new_position
                    bytes_sent += len(data)
                    no_data_count = 0
                else:
                    # No new data, wait a minimal amount
                    time.sleep(0.005)  # 5ms for ultra-low latency
                    no_data_count += 1

                    # Don't timeout - scanner may pause between
                    # transmissions. Just keep connection alive and wait
                    # for more data

                    # Periodically flush to detect disconnected clients
                    # Every ~1 second (200 * 5ms)
                    if no_data_count % 200 == 0:
                        try:
                            self.wfile.flush()
                        except:
                            logger.info(
                                f"Client disconnected after "
                                f"{bytes_sent} bytes sent"
                            )
                            break  # Client disconnected

        except (BrokenPipeError, ConnectionResetError) as e:
            # Client disconnected - this is normal behavior, not an
            # error
            logger.info(f"Client disconnected: {self.address_string()}")
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)

    def _make_wav_header(self, sample_rate, bits_per_sample, channels,
                         data_size):
        """Create WAV header"""
        byte_rate = sample_rate * channels * bits_per_sample // 8
        block_align = channels * bits_per_sample // 8

        header = bytearray()
        header += b'RIFF'
        # RIFF chunk size = data_size + 36 (for the rest of the header)
        # Cap at max 32-bit value
        riff_size = min(data_size + 36, 0xFFFFFFFF)
        header += riff_size.to_bytes(4, 'little', signed=False)
        header += b'WAVE'
        header += b'fmt '
        header += (16).to_bytes(4, 'little')  # fmt chunk size
        header += (1).to_bytes(2, 'little')   # PCM format
        header += channels.to_bytes(2, 'little')
        header += sample_rate.to_bytes(4, 'little')
        header += byte_rate.to_bytes(4, 'little')
        header += block_align.to_bytes(2, 'little')
        header += bits_per_sample.to_bytes(2, 'little')
        header += b'data'
        header += data_size.to_bytes(4, 'little', signed=False)

        return bytes(header)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """HTTP server with threading support"""
    daemon_threads = True
    allow_reuse_address = True


class AudioProxyServer(ThreadedHTTPServer):
    """Threaded HTTP server with audio buffer"""

    def __init__(self, server_address, handler_class, audio_buffer):
        super().__init__(server_address, handler_class)
        self.audio_buffer = audio_buffer


def start_audio_proxy(scanner_ip: str, port: int = 8765,
                      host: str = '0.0.0.0', low_latency: bool = False,
                      auto_reboot_callback=None) -> tuple:
    """
    Start the audio proxy server.

    Args:
        scanner_ip: Scanner IP address
        port: HTTP server port (default: 8765)
        host: HTTP server bind address (default: 0.0.0.0)
        low_latency: Enable ultra-low latency mode (default: False)
        auto_reboot_callback: Optional callback function to reboot
            scanner on connection failure

    Returns:
        Tuple of (server, streamer) for managing the proxy
    """
    logger.info("="*60)
    logger.info("Uniden Scanner Audio Proxy (radio-manager)")
    logger.info("="*60)
    logger.info(f"Scanner IP: {scanner_ip}")
    logger.info(f"HTTP Server: http://{host}:{port}")
    logger.info(f"Stream URL: http://{host}:{port}/stream")
    if low_latency:
        logger.info(f"Mode: ULTRA-LOW LATENCY (2KB buffer = ~0.125s)")
    else:
        logger.info(f"Mode: Low Latency (4KB buffer = ~0.25s)")
    logger.info("="*60)

    # Create audio buffer (smaller for lower latency)
    # At 8kHz 16-bit mono = 16KB/sec, so:
    # - 8KB = ~0.5 seconds
    # - 4KB = ~0.25 seconds
    # - 2KB = ~0.125 seconds
    buffer_size = 2 * 1024 if low_latency else 4 * 1024
    audio_buffer = AudioStreamBuffer(max_size=buffer_size)

    # Start RTSP streamer
    rtsp_streamer = RTSPAudioStreamer(scanner_ip, audio_buffer, auto_reboot_callback)
    rtsp_streamer.start()

    # Start HTTP server
    server = AudioProxyServer((host, port), AudioStreamHandler, audio_buffer)

    return server, rtsp_streamer
