# -*- coding: utf-8 -*-
'''
Created on 2019年12月5日

@author: siwenwei
'''

from .tags import Tags


class HtmlElement(object):
    def __init__(self, tag, text="", has_end_tag=True, **attributes):

        self._set_tag(tag)
        self._has_end_tag = has_end_tag
        self._attributes = attributes
        self._text = text
        self._child_elements = []
        self._following_sibling_elements = []
        self._preceding_sibling_elements = []

    @property
    def tag(self):
        return self._tag

    def _set_tag(self, tag):

        if tag and isinstance(tag, str):
            self._tag = tag
        else:
            raise TypeError("tag name must be string type")

    @property
    def child_elements(self):
        return self._child_elements

    @property
    def is_empty_element(self):
        """判断是否空元素（即没有结束标签的元素）"""

        return False if self._has_end_tag else True

    def rename_tag(self, tag):

        self._set_tag(tag)
        return self

    @property
    def text(self):

        return self._text

    @text.setter
    def text(self, value):

        self._text = value

    @property
    def attributes(self):

        return self._attributes

    def set_attr(self, name, value):

        self._attributes[name] = value
        return self

    def get_attr(self, name):

        return self._attributes[name]

    def set_attributes(self, **attributes):

        self._attributes.update(attributes)
        return self

    def remove_attributes(self, **attributes):

        for k in attributes.keys():
            if k in self._attributes.keys():
                self._attributes.pop(k)
        return self

    def add_css_class(self, *css_classes):

        vaild_css_classes = []
        for css_cls in css_classes:
            if isinstance(css_cls, str):
                vaild_css_classes.append(css_cls)
        if not vaild_css_classes:
            return self
        attr_name = "class"
        exists_css_classes = self._attributes.get(attr_name, "").strip()
        if exists_css_classes:
            css_class_list = exists_css_classes.split()
        else:
            css_class_list = []
        for css_class in vaild_css_classes:
            if " " not in css_class:
                css_class_list.append(css_class)
        value = " ".join(css_class_list)
        self.set_attr(attr_name, value)
        return self

    def clear_all_attributes(self):

        self._attributes.clear()
        return self

    def _validate_element(self, element):

        if not isinstance(element, HtmlElement):
            raise TypeError("elements is not html element")

    def remove_child_by_tag(self, tag):

        for el in self.get_child_elements_by_tag(tag):
            self._child_elements.remove(el)
        if self.get_child_elements_by_tag(tag):
            self.remove_child_by_tag(tag)
        return self

    def insert_child(self, child_element, index=0):

        self._child_elements.insert(index, child_element)

    def append_child(self, *child_elements):

        for child_element in child_elements:
            self._validate_element(child_element)
            if self.is_empty_element:
                self._following_sibling_elements.append(child_element)
            else:
                self._child_elements.append(child_element)
        return self

    def before(self, *preceding_sibling_elements):

        for element in preceding_sibling_elements:
            self._validate_element(element)
            self._preceding_sibling_elements.append(element)

    def after(self, *following_sibling_elements):

        for element in following_sibling_elements:
            self._validate_element(element)
            self._following_sibling_elements.append(element)

    def _element_to_html_text_list(self, element_list):

        return [el.to_html() for el in element_list]

    def _html_of_child_elements(self):

        return self._element_to_html_text_list(self._child_elements)

    def _attributes_to_text(self):

        if self._attributes:
            sep = " "
        else:
            sep = ""
        return sep.join(['%s="%s"' % (k, v) for k, v in self._attributes.items()])

    def get_child_elements_by_tag(self, tag):

        return [el for el in self._child_elements if el.tag == tag]

    def _build_normal_element(self):

        attrs = self._attributes_to_text()
        text = str(self._text) + "".join(self._html_of_child_elements())
        el_html = "<{tag} {attrs}>{text}</{tag}>".format(tag=self._tag, attrs=attrs, text=text)
        return el_html

    def _build_empty_element(self):
        """创建没有结束标签的元素"""

        attrs = self._attributes_to_text()
        el_html = "<{tag} {attrs} />".format(tag=self._tag, attrs=attrs)
        return el_html

    def to_html(self):

        preceding_siblings = self._element_to_html_text_list(self._preceding_sibling_elements)
        following_siblings = self._element_to_html_text_list(self._following_sibling_elements)

        if not self.is_empty_element:
            itself = self._build_normal_element()
        else:
            itself = self._build_empty_element()
        return "".join(preceding_siblings) + itself + "".join(following_siblings)


class HtmlNormalElement(HtmlElement):
    def __init__(self, tag, text=""):

        super().__init__(tag, text, has_end_tag=True)


class HtmlEmptyElement(HtmlElement):
    def __init__(self, tag):

        super().__init__(tag, "", has_end_tag=False)


class HTML(HtmlNormalElement):

    DOCTYPE = """<!DOCTYPE html>"""

    def __init__(self, text=""):
        super().__init__(Tags.html, text)
        self._allow_element_exclude_head_and_body = False
        self.append_child(Head())
        self.append_child(Body())

    @property
    def allow_add(self):
        return self._allow_element_exclude_head_and_body

    @allow_add.setter
    def allow_add(self, value):

        self._allow_element_exclude_head_and_body = value

    def _has_head(self):

        return True if self.get_child_elements_by_tag(Tags.head) else False

    def _has_body(self):
        return True if self.get_child_elements_by_tag(Tags.body) else False

    def _get_other_child_elements(self, child_elements):

        return [el for el in child_elements if el.tag != Tags.body and el.tag != Tags.head]

    def append_child(self, *child_elements):

        if not self._has_head():
            heads = [el for el in child_elements if el.tag == Tags.head]
            if heads:
                HtmlElement.append_child(self, heads[0])

        if not self._has_body():
            bodys = [el for el in child_elements if el.tag == Tags.body]
            if bodys:
                HtmlElement.append_child(self, bodys[0])

        other_child_elements = self._get_other_child_elements(child_elements)

        if not other_child_elements:
            return self
        if not self._allow_element_exclude_head_and_body:
            message = """"HTML already has head and body elements.
            It is not recommended to add any direct child elements.
            if you need to add, set self.allow_add = True"""
            raise Warning(message)
        return HtmlElement.append_child(self, *other_child_elements)

    @property
    def head(self):
        elements = self.get_child_elements_by_tag(Tags.head)
        return elements[0] if elements else None

    @property
    def body(self):
        elements = self.get_child_elements_by_tag(Tags.body)
        return elements[0] if elements else None


class Head(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.head, text)
        self.append_child(Title())

    @property
    def title(self):
        elements = self.get_child_elements_by_tag(Tags.title)
        return elements[0] if elements else None


class Title(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.title, text)


class Meta(HtmlEmptyElement):
    def __init__(self):
        super().__init__(Tags.meta)


class Style(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.style, text)


class Script(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.script, text)


class Body(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.body, text)


class Table(HtmlNormalElement):
    def __init__(self, text=""):

        super().__init__(Tags.table, text)

    def _is_only_one_thead_and_tbody(self, child_elements):

        thead_count = 0
        tbody_count = 0
        for el in child_elements:

            if thead_count > 1 or tbody_count > 1:
                raise ValueError("Table can only have one thead and one tbody")

            if el.tag == Tags.thead:
                thead_count = thead_count + 1
            elif el.tag == Tags.tbody:
                tbody_count = tbody_count + 1

    def append_child(self, *child_elements):

        self._is_only_one_thead_and_tbody(child_elements)
        return HtmlNormalElement.append_child(self, *child_elements)

    @property
    def thead(self):

        elements = self.get_child_elements_by_tag(Tags.thead)
        return elements[0] if elements else None

    @property
    def tbody(self):

        elements = self.get_child_elements_by_tag(Tags.tbody)
        return elements[0] if elements else None

    @property
    def header_rows(self):

        rows = self.get_child_elements_by_tag(Tags.tr)
        hrows = []
        for row in rows:
            if row.get_child_elements_by_tag(Tags.th):
                hrows.append(row)
        if self.thead:
            hrows.extend(self.thead.rows)
        return hrows

    @property
    def body_rows(self):

        rows = self.get_child_elements_by_tag(Tags.tr)
        brows = []
        for row in rows:
            if row.get_child_elements_by_tag(Tags.td):
                brows.append(row)
        if self.tbody:
            brows.extend(self.tbody.rows)
        return brows

    @property
    def rows(self):

        return self.header_rows + self.body_rows

    @property
    def nrows(self):

        return len(self.header_rows) + len(self.body_rows)

    @property
    def ncols(self):

        ncols_of_rows = [row.ncols for row in self.rows]
        return max(ncols_of_rows) if ncols_of_rows else 0

    def _build_header(self):

        pass

    def _build_body(self):

        pass

    def to_html(self):

        self._build_header()
        self._build_body()
        return HtmlNormalElement.to_html(self)


class Thead(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.thead, text)

    @property
    def rows(self):
        return self.get_child_elements_by_tag(Tags.tr)

    @property
    def nrows(self):
        return len(self.rows)

    @property
    def ncols(self):
        ncols_of_row = [row.ncols for row in self.rows]
        return max(ncols_of_row) if ncols_of_row else 0


class Tbody(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.tbody, text)

    @property
    def rows(self):
        return self.get_child_elements_by_tag(Tags.tr)

    @property
    def nrows(self):
        return len(self.rows)

    @property
    def ncols(self):
        ncols_of_row = [row.ncols for row in self.rows]
        return max(ncols_of_row) if ncols_of_row else 0


class TH(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.th, text)


class TR(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.tr, text)

    @property
    def cols(self):

        return self.get_child_elements_by_tag(Tags.td) or self.get_child_elements_by_tag(Tags.th)

    @property
    def ncols(self):

        return len(self.cols)


class TD(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.td, text)


class Div(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.div, text)


class Span(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.span, text)


class Fieldset(HtmlNormalElement):
    def __init__(self, text=""):
        """

        @param text: 组标题
        """
        super().__init__(Tags.fieldset, "")
        self.append_child(Legend(text))

    @property
    def legend(self):

        return self.get_child_elements_by_tag(Tags.legend)[0]

    @property
    def title(self):
        return self.legend.text

    @title.setter
    def title(self, value):
        self.legend.text = value
        return self

    def append_child(self, *child_elements):

        for el in child_elements:
            if el.tag != Tags.legend:
                HtmlNormalElement.append_child(self, el)
            else:
                if not self.get_child_elements_by_tag(Tags.legend):
                    HtmlNormalElement.append_child(self, el)
        return self


class Legend(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.legend, text)


class Label(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.label, text)


class Pre(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.pre, text)


class P(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.p, text)


class Svg(HtmlNormalElement):
    class Path(HtmlEmptyElement):
        def __init__(self):
            super().__init__(Tags.path)
            self.__commands = []

        @property
        def commands(self):

            return self.__commands

        def M(self, x, y):
            """构建移动到x, y坐标点指令"""

            cmd = "M {x},{y}".format(x=x, y=y)
            self.commands.append(cmd)
            return self

        def L(self, x, y):
            """构建画一条直线到x, y坐标点指令"""

            cmd = "L {x},{y}".format(x=x, y=y)
            self.commands.append(cmd)
            return self

        def A(self, x, y, rx, ry, large_arc_flag, x_axis_rotation="0", sweep_flag="1"):
            """构建弧度指令

            Args:
                x: 弧线终点x坐标
                y: 弧线终点y坐标
                rx: x轴半径
                ry: y轴半径
                large_arc_flag: 角度大小 决定弧线是大于还是小于180度，0表示小角度弧，1表示大角度弧
                x_axis_rotation: 弧形与 x 轴旋转角度
                sweep_flag: 弧线的方向，0表示从起点到终点沿逆时针画弧，1表示从起点到终点沿顺时针画弧
            """

            cmd = "A {rx},{ry}, {x_axis_rotation} {large_arc_flag} {sweep_flag} {x},{y}".format(rx=rx, ry=ry, x_axis_rotation=x_axis_rotation, large_arc_flag=large_arc_flag, sweep_flag=sweep_flag, x=x, y=y)
            self.commands.append(cmd)
            return self

        def Z(self):

            cmd = "Z"
            self.commands.append(cmd)
            return self

        def set_d_attr(self):

            space = " "
            d_cmd = space.join(self.commands)
            self.set_attr("d", d_cmd)
            return d_cmd

    class Circle(HtmlEmptyElement):
        def __init__(self):
            super().__init__(Tags.circle)

    class Rect(HtmlEmptyElement):
        def __init__(self):
            super().__init__(Tags.rect)

    class Text(HtmlNormalElement):
        def __init__(self, text=""):
            super().__init__(Tags.text, text)

    def __init__(self, width="300", height="150"):

        super().__init__(Tags.svg)
        self.set_attributes(width=width, height=height)
        self.__svg_paths = {}
        self.__svg_rects = {}
        self.__svg_texts = {}

    @property
    def svg_paths(self):
        return self.__svg_paths

    @property
    def svg_rects(self):
        return self.__svg_rects

    @property
    def svg_texts(self):
        return self.__svg_texts

    def svg_path_is_exists(self, name):

        return name in self.svg_paths

    def get_svg_path(self, name):
        return self.svg_paths[name]

    def draw_svg_path(self, name):

        svg_path = self.Path()
        self.svg_paths[name] = svg_path
        self.append_child(svg_path)
        return svg_path

    def draw_svg_circle(self, name):
        svg_path = self.Circle()
        self.svg_paths[name] = svg_path
        self.append_child(svg_path)
        return svg_path

    def draw_svg_rect(self, name):

        svg_rect = self.Rect()
        self.svg_rects[name] = svg_rect
        self.append_child(svg_rect)
        return svg_rect

    def draw_svg_text(self, name, text=""):

        svg_text = self.Text(text)
        self.svg_texts[name] = svg_text
        self.append_child(svg_text)
        return svg_text


class DL(HtmlNormalElement):
    def __init__(self):
        super().__init__(Tags.dl)


class DT(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.dt, text=text)


class DD(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.dd, text=text)


class Input(HtmlEmptyElement):
    def __init__(self, itype="text", value=""):
        super().__init__(Tags.input)
        self.set_attr("type", itype)
        self.set_attr("value", value)


class HR(HtmlEmptyElement):
    def __init__(self):
        super().__init__(Tags.hr)


class UL(HtmlNormalElement):
    def __init__(self):
        super().__init__(Tags.ul)


class LI(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.li, text)


class Textarea(HtmlNormalElement):
    def __init__(self, text=""):
        super().__init__(Tags.textarea, text)


class Italic(HtmlNormalElement):
    def __init__(self, *css_classes):
        super().__init__(Tags.italic)
        self.add_css_class(*css_classes)
