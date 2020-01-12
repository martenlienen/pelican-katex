import atexit
import json
import shutil
import socket
import struct
import tempfile
import time
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired

SRC_DIR = Path(__file__).parent
SCRIPT_PATH = str(SRC_DIR / "render-katex.js")

ONE_MILLISECOND = 0.001

TIMEOUT_EXPIRED_TEMPLATE = (
    "Rendering {} took too long. Consider increasing KATEX_RENDER_TIMEOUT"
)

STARTUP_TIMEOUT_EXPIRED_TEMPLATE = (
    "KaTeX server did not start up after {} seconds. "
    "Consider increasing KATEX_STARTUP_TIMEOUT."
)

# Default KaTeX options.
KATEX_DEFAULT_OPTIONS = {
    # Prefer KaTeX's debug coloring by default
    "throwOnError": False
}

# Path to the KaTeX program to run
KATEX_PATH = None

# How long to wait for the render server to start in seconds
KATEX_STARTUP_TIMEOUT = 1.0

# Timeout per rendering request in seconds
KATEX_RENDER_TIMEOUT = 1.0

# nodejs binary to run javascript
KATEX_NODEJS_BINARY = "node"


class KaTeXError(Exception):
    pass


class RenderServer:
    """Manages and communicates with an instance of the render server"""

    # The length of a message is transmitted as 32-bit little-endian integer
    LENGTH_STRUCT = struct.Struct("<i")

    # A global instance
    RENDER_SERVER = None

    # How long to wait for the server to stop in seconds
    STOP_TIMEOUT = 0.1

    @staticmethod
    def build_command(socket_path):
        cmd = [KATEX_NODEJS_BINARY, SCRIPT_PATH, "--socket", str(socket_path)]

        if KATEX_PATH:
            cmd.extend(["--katex", str(KATEX_PATH)])

        return cmd

    @classmethod
    def start(cls):
        rundir = Path(tempfile.mkdtemp(prefix="pelican_katex"))
        socket_path = rundir / "katex.sock"

        # Start the server process
        cmd = cls.build_command(socket_path)
        process = Popen(cmd, stdin=PIPE, stdout=PIPE)

        # Wait for the server to come up and create the socket. Is there a
        # better way to do this?
        startup_start = time.monotonic()
        while not socket_path.is_socket():
            time.sleep(ONE_MILLISECOND)
            if time.monotonic() - startup_start > KATEX_STARTUP_TIMEOUT:
                message = STARTUP_TIMEOUT_EXPIRED_TEMPLATE.format(KATEX_STARTUP_TIMEOUT)
                raise KaTeXError(message)

        # Connect to the server through a unix socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(str(socket_path))

        server = RenderServer(rundir, process, sock)

        # Clean up after ourselves when pelican is done. This does not work in
        # live-reload mode if you stop it with ctrl+c because that is not an
        # orderly exit. However, I don't want to register signal handlers here
        # and using pelican's signals.finalized has a high performance penalty
        # because this is triggered after every reload and negates the advantage
        # of reusing servers across renders.
        atexit.register(RenderServer.stop, server)

        return server

    @classmethod
    def get(cls):
        """Get the current render server or start one"""
        if cls.RENDER_SERVER is None:
            cls.RENDER_SERVER = RenderServer.start()

        return cls.RENDER_SERVER

    def __init__(self, rundir, process, sock):
        self.rundir = rundir
        self.process = process
        self.sock = sock

        # Pre-allocate a buffer for the responses. KaTeX renderings usually have
        # lots of tags so let's start with 100kb.
        self.buffer = bytearray(100 * 1024)

    def stop(self):
        """Stop the render server and clean up"""
        self.sock.close()
        try:
            self.process.terminate()
            self.process.wait(timeout=self.STOP_TIMEOUT)
        except TimeoutExpired:
            self.process.kill()
        shutil.rmtree(self.rundir)

    def render(self, request, timeout=None):
        # Configure timeouts
        if timeout is not None:
            start_time = time.monotonic()
            self.sock.settimeout(timeout)

        # Send the request
        request_bytes = json.dumps(request).encode("utf-8")
        length = len(request_bytes)
        self.sock.sendall(self.LENGTH_STRUCT.pack(length))
        self.sock.sendall(request_bytes)

        # Read the amount of bytes we are about to receive
        length = self.LENGTH_STRUCT.unpack(self.sock.recv(self.LENGTH_STRUCT.size))[0]

        # Ensure that the buffer is large enough
        if len(self.buffer) < length:
            self.buffer = bytearray(length)

        with memoryview(self.buffer) as view:
            # Keep reading from the socket until we have received all bytes
            received = 0
            remaining = length
            while remaining > 0:
                # Abort if we are not done yet but the timeout has expired
                if timeout is not None:
                    elapsed = time.monotonic() - start_time
                    if elapsed >= timeout:
                        raise socket.timeout()
                    else:
                        # Subsequent recvs only get the remaining time instead
                        # of the whole timeout again
                        self.sock.settimeout(timeout - elapsed)

                n_received = self.sock.recv_into(view[received:length], remaining)
                received += n_received
                remaining -= n_received

            # Decode the response
            serialized = view[:length].tobytes().decode("utf-8")
            return json.loads(serialized)


def render_latex(latex, options=None):
    """Ask the KaTeX server to render some LaTeX.

    Parameters
    ----------
    latex : str
        LaTeX to render
    options : optional dict
        KaTeX options such as displayMode
    """

    # Combine caller-defined options with the default options
    katex_options = KATEX_DEFAULT_OPTIONS
    if options is not None:
        katex_options = katex_options.copy()
        katex_options.update(options)

    server = RenderServer.get()
    request = {"latex": latex, "katex_options": katex_options}

    try:
        response = server.render(request, KATEX_RENDER_TIMEOUT)

        if "html" in response:
            return response["html"]
        elif "error" in response:
            raise KaTeXError(response["error"])
        else:
            raise KaTeXError("Unknown response from KaTeX renderer")
    except socket.timeout:
        raise KaTeXError(TIMEOUT_EXPIRED_TEMPLATE.format(latex))
