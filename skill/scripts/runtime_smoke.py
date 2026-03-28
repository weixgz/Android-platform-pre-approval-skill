#!/usr/bin/env python3
"""
Runtime smoke test helper for Android APK review.

This script is intentionally lightweight:
- prep: install + launch + clear logcat
- collect: take a screenshot + dump logcat and extract highlights

It is designed for "evidence collection" rather than full UI automation.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from androguard.core.apk import APK  # type: ignore
except Exception:
    APK = None  # type: ignore


URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

# Focused on the common causes of "video cannot load" and network failures.
HIGHLIGHT_RE = re.compile(
    r"("
    r"UnknownHostException|"
    r"SSLHandshake|CERTIFICATE|CertPath|"
    r"timed out|timeout|"
    r"\bHTTP\/1\.[01]\b|\bHTTP\/2\b|"
    r"\b40[034]\b|\b50[0-9]\b|"
    r"ExoPlayer|MediaCodec|OMX|IJKMEDIA|IjkMediaPlayer|"
    r"m3u8|\.mp4\b|rtmp|"
    r"\bE\/[A-Za-z0-9_.-]+\b"
    r")",
    re.IGNORECASE,
)


def _run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=check,
        text=True,
        capture_output=True,
    )


def adb(serial: str | None, args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += args
    return _run(cmd, check=check)


def parse_device_list(adb_devices_output: str) -> list[str]:
    serials: list[str] = []
    for line in adb_devices_output.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        serial, state = parts[0], parts[1]
        if state == "device":
            serials.append(serial)
    return serials


def detect_serial(user_serial: str | None) -> str:
    if user_serial:
        return user_serial
    out = adb(None, ["devices", "-l"]).stdout
    serials = parse_device_list(out)
    if not serials:
        raise SystemExit("no adb device found: please connect a phone or start an emulator first")
    if len(serials) > 1:
        raise SystemExit(
            "multiple adb devices found; please pass --serial. devices: " + ", ".join(serials)
        )
    return serials[0]


def normalize_activity(package: str, activity: str | None) -> str | None:
    if not activity:
        return None
    if activity.startswith("."):
        return package + activity
    if "." in activity:
        return activity
    return package + "." + activity


def apk_identity(apk_path: Path) -> dict[str, str | None]:
    if APK is None:
        raise SystemExit("androguard is required for runtime_smoke.py (pip install androguard)")
    apk = APK(str(apk_path))
    package = apk.get_package()
    main_activity = apk.get_main_activity()
    return {
        "package_name": package,
        "main_activity": main_activity,
    }


def dumpsys_current_focus(serial: str) -> str | None:
    out = adb(serial, ["shell", "dumpsys", "window"]).stdout
    for line in out.splitlines():
        if "mCurrentFocus=" in line:
            return line.strip()
    return None


def list_pids(serial: str, package: str) -> list[int]:
    out = adb(serial, ["shell", "sh", "-c", f"ps -A | grep {package} || true"]).stdout
    pids: list[int] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].startswith(package):
            try:
                pids.append(int(parts[1]))
            except Exception:
                continue
    return sorted(set(pids))


def dump_logcat(serial: str) -> str:
    return adb(serial, ["logcat", "-d", "-v", "time"]).stdout


def dump_logcat_by_pid(serial: str, pid: int) -> str:
    # --pid is supported by modern adb/logcat, but not always present on older stacks.
    cp = adb(serial, ["logcat", f"--pid={pid}", "-d", "-v", "time"], check=False)
    return cp.stdout or ""


def extract_highlights(text: str, *, limit: int = 200) -> list[str]:
    hits: list[str] = []
    for line in text.splitlines():
        if HIGHLIGHT_RE.search(line):
            hits.append(line)
            if len(hits) >= limit:
                break
    return hits


def extract_urls(text: str, *, limit: int = 50) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for m in URL_RE.finditer(text):
        u = m.group(0)
        if u in seen:
            continue
        seen.add(u)
        urls.append(u)
        if len(urls) >= limit:
            break
    return urls


def take_screencap(serial: str, out_path: Path) -> None:
    remote = "/sdcard/runtime_smoke.png"
    adb(serial, ["shell", "screencap", "-p", remote])
    # Ensure parent exists before pulling.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    adb(serial, ["pull", remote, str(out_path)])


@dataclass
class PrepResult:
    serial: str
    package_name: str
    component: str | None
    focused: str | None
    pids: list[int]
    started_at_epoch_s: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "serial": self.serial,
            "package_name": self.package_name,
            "component": self.component,
            "focused": self.focused,
            "pids": self.pids,
            "started_at_epoch_s": self.started_at_epoch_s,
        }


def cmd_prep(args: argparse.Namespace) -> int:
    apk_path = Path(args.apk_path)
    if not apk_path.exists():
        raise SystemExit(f"apk not found: {apk_path}")

    ident = apk_identity(apk_path)
    package = ident.get("package_name")
    if not package:
        raise SystemExit("failed to read package name from apk")

    serial = detect_serial(args.serial)
    if args.install:
        adb(serial, ["install", "-r", str(apk_path)])

    # Clear logcat so the later collect is naturally scoped.
    adb(serial, ["logcat", "-c"])

    component: str | None = None
    activity = normalize_activity(package, ident.get("main_activity"))
    if args.launch and activity:
        component = f"{package}/{activity}"
        adb(serial, ["shell", "am", "start", "-n", component], check=False)
        time.sleep(max(0.0, float(args.wait_s)))

    focused = dumpsys_current_focus(serial)
    pids = list_pids(serial, package)

    result = PrepResult(
        serial=serial,
        package_name=package,
        component=component,
        focused=focused,
        pids=pids,
        started_at_epoch_s=int(time.time()),
    )

    payload = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    serial = detect_serial(args.serial)
    package = args.package

    pids = list_pids(serial, package)
    logs: dict[str, str] = {}

    # Try pid-filtered log first (lower noise), fall back to full logcat if needed.
    for pid in pids:
        t = dump_logcat_by_pid(serial, pid).strip()
        if t:
            logs[str(pid)] = t

    full_log = ""
    if not logs:
        full_log = dump_logcat(serial)
    else:
        # Still keep a small slice of full logcat for cross-process system errors if requested.
        if args.include_full:
            full_log = dump_logcat(serial)

    combined = "\n".join(list(logs.values()) + ([full_log] if full_log else []))
    highlights = extract_highlights(combined, limit=int(args.highlight_limit))
    urls = extract_urls(combined)

    screenshot_path: str | None = None
    if args.screenshot:
        out_path = Path(args.screenshot)
        take_screencap(serial, out_path)
        screenshot_path = str(out_path)

    payload = {
        "serial": serial,
        "package_name": package,
        "pids": pids,
        "focused": dumpsys_current_focus(serial),
        "highlights": highlights,
        "urls": urls,
        "screenshot": screenshot_path,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Android runtime smoke test helper (adb-based)")
    sub = p.add_subparsers(dest="cmd", required=True)

    prep = sub.add_parser("prep", help="install+launch+clear logcat")
    prep.add_argument("apk_path", help="path to apk file")
    prep.add_argument("--serial", help="adb serial (if multiple devices connected)")
    prep.add_argument("--no-install", dest="install", action="store_false", help="skip adb install")
    prep.add_argument("--no-launch", dest="launch", action="store_false", help="skip am start")
    prep.add_argument("--wait-s", type=float, default=1.0, help="wait seconds after launch")
    prep.add_argument("--output", help="write json result to file")
    prep.set_defaults(func=cmd_prep, install=True, launch=True)

    collect = sub.add_parser("collect", help="collect screenshot+logcat and extract highlights")
    collect.add_argument("--package", required=True, help="package name (e.g. com.example.app)")
    collect.add_argument("--serial", help="adb serial (if multiple devices connected)")
    collect.add_argument("--screenshot", help="write screenshot png to this path")
    collect.add_argument("--include-full", action="store_true", help="include full logcat in url/highlight scan")
    collect.add_argument("--highlight-limit", type=int, default=200, help="max highlight lines")
    collect.add_argument("--output", help="write json result to file")
    collect.set_defaults(func=cmd_collect)

    return p


def main(argv: Iterable[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv))
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

