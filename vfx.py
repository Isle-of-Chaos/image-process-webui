from PIL import Image


class ImageVFX:
    @classmethod
    def resize(cls, img_path, width=None, height=None):
        """
        缩放图片大小，按比例缩放，保持宽高比
        :param img_path: 图片路径
        :param width: 缩放后的宽度
        :param height: 缩放后的高度
        :return: PIL.Image对象
        """
        with Image.open(img_path) as img:
            if not width and not height:
                return img
            if not width:
                width = int(img.width * height / img.height)
            if not height:
                height = int(img.height * width / img.width)
            return img.resize((width, height))

    @classmethod
    def rotate(cls, img_path, angle):
        """
        旋转图片
        :param img_path: 图片路径
        :param angle: 旋转角度
        :return: PIL.Image对象
        """
        with Image.open(img_path) as img:
            return img.rotate(angle)

    @classmethod
    def crop(cls, img_path, left, top, right, bottom):
        """
        裁剪图片
        :param img_path: 图片路径
        :param left: 左边界
        :param top: 上边界
        :param right: 右边界
        :param bottom: 下边界
        :return: PIL.Image对象
        """
        with Image.open(img_path) as img:
            return img.crop((left, top, right, bottom))

    @classmethod
    def save(cls, img, save_path):
        """
        保存图片
        :param img: PIL.Image对象
        :param save_path: 保存路径
        """
        img.save(save_path)

    @classmethod
    def convert_to_grayscale(cls, image):
        # 转换为灰度图像
        grayscale_image = image.convert('L')
        # 返回转换后的图像
        return grayscale_image
