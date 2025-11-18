# -*- coding: utf-8 -*-
import types, csv
import utils  # noqa: E402


def _patch_psutil(monkeypatch, *, cpu=12.3, mem=45.6, battery=88):
    """Unified patching: cpu_percent / virtual_memory / sensors_battery"""
    monkeypatch.setattr(utils.psutil, "cpu_percent", lambda interval=1: cpu, raising=True)
    monkeypatch.setattr(utils.psutil, "virtual_memory",
                        lambda: types.SimpleNamespace(percent=mem), raising=True)
    if battery is None:
        monkeypatch.setattr(utils.psutil, "sensors_battery", lambda: None, raising=True)
    else:
        monkeypatch.setattr(utils.psutil, "sensors_battery",
                            lambda: types.SimpleNamespace(percent=battery), raising=True)


def test_new_file_writes_header_and_one_row(monkeypatch, tmp_path):
    _patch_psutil(monkeypatch, cpu=10.0, mem=20.0, battery=30)
    out = tmp_path / "metrics.csv"

    metrics = utils.capture_system_metrics(event="BOOT", output_file=str(out))

    # Return value field validation
    assert set(metrics.keys()) == {"timestamp", "event", "cpu_percent", "memory_percent", "battery_percent"}
    assert metrics["event"] == "BOOT"
    assert metrics["cpu_percent"] == 10.0
    assert metrics["memory_percent"] == 20.0
    assert metrics["battery_percent"] == 30
    assert "T" in metrics["timestamp"]  # ISO format rough check

    # CSV content validation (header + one data row)
    with out.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["event"] == "BOOT"
    assert float(rows[0]["cpu_percent"]) == 10.0
    assert float(rows[0]["memory_percent"]) == 20.0
    assert rows[0]["battery_percent"] == "30"


def test_append_existing_file_no_duplicate_header(monkeypatch, tmp_path):
    _patch_psutil(monkeypatch, cpu=11.0, mem=22.0, battery=33)
    out = tmp_path / "metrics.csv"

    # First write (creates header)
    utils.capture_system_metrics(event="E1", output_file=str(out))
    # Second write (appends, should not duplicate header)
    _patch_psutil(monkeypatch, cpu=12.0, mem=23.0, battery=34)
    utils.capture_system_metrics(event="E2", output_file=str(out))

    # DictReader should read two data rows
    with out.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    events = [r["event"] for r in rows]
    assert events == ["E1", "E2"]


def test_no_battery_sets_NA(monkeypatch, tmp_path):
    _patch_psutil(monkeypatch, cpu=7.0, mem=8.0, battery=None)
    out = tmp_path / "metrics.csv"

    metrics = utils.capture_system_metrics(event="NOBATT", output_file=str(out))
    assert metrics["battery_percent"] == "N/A"

    with out.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["battery_percent"] == "N/A"


def test_write_error_raises_runtimeerror(monkeypatch, tmp_path):
    _patch_psutil(monkeypatch, cpu=1.0, mem=2.0, battery=3)
    out = tmp_path / "metrics.csv"

    # Force open to fail
    import builtins
    def _boom(*a, **k):
        raise OSError("disk full")
    monkeypatch.setattr(builtins, "open", _boom, raising=True)

    import pytest
    with pytest.raises(RuntimeError) as ei:
        utils.capture_system_metrics(event="ERR", output_file=str(out))
    assert "Failed to capture system metrics" in str(ei.value)
