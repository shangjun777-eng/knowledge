"""Generate PCIe explanatory GIFs with Pillow.

Outputs:
  static/images/pcie/pcie-read-path.gif
  static/images/pcie/pcie-posted.gif
  static/images/pcie/pcie-encapsulation.gif
  static/images/pcie/pcie-ltssm.gif

Preview contact sheets are written to the temp directory so they can be
inspected without committing them.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "images" / "pcie"
PREVIEW = Path(os.environ.get("TEMP", str(ROOT))) / "pcie-gif-preview"
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW.mkdir(parents=True, exist_ok=True)

# Palette
BG = (248, 250, 252)
CARD = (255, 255, 255)
TEXT = (15, 23, 42)
MUTED = (100, 116, 139)
BLUE = (37, 99, 235)
LIGHT_BLUE = (219, 234, 254)
GREEN = (22, 163, 74)
LIGHT_GREEN = (220, 252, 231)
ORANGE = (217, 119, 6)
LIGHT_ORANGE = (254, 243, 199)
GRAY = (148, 163, 184)
LIGHT_GRAY = (226, 232, 240)
WHITE = (255, 255, 255)
RED = (220, 38, 38)
PURPLE = (124, 58, 237)

PALETTE_COLORS = [
    BG, CARD, TEXT, MUTED, BLUE, LIGHT_BLUE, GREEN, LIGHT_GREEN,
    ORANGE, LIGHT_ORANGE, GRAY, LIGHT_GRAY, WHITE, RED, PURPLE,
]

FONT_REGULAR = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"
_FONT_CACHE: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}

try:
    DITHER = Image.Dither.NONE
except AttributeError:  # pragma: no cover
    DITHER = Image.NONE


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key not in _FONT_CACHE:
        path = FONT_BOLD if bold else FONT_REGULAR
        _FONT_CACHE[key] = ImageFont.truetype(path, size, index=0)
    return _FONT_CACHE[key]


def new_frame(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    return image, ImageDraw.Draw(image)


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    value: str,
    size: int = 18,
    color: tuple[int, int, int] = TEXT,
    bold: bool = False,
    anchor: str = "mm",
    align: str = "center",
    spacing: int = 4,
) -> None:
    draw.multiline_text(
        xy,
        value,
        font=font(size, bold),
        fill=color,
        anchor=anchor,
        align=align,
        spacing=spacing,
    )


def rounded(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    w: float,
    h: float,
    fill=CARD,
    outline=LIGHT_GRAY,
    width: int = 2,
    radius: int = 14,
) -> None:
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def box_with_sub(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    subtitle: str,
    active: bool = False,
    accent=BLUE,
) -> None:
    if active:
        rounded(draw, x - 7, y - 7, w + 14, h + 14, fill=LIGHT_BLUE, outline=accent, width=3, radius=20)
        fill = CARD
        outline = accent
        width = 3
    else:
        fill = CARD
        outline = LIGHT_GRAY
        width = 2
    rounded(draw, x, y, w, h, fill=fill, outline=outline, width=width, radius=14)
    text(draw, (x + w / 2, y + h / 2 - 13), title, 18, TEXT, True)
    text(draw, (x + w / 2, y + h / 2 + 16), subtitle, 12, MUTED)


def arrow(
    draw: ImageDraw.ImageDraw,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color=GRAY,
    width: int = 2,
    head: int = 9,
    dashed: bool = False,
) -> None:
    if dashed:
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            return
        dx, dy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0.0
        while pos < length - head:
            end = min(pos + 8, length - head)
            draw.line(
                [x1 + dx * pos, y1 + dy * pos, x1 + dx * end, y1 + dy * end],
                fill=color,
                width=width,
            )
            pos += 14
    else:
        draw.line([x1, y1, x2, y2], fill=color, width=width)

    angle = math.atan2(y2 - y1, x2 - x1)
    for delta in (math.pi / 7, -math.pi / 7):
        hx = x2 - head * math.cos(angle + delta)
        hy = y2 - head * math.sin(angle + delta)
        draw.line([x2, y2, hx, hy], fill=color, width=width)


def packet(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    color,
    text_color=WHITE,
) -> None:
    draw.rounded_rectangle([x + 3, y + 4, x + w + 3, y + h + 4], radius=10, fill=LIGHT_GRAY)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=color)
    text(draw, (x + w / 2, y + h / 2), label, 15, text_color, True)


def legend(draw: ImageDraw.ImageDraw, x: float, y: float, color, label: str) -> None:
    draw.ellipse([x, y, x + 12, y + 12], fill=color)
    text(draw, (x + 20, y + 6), label, 13, MUTED, anchor="lm")


def progress(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    total: int,
    current: int,
    seg_w: float = 96,
    seg_h: float = 8,
    gap: float = 8,
) -> None:
    for i in range(total):
        if i < current:
            fill = GREEN
        elif i == current:
            fill = BLUE
        else:
            fill = LIGHT_GRAY
        x0 = x + i * (seg_w + gap)
        draw.rounded_rectangle([x0, y, x0 + seg_w, y + seg_h], radius=4, fill=fill)


def save_gif(frames: list[Image.Image], path: Path, duration: int = 900) -> None:
    palette = Image.new("P", (1, 1))
    flat: list[int] = []
    for color in PALETTE_COLORS:
        flat.extend(color)
    flat.extend([0, 0, 0] * (256 - len(PALETTE_COLORS)))
    palette.putpalette(flat)
    converted = [frame.quantize(palette=palette, dither=DITHER) for frame in frames]
    converted[0].save(
        path,
        save_all=True,
        append_images=converted[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def contact_sheet(
    frames: list[Image.Image],
    path: Path,
    picks: list[int] | None = None,
) -> None:
    if picks is None:
        picks = [0, len(frames) // 3, (2 * len(frames)) // 3, len(frames) - 1]
    picks = [min(max(0, p), len(frames) - 1) for p in picks]
    picks = sorted(set(picks))
    while len(picks) < 4:
        picks.append(picks[-1])
    thumbs = []
    for index in picks[:4]:
        frame = frames[index]
        ratio = 480 / frame.width
        thumbs.append(frame.resize((480, int(frame.height * ratio)), Image.Resampling.LANCZOS))
    sheet = Image.new("RGB", (960, thumbs[0].height * 2), BG)
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 2) * 480, (i // 2) * thumb.height))
    sheet.save(path)


def make_read_path() -> None:
    width, height = 960, 480
    boxes = [
        ("CPU", "发起 load", 40),
        ("Root Complex", "组装 / 匹配", 250),
        ("Switch", "转发 TLP", 460),
        ("Endpoint", "读寄存器", 670),
    ]
    steps = [
        (0, "MRd", 55, 81, "1/8  CPU 发起 load，访问 BAR 映射地址"),
        (1, "MRd", 265, 81, "2/8  Root Complex 组装 MRd：Requester ID + Tag + 地址"),
        (1, "MRd", 265, 81, "3/8  Data Link 加序列号 + LCRC，Physical 编码发送"),
        (2, "MRd", 475, 81, "4/8  Switch 按地址转发到下游端口"),
        (3, "MRd", 685, 81, "5/8  Endpoint 命中 BAR，读出寄存器"),
        (3, "CplD", 685, 270, "6/8  Endpoint 返回 CplD，携带相同的 Tag"),
        (1, "CplD", 265, 270, "7/8  Root Complex 按 Requester ID + Tag 匹配"),
        (0, "CplD", 55, 270, "8/8  CPU 拿到寄存器值，一次 MMIO 读完成"),
    ]
    frames: list[Image.Image] = []
    for index, (active, pkt, px, py, step) in enumerate(steps):
        image, draw = new_frame(width, height)
        text(draw, (48, 34), "一次 MMIO 读：MRd 去，CplD 回", 24, TEXT, True, anchor="lm")
        text(draw, (48, 64), "驱动读 BAR 寄存器 → Root Complex → Switch → Endpoint → 返回", 14, MUTED, anchor="lm")
        legend(draw, 670, 34, BLUE, "MRd 读请求")
        legend(draw, 670, 58, GREEN, "CplD 数据返回")

        for i in range(3):
            x_left = boxes[i][2] + 150
            x_right = boxes[i + 1][2]
            arrow(draw, x_left, 100, x_right, 100, GRAY)
            arrow(draw, x_right, 320, x_left, 320, GRAY)
        for name, subtitle, x in boxes:
            draw.line([x + 75, 130, x + 75, 100], fill=GRAY, width=1)
            draw.line([x + 75, 222, x + 75, 320], fill=GRAY, width=1)
        text(draw, (480, 344), "返回路径", 12, MUTED)

        for i, (name, subtitle, x) in enumerate(boxes):
            box_with_sub(draw, x, 130, 150, 92, name, subtitle, active=(i == active))

        color = BLUE if pkt == "MRd" else GREEN
        packet(draw, px, py, 96, 38, pkt, color)

        text(draw, (480, 400), step, 15, TEXT)
        progress(draw, 68, 430, 8, index)
        text(draw, (480, 462), "读是 non-posted：MRd 必须等到 CplD；写通常是 posted，发完即结束。", 12, MUTED)
        frames.append(image)

    save_gif(frames, OUT / "pcie-read-path.gif")
    contact_sheet(frames, PREVIEW / "preview-pcie-read-path.png", picks=[0, 2, 5, 7])


def make_posted() -> None:
    width, height = 960, 320
    labels = [
        "MWr 发出：posted，不需要 Completion",
        "MWr 在链路中传输",
        "MWr 到达：发送方发完即结束",
        "MRd 发出：non-posted，需要 Completion",
        "MRd 到达，Endpoint 返回 CplD",
        "CplD 回到 RC：读完成，拿到数据",
    ]
    frames: list[Image.Image] = []
    for index in range(6):
        image, draw = new_frame(width, height)
        text(draw, (48, 30), "Posted vs Non-Posted", 24, TEXT, True, anchor="lm")
        text(draw, (48, 58), "写通常 posted，读必须等 Completion", 14, MUTED, anchor="lm")

        box_with_sub(draw, 40, 90, 150, 170, "CPU / RC", "发起事务")
        box_with_sub(draw, 740, 90, 150, 170, "Endpoint", "处理并返回")

        text(draw, (205, 103), "Posted：Memory Write（MWr）", 14, ORANGE, True, anchor="lm")
        text(draw, (205, 174), "Non-Posted：Memory Read（MRd）", 14, BLUE, True, anchor="lm")

        arrow(draw, 190, 140, 740, 140, GRAY)
        arrow(draw, 190, 200, 740, 200, GRAY)
        arrow(draw, 740, 235, 190, 235, GRAY)

        mwr_x = 195 if index == 0 else (430 if index == 1 else 640)
        packet(draw, mwr_x, 123, 90, 34, "MWr", ORANGE)

        if index >= 3:
            mrd_x = 195 if index == 3 else 640
            packet(draw, mrd_x, 183, 90, 34, "MRd", BLUE)
        if index >= 4:
            cpld_x = 640 if index == 4 else 195
            packet(draw, cpld_x, 218, 90, 34, "CplD", GREEN)

        if index >= 2:
            draw.line([688, 100, 700, 112, 718, 88], fill=GREEN, width=4)
            text(draw, (722, 100), "OK", 10, GREEN, anchor="lm")
        if index >= 5:
            draw.line([606, 240, 618, 252, 636, 228], fill=GREEN, width=4)
            text(draw, (642, 238), "拿到数据", 11, GREEN, anchor="lm")

        text(draw, (480, 290), labels[index], 14, TEXT)
        frames.append(image)

    save_gif(frames, OUT / "pcie-posted.gif")
    contact_sheet(frames, PREVIEW / "preview-pcie-posted.png", picks=[0, 2, 4, 5])


def make_encapsulation() -> None:
    width, height = 960, 480
    layers = [
        ("Transaction", "TLP", BLUE, LIGHT_BLUE, 140),
        ("Data Link", "DLL 帧 / DLLP", ORANGE, LIGHT_ORANGE, 240),
        ("Physical", "符号 / 电信号", GREEN, LIGHT_GREEN, 340),
    ]
    frames: list[Image.Image] = []

    for index in range(12):
        if index < 3:
            active = 0
        elif index < 6:
            active = 1
        elif index < 9:
            active = 2
        else:
            active = 2 - (index - 9)  # 2, 1, 0

        image, draw = new_frame(width, height)
        text(draw, (48, 30), "数据在每一层怎么封装", 24, TEXT, True, anchor="lm")
        text(draw, (48, 58), "发送：逐层加信封；接收：逐层拆并校验", 14, MUTED, anchor="lm")

        for i, (name, sub, color, light, y) in enumerate(layers):
            if i == active:
                rounded(draw, 38, y - 34, 200, 68, fill=light, outline=color, width=2, radius=16)
                title_color = color
            else:
                title_color = MUTED
            draw.ellipse([50, y - 8, 62, y + 4], fill=color)
            text(draw, (74, y - 8), name, 17, title_color, True, anchor="lm")
            text(draw, (74, y + 14), sub, 11, MUTED, anchor="lm")

        if index < 3:
            text(draw, (590, 118), "TLP", 20, BLUE, True)
            rounded(draw, 355, 165, 140, 80, fill=BLUE, outline=BLUE)
            text(draw, (425, 205), "Header", 15, WHITE, True)
            rounded(draw, 495, 165, 220, 80, fill=LIGHT_BLUE, outline=LIGHT_BLUE)
            text(draw, (605, 205), "Data", 15, TEXT, True)
            rounded(draw, 715, 165, 90, 80, fill=GRAY, outline=GRAY)
            text(draw, (760, 205), "ECRC", 13, WHITE, True)
            if index == 1:
                rounded(draw, 343, 153, 474, 104, fill=None, outline=BLUE, width=3, radius=16)
            text(draw, (590, 275), "Transaction Layer：组装/解析 TLP", 13, MUTED)
        elif index < 6:
            progress_value = (index - 3) / 2.0
            seq_x = 155 + 100 * progress_value
            lcrc_x = 905 - 100 * progress_value
            text(draw, (590, 118), "DLL 帧 = Seq + TLP + LCRC", 17, ORANGE, True)
            rounded(draw, seq_x, 165, 100, 80, fill=ORANGE, outline=ORANGE)
            text(draw, (seq_x + 50, 205), "Seq", 14, WHITE, True)
            rounded(draw, 355, 165, 140, 80, fill=BLUE, outline=BLUE)
            text(draw, (425, 205), "Header", 15, WHITE, True)
            rounded(draw, 495, 165, 220, 80, fill=LIGHT_BLUE, outline=LIGHT_BLUE)
            text(draw, (605, 205), "Data", 15, TEXT, True)
            rounded(draw, 715, 165, 90, 80, fill=GRAY, outline=GRAY)
            text(draw, (760, 205), "ECRC", 13, WHITE, True)
            rounded(draw, lcrc_x, 165, 100, 80, fill=GREEN, outline=GREEN)
            text(draw, (lcrc_x + 50, 205), "LCRC", 14, WHITE, True)
            text(draw, (590, 275), "Data Link Layer：加序列号和 LCRC，支持 ACK/NAK 与重传", 13, MUTED)
        elif index < 9:
            text(draw, (590, 118), "PHY：Framing + 编码 + SerDes", 17, GREEN, True)
            rounded(draw, 355, 150, 250, 60, fill=LIGHT_BLUE, outline=BLUE)
            text(draw, (480, 180), "DLL 帧", 16, BLUE, True)
            arrow(draw, 480, 212, 480, 292, GREEN, width=2)
            text(draw, (500, 252), "编码 + 串行化", 12, MUTED, anchor="lm")
            rounded(draw, 255, 300, 630, 74, fill=LIGHT_GREEN, outline=GREEN)
            for i in range(18):
                x = 270 + i * 34
                draw.rounded_rectangle([x, 322, x + 22, 344], radius=4, fill=(BLUE if i % 3 == 0 else ORANGE if i % 3 == 1 else GREEN))
            text(draw, (590, 395), "Physical Layer：framing、加扰、编码、SerDes", 13, MUTED)
        else:
            text(draw, (590, 118), "接收：解码 → 校验 LCRC/Seq → 恢复 TLP", 16, GREEN, True)
            rounded(draw, 255, 300, 630, 74, fill=LIGHT_GREEN, outline=GREEN)
            for i in range(18):
                x = 270 + i * 34
                draw.rounded_rectangle([x, 322, x + 22, 344], radius=4, fill=(BLUE if i % 3 == 0 else ORANGE if i % 3 == 1 else GREEN))
            arrow(draw, 570, 290, 570, 258, GREEN, width=2)
            rounded(draw, 355, 165, 450, 80, fill=LIGHT_BLUE, outline=BLUE, width=2)
            text(draw, (580, 205), "TLP", 18, BLUE, True)
            draw.line([728, 158, 742, 172, 762, 144], fill=GREEN, width=4)
            text(draw, (770, 160), "校验通过", 11, GREEN, anchor="lm")
            text(draw, (590, 395), "接收方向：逐层拆信封，DLL 负责校验和重传", 13, MUTED)

        text(draw, (480, 448), "发送：TLP → DLL 帧 → 符号；接收：符号 → DLL 帧 → TLP", 13, MUTED)
        frames.append(image)

    save_gif(frames, OUT / "pcie-encapsulation.gif", duration=800)
    contact_sheet(frames, PREVIEW / "preview-pcie-encapsulation.png", picks=[0, 4, 7, 10])


def make_ltssm() -> None:
    width, height = 960, 400
    states = [
        ("Detect", "检测对端", 40),
        ("Polling", "位锁 / 符号锁", 235),
        ("Configuration", "协商宽度 / 速率", 430),
        ("L0", "正常工作", 625),
    ]
    active_sequence = [0, 1, 2, 3, 3, 4, 3, 0]
    frames: list[Image.Image] = []

    for index, active in enumerate(active_sequence):
        image, draw = new_frame(width, height)
        text(draw, (48, 30), "LTSSM：链路训练到 L0", 24, TEXT, True, anchor="lm")
        text(draw, (48, 58), "先对暗号、测车道、协商速率，再放行 TLP", 14, MUTED, anchor="lm")

        for i in range(3):
            x1 = states[i][2] + 170
            x2 = states[i + 1][2]
            arrow(draw, x1, 160, x2, 160, GRAY)

        for i, (name, subtitle, x) in enumerate(states):
            box_with_sub(draw, x, 120, 170, 80, name, subtitle, active=(active == i))

        arrow(draw, 720, 200, 720, 245, GRAY)
        arrow(draw, 700, 245, 700, 200, GRAY, dashed=True)
        box_with_sub(draw, 625, 245, 170, 70, "Recovery", "重新训练", active=(active == 4), accent=ORANGE)

        if active == 3:
            packet(draw, 820, 140, 90, 36, "TLP", BLUE)
            arrow(draw, 795, 158, 820, 158, GREEN, width=2)
            draw.line([850, 200, 862, 212, 880, 186], fill=GREEN, width=4)
            text(draw, (888, 198), "可以传", 11, GREEN, anchor="lm")

        text(draw, (48, 300), "低功耗：L0s / L1 / L2（进入和退出也要验证）", 12, MUTED, anchor="lm")
        text(draw, (480, 350), "Detect → Polling → Configuration → L0；L0 之后才能传 TLP", 15, TEXT)
        text(draw, (480, 380), "训练失败时可能重试、降速、降宽，或停在 Recovery", 12, MUTED)
        frames.append(image)

    save_gif(frames, OUT / "pcie-ltssm.gif", duration=900)
    contact_sheet(frames, PREVIEW / "preview-pcie-ltssm.png", picks=[0, 3, 5, 6])


if __name__ == "__main__":
    make_read_path()
    make_posted()
    make_encapsulation()
    make_ltssm()
    print("generated:", OUT)
    print("previews:", PREVIEW)
