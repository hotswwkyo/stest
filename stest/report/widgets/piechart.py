# -*- coding:utf-8 -*-
'''
Created on 2020年6月20日

@author: siwenwei
'''

import math
from ..html import elements


class PieChart(elements.Svg):
    """饼图"""

    DATA_KEY = "data"
    LABEL_KEY = "label"
    COLOR_KEY = "color"
    PIE_CHART_CSS_CLASS_KEY = "pie_chart_css_class"  # 饼图样式
    LEGEND_CSS_CLASS_KEY = "legend_css_class"  # 图例样式
    LEGEND_TEXT_CSS_CLASS_KEY = "legend_text_css_class"  # 图例文本样式

    def __init__(self, parts, width, height, cx, cy, r):
        """创建一个<svg>元素，并在其中绘制一个饼状图

        Args:
            parts: 用于绘制的扇形数据的数组，数组每一项都表示饼状图的一个楔，[part,...], part={"data":12,"label":"成功","color":"antiquewhite"}
            width,height: SVG图形的大小，单位为像素
            cx cy r :  饼状图的圆心及半径

        Returns:
            一个保存饼状图的<svg>元素
        """
        super().__init__(width, height)
        self.r = r
        self.cx = cx
        self.cy = cy
        self.parts = parts
        self.width = width
        self.height = height

        self.lx = self.cx + self.r * 1.5
        self.ly = (self.cy + self.r * 2) / 6

        self._build()

    @classmethod
    def build_part(cls, data, label, color, **css_classes):
        """构建饼图数据

        Args:
            data: 用于绘制的数字,饼图大小
            label: 饼图名称
            color：饼图颜色
        """

        part = {cls.DATA_KEY: data, cls.LABEL_KEY: label, cls.COLOR_KEY: color}
        EXCLUDE_KEYS = [cls.DATA_KEY, cls.LABEL_KEY, cls.COLOR_KEY]
        for k, v in css_classes.items():
            if k not in EXCLUDE_KEYS:
                part[k] = v

        return part

    @classmethod
    def percent(cls, divisor, dividend, precision=2):
        fmt = "{:." + str(precision) + "f}%"
        return fmt.format(divisor / dividend * 100)

    @classmethod
    def attach_suffix(cls, text, suffix):
        fmt = "{}({})"
        return fmt.format(text, suffix)

    def _build(self):

        viewbox = "{x} {y} {width} {height}".format(
            x="0", y="0", width=self.width, height=self.height)
        self.set_attr("viewBox", viewbox)

        # 累加datas的值，以便于知道饼状图的大小
        total = 0
        for part in self.parts:
            total = total + part[self.DATA_KEY]

        # 现在计算出饼状图每个分片的大小，其中角度以弧度制计算
        angle_parts = []
        for part in self.parts:
            data = part[self.DATA_KEY]
            angle = data / total * 360
            angle = 359.9 if angle == 360 else angle
            radian = angle / 180 * math.pi
            angle_parts.append((radian, part))

        # 遍历饼状图的每个分片
        startangle = 0
        for i, angle_part in enumerate(angle_parts):

            angle, part = angle_part
            # 这里表示楔的结束位置
            endagle = startangle + angle

            # 计算出楔和园相交的两个点
            # 这些计算公式都是以12点钟方向为0度
            # 顺时针方向角度递增
            x1 = int(self.cx) + int(self.r) * math.sin(startangle)
            y1 = int(self.cy) - int(self.r) * math.cos(startangle)
            x2 = int(self.cx) + int(self.r) * math.sin(endagle)
            y2 = int(self.cx) - int(self.r) * math.cos(endagle)

            # 这个标记表示角度大于半圆
            # 此标记在绘制svg弧形组件的时候需要
            big = 0
            if endagle - startangle > math.pi:
                big = 1
            data = part[self.DATA_KEY]
            label = part[self.LABEL_KEY]
            color = part[self.COLOR_KEY]

            # 使用<svg:path>元素来描述楔
            svg_path = self.draw_svg_path(label)

            # 下面的字符串包含路径的详细信息
            # 设置<svg:path>元素的属性
            svg_path.M(self.cx, self.cy).L(x1, y1).A(
                x2, y2, self.r, self.r, big, "0", "1").Z().set_d_attr()
            svg_path.set_attr("fill", color)  # 设置楔的颜色
            svg_path.set_attr("stroke", "black")  # 楔的外边框为黑色
            svg_path.set_attr("stroke-width", "0.7")  # 两个单位宽
            if self.PIE_CHART_CSS_CLASS_KEY in part:
                svg_path.add_css_class(part[self.PIE_CHART_CSS_CLASS_KEY])

            # 当前楔的结束就是下一个楔的开始
            startangle = endagle

            # 现在绘制一些相应的小方块来表示图例
            icon_width = 10
            icon = self.draw_svg_rect(label)
            icon.set_attr("x", self.lx)  # 定位小方块
            icon.set_attr("y", str(int(self.ly) + 30 * i))
            icon.set_attr("width", icon_width)  # 设置小方块的大小
            icon.set_attr("height", "7")
            icon.set_attr("fill", color)  # 填充小方块的颜色和对应的楔的颜色相同
            icon.set_attr("stroke", "black")  # 子外边框颜色也相同
            icon.set_attr("stroke-width", "0.7")
            if self.LEGEND_CSS_CLASS_KEY in part:
                icon.add_css_class(part[self.LEGEND_CSS_CLASS_KEY])

            # 在小方块的右边添加标签
            icon_text = self.draw_svg_text(
                label, self.attach_suffix(label, self.percent(data, total)))
            icon_text.set_attr("x", str(int(self.lx) + icon_width + 10))  # 定位标签文本
            icon_text.set_attr("y", str(int(self.ly) + 30 * i + 9))  # 文本样式属性还可以通过CSS来设置
            icon_text.set_attr("fill", color)
            icon_text.set_attr("font-size", "16")
            icon_text.set_attr("font-family", "sans-serif")
            if self.LEGEND_TEXT_CSS_CLASS_KEY in part:
                icon_text.add_css_class(part[self.LEGEND_TEXT_CSS_CLASS_KEY])


if __name__ == "__main__":

    html = """<!DOCTYPE html><html><head><title>表格属性</title><meta charset="utf-8" /></head><body>{}</body></html>"""
    width = 500
    height = 260
    cx = 100
    cy = 100
    r = 100
    parts = [
        PieChart.build_part(0, "失败", "red", pie_chart_css_class="fail",
                            legend_css_class="fail-legend", legend_text_css_class="fail-legend-text"),
        PieChart.build_part(27, "成功", "green", pie_chart_css_class="success",
                            legend_css_class="success-legend", legend_text_css_class="success-legend-text"),
        PieChart.build_part(0, "阻塞", "sandybrown", pie_chart_css_class="block",
                            legend_css_class="block-legend", legend_text_css_class="block-legend-text"),
        PieChart.build_part(0, "异常", "antiquewhite", pie_chart_css_class="error",
                            legend_css_class="error-legend", legend_text_css_class="error-legend-text")
    ]
    pie = PieChart(parts, width, height, cx, cy, r)
    with open(r"D:\tmsuitest\sp.html", "w", encoding="utf-8") as f:
        f.write(html.format(pie.to_html()))
