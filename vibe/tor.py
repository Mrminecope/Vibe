import socket, subprocess, tempfile, shutil, time
from pathlib import Path
from PySide6 import QtCore

class TorSession(QtCore.QObject):
    progress=QtCore.Signal(int,str)
    ready=QtCore.Signal(int)
    failed=QtCore.Signal(str)

    def __init__(self, timeout=90):
        super().__init__(); self.timeout=timeout; self.process=None; self.root=None; self.socks_port=None

    @staticmethod
    def free_port():
        s=socket.socket(); s.bind(("127.0.0.1",0)); p=s.getsockname()[1]; s.close(); return p

    def start(self):
        if self.process and self.process.poll() is None: return self.socks_port
        if not shutil.which("tor") or not shutil.which("torsocks"):
            raise RuntimeError("Install Tor support with: sudo apt install tor torsocks")
        self.root=Path(tempfile.mkdtemp(prefix="vibe-tor-"))
        self.socks_port=self.free_port()
        cmd=["tor","--SocksPort",f"127.0.0.1:{self.socks_port}",
             "--DataDirectory",str(self.root),"--CookieAuthentication","0",
             "--AvoidDiskWrites","1","--Log","notice stdout"]
        self.process=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,text=True,bufsize=1)
        deadline=time.monotonic()+self.timeout
        while time.monotonic()<deadline:
            if self.process.poll() is not None: raise RuntimeError("Tor exited during startup.")
            line=self.process.stdout.readline()
            if "Bootstrapped " in line:
                try:pct=int(line.split("Bootstrapped ",1)[1].split("%",1)[0])
                except Exception:pct=0
                self.progress.emit(pct,line.strip())
                if pct>=100:
                    self.ready.emit(self.socks_port); return self.socks_port
        self.stop(); raise TimeoutError("Tor bootstrap timed out.")

    def prefix(self):
        if not self.socks_port: raise RuntimeError("Tor is not ready.")
        return ["torsocks","--isolate"]

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:self.process.kill()
        self.process=None; self.socks_port=None
        if self.root: shutil.rmtree(self.root,ignore_errors=True)
        self.root=None
