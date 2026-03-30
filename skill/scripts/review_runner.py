#!/usr/bin/env python3
"""End-to-end APK review runner.

This script orchestrates:
- static analysis
- optional runtime prep / runtime collection
- Chinese markdown report generation

It is intentionally semi-automatic:
- good at collecting evidence and generating reports
- still expects human help for login / captcha / complex WebView flows
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parent
APK_REVIEW = SCRIPTS_DIR / "apk_review.py"
RUNTIME_SMOKE = SCRIPTS_DIR / "runtime_smoke.py"

DEFAULT_DYNAMIC_MUST_TEST = [
    "首启隐私弹窗",
    "应用内常驻隐私政策入口",
    "应用内常驻用户协议入口",
    "一级页面与主要导航",
    "测试数据/占位数据排查",
    "账号注销/删除路径",
    "账号资料/设置页",
    "投诉建议/上传图片等权限触发页",
    "视频/直播/积分等核心媒体页",
]


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def now_tag() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def infer_app_type(static_report: dict[str, Any]) -> str:
    package = (static_report.get("package") or {}).get("package_name") or ""
    app_name = (static_report.get("package") or {}).get("app_name") or ""
    blob = " ".join(
        [
            package.lower(),
            str(app_name).lower(),
            " ".join((static_report.get("asset_signals") or {}).get("video_keys_found") or []).lower(),
        ]
    )
    string_blob = json.dumps(static_report.get("string_signals") or {}, ensure_ascii=False).lower()
    full = blob + " " + string_blob

    if any(k in full for k in ["cart", "order", "coupon", "goods", "sku", "shopping", "settlement", "商品", "订单", "积分", "福利"]):
        return "电商/消费"
    if any(k in full for k in ["health", "medical", "fitness", "doctor", "健康", "医疗", "运动"]):
        return "医疗健康"
    return "通用工具/待人工判断"


def permission_names(static_report: dict[str, Any]) -> set[str]:
    perms = static_report.get("permissions") or []
    return {item.get("name") for item in perms if item.get("name")}


def has_test_domain(static_report: dict[str, Any]) -> bool:
    asset = static_report.get("asset_signals") or {}
    network = static_report.get("network_indicators") or {}
    return bool(asset.get("test_domains") or network.get("local_or_test"))


def static_findings(static_report: dict[str, Any]) -> dict[str, list[str]]:
    pkg = static_report.get("package") or {}
    findings = {"blocking": [], "warning": [], "info": []}
    perms = permission_names(static_report)

    if "android.permission.REQUEST_INSTALL_PACKAGES" in perms:
        findings["blocking"].append("声明了 `REQUEST_INSTALL_PACKAGES`，属于高敏感装包能力")

    if str(pkg.get("uses_cleartext_traffic")).lower() == "true":
        findings["warning"].append("`usesCleartextTraffic=true`，发布包传输配置偏弱")

    if has_test_domain(static_report):
        findings["warning"].append("资源中仍存在 `.test` / 测试环境域名")

    if not (static_report.get("string_signals") or {}).get("account_deletion"):
        findings["warning"].append("静态资源中未看到明确的账号注销/删除信号")

    if not (static_report.get("string_signals") or {}).get("privacy_policy"):
        findings["warning"].append("静态资源中未看到明确的隐私政策/用户协议信号")

    asset = static_report.get("asset_signals") or {}
    if asset.get("video_keys_found"):
        findings["info"].append(
            "资源中存在视频相关关键字："
            + "、".join(asset.get("video_keys_found")[:5])
        )

    return findings


def status_from_findings(blocking: list[str], warning: list[str]) -> str:
    if blocking:
        return "high risk of rejection"
    if warning:
        return "needs rectification"
    return "likely pass"


def per_platform_static(static_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    findings = static_findings(static_report)
    base_notes = findings["blocking"] + findings["warning"]

    result: dict[str, dict[str, Any]] = {}
    for platform in ["google play", "huawei appgallery", "xiaomi", "yingyongbao", "vivo", "oppo"]:
        notes = list(base_notes)
        if platform == "google play" and not notes:
            notes = ["no extra static risk detected from the apk"]
        elif platform != "google play" and not notes:
            notes = ["no extra static risk beyond the domestic baseline"]
        result[platform] = {
            "status": status_from_findings(findings["blocking"], findings["warning"]),
            "notes": notes,
        }
    return result


def runtime_error_notes(runtime_collect: dict[str, Any] | None) -> list[str]:
    if not runtime_collect:
        return []
    highlights = runtime_collect.get("highlights") or []
    text = "\n".join(highlights)
    notes: list[str] = []
    patterns = [
        (r"UnknownHostException", "运行日志出现 DNS 解析失败"),
        (r"SSLHandshake|CertPath|CERTIFICATE", "运行日志出现 TLS/证书握手失败"),
        (r"timed out|timeout", "运行日志出现超时"),
        (r"\b403\b", "运行日志出现 403 拒绝访问"),
        (r"\b404\b", "运行日志出现 404 资源不存在"),
        (r"\b50\d\b", "运行日志出现 5xx 服务端错误"),
    ]
    for pattern, note in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            notes.append(note)
    return notes


def default_notes_template() -> dict[str, Any]:
    return {
        "tested_and_verified": [],
        "tested_and_failed": [],
        "blocked_by_login": [],
        "not_tested_yet": list(DEFAULT_DYNAMIC_MUST_TEST),
        "page_coverage": {
            "tested_pages": [],
            "blocked_pages": [],
            "not_reached_pages": [],
        },
        "comments": [
            "登录、验证码、短信、人机校验等复杂交互需要人工协助完成。",
            "WebView 页面较多时，建议按一级页面 + 关键二级页面记录覆盖情况。",
        ],
    }


def render_report(task_dir: Path) -> str:
    static_report = read_json(task_dir / "static.json", {})
    runtime_prep = read_json(task_dir / "runtime_prep.json", None)
    runtime_collect = read_json(task_dir / "runtime_collect.json", None)
    notes = read_json(task_dir / "notes.json", default_notes_template())

    pkg = static_report.get("package") or {}
    app_type = infer_app_type(static_report)
    findings = static_findings(static_report)
    per_platform = per_platform_static(static_report)
    runtime_errors = runtime_error_notes(runtime_collect)

    shared_evidence: list[str] = []
    shared_evidence.append(
        f"包信息：`{pkg.get('package_name')}` / `{pkg.get('app_name')}` / "
        f"`versionName={pkg.get('version_name')}` / `versionCode={pkg.get('version_code')}`"
    )
    shared_evidence.append(f"应用类型推断：{app_type}")
    if findings["blocking"]:
        shared_evidence.extend(findings["blocking"])
    if findings["warning"]:
        shared_evidence.extend(findings["warning"])

    static_missing = []
    if "静态资源中未看到明确的账号注销/删除信号" in findings["warning"]:
        static_missing.append("需要人工确认应用内是否存在注销/删除账号功能及完整路径")
    if "静态资源中未看到明确的隐私政策/用户协议信号" in findings["warning"]:
        static_missing.append("需要人工确认应用内是否存在常驻的隐私政策/用户协议入口")
    if has_test_domain(static_report):
        static_missing.append("需要确认所有隐私政策/用户协议/API 链接已切到生产域名")

    runtime_platform_status = "likely pass"
    runtime_platform_notes: list[str] = []
    if runtime_errors:
        runtime_platform_status = "needs rectification"
        runtime_platform_notes.extend(runtime_errors)
    if notes.get("tested_and_failed"):
        runtime_platform_status = "needs rectification"
        runtime_platform_notes.extend([f"已测失败：{item}" for item in notes.get("tested_and_failed")])
    if not runtime_collect and not runtime_prep:
        runtime_platform_status = "manual verification needed"
        runtime_platform_notes.append("尚未执行动态验证")
    elif runtime_collect and not runtime_errors:
        runtime_platform_notes.append("当前已收集到运行态证据，未见明显网络/播放器硬错误")

    verified = notes.get("tested_and_verified") or []
    blocked = notes.get("blocked_by_login") or []
    not_tested = notes.get("not_tested_yet") or []

    runtime_evidence: list[str] = []
    if runtime_prep:
        runtime_evidence.append(
            f"设备信息：`{runtime_prep.get('serial')}`，前台焦点：`{runtime_prep.get('focused')}`"
        )
    if runtime_collect and runtime_collect.get("screenshot"):
        runtime_evidence.append(f"截图：`{runtime_collect.get('screenshot')}`")
    if runtime_collect and runtime_collect.get("urls"):
        runtime_evidence.append(
            "日志中提取到的运行态 URL："
            + "、".join((runtime_collect.get("urls") or [])[:3])
        )
    if runtime_collect and runtime_collect.get("highlights"):
        runtime_evidence.append(
            "关键日志："
            + " | ".join((runtime_collect.get("highlights") or [])[:3])
        )
    if notes.get("page_coverage", {}).get("tested_pages"):
        runtime_evidence.append(
            "已覆盖页面："
            + "、".join(notes.get("page_coverage", {}).get("tested_pages", [])[:12])
        )

    suggestions: list[str] = []
    if "android.permission.REQUEST_INSTALL_PACKAGES" in permission_names(static_report):
        suggestions.append("优先评估是否可以移除 `REQUEST_INSTALL_PACKAGES`；若必须保留，需准备强业务说明和提审材料")
    if str(pkg.get("uses_cleartext_traffic")).lower() == "true":
        suggestions.append("关闭 `usesCleartextTraffic` 或通过更严格的网络安全配置限制例外域名")
    if has_test_domain(static_report):
        suggestions.append("把所有 `.test` / 测试环境链接替换为生产域名，并重新打包验证")
    if "账号注销/删除路径" in not_tested:
        suggestions.append("在动态验证中补测账号注销/删除路径，并保留截图或录屏证据")
    if "应用内常驻隐私政策入口" in not_tested or "应用内常驻用户协议入口" in not_tested:
        suggestions.append("在动态验证中补测常驻隐私政策/用户协议入口，并记录入口路径")
    if runtime_errors:
        suggestions.append("根据运行日志修复网络/播放器错误后，再做一轮动态回归验证")
    if not suggestions:
        suggestions.append("继续补全登录后页面覆盖，确保经典必测项都有运行态证据")

    final_status = "LIKELY TO PASS"
    if findings["blocking"]:
        final_status = "HIGH RISK OF REJECTION"
    elif findings["warning"] or runtime_errors or notes.get("tested_and_failed"):
        final_status = "NEEDS RECTIFICATION"

    lines: list[str] = []
    lines.append("# 中文监测报告")
    lines.append("")
    lines.append("## 任务信息")
    lines.append(f"- APK：`{static_report.get('file')}`")
    lines.append(f"- 生成时间：`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    lines.append("")
    lines.append("## 静态预审（APK）")
    lines.append("")
    lines.append("### 平台结果（静态）")
    for platform in ["google play", "huawei appgallery", "xiaomi", "yingyongbao", "vivo", "oppo"]:
        item = per_platform[platform]
        lines.append(f"#### {platform}: {item['status']}")
        for note in item["notes"]:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("### 共享证据（静态）")
    for item in shared_evidence:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### 待补充项（静态）")
    for item in static_missing or ["无额外静态待补充项"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 动态运行验证")
    lines.append("")
    lines.append("### 平台结果（动态）")
    for platform in ["google play", "huawei appgallery", "xiaomi", "yingyongbao", "vivo", "oppo"]:
        lines.append(f"#### {platform}: {runtime_platform_status}")
        for note in runtime_platform_notes or ["动态验证尚未完整执行或尚无额外失败信号"]:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("### 动态必测清单状态")
    lines.append("#### tested and verified")
    for item in verified or ["暂无已确认通过项"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("#### tested and failed")
    for item in (notes.get("tested_and_failed") or ["暂无已确认失败项"]):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("#### blocked by login / account")
    for item in blocked or ["暂无登录受限项"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("#### not tested yet")
    for item in not_tested or ["暂无未测项"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("### 运行证据")
    for item in runtime_evidence or ["暂无运行证据，请先执行 runtime prep / collect"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 修改建议")
    for item in suggestions:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 最终结论")
    lines.append(final_status)
    lines.append("TOP RISKS: " + "; ".join((findings["blocking"] + findings["warning"] + runtime_errors)[:5] or ["待补充更多运行态证据"]))
    lines.append("")
    return "\n".join(lines)


def ensure_notes(task_dir: Path) -> None:
    notes_path = task_dir / "notes.json"
    if not notes_path.exists():
        write_json(notes_path, default_notes_template())


def cmd_start(args: argparse.Namespace) -> int:
    apk_path = Path(args.apk_path).resolve()
    if not apk_path.exists():
        raise SystemExit(f"apk not found: {apk_path}")

    task_dir = Path(args.task_dir).resolve() if args.task_dir else (ROOT / "runs" / f"{apk_path.stem}-{now_tag()}")
    task_dir.mkdir(parents=True, exist_ok=True)

    static_json = task_dir / "static.json"
    run([sys.executable, str(APK_REVIEW), str(apk_path), "--output", str(static_json)])

    if args.dynamic_prep:
        runtime_prep = task_dir / "runtime_prep.json"
        cmd = [sys.executable, str(RUNTIME_SMOKE), "prep", str(apk_path), "--output", str(runtime_prep)]
        if args.serial:
            cmd += ["--serial", args.serial]
        run(cmd)

    ensure_notes(task_dir)
    write_text(task_dir / "report.md", render_report(task_dir))
    print(json.dumps({"task_dir": str(task_dir), "report": str(task_dir / "report.md")}, ensure_ascii=False, indent=2))
    return 0


def cmd_collect_runtime(args: argparse.Namespace) -> int:
    task_dir = Path(args.task_dir).resolve()
    static_report = read_json(task_dir / "static.json", {})
    package = args.package or (static_report.get("package") or {}).get("package_name")
    if not package:
        raise SystemExit("package name not found; pass --package explicitly")

    screenshot = task_dir / "runtime-screen.png"
    runtime_collect = task_dir / "runtime_collect.json"
    cmd = [
        sys.executable,
        str(RUNTIME_SMOKE),
        "collect",
        "--package",
        package,
        "--screenshot",
        str(screenshot),
        "--output",
        str(runtime_collect),
        "--include-full",
    ]
    if args.serial:
        cmd += ["--serial", args.serial]
    run(cmd)

    ensure_notes(task_dir)
    write_text(task_dir / "report.md", render_report(task_dir))
    print(json.dumps({"task_dir": str(task_dir), "report": str(task_dir / "report.md")}, ensure_ascii=False, indent=2))
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    task_dir = Path(args.task_dir).resolve()
    ensure_notes(task_dir)
    write_text(task_dir / "report.md", render_report(task_dir))
    print(str(task_dir / "report.md"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="APK review task runner")
    sub = p.add_subparsers(dest="cmd", required=True)

    start = sub.add_parser("start", help="create a new review task")
    start.add_argument("apk_path", help="path to apk file")
    start.add_argument("--task-dir", help="output task directory")
    start.add_argument("--dynamic-prep", action="store_true", help="also run runtime prep")
    start.add_argument("--serial", help="adb serial")
    start.set_defaults(func=cmd_start)

    collect = sub.add_parser("collect-runtime", help="collect runtime evidence into an existing task")
    collect.add_argument("task_dir", help="task directory created by start")
    collect.add_argument("--package", help="package name override")
    collect.add_argument("--serial", help="adb serial")
    collect.set_defaults(func=cmd_collect_runtime)

    render = sub.add_parser("render-report", help="re-render report.md from task files")
    render.add_argument("task_dir", help="task directory created by start")
    render.set_defaults(func=cmd_render)
    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

