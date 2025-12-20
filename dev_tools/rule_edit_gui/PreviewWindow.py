from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel


class PreviewWindow(QLabel):
    """预览截图窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 150)
        self.setMaximumSize(300, 225)
        # 移除硬编码样式，将在apply_theme中设置
        self.setAlignment(Qt.AlignCenter)
        self.setText("预览区域\n选择红色框后显示截图")
        self.setWordWrap(True)

        # 存储原始图片和父窗口引用
        self.original_pixmap = None
        self.parent_window = None
        self.is_grayscale = False

    def set_parent_window(self, parent_window):
        """设置父窗口引用"""
        self.parent_window = parent_window

    def set_grayscale_mode(self, enabled):
        """设置灰度模式"""
        self.is_grayscale = enabled

    def apply_theme(self, theme):
        """应用主题到预览窗口"""
        style_sheet = f"""
        border: 1px solid #ccc;
        background-color: {theme['entry_bg']};
        color: {theme['entry_fg']};
        border-radius: 3px;
        """
        self.setStyleSheet(style_sheet)

    def update_preview(self, image_path, roi_coords):
        """更新预览图片"""
        if not image_path or not roi_coords:
            self.clear_preview()
            return

        try:
            x, y, w, h = roi_coords

            # 使用PIL截取ROI区域
            img = Image.open(image_path)
            roi_img = img.crop((x, y, x + w, y + h))

            # 如果启用了灰度模式，转换为灰度图
            if self.is_grayscale:
                roi_img = roi_img.convert('L')
                # 转换为RGB格式以便显示
                roi_img = roi_img.convert('RGB')
            else:
                # 转换为RGB格式确保兼容性
                roi_img = roi_img.convert('RGB')

            # 手动转换为QImage
            import numpy as np
            arr = np.array(roi_img)
            height, width, channel = arr.shape
            bytes_per_line = 3 * width
            qimage = QImage(arr.data, width, height, bytes_per_line, QImage.Format_RGB888)

            preview_pixmap = QPixmap.fromImage(qimage)

            # 缩放以适应预览窗口
            scaled_pixmap = preview_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            self.setPixmap(scaled_pixmap)

        except Exception as e:
            print(f"更新预览失败: {e}")
            self.setText(f"预览失败\n{str(e)}")

    def clear_preview(self):
        """清除预览"""
        self.clear()
        self.setText("预览区域\n选择红色框后显示截图")
