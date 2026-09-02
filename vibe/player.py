from PySide6 import QtCore
import json, socket, subprocess, threading, time, shutil, uuid

class MpvPlayer(QtCore.QObject):
    state=QtCore.Signal(str)
    timeline=QtCore.Signal(float,float)
    paused=QtCore.Signal(bool)
    error=QtCore.Signal(str)

    def __init__(self):
        super().__init__(); self.proc=None; self.sock=None; self.socket_name=None; self.thread=None; self.stop_event=threading.Event(); self.duration=0.0

    def _send(self, command):
        if not self.sock: return
        try:self.sock.sendall((json.dumps({"command":command},separators=(",",":"))+"\n").encode())
        except OSError: pass

    def _reader(self):
        buf=b""
        while not self.stop_event.is_set() and self.sock:
            try:
                data=self.sock.recv(65536)
                if not data: break
                buf += data
                while b"\n" in buf:
                    line,buf=buf.split(b"\n",1)
                    if not line: continue
                    try: msg=json.loads(line.decode())
                    except Exception: continue
                    if msg.get("event")=="property-change":
                        name,value=msg.get("name"),msg.get("data")
                        if name=="duration" and isinstance(value,(int,float)):
                            self.duration=float(value); self.timeline.emit(0.0,self.duration)
                        elif name=="time-pos" and isinstance(value,(int,float)): self.timeline.emit(float(value),self.duration)
                        elif name=="pause": self.paused.emit(bool(value))
                    elif msg.get("event")=="end-file":
                        reason=msg.get("reason",""); self.state.emit("ENDED" if reason in ("eof","stop") else "PLAYBACK ERROR")
            except OSError: break

    def play(self,url,prefix):
        self.stop()
        if not shutil.which("mpv"):
            self.error.emit("mpv is not installed. Install it with: sudo apt install mpv"); return False
        self.socket_name="@vibe-mpv-"+uuid.uuid4().hex
        cmd=[*prefix,"mpv","--no-config","--no-video","--cache=yes","--cache-on-disk=no","--cache-secs=3","--demuxer-max-bytes=16MiB","--demuxer-max-back-bytes=0","--input-ipc-server="+self.socket_name,"--idle=no","--really-quiet",url]
        try:self.proc=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,close_fds=True)
        except OSError as e:
            self.error.emit(f"Could not start mpv: {e}"); self.stop(); return False
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            if self.proc.poll() is not None:
                err=self.proc.stderr.read().strip() if self.proc.stderr else ""; self.error.emit("mpv exited before IPC became ready."+(f"\n\n{err[-700:]}" if err else "")); self.stop(); return False
            try:
                s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(.4); s.connect("\0"+self.socket_name[1:]); s.settimeout(None); self.sock=s; break
            except OSError:
                try:s.close()
                except Exception:pass
                time.sleep(.05)
        if not self.sock:
            err=self.proc.stderr.read().strip() if self.proc and self.proc.stderr else ""; self.error.emit("Vibe could not connect to mpv IPC.\n\nThe player process was started, but its local control socket was unavailable."+(f"\n\nmpv: {err[-700:]}" if err else "")); self.stop(); return False
        self.stop_event.clear(); self.thread=threading.Thread(target=self._reader,daemon=True); self.thread.start()
        for i,name in enumerate(("time-pos","duration","pause"),1): self._send(["observe_property",i,name])
        self._send(["get_property","time-pos"]); self._send(["get_property","duration"]); self._send(["get_property","pause"]); self.state.emit("PLAYING"); return True

    def pause(self): self._send(["cycle","pause"])
    def seek(self,seconds): self._send(["set_property","time-pos",max(0.0,float(seconds))])
    def stop(self):
        self.stop_event.set()
        if self.sock:
            try:self.sock.close()
            except OSError:pass
        self.sock=None
        if self.proc and self.proc.poll() is None:
            try:self.proc.terminate(); self.proc.wait(timeout=1.5)
            except subprocess.TimeoutExpired:self.proc.kill()
        self.proc=None; self.socket_name=None; self.duration=0.0
