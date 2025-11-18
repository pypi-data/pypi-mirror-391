# -*- coding: utf-8 -*-
import json
import pytest
import app_manager as am

# ---------- launch() ----------
def test_launch_with_exe_path_success(patch_env):
    m = am.AppManager()
    p = m.launch(exe_path=r"C:\Program Files\foo.exe")
    assert hasattr(p, "pid")
    # Popen received the exe path directly
    assert p.args == [r"C:\Program Files\foo.exe"]

def test_launch_with_missing_exe_raises(monkeypatch):
    monkeypatch.setattr("app_manager.os.path.exists", lambda p: False, raising=True)
    m = am.AppManager()
    with pytest.raises(FileNotFoundError):
        m.launch(exe_path=r"C:\bad\missing.exe")

def test_launch_with_app_name_uses_aumid(monkeypatch):
    m = am.AppManager()
    # ensure _get_aumid returns a known value
    monkeypatch.setattr(m, "_get_aumid", lambda name: "Fake.AUMID!123", raising=True)
    p = m.launch(app_name="LM Studio")
    assert p.args[0] == "explorer.exe"
    assert p.args[1].startswith("shell:AppsFolder\\Fake.AUMID!123")

def test_launch_both_or_none_raises():
    m = am.AppManager()
    with pytest.raises(ValueError):
        m.launch()  # neither
    with pytest.raises(ValueError):
        m.launch(exe_path="a.exe", app_name="b")  # both

# ---------- connect() ----------
def test_connect_by_window_title_returns_window(patch_env):
    m = am.AppManager()
    w = m.connect(window_title="RootWindow", timeout=1)
    assert w.window_text() == "RootWindow"
    assert m._window is w

def test_connect_by_process_name_returns_window(patch_env):
    m = am.AppManager()
    w = m.connect(process_name="LM Studio.exe", timeout=1)
    assert w.window_text() == "RootWindow"

def test_connect_requires_param():
    m = am.AppManager()
    with pytest.raises(ValueError):
        m.connect()

# ---------- ensure_connected() ----------
def test_ensure_connected_relaunch_flow(monkeypatch, patch_env):
    m = am.AppManager()

    # First connect attempt should fail
    def _fail_connect(**kwargs):
        raise RuntimeError("not running")
    monkeypatch.setattr(m, "connect", lambda **kw: _fail_connect(**kw), raising=True)

    # After launch, connect should succeed
    def _succeed_connect(**kwargs):
        return patch_env["fake_app"].top_window().wrapper_object()
    calls = {"n": 0}
    def _connect_proxy(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("first fail")
        return _succeed_connect(**kwargs)
    monkeypatch.setattr(m, "connect", _connect_proxy, raising=True)

    w = m.ensure_connected(
        launch_exe=r"C:\Program Files\foo.exe",
        connect_window="RootWindow",
        connect_timeout=1,
        relaunch_connect_timeout=2,
        relaunch_delay=0
    )
    assert w.window_text() == "RootWindow"
    assert calls["n"] >= 2

def test_ensure_connected_param_checks():
    m = am.AppManager()
    with pytest.raises(ValueError):
        m.ensure_connected()  # neither connect_window/process

# ---------- element finding ----------
def test_element_found_after_refresh(monkeypatch, patch_env):
    m = am.AppManager()
    # set a connected window
    m._app = patch_env["fake_app"]
    m._window = patch_env["fake_app"].top_window().wrapper_object()

    # First refresh returns empty; second returns a matching element
    from app_manager import ElementInfo
    fake_ctrl = patch_env["root"].children()[0]  # doc
    ei = ElementInfo(handle=fake_ctrl.handle, control_type="Document", name=fake_ctrl.element_info.name,
                     automation_id="", rectangle="", depth=1)

    calls = {"n": 0}
    def _extract(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return []  # first poll sees nothing
        return [(ei, fake_ctrl)]

    monkeypatch.setattr(m, "extract_elements", _extract, raising=True)

    ctrl = m.element({"name": fake_ctrl.element_info.name, "control_type": "Document"})
    assert ctrl is fake_ctrl
    assert calls["n"] >= 2

def test_element_not_found_raises(monkeypatch, patch_env):
    m = am.AppManager()
    m._app = patch_env["fake_app"]
    m._window = patch_env["fake_app"].top_window().wrapper_object()
    monkeypatch.setattr(m, "extract_elements", lambda **k: [], raising=True)
    with pytest.raises(am.ElementNotFoundError):
        m.element({"name": "nope"})

# ---------- extract_elements ----------
def test_extract_elements_traversal_isolation_and_enrich(tmp_path, patch_env):
    m = am.AppManager()
    m._app = patch_env["fake_app"]
    m._window = patch_env["fake_app"].top_window().wrapper_object()

    dump_file = tmp_path / "dump.json"
    visited = m.extract_elements(max_depth=0, include_invisible=False, dump_file=dump_file,
                                 isolate=True, enrich_rect=True)

    # Should include at least root + doc + pane + button
    names = {(ei.name, ei.control_type, ei.depth) for ei, _ in visited}
    assert ("Root", "Window", 0) in names
    assert ("Chrome Legacy Window", "Document", 1) in names   # depth==1 Document whitelisted
    assert ("OK", "Button", 2) in names

    # rectangles filled
    assert all(ei.rectangle for ei, _ in visited)

    data = json.loads(dump_file.read_text(encoding="utf-8"))
    assert isinstance(data, list) and len(data) == len(visited)

def test_extract_elements_max_depth_limits(patch_env):
    m = am.AppManager()
    m._app = patch_env["fake_app"]
    m._window = patch_env["fake_app"].top_window().wrapper_object()

    visited = m.extract_elements(max_depth=1, include_invisible=False, isolate=False, enrich_rect=False)
    depths = [ei.depth for ei, _ in visited]
    assert all(d <= 1 for d in depths)

# ---------- close() ----------
def test_close_graceful(monkeypatch, patch_env):
    m = am.AppManager()
    m._app = patch_env["fake_app"]
    m._window = patch_env["fake_app"].top_window().wrapper_object()

    # top_window().close() succeeds
    m.close(graceful=True)
    assert m._app is None and m._window is None

def test_close_fallback_to_kill(monkeypatch, patch_env):
    m = am.AppManager()
    m._app = patch_env["fake_app"]
    m._window = patch_env["fake_app"].top_window().wrapper_object()

    def _fail_close():
        raise RuntimeError("nope")
    monkeypatch.setattr(m._app.top_window(), "close", _fail_close, raising=True)

    m.close(graceful=True)
    # should have been nulled out
    assert m._app is None and m._window is None

# ---------- _get_aumid ----------
def test_get_aumid_success_exact(monkeypatch):
    def _fake_query(self, name, exact):
        assert name == "LM Studio"
        if exact:
            return [{"name": "LM Studio", "app_id": "Fake.AUMID!123"}]
        return []

    monkeypatch.setattr(am.AppManager, "_query_aumids", _fake_query, raising=True)

    m = am.AppManager()
    assert m._get_aumid("LM Studio") == "Fake.AUMID!123"


def test_get_aumid_success_fuzzy(monkeypatch):
    calls: list[bool] = []

    def _fake_query(self, name, exact):
        assert name == "Cool App"
        calls.append(exact)
        if exact:
            return []
        return [
            {"name": "Cool App Beta", "app_id": "Fake.AUMID!999"},
            {"name": "Cool App", "app_id": "Fake.AUMID!123"},
        ]

    monkeypatch.setattr(am.AppManager, "_query_aumids", _fake_query, raising=True)

    m = am.AppManager()
    assert m._get_aumid("Cool App") == "Fake.AUMID!999"
    assert calls == [True, False]


def test_get_aumid_not_found(monkeypatch):
    def _fake_query(self, name, exact):
        assert name == "UnknownApp"
        return []

    monkeypatch.setattr(am.AppManager, "_query_aumids", _fake_query, raising=True)

    m = am.AppManager()
    with pytest.raises(am.AumidNotFoundError):
        m._get_aumid("UnknownApp")
