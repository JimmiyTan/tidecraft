"""生成 Jerry 谭梓健的 TideCraft 完整项目作品集 PDF。

输入：portfolio/assets 下的概念配图与公开展示用脱敏原型图。
输出：output/pdf/Jerry_Tan_TideCraft_Portfolio.pdf。
失败处理：字体或任一必需图片缺失时立即停止，避免输出缺图或乱码版本。
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "portfolio" / "assets"
OUTPUT = ROOT / "output" / "pdf" / "Jerry_Tan_TideCraft_Portfolio.pdf"

PAGE_W, PAGE_H = A4
MARGIN = 38
CONTENT_W = PAGE_W - MARGIN * 2
TOTAL_PAGES = 9

NAVY = HexColor("#0B1D38")
TEAL = HexColor("#168A78")
TEAL_DARK = HexColor("#0F5D52")
TEAL_PALE = HexColor("#DDF2EB")
GREEN = HexColor("#4FA67A")
CORAL = HexColor("#F47C62")
CORAL_PALE = HexColor("#FCE5DE")
WARM = HexColor("#F7F4EC")
WHITE = HexColor("#FFFFFF")
TEXT = HexColor("#304456")
MUTED = HexColor("#6D7C88")
LINE = HexColor("#D9DFDC")

FONT_REGULAR = "PortfolioRegular"
FONT_BOLD = "PortfolioBold"


def register_fonts() -> None:
    """注册 Windows 中文字体。"""
    regular = Path(r"C:\Windows\Fonts\msyh.ttc")
    bold = Path(r"C:\Windows\Fonts\msyhbd.ttc")
    if not regular.exists() or not bold.exists():
        raise FileNotFoundError("未找到微软雅黑字体，无法安全生成中文 PDF。")
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(regular)))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))


def require_assets() -> dict[str, Path]:
    """检查所有视觉资源，避免生成缺图版本。"""
    assets = {
        "cover": ASSETS / "cover-concept.jpg",
        "challenge": ASSETS / "challenge-concept.jpg",
        "delivery": ASSETS / "delivery-concept.jpg",
        "workflow": ASSETS / "prototype-workflow-sanitized.png",
        "review": ASSETS / "prototype-review-sanitized.png",
        "export": ASSETS / "prototype-delivery-sanitized.png",
    }
    missing = [str(path) for path in assets.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("缺少作品集图片：" + ", ".join(missing))
    return assets


def set_font(c: canvas.Canvas, size: float, bold: bool = False) -> None:
    c.setFont(FONT_BOLD if bold else FONT_REGULAR, size)


def text_width(text: str, size: float, bold: bool = False) -> float:
    return pdfmetrics.stringWidth(text, FONT_BOLD if bold else FONT_REGULAR, size)


def wrap_text(text: str, max_width: float, size: float, bold: bool = False) -> list[str]:
    """按实际字宽换行，兼容中英文混排。"""
    lines: list[str] = []
    current = ""
    for char in text:
        if char == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = current + char
        if current and text_width(candidate, size, bold) > max_width:
            if char in "，。；：、！？）】》":
                lines.append(candidate)
                current = ""
            else:
                lines.append(current)
                current = char
        else:
            current = candidate
    if current or not lines:
        lines.append(current)
    return lines


def paragraph(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    size: float = 8.2,
    leading: float = 12.4,
    color=TEXT,
    bold: bool = False,
) -> float:
    c.setFillColor(color)
    set_font(c, size, bold)
    for line in wrap_text(text, width, size, bold):
        c.drawString(x, y, line)
        y -= leading
    return y


def bullets(
    c: canvas.Canvas,
    items: Iterable[str],
    x: float,
    y: float,
    width: float,
    size: float = 7.7,
    leading: float = 11.5,
    bullet_color=TEAL,
) -> float:
    for item in items:
        lines = wrap_text(item, width - 19, size)
        c.setFillColor(bullet_color)
        c.circle(x + 4, y + 2.5, 2.1, fill=1, stroke=0)
        c.setFillColor(TEXT)
        set_font(c, size)
        for line in lines:
            c.drawString(x + 15, y, line)
            y -= leading
        y -= 4
    return y


def rounded(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill,
    stroke=LINE,
    radius: float = 12,
    stroke_width: float = 0.7,
) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(stroke_width)
    c.roundRect(x, y, width, height, radius, fill=1, stroke=1)


def pill(c: canvas.Canvas, text: str, x: float, y: float, fill, color, size: float = 7.6) -> float:
    width = text_width(text, size, True) + 18
    c.setFillColor(fill)
    c.roundRect(x, y, width, 21, 10.5, fill=1, stroke=0)
    c.setFillColor(color)
    set_font(c, size, True)
    c.drawString(x + 9, y + 6.5, text)
    return width


def draw_image_cover(c: canvas.Canvas, path: Path, x: float, y: float, width: float, height: float) -> None:
    """等比裁切图片填满容器。"""
    with Image.open(path) as image:
        iw, ih = image.size
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (width - dw) / 2, y + (height - dh) / 2
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, width, height)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(ImageReader(str(path)), dx, dy, dw, dh, mask="auto")
    c.restoreState()


def draw_image_contain(c: canvas.Canvas, path: Path, x: float, y: float, width: float, height: float) -> None:
    """完整放入界面截图，不裁切标题、状态或脱敏说明。"""
    with Image.open(path) as image:
        iw, ih = image.size
    scale = min(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = x + (width - dw) / 2, y + (height - dh) / 2
    c.drawImage(ImageReader(str(path)), dx, dy, dw, dh, mask="auto")


def header(c: canvas.Canvas, page: int, kicker: str, title: str, subtitle: str = "") -> float:
    """绘制统一浅色页面标题，并返回正文起始坐标。"""
    c.setFillColor(WARM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(MARGIN, PAGE_H - 54, 24, 3, fill=1, stroke=0)
    c.setFillColor(MUTED)
    set_font(c, 7.8, True)
    c.drawString(MARGIN + 32, PAGE_H - 57, kicker.upper())
    c.setFillColor(NAVY)
    set_font(c, 8, True)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 57, f"{page:02d} / {TOTAL_PAGES:02d}")
    title_size = 22.5
    title_y = PAGE_H - 100
    for line in wrap_text(title, CONTENT_W, title_size, True):
        c.drawString(MARGIN, title_y, line)
        title_y -= 29
    y = title_y + 5
    if subtitle:
        y = paragraph(c, subtitle, MARGIN, y, CONTENT_W, 9.1, 13.8, TEXT) - 5
    return y


def footer(c: canvas.Canvas, source: str, dark: bool = False) -> None:
    color = Color(1, 1, 1, 0.58) if dark else MUTED
    line_color = Color(1, 1, 1, 0.16) if dark else LINE
    c.setStrokeColor(line_color)
    c.setLineWidth(0.5)
    c.line(MARGIN, 28, PAGE_W - MARGIN, 28)
    c.setFillColor(color)
    source_text = f"证据定位：{source}"
    source_size = 6.3
    while text_width(source_text, source_size) > 335 and source_size > 4.8:
        source_size -= 0.2
    set_font(c, source_size)
    c.drawString(MARGIN, 15, source_text)
    set_font(c, 6.2)
    c.drawRightString(PAGE_W - MARGIN, 15, "Jerry 谭梓健 · 独立全栈开发项目")


def draw_cover(c: canvas.Canvas, assets: dict[str, Path]) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    image_x = 322
    draw_image_cover(c, assets["cover"], image_x, 0, PAGE_W - image_x, PAGE_H)
    c.setFillColor(Color(0.043, 0.114, 0.22, 0.18))
    c.rect(image_x, 0, PAGE_W - image_x, PAGE_H, fill=1, stroke=0)

    c.setFillColor(TEAL)
    c.rect(MARGIN, PAGE_H - 70, 32, 4, fill=1, stroke=0)
    c.setFillColor(TEAL_PALE)
    set_font(c, 8, True)
    c.drawString(MARGIN, PAGE_H - 91, "COMPLETE PROJECT CASE · PHASE 07 CLOSED")

    c.setFillColor(WHITE)
    set_font(c, 29, True)
    c.drawString(MARGIN, PAGE_H - 156, "TideCraft")
    set_font(c, 19, True)
    c.drawString(MARGIN, PAGE_H - 188, "潮生内容工场")
    c.setFillColor(TEAL_PALE)
    set_font(c, 11.4, True)
    c.drawString(MARGIN, PAGE_H - 224, "完整交付的本地短视频内容生产与人工审核系统")

    paragraph(
        c,
        "从主题输入、候选内容、审核材料和视频结果，到人工审核、双平台交付包、人工发布回执与归档，形成可运行、可追踪、可审计的完整业务闭环。",
        MARGIN,
        PAGE_H - 266,
        250,
        9.3,
        15,
        Color(1, 1, 1, 0.82),
    )

    y = PAGE_H - 355
    x = MARGIN
    for text in ["独立全栈开发", "Python", "状态机", "适配器架构", "安全交付"]:
        width = pill(c, text, x, y, Color(1, 1, 1, 0.10), TEAL_PALE, 7.1)
        x += width + 7
        if x > 295:
            x = MARGIN
            y -= 29

    rounded(c, MARGIN, 202, 252, 106, Color(1, 1, 1, 0.07), Color(1, 1, 1, 0.15), 14)
    c.setFillColor(CORAL)
    set_font(c, 7.3, True)
    c.drawString(MARGIN + 16, 284, "PROJECT OUTCOME")
    c.setFillColor(WHITE)
    set_font(c, 12.5, True)
    c.drawString(MARGIN + 16, 257, "完整闭环已实现并通过 Windows 结项验证")
    paragraph(
        c,
        "项目完成 Phase 07 收尾并进入冻结维护；完整交付边界是人工审核与人工发布回执，不包含平台自动发布。",
        MARGIN + 16,
        233,
        220,
        7.5,
        11.3,
        Color(1, 1, 1, 0.72),
    )

    c.setFillColor(WHITE)
    set_font(c, 18, True)
    c.drawString(MARGIN, 126, "Jerry 谭梓健")
    c.setFillColor(TEAL_PALE)
    set_font(c, 9, True)
    c.drawString(MARGIN, 104, "独立全栈开发者 · 从需求定义到验收落地")
    c.setFillColor(Color(1, 1, 1, 0.75))
    set_font(c, 8.2)
    c.drawString(MARGIN, 78, "Jerrytan1221@gmail.com")
    c.drawString(MARGIN, 60, "适用于猎聘、BOSS 直聘等招聘平台")
    footer(c, "README.md · PROJECT_CLOSURE.md · CURRENT_STATUS.md", dark=True)
    c.showPage()


def draw_overview(c: canvas.Canvas, assets: dict[str, Path]) -> None:
    y = header(
        c,
        2,
        "PROJECT OVERVIEW",
        "这是一套完成既定范围并正式结项的系统。",
        "项目从内容生产问题出发，将生成、审核、交付和归档组织为本地可运行的人工审核内容中台。",
    )

    rounded(c, MARGIN, y - 112, CONTENT_W, 98, NAVY, NAVY, 14)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7.4, True)
    c.drawString(MARGIN + 16, y - 37, "项目结论")
    c.setFillColor(WHITE)
    set_font(c, 13, True)
    c.drawString(MARGIN + 16, y - 65, "Phase 07 已完成功能收尾、验证、文档和公开发布准备。")
    paragraph(
        c,
        "完成标准：端到端业务闭环可运行，关键状态可追踪，外部能力可替换，人工决策边界明确，验证与回滚资料齐备。",
        MARGIN + 16,
        y - 86,
        CONTENT_W - 32,
        7.4,
        10.8,
        Color(1, 1, 1, 0.75),
    )

    stats = [("5", "候选选题与脚本"), ("2", "平台交付准备包"), ("100%", "人工审核决策"), ("0", "自动正式发布")]
    stat_y = y - 202
    stat_w = (CONTENT_W - 24) / 4
    for index, (value, label) in enumerate(stats):
        x = MARGIN + index * (stat_w + 8)
        rounded(c, x, stat_y, stat_w, 76, WHITE, LINE, 12)
        c.setFillColor(CORAL if index == 3 else TEAL)
        set_font(c, 18, True)
        c.drawString(x + 13, stat_y + 41, value)
        c.setFillColor(TEXT)
        set_font(c, 7.2, True)
        c.drawString(x + 13, stat_y + 18, label)

    bottom_y = 92
    bottom_h = stat_y - bottom_y - 16
    left_w = 286
    rounded(c, MARGIN, bottom_y, left_w, bottom_h, WHITE, LINE, 14)
    c.setFillColor(NAVY)
    set_font(c, 11, True)
    c.drawString(MARGIN + 16, bottom_y + bottom_h - 28, "解决的真实问题")
    bullets(
        c,
        [
            "内容生成、审核、交付分散，过程状态难以统一追踪。",
            "外部消息和视频服务存在切换、超时与失败风险。",
            "自动发布涉及账号和业务责任，需要保留人工决策。",
            "本地项目必须可重建、可回滚、可审计并便于演示。",
        ],
        MARGIN + 14,
        bottom_y + bottom_h - 56,
        left_w - 28,
        7.6,
        11.7,
    )
    c.setFillColor(CORAL_PALE)
    c.roundRect(MARGIN + 14, bottom_y + 14, left_w - 28, 47, 10, fill=1, stroke=0)
    c.setFillColor(NAVY)
    set_font(c, 7.2, True)
    c.drawString(MARGIN + 27, bottom_y + 43, "完成项目的定义")
    paragraph(c, "在明确边界内形成可运行、可验证、可交付的闭环。", MARGIN + 27, bottom_y + 26, left_w - 54, 7.1, 10, TEXT)

    image_x = MARGIN + left_w + 14
    image_w = CONTENT_W - left_w - 14
    rounded(c, image_x, bottom_y, image_w, bottom_h, WHITE, LINE, 14)
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(image_x + 6, bottom_y + 6, image_w - 12, bottom_h - 12, 10)
    c.clipPath(clip, stroke=0, fill=0)
    draw_image_cover(c, assets["challenge"], image_x + 6, bottom_y + 6, image_w - 12, bottom_h - 12)
    c.restoreState()
    c.setFillColor(NAVY)
    c.roundRect(image_x + 12, bottom_y + 12, 94, 19, 9.5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    set_font(c, 6.6, True)
    c.drawString(image_x + 22, bottom_y + 18.5, "概念配图 · 业务闭环")
    footer(c, "README.md · CURRENT_STATUS.md · PROJECT_CLOSURE.md")
    c.showPage()


def draw_complete_flow(c: canvas.Canvas) -> None:
    y = header(
        c,
        3,
        "END-TO-END DELIVERY",
        "完整链路由 11 个业务节点组成。",
        "系统负责组织内容、状态和交付物；人工负责审核决定与正式发布，边界清晰且全过程留痕。",
    )
    steps = [
        ("01", "输入主题", "行业、产品或营销方向"), ("02", "候选选题", "生成 5 条内容方向"),
        ("03", "脚本生成", "开场、主体与行动引导"), ("04", "审核材料", "整理飞书消息与摘要"),
        ("05", "视频结果", "mock 或 API provider"), ("06", "待审核包", "导出人工审核材料"),
        ("07", "人工审核", "通过、拒绝或退回"), ("08", "双平台包", "抖音与视频号准备包"),
        ("09", "人工发布", "由运营人员登录平台"), ("10", "发布回执", "记录状态、链接和备注"),
        ("11", "任务归档", "形成完整审计记录"),
    ]
    columns = 4
    card_w = (CONTENT_W - 27) / columns
    card_h = 84
    gap_x = 9
    gap_y = 13
    top = y - 5
    for index, (number, title, note) in enumerate(steps):
        row, col = divmod(index, columns)
        x = MARGIN + col * (card_w + gap_x)
        card_y = top - (row + 1) * card_h - row * gap_y
        fill = TEAL_PALE if index in {6, 7, 9, 10} else WHITE
        rounded(c, x, card_y, card_w, card_h, fill, LINE, 11)
        c.setFillColor(CORAL if index in {6, 9} else TEAL)
        set_font(c, 7.1, True)
        c.drawString(x + 11, card_y + 61, number)
        c.setFillColor(NAVY)
        set_font(c, 9.2, True)
        c.drawString(x + 11, card_y + 39, title)
        paragraph(c, note, x + 11, card_y + 20, card_w - 22, 6.5, 9, MUTED)
        if col < columns - 1 and index < len(steps) - 1:
            c.setStrokeColor(TEAL)
            c.setLineWidth(1.1)
            c.line(x + card_w + 2, card_y + card_h / 2, x + card_w + gap_x - 2, card_y + card_h / 2)

    state_y = 187
    rounded(c, MARGIN, state_y, CONTENT_W, 82, NAVY, NAVY, 13)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7.2, True)
    c.drawString(MARGIN + 15, state_y + 60, "核心状态链")
    c.setFillColor(WHITE)
    set_font(c, 9, True)
    c.drawString(MARGIN + 15, state_y + 34, "completed  →  approved  →  ready_to_publish  →  manually_published  →  archived")
    c.setFillColor(Color(1, 1, 1, 0.62))
    set_font(c, 6.8)
    c.drawString(MARGIN + 15, state_y + 16, "拒绝非法流转；审核与发布结果均按 task_id 落盘。")

    deliverables = [
        ("内容资产", "候选选题、脚本、改写结果、视频结果"),
        ("审核资产", "飞书消息、审核决定、备注和状态"),
        ("交付资产", "双平台文案、标签、检查清单和发布回执"),
    ]
    box_w = (CONTENT_W - 18) / 3
    for index, (title, note) in enumerate(deliverables):
        x = MARGIN + index * (box_w + 9)
        rounded(c, x, 90, box_w, 74, WHITE, LINE, 11)
        c.setFillColor(NAVY)
        set_font(c, 8.5, True)
        c.drawString(x + 12, 140, title)
        paragraph(c, note, x + 12, 119, box_w - 24, 6.8, 10, TEXT)
    footer(c, "docs/architecture.md · docs/demo.md · docs/review-workflow.md · docs/publishing-workflow.md")
    c.showPage()


def draw_architecture(c: canvas.Canvas) -> None:
    y = header(
        c,
        4,
        "SYSTEM ARCHITECTURE",
        "系统按职责拆分，并为外部能力保留可替换接口。",
        "核心工作流不依赖单一平台：消息渠道使用 Adapter，视频能力使用 Provider，发布阶段只管理准备包与人工回执。",
    )
    layers = [
        ("入口层", "OpenClaw 配置 · 浏览器客户演示 · CLI 与 Windows 快捷入口", NAVY, "接收主题与操作指令，提供演示和日常使用入口。"),
        ("编排层", "Orchestrator · 状态机 · 重试 · 任务索引 · 队列与归档", TEAL_DARK, "统一推进任务，拒绝非法状态流转并记录失败原因。"),
        ("内容层", "Trend Radar · Viral Analyzer · Rewrite Engine · Content Pipeline", TEAL, "负责选题、结构分析、原创改写和双平台内容组织。"),
        ("集成层", "Feishu Adapter · Video Provider · Publishing Adapter", GREEN, "屏蔽外部服务差异，支持 dry-run/mock 与真实配置路径。"),
        ("数据与审计层", "JSON/TXT 文件状态 · logs · cache · exports · review receipts", CORAL, "每个关键动作均生成可检查文件，便于审计、恢复和回滚。"),
    ]
    layer_y = y - 76
    for index, (name, detail, color, note) in enumerate(layers):
        box_y = layer_y - index * 70
        rounded(c, MARGIN, box_y, CONTENT_W, 55, WHITE, LINE, 12)
        c.setFillColor(color)
        c.roundRect(MARGIN, box_y, 90, 55, 12, fill=1, stroke=0)
        c.rect(MARGIN + 45, box_y, 45, 55, fill=1, stroke=0)
        c.setFillColor(WHITE)
        set_font(c, 9, True)
        c.drawString(MARGIN + 17, box_y + 22, name)
        c.setFillColor(NAVY)
        set_font(c, 8.2, True)
        c.drawString(MARGIN + 108, box_y + 31, detail)
        c.setFillColor(MUTED)
        set_font(c, 6.7)
        c.drawString(MARGIN + 108, box_y + 15, note)
        if index < len(layers) - 1:
            c.setStrokeColor(LINE)
            c.setLineWidth(1)
            c.line(PAGE_W / 2, box_y - 3, PAGE_W / 2, box_y - 12)

    decision_y = 92
    decision_h = layer_y - 4 * 70 - decision_y - 18
    cards = [
        ("可替换", "消息、视频和发布平台不写死在核心流程中。"),
        ("可追踪", "task_id 串联任务目录、状态、审核、发布与归档。"),
        ("可恢复", "失败分类、超时与重试策略避免静默丢失任务。"),
    ]
    card_w = (CONTENT_W - 18) / 3
    for index, (title, detail) in enumerate(cards):
        x = MARGIN + index * (card_w + 9)
        dark = index == 1
        rounded(c, x, decision_y, card_w, decision_h, NAVY if dark else WHITE, NAVY if dark else LINE, 12)
        c.setFillColor(CORAL if dark else TEAL)
        set_font(c, 7.1, True)
        c.drawString(x + 13, decision_y + decision_h - 22, f"0{index + 1}")
        c.setFillColor(WHITE if dark else NAVY)
        set_font(c, 10, True)
        c.drawString(x + 13, decision_y + decision_h - 44, title)
        paragraph(c, detail, x + 13, decision_y + decision_h - 64, card_w - 26, 6.8, 10, Color(1, 1, 1, 0.72) if dark else TEXT)
    footer(c, "docs/architecture.md · src/lobster_farm/ · services/")
    c.showPage()


def draw_engineering(c: canvas.Canvas) -> None:
    y = header(
        c,
        5,
        "CORE ENGINEERING",
        "把完整业务过程做成可靠系统。",
        "实现围绕状态一致性、外部服务可替换、失败可诊断和人工责任边界展开。",
    )
    decisions = [
        ("01", "显式状态机", "定义审核、发布与归档状态；非法流转直接拒绝，避免任务跳步或误归档。", "state_machine.py · review_state.py"),
        ("02", "文件化审计", "使用 task_id 组织 JSON/TXT 输出，状态、审核、发布和摘要可独立检查。", "state_store.py · exporter.py"),
        ("03", "Adapter / Provider", "飞书、视频和发布接口与核心流程解耦，默认 dry-run/mock，真实配置可校验。", "adapters/ · providers/"),
        ("04", "人工最终决策", "系统只生成交付包与回执入口，不接管平台账号，不执行自动正式发布。", "publishing/service.py"),
    ]
    card_w = (CONTENT_W - 12) / 2
    card_h = 138
    top = y - 10
    for index, (number, title, detail, evidence) in enumerate(decisions):
        row, col = divmod(index, 2)
        x = MARGIN + col * (card_w + 12)
        card_y = top - (row + 1) * card_h - row * 12
        dark = index == 3
        rounded(c, x, card_y, card_w, card_h, NAVY if dark else WHITE, NAVY if dark else LINE, 13)
        c.setFillColor(CORAL if index in {0, 3} else TEAL)
        set_font(c, 7.2, True)
        c.drawString(x + 14, card_y + card_h - 25, number)
        c.setFillColor(WHITE if dark else NAVY)
        set_font(c, 11, True)
        c.drawString(x + 14, card_y + card_h - 49, title)
        paragraph(c, detail, x + 14, card_y + card_h - 72, card_w - 28, 7.2, 11, Color(1, 1, 1, 0.74) if dark else TEXT)
        c.setFillColor(TEAL_PALE if dark else MUTED)
        set_font(c, 6.3)
        c.drawString(x + 14, card_y + 15, evidence)

    table_y = 92
    table_h = top - 2 * card_h - 12 - table_y - 18
    rounded(c, MARGIN, table_y, CONTENT_W, table_h, WHITE, LINE, 13)
    c.setFillColor(NAVY)
    set_font(c, 10.2, True)
    c.drawString(MARGIN + 15, table_y + table_h - 25, "模块输入、输出与失败处理")
    rows = [
        ("Orchestrator", "主题与配置", "任务目录、状态、审核包", "错误分类并进入失败状态"),
        ("Feishu Bridge", "审核消息", "dry-run 或发送结果", "配置、权限、网络与超时"),
        ("Video Gateway", "任务与视频配置", "mock 或 API 结果", "轮询、超时、重试与分类"),
        ("Review / Publishing", "task_id 与人工决定", "平台包、回执、归档", "拒绝未知任务和非法状态"),
    ]
    widths = [100, 100, 145, CONTENT_W - 30 - 345]
    x0 = MARGIN + 15
    row_top = table_y + table_h - 48
    headers = ["模块", "输入", "输出", "失败处理"]
    x = x0
    c.setFillColor(TEAL_PALE)
    c.rect(x0, row_top - 19, CONTENT_W - 30, 22, fill=1, stroke=0)
    for index, value in enumerate(headers):
        c.setFillColor(NAVY)
        set_font(c, 6.8, True)
        c.drawString(x + 6, row_top - 12, value)
        x += widths[index]
    current_y = row_top - 39
    for row in rows:
        x = x0
        c.setStrokeColor(LINE)
        c.line(x0, current_y - 6, x0 + CONTENT_W - 30, current_y - 6)
        for index, value in enumerate(row):
            c.setFillColor(TEXT)
            set_font(c, 6.2, index == 0)
            c.drawString(x + 6, current_y + 5, value)
            x += widths[index]
        current_y -= 25
    footer(c, "src/lobster_farm/orchestrator/ · feishu_bridge/ · video_gateway/ · publishing/")
    c.showPage()


def draw_product_workflow(c: canvas.Canvas, assets: dict[str, Path]) -> None:
    y = header(
        c,
        6,
        "COMPLETE PRODUCT SYSTEM",
        "完整系统具备浏览器演示与命令行工作流。",
        "下面是公开展示用脱敏界面，功能结构对应已实现链路；所有品牌、编号和时间均为演示占位数据。",
    )
    image_y = y - 310
    rounded(c, MARGIN, image_y, CONTENT_W, 290, WHITE, LINE, 14)
    draw_image_contain(c, assets["workflow"], MARGIN + 6, image_y + 6, CONTENT_W - 12, 278)
    c.setFillColor(NAVY)
    c.roundRect(MARGIN + 12, image_y + 12, 116, 20, 10, fill=1, stroke=0)
    c.setFillColor(WHITE)
    set_font(c, 6.8, True)
    c.drawString(MARGIN + 22, image_y + 19, "脱敏界面 · 完整结果页")

    cards = [
        ("用户如何使用", ["Windows 双击启动客户演示，浏览器访问本机服务。", "输入行业或主题，生成候选内容并展示闭环结果。", "正式流程通过 CLI 写回审核决定与人工发布结果。"]),
        ("系统最终交付", ["内容包：选题、脚本、视频结果与摘要。", "审核包：飞书消息、审核决定、备注和状态。", "发布包：双平台文案、标签、检查清单和回执。"]),
    ]
    card_w = (CONTENT_W - 12) / 2
    card_y = 140
    card_h = image_y - card_y - 15
    for index, (title, items) in enumerate(cards):
        x = MARGIN + index * (card_w + 12)
        rounded(c, x, card_y, card_w, card_h, WHITE, LINE, 12)
        c.setFillColor(NAVY)
        set_font(c, 10, True)
        c.drawString(x + 14, card_y + card_h - 27, title)
        bullets(c, items, x + 12, card_y + card_h - 53, card_w - 24, 7.2, 10.8)

    rounded(c, MARGIN, 78, CONTENT_W, 47, NAVY, NAVY, 11)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7.2, True)
    c.drawString(MARGIN + 15, 106, "完整项目边界")
    c.setFillColor(WHITE)
    set_font(c, 8.4, True)
    c.drawString(MARGIN + 15, 88, "完整内容闭环已交付 · 正式发布由人工完成 · 系统记录回执并归档")
    footer(c, "apps/customer-demo/ · docs/customer-demo.md · docs/demo.md")
    c.showPage()


def draw_product_review(c: canvas.Canvas, assets: dict[str, Path]) -> None:
    y = header(
        c,
        7,
        "HUMAN REVIEW & DELIVERY",
        "人工审核是系统中的正式业务节点。",
        "审核决定驱动状态流转；通过后生成双平台准备包，发布完成后写回结果并进入归档。",
    )
    frame_h = 245
    first_y = y - frame_h - 8
    second_y = first_y - frame_h - 16
    views = [
        (assets["review"], first_y, "01 · 人工审核工作台", "脚本、结论和备注在一个任务上下文中完成。"),
        (assets["export"], second_y, "02 · 交付与审计归档", "交付包、检查清单、回执状态和审计节点统一呈现。"),
    ]
    for image_path, image_y, label, note in views:
        rounded(c, MARGIN, image_y, CONTENT_W, frame_h, WHITE, LINE, 13)
        draw_image_contain(c, image_path, MARGIN + 6, image_y + 6, CONTENT_W - 12, frame_h - 12)
        c.setFillColor(NAVY)
        c.roundRect(MARGIN + 12, image_y + 12, 133, 20, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        set_font(c, 6.8, True)
        c.drawString(MARGIN + 22, image_y + 19, label)
        c.setFillColor(Color(1, 1, 1, 0.94))
        c.roundRect(MARGIN + 151, image_y + 12, CONTENT_W - 163, 20, 10, fill=1, stroke=0)
        c.setFillColor(TEXT)
        set_font(c, 6.3)
        c.drawString(MARGIN + 162, image_y + 19, note)

    rounded(c, MARGIN, 80, CONTENT_W, 51, NAVY, NAVY, 11)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7, True)
    c.drawString(MARGIN + 15, 110, "公开展示脱敏范围")
    c.setFillColor(WHITE)
    set_font(c, 7.8, True)
    c.drawString(MARGIN + 15, 91, "真实品牌与客户 · 任务编号与时间 · 账号与联系方式 · 内部路径、链接与令牌")
    footer(c, "docs/review-workflow.md · docs/publishing-workflow.md · 公开展示用脱敏界面")
    c.showPage()


def draw_validation(c: canvas.Canvas) -> None:
    y = header(
        c,
        8,
        "ENGINEERING QUALITY",
        "完整项目具备功能、验证、安全与回滚能力。",
        "以下结项证据来自项目内记录；对未执行的环境和外部服务验证保持明确区分。",
    )
    rounded(c, MARGIN, y - 88, CONTENT_W, 72, NAVY, NAVY, 13)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7.2, True)
    c.drawString(MARGIN + 15, y - 39, "Windows 结项验证")
    c.setFillColor(WHITE)
    set_font(c, 12.2, True)
    c.drawString(MARGIN + 15, y - 63, "最小工作流 completed · 7 个 smoke 通过 · 34 个单元测试通过")

    cards = [
        ("L1", "代码与结构", GREEN, ["96 个 Python 文件", "34 个测试函数", "模块化 Adapter / Provider", "git diff 检查通过"]),
        ("L2", "本地运行", TEAL, ["Windows 最小闭环完成", "dry-run Feishu", "mock Video", "任务输出与归档通过"]),
        ("L3", "用户流程", CORAL, ["浏览器客户演示", "人工审核写回", "双平台准备包", "人工发布回执与归档"]),
        ("L4", "交付治理", NAVY, ["30 个自动化脚本", "17 份项目文档", "隐私审计高风险 0", "公开仓库前复核"]),
    ]
    card_w = (CONTENT_W - 12) / 2
    card_h = 153
    top = y - 105
    for index, (level, title, color, items) in enumerate(cards):
        row, col = divmod(index, 2)
        x = MARGIN + col * (card_w + 12)
        card_y = top - (row + 1) * card_h - row * 12
        rounded(c, x, card_y, card_w, card_h, WHITE, LINE, 12)
        c.setFillColor(color)
        c.roundRect(x + 13, card_y + card_h - 39, 34, 24, 12, fill=1, stroke=0)
        c.setFillColor(WHITE)
        set_font(c, 7.3, True)
        c.drawCentredString(x + 30, card_y + card_h - 31, level)
        c.setFillColor(NAVY)
        set_font(c, 10, True)
        c.drawString(x + 58, card_y + card_h - 31, title)
        bullets(c, items, x + 14, card_y + card_h - 61, card_w - 28, 7.1, 10.4, color)

    verify_y = 78
    verify_h = top - 2 * card_h - 12 - verify_y - 16
    left_w = (CONTENT_W - 12) / 2
    rounded(c, MARGIN, verify_y, left_w, verify_h, TEAL_PALE, LINE, 12)
    c.setFillColor(TEAL_DARK)
    set_font(c, 9, True)
    c.drawString(MARGIN + 14, verify_y + verify_h - 24, "已完成并有证据")
    bullets(c, ["Phase 07 功能结项与冻结维护", "Windows 安全模式完整闭环", "隐私检查与中文交付文档"], MARGIN + 12, verify_y + verify_h - 49, left_w - 24, 6.9, 10.2)

    right_x = MARGIN + left_w + 12
    rounded(c, right_x, verify_y, left_w, verify_h, CORAL_PALE, LINE, 12)
    c.setFillColor(NAVY)
    set_font(c, 9, True)
    c.drawString(right_x + 14, verify_y + verify_h - 24, "不冒充已验证")
    bullets(c, ["WSL2 与 Hyper-V/systemd 运行", "真实飞书和真实视频 API", "生产部署与真实业务效果"], right_x + 12, verify_y + verify_h - 49, left_w - 24, 6.9, 10.2, CORAL)
    footer(c, "PROJECT_CLOSURE.md · docs/verification.md · PRIVACY_AUDIT.md")
    c.showPage()


def draw_ownership(c: canvas.Canvas, assets: dict[str, Path]) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    image_x = 338
    draw_image_cover(c, assets["delivery"], image_x, 0, PAGE_W - image_x, PAGE_H)
    c.setFillColor(Color(0.043, 0.114, 0.22, 0.15))
    c.rect(image_x, 0, PAGE_W - image_x, PAGE_H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(MARGIN, PAGE_H - 54, 24, 3, fill=1, stroke=0)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7.8, True)
    c.drawString(MARGIN + 32, PAGE_H - 57, "INDEPENDENT OWNERSHIP")
    c.setFillColor(WHITE)
    set_font(c, 8, True)
    c.drawRightString(318, PAGE_H - 57, f"09 / {TOTAL_PAGES:02d}")
    set_font(c, 22.5, True)
    c.drawString(MARGIN, PAGE_H - 110, "从需求定义到验收落地，")
    c.drawString(MARGIN, PAGE_H - 140, "全流程由我独立完成。")
    paragraph(c, "项目证明的不是单一页面开发，而是完整产品、架构、工程和交付能力。", MARGIN, PAGE_H - 174, 274, 8.8, 13.5, Color(1, 1, 1, 0.72))

    responsibilities = [
        ("01", "需求与边界", "拆解业务目标，明确人工审核与发布边界。"),
        ("02", "架构与实现", "完成状态机、适配器、核心流程和浏览器演示。"),
        ("03", "验证与安全", "编写测试、Smoke、隐私检查与失败处理。"),
        ("04", "交付与维护", "提供脚本、文档、回滚方案并完成项目结项。"),
    ]
    y = PAGE_H - 248
    for number, title, note in responsibilities:
        c.setFillColor(CORAL if number in {"01", "04"} else TEAL)
        c.circle(MARGIN + 12, y + 10, 12, fill=1, stroke=0)
        c.setFillColor(WHITE)
        set_font(c, 6.5, True)
        c.drawCentredString(MARGIN + 12, y + 8, number)
        set_font(c, 9.5, True)
        c.drawString(MARGIN + 35, y + 14, title)
        paragraph(c, note, MARGIN + 35, y - 4, 240, 6.9, 10, Color(1, 1, 1, 0.66))
        y -= 78

    c.setFillColor(Color(1, 1, 1, 0.08))
    c.roundRect(MARGIN, 184, 268, 106, 13, fill=1, stroke=0)
    c.setFillColor(TEAL_PALE)
    set_font(c, 7.2, True)
    c.drawString(MARGIN + 15, 266, "能力匹配")
    c.setFillColor(WHITE)
    set_font(c, 8.3, True)
    for index, text in enumerate(["0→1 产品与系统落地", "Python 全栈与工作流自动化", "AI 服务集成与安全边界", "企业内部工具与交付治理"]):
        c.drawString(MARGIN + 15, 242 - index * 19, f"•  {text}")

    c.setFillColor(WHITE)
    set_font(c, 18, True)
    c.drawString(MARGIN, 128, "Jerry 谭梓健")
    c.setFillColor(TEAL_PALE)
    set_font(c, 9, True)
    c.drawString(MARGIN, 106, "独立全栈开发者")
    c.setFillColor(WHITE)
    set_font(c, 8.3)
    c.drawString(MARGIN, 81, "Jerrytan1221@gmail.com")
    c.drawString(MARGIN, 61, "猎聘 / BOSS 直聘站内联系")
    footer(c, "README.md · PROJECT_CLOSURE.md · 完整项目交付证据", dark=True)
    c.showPage()


def build_pdf() -> Path:
    """生成最终 9 页 A4 完整项目作品集。"""
    register_fonts()
    assets = require_assets()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("Jerry 谭梓健 - TideCraft 完整项目作品集")
    c.setAuthor("Jerry 谭梓健")
    c.setSubject("用于猎聘、BOSS 直聘等招聘平台的完整项目案例")
    c.setCreator("ReportLab")
    draw_cover(c, assets)
    draw_overview(c, assets)
    draw_complete_flow(c)
    draw_architecture(c)
    draw_engineering(c)
    draw_product_workflow(c, assets)
    draw_product_review(c, assets)
    draw_validation(c)
    draw_ownership(c, assets)
    c.save()
    return OUTPUT


if __name__ == "__main__":
    result = build_pdf()
    print(result.as_posix())
