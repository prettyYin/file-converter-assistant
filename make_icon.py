"""生成应用 Logo / 图标 — 简约扁平风格，符合文件转换工具调性

设计理念：
- 圆角方形蓝色底（品牌色 #4A90D9 渐变）
- 中央两个层叠的文档页面，象征"文件"
- 环绕的循环箭头，象征"格式转换"
- 扁平、简约、辨识度高
"""
import os
import math
from PIL import Image, ImageDraw


# 品牌配色
BLUE = (74, 144, 217)        # #4A90D9 主色
BLUE_DARK = (58, 123, 192)   # #3A7BC0 深色
WHITE = (255, 255, 255)
PAPER = (255, 255, 255)
PAPER_SHADOW = (224, 233, 244)  # 浅蓝灰


def rounded_rect(draw, xy, radius, fill):
    """绘制圆角矩形"""
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def lerp_color(c1, c2, t):
    """颜色线性插值"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient_rounded(size, radius, c_top, c_bottom):
    """绘制垂直渐变的圆角方形（带透明背景）"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # 先在临时图上画垂直渐变
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        color = lerp_color(c_top, c_bottom, t)
        gdraw.line([(0, y), (size, y)], fill=color + (255,))

    # 圆角遮罩
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)

    img.paste(grad, (0, 0), mask)
    return img


def draw_document(draw, x, y, w, h, fill, fold=0.28, line_color=None):
    """绘制一个带折角的文档页面"""
    r = max(2, int(w * 0.06))
    fold_size = int(w * fold)

    # 文档主体（右上角折角）
    points = [
        (x + r, y),
        (x + w - fold_size, y),
        (x + w, y + fold_size),
        (x + w, y + h - r),
        (x + w - r, y + h),
        (x + r, y + h),
        (x, y + h - r),
        (x, y + r),
    ]
    # 用多边形 + 圆角近似
    draw.polygon(points, fill=fill)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)

    # 盖住右上角画折角
    draw.polygon([
        (x + w - fold_size, y),
        (x + w, y + fold_size),
        (x + w - fold_size, y + fold_size),
    ], fill=line_color if line_color else PAPER_SHADOW)

    # 文档内的横线（文字示意）
    if line_color:
        line_x1 = x + int(w * 0.18)
        line_x2 = x + int(w * 0.82)
        n_lines = 3
        gap = int(h * 0.16)
        start_y = y + int(h * 0.42)
        lw = max(2, int(h * 0.05))
        for i in range(n_lines):
            ly = start_y + i * gap
            x2 = line_x2 if i < n_lines - 1 else x + int(w * 0.6)
            draw.line([(line_x1, ly), (x2, ly)], fill=line_color, width=lw)


def draw_convert_arrows(draw, cx, cy, radius, color, width):
    """绘制循环转换的双箭头（环形）"""
    # 上半弧（从左到右）+ 下半弧（从右到左）
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]

    # 上弧
    draw.arc(bbox, start=200, end=340, fill=color, width=width)
    # 下弧
    draw.arc(bbox, start=20, end=160, fill=color, width=width)

    # 箭头头部
    ah = int(radius * 0.42)
    # 右侧箭头（上弧末端，指向右下）
    ang = math.radians(340)
    ex = cx + radius * math.cos(ang)
    ey = cy + radius * math.sin(ang)
    draw.polygon([
        (ex + ah * 0.2, ey - ah * 0.5),
        (ex + ah * 0.7, ey + ah * 0.4),
        (ex - ah * 0.5, ey + ah * 0.35),
    ], fill=color)

    # 左侧箭头（下弧末端，指向左上）
    ang2 = math.radians(160)
    ex2 = cx + radius * math.cos(ang2)
    ey2 = cy + radius * math.sin(ang2)
    draw.polygon([
        (ex2 - ah * 0.2, ey2 + ah * 0.5),
        (ex2 - ah * 0.7, ey2 - ah * 0.4),
        (ex2 + ah * 0.5, ey2 - ah * 0.35),
    ], fill=color)


def make_icon(size):
    """生成单个尺寸的图标"""
    # 用 4 倍超采样获得平滑边缘
    scale = 4
    s = size * scale

    radius = int(s * 0.22)
    img = draw_gradient_rounded(s, radius, BLUE, BLUE_DARK)
    draw = ImageDraw.Draw(img)

    # 两个层叠文档
    doc_w = int(s * 0.40)
    doc_h = int(s * 0.50)

    # 后面的文档（浅色阴影）
    bx = int(s * 0.30)
    by = int(s * 0.20)
    draw_document(draw, bx, by, doc_w, doc_h, PAPER_SHADOW, line_color=None)

    # 前面的文档（白色 + 文字线）
    fx = int(s * 0.22)
    fy = int(s * 0.28)
    draw_document(draw, fx, fy, doc_w, doc_h, PAPER, line_color=BLUE)

    # 右下角的转换箭头徽标
    badge_cx = int(s * 0.72)
    badge_cy = int(s * 0.72)
    badge_r = int(s * 0.17)
    # 白色圆底
    draw.ellipse(
        [badge_cx - badge_r - int(s*0.03), badge_cy - badge_r - int(s*0.03),
         badge_cx + badge_r + int(s*0.03), badge_cy + badge_r + int(s*0.03)],
        fill=WHITE,
    )
    draw_convert_arrows(draw, badge_cx, badge_cy, int(badge_r * 0.7), BLUE, max(3, int(s * 0.025)))

    # 缩回目标尺寸
    img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 生成多尺寸 PNG，用于 .ico 和应用内显示
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    for sz in sizes:
        icon = make_icon(sz)
        images.append(icon)

    # 保存 256 的 PNG 作为应用内 logo
    png_path = os.path.join(assets_dir, "icon.png")
    images[-1].save(png_path)
    print(f"已生成 PNG: {png_path}")

    # 保存为 .ico（包含多个尺寸）
    ico_path = os.path.join(assets_dir, "icon.ico")
    images[-1].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
    )
    print(f"已生成 ICO: {ico_path}")

    # 额外保存一个大尺寸预览图
    preview = make_icon(512)
    preview_path = os.path.join(assets_dir, "icon_preview.png")
    preview.save(preview_path)
    print(f"已生成预览: {preview_path}")


if __name__ == "__main__":
    main()
