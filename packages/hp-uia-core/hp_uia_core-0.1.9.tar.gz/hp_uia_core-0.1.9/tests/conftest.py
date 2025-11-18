# -*- coding: utf-8 -*-
import logging
import pytest
import app_manager as am

@pytest.fixture(autouse=True)
def _silence_logs():
    logging.getLogger().setLevel(logging.CRITICAL)
    yield
    
@pytest.fixture(autouse=True)
def _autopatch_subproc_and_sleep(monkeypatch):
    """全局拦截：防止任何测试真的启动 explorer.exe / shell:AppsFolder... / 等。
    同时把 time.sleep() 变为 no-op 加速测试。
    """
    # ---- Fake Popen（不启动任何进程）----
    class _FakePopen:
        def __init__(self, args, *a, **kw):
            self.args = args
            self.pid = 99999
    monkeypatch.setattr(am.subprocess, "Popen", _FakePopen, raising=True)

    # ---- Fake run（给 Get-StartApps 一个稳定返回；其余返回空）----
    class _Completed:
        def __init__(self, out):
            self.stdout = out
    def _fake_run(cmd, capture_output=False, text=False, check=False):
        cmd_str = " ".join(cmd) if isinstance(cmd, (list, tuple)) else str(cmd)
        if "Get-StartApps" in cmd_str:
            return _Completed("Fake.AUMID!123")
        return _Completed("")
    monkeypatch.setattr(am.subprocess, "run", _fake_run, raising=True)

    # ---- 加速：避免真正 sleep ----
    monkeypatch.setattr(am.time, "sleep", lambda s: None, raising=True)

# --------- Fakes for pywinauto-like wrappers ---------
class FakeElementInfo:
    def __init__(self, control_type="", name="", automation_id="", pid=123):
        self.control_type = control_type
        self.name = name
        self.automation_id = automation_id
        self._pid = pid
        self._children = []

    def children(self):
        return [c._ei for c in self._children]

    def add_child(self, wrapper):
        self._children.append(wrapper)

class FakeWrapper:
    def __init__(self, text="win", pid=123, control_type="Window", name="root", automation_id="", visible=True, handle=100):
        self._text = text
        self._pid = pid
        self._visible = visible
        self.handle = handle
        self._ei = FakeElementInfo(control_type=control_type, name=name, automation_id=automation_id, pid=pid)
        self._children = []
        self._closed = False

    # ---- pywinauto 常见接口 ----
    def window_text(self):
        return self._text

    def set_focus(self):
        return True

    def is_visible(self):
        return self._visible

    def rectangle(self):
        class R:
            def __str__(self_non):  # noqa: N807
                return "Rect(l,t,r,b)"
        return R()

    @property
    def element_info(self):
        return self._ei

    def children(self):
        return self._children

    def add_child(self, child):
        self._children.append(child)
        self._ei.add_child(child)

    # ---- 关键补充：与 pywinauto 行为对齐 ----
    def wrapper_object(self):
        """pywinauto 的 window()/top_window() 等经常通过 .wrapper_object() 拿到 Wrapper。
        我们的 Fake 直接返回自身即可。"""
        return self

    def process_id(self):
        """与 pywinauto.BaseWrapper.process_id() 一致"""
        return self._pid

    def close(self):    
        """用于 graceful close 分支"""
        self._closed = True
        return True


class FakeApp:
    def __init__(self, top: FakeWrapper):
        self._top = top
        self._killed = False

    # app_manager uses .connect(handle=...) or .connect(title_re=..., timeout=..)
    def connect(self, **kwargs):
        return self

    def top_window(self):
        return self._top

    def kill(self):
        self._killed = True

    def window(self, handle):
        # returns something with wrapper_object
        class _W:
            def __init__(self, top):
                self._top = top
            def wrapper_object(self):
                return self._top
        return _W(self._top)

# Desktop(backend="uia").windows() → list of top windows
class FakeDesktop:
    def __init__(self, wins):
        self._wins = wins
    def windows(self):
        return self._wins

# UIAWrapper(ei) → wrapper; we’ll wrap FakeElementInfo into a lightweight FakeWrapper
class FakeUIAWrapper(FakeWrapper):
    def __init__(self, ei: FakeElementInfo):
        super().__init__(text="child", pid=ei._pid, control_type=ei.control_type, name=ei.name, automation_id=ei.automation_id, visible=True, handle=200)
        self._ei = ei

@pytest.fixture
def fake_tree():
    """Build a small UI tree:
    root(Window)
      ├─ doc(Document, depth=1)
      │    └─ btn(Button, visible=False by default? we’ll set visible=True)
      └─ pane(Pane)
    """
    root = FakeWrapper(text="RootWindow", control_type="Window", name="Root", visible=True, handle=101)
    doc  = FakeWrapper(text="Doc", control_type="Document", name="Chrome Legacy Window", visible=True, handle=102)
    btn  = FakeWrapper(text="Button", control_type="Button", name="OK", visible=True, handle=103)
    pane = FakeWrapper(text="Pane", control_type="Pane", name="", visible=True, handle=104)
    doc.add_child(btn)
    root.add_child(doc)
    root.add_child(pane)
    return root, doc, btn, pane

@pytest.fixture
def patch_env(monkeypatch, fake_tree, tmp_path):
    """
    Patch external modules that app_manager imports:
    - pywinauto.Application / Desktop / controls.uiawrapper.UIAWrapper / base_wrapper.BaseWrapper
    - psutil.process_iter
    - subprocess.Popen / subprocess.run
    """
    root, *_ = fake_tree

    # ---- patch pywinauto symbols on the already-imported module ----
    

    fake_app = FakeApp(root)

    class _Application:
        def __init__(self, backend):
            self.backend = backend
        def connect(self, **kwargs):
            return fake_app

    def _Desktop(backend="uia"):
        return FakeDesktop([root])

    # Inject
    monkeypatch.setattr(am, "Application", _Application, raising=True)
    monkeypatch.setattr(am, "Desktop", _Desktop, raising=True)
    monkeypatch.setattr(am, "UIAWrapper", FakeUIAWrapper, raising=True)

    # BaseWrapper is only for typing; provide alias
    class _BaseWrapper(FakeWrapper): ...
    monkeypatch.setattr(am, "BaseWrapper", _BaseWrapper, raising=True)

    # ---- psutil.process_iter ----
    class Proc:
        def __init__(self, pid, name):
            self.info = {"pid": pid, "name": name}

    # 让进程 PID 与 fake 窗口 PID 一致
    def _proc_iter(attrs=None):
        return [Proc(root.process_id(), "LM Studio.exe")]

    monkeypatch.setattr("app_manager.psutil.process_iter", _proc_iter, raising=True)

    # 避免 connect 里真的 sleep
    monkeypatch.setattr("app_manager.time.sleep", lambda s: None, raising=True)

    # ---- subprocess.Popen / run ----
    class _Popen:
        def __init__(self, args):
            self.args = args
            self.pid = 999
    monkeypatch.setattr("app_manager.subprocess.Popen", _Popen, raising=True)

    class _Completed:
        def __init__(self, out):
            self.stdout = out
    def _run(cmd, capture_output=False, text=False, check=False):
        # simulate powershell Get-StartApps output
        if "Get-StartApps" in " ".join(cmd):
            return _Completed("Fake.AUMID!123")
        return _Completed("")
    monkeypatch.setattr("app_manager.subprocess.run", _run, raising=True)

    # ---- os.path.exists for exe ----
    monkeypatch.setattr("app_manager.os.path.exists", lambda p: str(p).endswith(".exe"), raising=True)

    return {"fake_app": fake_app, "root": root, "tmp_path": tmp_path}
