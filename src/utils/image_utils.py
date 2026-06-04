"""图像预处理工具 — 用于 OCR 前的图像增强"""
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np


def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """
    对图像进行 OCR 预处理：灰度化 → 增强对比度 → 二值化 → 去噪

    Args:
        image: PIL Image 对象

    Returns:
        处理后的 PIL Image
    """
    # 1. 转为灰度
    if image.mode != "L":
        image = image.convert("L")

    # 2. 增强对比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # 3. 增强锐度
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)

    # 4. 二值化（Otsu 阈值法）
    image = _binary_otsu(image)

    # 5. 去噪（中值滤波）
    image = image.filter(ImageFilter.MedianFilter(3))

    return image


def _binary_otsu(image: Image.Image) -> Image.Image:
    """使用 Otsu 方法进行二值化"""
    img_array = np.array(image, dtype=np.uint8)

    # 计算直方图
    hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
    hist = hist.astype(float)
    hist /= hist.sum()

    # Otsu 算法
    max_variance = 0
    best_threshold = 127

    for t in range(1, 256):
        w0 = hist[:t].sum()
        w1 = hist[t:].sum()
        if w0 == 0 or w1 == 0:
            continue
        m0 = (np.arange(t) * hist[:t]).sum() / w0
        m1 = (np.arange(t, 256) * hist[t:]).sum() / w1
        variance = w0 * w1 * (m0 - m1) ** 2
        if variance > max_variance:
            max_variance = variance
            best_threshold = t

    # 应用阈值
    binary = (img_array > best_threshold).astype(np.uint8) * 255
    return Image.fromarray(binary, mode="L")


def deskew(image: Image.Image) -> Image.Image:
    """矫正图像倾斜（简化版）"""
    img_array = np.array(image, dtype=np.uint8)
    # 找到所有非零像素（文字像素）
    coords = np.column_stack(np.where(img_array < 128))
    if len(coords) < 100:
        return image

    # 简单的最小面积矩形估计倾斜角度
    from cv2 import minAreaRect, getRotationMatrix2D, warpAffine  # 需要 opencv
    try:
        rect = minAreaRect(coords.astype(np.float32))
        angle = rect[2]
        if angle < -45:
            angle = 90 + angle
        if abs(angle) < 0.5:
            return image

        h, w = img_array.shape
        center = (w // 2, h // 2)
        matrix = getRotationMatrix2D(center, angle, 1.0)
        rotated = warpAffine(img_array, matrix, (w, h), borderValue=255)
        return Image.fromarray(rotated, mode="L")
    except ImportError:
        # 无 opencv 时跳过纠偏
        return image
