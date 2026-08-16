"""GitHub 上传前隐私与密钥检查。

只扫描当前项目中 Git 已跟踪或未忽略的候选文件，以及现有 Git 历史补丁。
报告只输出规则名称和文件位置，不输出疑似敏感值原文。
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_FILE_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class Finding:
    """单条隐私检查结果。"""

    severity: str
    rule: str
    location: str
    note: str


HIGH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "embedded-basic-auth",
        re.compile(r"https?://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE),
    ),
)

SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)^\s*[A-Za-z0-9_.-]*(?:secret|password|passwd|api[_-]?key|access[_-]?token|"
    r"refresh[_-]?token|webhook|cookie|private[_-]?key)[A-Za-z0-9_.-]*\s*[:=]\s*(.+?)\s*$"
)
SENSITIVE_NAME = re.compile(
    r"(?i)(?:secret|password|passwd|api[_-]?key|access[_-]?token|"
    r"refresh[_-]?token|webhook|cookie|private[_-]?key)"
)
PLACEHOLDER_VALUE = re.compile(
    r"(?i)^(?:[\"']?[\"']?|none|null|false|0|example|sample|placeholder|"
    r"your[_ -]?(?:key|token|secret|password)|<[^>]+>|\$\{[^}]+\}|xxx+|待填写|你的.+)$"
)
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
MOBILE_PATTERN = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
USER_PATH_PATTERN = re.compile(r"(?i)\b[A-Z]:[\\/]Users[\\/][^\\/\s]+")

SENSITIVE_FILE_NAMES = {
    ".envrc",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "service-account.json",
    "service_account.json",
}
SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
    ".session",
}
TEXT_SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".zip",
    ".gz",
    ".tar",
    ".pdf",
    ".docx",
    ".pptx",
    ".xlsx",
    ".pyc",
}
CONFIG_SUFFIXES = {".env", ".ini", ".cfg", ".conf", ".yaml", ".yml", ".toml"}


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _candidate_files() -> list[Path]:
    payload = _git("ls-files", "-co", "--exclude-standard", "-z").stdout
    paths = []
    for raw_path in payload.split(b"\0"):
        if not raw_path:
            continue
        path = PROJECT_ROOT / raw_path.decode("utf-8", errors="surrogateescape")
        if path.is_file():
            paths.append(path)
    return sorted(set(paths), key=lambda item: item.as_posix().lower())


def _relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _scan_filename(path: Path) -> list[Finding]:
    relative = _relative(path)
    name_lower = path.name.lower()
    findings = []
    if name_lower == ".env" or (name_lower.startswith(".env.") and name_lower != ".env.example"):
        findings.append(Finding("HIGH", "environment-file", relative, "真实环境文件不应上传"))
    if name_lower in SENSITIVE_FILE_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
        findings.append(Finding("HIGH", "sensitive-file", relative, "疑似私钥或凭据文件"))
    if name_lower.startswith("cookies") and path.suffix.lower() == ".json":
        findings.append(Finding("HIGH", "browser-cookie-file", relative, "疑似浏览器 Cookie 文件"))
    if name_lower in {"storage-state.json", "storage_state.json"}:
        findings.append(Finding("HIGH", "browser-session-file", relative, "疑似浏览器会话文件"))
    return findings


def _scan_text(path: Path) -> list[Finding]:
    if path.suffix.lower() in TEXT_SKIP_SUFFIXES or path.stat().st_size > MAX_TEXT_FILE_BYTES:
        return []
    raw = path.read_bytes()
    if b"\0" in raw:
        return []
    text = raw.decode("utf-8", errors="replace")
    relative = _relative(path)
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        location = f"{relative}:{line_number}"
        for rule, pattern in HIGH_PATTERNS:
            if pattern.search(line):
                findings.append(Finding("HIGH", rule, location, "发现高风险密钥格式"))

        if path.suffix.lower() in CONFIG_SUFFIXES or path.name.lower().startswith(".env"):
            assignment = SENSITIVE_ASSIGNMENT.match(line)
            if assignment:
                value = assignment.group(1).strip().strip('"\'')
                if value and not PLACEHOLDER_VALUE.match(value):
                    findings.append(
                        Finding("HIGH", "non-empty-secret-assignment", location, "敏感配置项存在非占位值")
                    )

        if EMAIL_PATTERN.search(line):
            findings.append(Finding("REVIEW", "email-address", location, "请确认邮箱是否可公开"))
        if MOBILE_PATTERN.search(line):
            findings.append(Finding("REVIEW", "mobile-number", location, "请确认手机号是否可公开"))
        if USER_PATH_PATTERN.search(line):
            findings.append(Finding("REVIEW", "windows-user-path", location, "可能暴露 Windows 用户名"))
    return findings


def _assignment_names(node: ast.AST) -> list[str]:
    """提取赋值目标名称，忽略普通属性读取和变量传递。"""
    if isinstance(node, ast.Name):
        return [node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        names = []
        for element in node.elts:
            names.extend(_assignment_names(element))
        return names
    return []


def _scan_python_literals(path: Path) -> list[Finding]:
    """只拦截 Python 中直接硬编码到敏感变量的非占位字符串。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    findings = []
    for node in ast.walk(tree):
        targets: list[ast.AST] = []
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
            value_node = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value_node = node.value
        if value_node is None or not isinstance(value_node, ast.Constant):
            continue
        if not isinstance(value_node.value, str):
            continue
        value = value_node.value.strip()
        if not value or PLACEHOLDER_VALUE.match(value):
            continue
        names = [name for target in targets for name in _assignment_names(target)]
        if any(SENSITIVE_NAME.search(name) for name in names):
            findings.append(
                Finding(
                    "HIGH",
                    "python-hardcoded-secret",
                    f"{_relative(path)}:{node.lineno}",
                    "敏感变量被直接赋予非占位字符串",
                )
            )
    return findings


def _scan_history() -> list[Finding]:
    history = _git("log", "--all", "--format=commit:%H", "-p", "--no-ext-diff", check=False)
    text = history.stdout.decode("utf-8", errors="replace")
    findings = []
    for rule, pattern in HIGH_PATTERNS:
        if pattern.search(text):
            findings.append(
                Finding("HIGH", f"history-{rule}", "Git history", "历史补丁中发现高风险密钥格式")
            )
    return findings


def _scan_remote_urls() -> list[Finding]:
    """检查 Git 远程地址是否内嵌凭据，不输出完整 URL。"""
    remote_names = _git("remote", check=False).stdout.decode("utf-8", errors="replace").splitlines()
    findings = []
    for remote_name in remote_names:
        result = _git("remote", "get-url", "--all", remote_name, check=False)
        for raw_url in result.stdout.decode("utf-8", errors="replace").splitlines():
            url = raw_url.strip()
            if not url:
                continue
            if "://" in url:
                parsed = urlparse(url)
                if parsed.username or parsed.password:
                    findings.append(
                        Finding(
                            "HIGH",
                            "remote-embedded-credentials",
                            f"Git remote:{remote_name}",
                            "远程 URL 内嵌用户名或密码",
                        )
                    )
                sensitive_query_names = {
                    key.lower()
                    for key in parse_qs(parsed.query)
                    if SENSITIVE_NAME.search(key)
                }
                if sensitive_query_names:
                    findings.append(
                        Finding(
                            "HIGH",
                            "remote-query-credential",
                            f"Git remote:{remote_name}",
                            "远程 URL 查询参数疑似包含凭据",
                        )
                    )
            elif "@" in url and ":" in url:
                ssh_user = url.split("@", 1)[0]
                if ssh_user and ssh_user != "git":
                    findings.append(
                        Finding(
                            "REVIEW",
                            "remote-ssh-username",
                            f"Git remote:{remote_name}",
                            "请确认 SSH 用户名是否可公开",
                        )
                    )
    return findings


def _deduplicate(findings: list[Finding]) -> list[Finding]:
    return sorted(
        set(findings),
        key=lambda item: (item.severity != "HIGH", item.rule, item.location),
    )


def main() -> int:
    """执行隐私审计并以非零退出码阻止高风险上传。"""
    parser = argparse.ArgumentParser(description="lobster-farm GitHub 上传前隐私检查")
    parser.add_argument("--skip-history", action="store_true", help="跳过 Git 历史检查")
    args = parser.parse_args()

    files = _candidate_files()
    findings: list[Finding] = []
    for path in files:
        findings.extend(_scan_filename(path))
        findings.extend(_scan_text(path))
        if path.suffix.lower() == ".py":
            findings.extend(_scan_python_literals(path))
    if not args.skip_history:
        findings.extend(_scan_history())
    findings.extend(_scan_remote_urls())
    findings = _deduplicate(findings)

    high = [item for item in findings if item.severity == "HIGH"]
    review = [item for item in findings if item.severity == "REVIEW"]
    print("lobster-farm GitHub 上传前隐私检查")
    print(f"候选文件：{len(files)}")
    print(f"高风险：{len(high)}")
    print(f"需人工确认：{len(review)}")
    for item in findings:
        print(f"[{item.severity}] {item.rule} | {item.location} | {item.note}")

    if high:
        print("结论：未通过。请先移除高风险内容，再准备上传。")
        return 2
    if review:
        print("结论：未发现密钥；存在需人工确认的公开信息位置。")
        return 0
    print("结论：通过。未发现已知密钥格式、敏感文件名或常见个人信息。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
