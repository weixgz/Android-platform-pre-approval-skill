#!/usr/bin/env python3
"""Static APK prescreen analyzer.

Usage:
  python scripts/apk_review.py app.apk --output report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

SENSITIVE_PERMISSION_KEYWORDS = [
    "ACCESS_FINE_LOCATION",
    "ACCESS_COARSE_LOCATION",
    "ACCESS_BACKGROUND_LOCATION",
    "READ_CONTACTS",
    "WRITE_CONTACTS",
    "READ_CALL_LOG",
    "WRITE_CALL_LOG",
    "READ_SMS",
    "SEND_SMS",
    "RECEIVE_SMS",
    "RECORD_AUDIO",
    "CAMERA",
    "READ_MEDIA",
    "READ_EXTERNAL_STORAGE",
    "WRITE_EXTERNAL_STORAGE",
    "MANAGE_EXTERNAL_STORAGE",
    "QUERY_ALL_PACKAGES",
    "SYSTEM_ALERT_WINDOW",
    "PACKAGE_USAGE_STATS",
    "REQUEST_INSTALL_PACKAGES",
    "BIND_ACCESSIBILITY_SERVICE",
    "BIND_NOTIFICATION_LISTENER_SERVICE",
    "SCHEDULE_EXACT_ALARM",
    "USE_EXACT_ALARM",
    "POST_NOTIFICATIONS",
    "READ_PHONE_STATE",
    "READ_PHONE_NUMBERS",
]

HIGH_RISK_STRING_PATTERNS = {
    "placeholder_text": [r"\btest\b", r"\bdemo\b", r"\btodo\b", r"\bsample\b", r"\bdebug\b"],
    "account_deletion": [r"delete account", r"注销", r"account cancellation", r"remove account"],
    "privacy_policy": [r"privacy policy", r"隐私政策", r"personal information", r"用户协议"],
    "consent_flow": [r"agree", r"reject", r"consent", r"授权", r"同意", r"拒绝"],
    "device_identifier": [r"imei", r"imsi", r"oaid", r"android id", r"mac address", r"boot_id", r"cpuid"],
    "installed_apps": [r"installed apps", r"app list", r"应用列表"],
    "silent_install": [r"silent install", r"静默安装", r"auto install", r"自动安装"],
    "self_update": [r"self update", r"hot update", r"dynamic code", r"热更新", r"补丁包"],
}

DOMAIN_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
HOST_PATTERN = re.compile(r"\b(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")
IP_PATTERN = re.compile(r"\b(?:127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b")
ASSET_URL_PATTERN = re.compile(rb"https?://[^\s\"'<>]+", re.IGNORECASE)
ASSET_VIDEO_KEYS = [
    b"video_url",
    b"videourl",
    b"playurl",
    b"play_url",
    b"m3u8",
    b".mp4",
    b"rtmp",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("apk_path", help="Path to APK file")
    parser.add_argument("--output", help="Write JSON report to file")
    return parser.parse_args()


def load_apk(apk_path: str):
    try:
        from loguru import logger
        from androguard.core.apk import APK
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "androguard is required. install it with: python -m pip install androguard"
        ) from exc
    logger.remove()
    logger.add(sys.stderr, level="ERROR")
    return APK(apk_path)


def safe_get(value: Any, default: Any = None) -> Any:
    return value if value not in (None, "") else default


def manifest_attr(
    apk, tag_name: str, attribute: str, default: Any = None, **attribute_filter
) -> Any:
    try:
        return safe_get(
            apk.get_attribute_value(tag_name, attribute, **attribute_filter), default
        )
    except Exception:
        return default


def scan_text_assets(apk_path: Path) -> dict[str, Any]:
    """Lightweight scan of bundled web assets for URLs, staging domains, and video keys.

    This does not prove runtime behavior, but it provides actionable hints for smoke tests
    (e.g. playback endpoints are usually fetched dynamically via API).
    """
    if not apk_path.exists():
        return {}

    url_set: set[str] = set()
    host_set: set[str] = set()
    test_domains: set[str] = set()
    video_keys_found: set[str] = set()
    files_with_hits: set[str] = set()

    asset_allowlist_re = re.compile(
        r"^(assets/apps/[^/]+/www/"
        r"(app-service\.js|app-view\.js|app-config-service\.js|manifest\.json|androidPrivacy\.json|view\.umd\.min\.js)"
        r"|assets/data/dcloud_properties\.xml)$"
    )

    def add_url(u: str) -> None:
        if len(url_set) >= 80:
            return
        url_set.add(u)
        m = re.match(r"^https?://([^/]+)", u, re.IGNORECASE)
        if m and len(host_set) < 80:
            host = m.group(1)
            host_set.add(host)
            if ".test." in host.lower() or host.lower().endswith(".test"):
                if len(test_domains) < 50:
                    test_domains.add(host)

    try:
        with zipfile.ZipFile(apk_path, "r") as zf:
            for name in zf.namelist():
                if not asset_allowlist_re.match(name):
                    continue
                try:
                    data = zf.read(name)
                except Exception:
                    continue

                lowered = data.lower()
                file_hit = False

                for key in ASSET_VIDEO_KEYS:
                    if key in lowered:
                        video_keys_found.add(key.decode("utf-8", "ignore"))
                        file_hit = True

                for m in ASSET_URL_PATTERN.finditer(data):
                    add_url(m.group(0).decode("utf-8", "ignore"))
                    file_hit = True

                if file_hit:
                    files_with_hits.add(name)
    except Exception:
        return {}

    return {
        "urls": sorted(url_set),
        "hosts": sorted(host_set),
        "test_domains": sorted(test_domains),
        "video_keys_found": sorted(video_keys_found),
        "files_with_hits": sorted(files_with_hits)[:50],
    }


def permission_flags(permission: str) -> dict[str, bool]:
    return {
        "sensitive": any(key in permission for key in SENSITIVE_PERMISSION_KEYWORDS),
        "signature_or_special": any(
            key in permission
            for key in [
                "BIND_",
                "MANAGE_",
                "QUERY_ALL_PACKAGES",
                "REQUEST_INSTALL_PACKAGES",
                "SYSTEM_ALERT_WINDOW",
                "PACKAGE_USAGE_STATS",
                "SCHEDULE_EXACT_ALARM",
                "USE_EXACT_ALARM",
            ]
        ),
    }


def collect_strings(apk) -> list[str]:
    strings: list[str] = []
    try:
        resources = apk.get_android_resources()
        if resources:
            for package in resources.get_packages_names():
                locales = resources.get_resolved_strings()
                if not locales:
                    continue
                for locale_map in locales.values():
                    if isinstance(locale_map, dict):
                        for _, text in locale_map.items():
                            if isinstance(text, str):
                                strings.append(text)
    except Exception:
        pass
    # Add manifest and file names as a light-weight supplement.
    try:
        strings.extend(list(apk.get_files().keys()))
    except Exception:
        pass
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in strings:
        s = item.strip()
        if len(s) < 3 or len(s) > 500:
            continue
        if s not in seen:
            seen.add(s)
            cleaned.append(s)
    return cleaned


def scan_string_patterns(strings: list[str]) -> dict[str, list[str]]:
    results: dict[str, list[str]] = {k: [] for k in HIGH_RISK_STRING_PATTERNS}
    for text in strings:
        lowered = text.lower()
        for category, patterns in HIGH_RISK_STRING_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, lowered, re.IGNORECASE):
                    results[category].append(text)
                    break
    for key in results:
        results[key] = results[key][:20]
    return results


def extract_domains(strings: list[str]) -> dict[str, list[str]]:
    urls: set[str] = set()
    hosts: set[str] = set()
    local_or_test: set[str] = set()
    for text in strings:
        for url in DOMAIN_PATTERN.findall(text):
            urls.add(url)
            if any(token in url.lower() for token in ["localhost", "127.0.0.1", ".local", ".test", "10.", "192.168."]):
                local_or_test.add(url)
        for host in HOST_PATTERN.findall(text):
            hosts.add(host)
            if any(token in host.lower() for token in ["localhost", ".local", ".test"]):
                local_or_test.add(host)
        for ip in IP_PATTERN.findall(text):
            local_or_test.add(ip)
    return {
        "urls": sorted(urls)[:100],
        "hosts": sorted(hosts)[:100],
        "local_or_test": sorted(local_or_test)[:50],
    }


def component_rows(apk, kind: str) -> list[dict[str, Any]]:
    getters = {
        "activities": apk.get_activities,
        "services": apk.get_services,
        "receivers": apk.get_receivers,
        "providers": apk.get_providers,
    }
    intent_kinds = {
        "activities": "activity",
        "services": "service",
        "receivers": "receiver",
        "providers": "provider",
    }
    names = getters[kind]() or []
    rows = []
    for name in names:
        exported = manifest_attr(apk, intent_kinds[kind], "exported", None, name=name)
        if exported is None:
            try:
                filters = apk.get_intent_filters(intent_kinds[kind], name)
                exported = "implicit_via_intent_filter" if filters else None
            except Exception:
                exported = None
        rows.append({"name": name, "exported": exported})
    return rows


def main() -> int:
    args = parse_args()
    apk_file = Path(args.apk_path)
    if not apk_file.exists():
        raise SystemExit(f"APK not found: {apk_file}")

    apk = load_apk(str(apk_file))
    strings = collect_strings(apk)
    permissions = sorted(set(apk.get_permissions() or []))
    permission_details = [
        {"name": perm, **permission_flags(perm)} for perm in permissions
    ]

    report = {
        "file": str(apk_file),
        "package": {
            "package_name": safe_get(apk.get_package()),
            "app_name": safe_get(apk.get_app_name()),
            "version_name": safe_get(apk.get_androidversion_name()),
            "version_code": safe_get(apk.get_androidversion_code()),
            "min_sdk": safe_get(apk.get_min_sdk_version()),
            "target_sdk": safe_get(apk.get_target_sdk_version()),
            "main_activity": safe_get(apk.get_main_activity()),
            "debuggable": manifest_attr(apk, "application", "debuggable", False),
            "allows_backup": manifest_attr(apk, "application", "allowBackup"),
            "network_security_config": manifest_attr(apk, "application", "networkSecurityConfig"),
            "uses_cleartext_traffic": manifest_attr(apk, "application", "usesCleartextTraffic"),
            "test_only": manifest_attr(apk, "application", "testOnly"),
        },
        "permissions": permission_details,
        "components": {
            "activities": component_rows(apk, "activities"),
            "services": component_rows(apk, "services"),
            "receivers": component_rows(apk, "receivers"),
            "providers": component_rows(apk, "providers"),
        },
        "string_signals": scan_string_patterns(strings),
        "network_indicators": extract_domains(strings),
        "asset_signals": scan_text_assets(apk_file),
        "file_count": len(apk.get_files() or []),
    }

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
