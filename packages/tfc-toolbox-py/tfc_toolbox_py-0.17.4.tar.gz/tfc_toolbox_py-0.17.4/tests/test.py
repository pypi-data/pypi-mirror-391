import tfc_toolbox_py as tfc
image = "furina.webp"

# 创建拼接器实例
stitcher = tfc.cv.ImageStitcher(image, image)

# 左右拼接(带10像素黑色间距)
horizontal = stitcher.stitch_horizontal(padding=10)
stitcher.show_image(horizontal, 'Horizontal Stitch')

# 上下拼接(带5像素白色间距)
vertical = stitcher.stitch_vertical(padding=5, padding_color=(255, 255, 255))
stitcher.show_image(vertical, 'Vertical Stitch')
stitcher.save_image(vertical, 'vertical_stitch.jpg')