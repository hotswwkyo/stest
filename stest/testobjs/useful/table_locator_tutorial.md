# Table 类使用教程

## 1. 概述

`Table` 是基于 Playwright 的表格通用定位器，采用**"由列定表"**的设计理念：只需提供关心的列标题或列索引，Table 即可自动生成复杂的 XPath，在页面中精准定位到包含这些列的目标表格，并提供对行、单元格的快速查找与数据提取能力。

**核心能力：**

- **结构化定位**：按列标题、列索引或混合字典配置表格结构，自动生成高精度 XPath
- **智能检测与修复**：通过 `sync_from_dom` 方法根据 DOM 检测结果同步或重建内部列配置
- **多级表头支持**：自动解析 `colspan`/`rowspan`，将多行表头合并为扁平化的列标题
- **便捷数据提取**：提供 `row()`、`cells()`、`cell()` 等链式 API

---

## 2. 快速开始

### 假设页面表格结构

```html
<div class="el-table__header-wrapper">
    <table>
        <thead>
            <tr>
                <th><div class="cell">序号</div></th>
                <th><div class="cell">专资编码</div></th>
                <th><div class="cell">影城名称</div></th>
                <th><div class="cell">营业状态</div></th>
                <th><div class="cell">操作</div></th>
            </tr>
        </thead>
    </table>
</div>
<div class="el-table__body-wrapper">
    <table>
        <tbody>
            <tr class="el-table__row">
                <td><div class="cell">1</div></td>
                <td><div class="cell">80002048</div></td>
                <td><div class="cell">影院名称-80002048</div></td>
                <td><div class="cell">开业</div></td>
                <td><div class="cell"><button>编辑</button></div></td>
            </tr>
            <tr class="el-table__row">
                <td><div class="cell">2</div></td>
                <td><div class="cell">80002105</div></td>
                <td><div class="cell">影院名称-80002105</div></td>
                <td><div class="cell">停业</div></td>
                <td><div class="cell"><button>编辑</button></div></td>
            </tr>
        </tbody>
    </table>
</div>
```

### 最简用法

```python
from stest.testobjs.useful.table_locator import Table

# 1. 创建 Table 实例 —— 传入列标题，按顺序匹配
table = Table(page, '序号', '专资编码', '影城名称', '营业状态', '操作')

# 2. 根据内容查找行
row_el = table.row({"专资编码": "80002048"}, el_type="row")

# 3. 提取行数据
data = table.cells(row_el)
# => {'序号': '1', '专资编码': '80002048', '影城名称': '影院名称-80002048', '营业状态': '开业', '操作': '编辑'}
```

---

## 3. 初始化配置详解

`Table` 的 `__init__` 方法支持多种 `config` 类型，**同一批次必须使用相同类型，不能混用**。

### 3.1 字符串配置（列标题）

最常用方式，传入列标题名称。

```python
# auto_set_position=True（默认）：标题顺序必须与表格实际列顺序一致
table = Table(page, '序号', '专资编码', '影城名称', '营业状态')

# auto_set_position=False：不关心列顺序，只要表格包含这些标题即可定位
table = Table(page, '专资编码', '营业状态', auto_set_position=False)
```

> **关键点**：`auto_set_position=True` 时，传入的标题顺序必须与 DOM 中的列顺序完全一致，否则定位会出错。如果只关心"表格是否包含这些列"而不关心顺序，使用 `auto_set_position=False`。

### 3.2 整数配置（列索引）

仅通过列索引（从1开始）定位，不依赖标题文本。适用于表头动态生成或无明确标题的表格。

```python
# 定位包含第2列和第5列的表格
table = Table(page, 2, 5, auto_set_position=False)

# 定位一个有9列的表格
table = Table(page, *list(range(1, 10)), auto_set_position=False)
```

### 3.3 字典配置（精细控制）

每个列使用字典描述，支持 `index`、`title`、`value`、`xpath`、`tagname` 等键。

```python
table = Table(page,
    {"index": 1, "title": "序号"},
    {"index": 2, "title": "专资编码"},
    {"index": 3, "title": "影城名称", "xpath": 'div[@class="cell"]'},
    {"index": 5, "title": "营业状态", "value": "开业"},  # value 用于生成 XPath 筛选条件
)
```

> **关键点**：`index` 和 `title` 为必填项。`xpath` 指定单元格内内容元素的相对路径，`value` 指定单元格内容用于 XPath 精确匹配。

### 3.4 列表/元组配置（位置传参）

按位置传参，支持 2~5 个元素：

| 元素个数 | 含义 |
|---------|------|
| 2 | `(索引, 标题)` |
| 3 | `(索引, 标题, 相对xpath)` |
| 4 | `(索引, 标题, 相对xpath, 单元格内容)` |
| 5 | `(索引, 标题, 相对xpath, 单元格内容, 元素标签)` |

```python
table = Table(page,
    (1, '序号'),
    (2, '专资编码'),
    (3, '影城名称', 'div[@class="cell"]'),
    (5, '营业状态', 'div[@class="cell"]', '开业'),
)
```

### 3.5 header_cell_xpath / body_cell_xpath 参数

统一设置所有表头/主体单元格内内容元素的相对 XPath，避免逐列配置。

```python
# Element UI 表格中，单元格内容通常在 <div class="cell"> 内
table = Table(page, '序号', '专资编码', '影城名称',
             header_cell_xpath='div[@class="cell"]',
             body_cell_xpath='div[@class="cell"]')
```

> **关键点**：此参数为全局默认值，优先级低于各列单独配置的 `xpath`。若某列需要不同的内部路径，可通过 `set_body_cell_xpath` 或 `set_head_cell_xpath` 单独覆盖。

---

## 4. 核心概念："由列定表"

`Table` 不直接定位 `<table>` 元素，而是通过**列条件组合**生成高精度 XPath，确保只匹配包含指定列的目标表格。

### 生成的 XPath 结构示例

```python
table = Table(page, '专资编码', '营业状态')
```

生成的 `head_xpath` 大致为：

```
xpath=//div[@id="app"]//div[contains(@class,"el-table__header-wrapper")]/table/thead
       /tr/th[2]/div[normalize-space()="专资编码"]
       /ancestor::tr/th[4]/div[normalize-space()="营业状态"]
       /ancestor::thead
```

**逻辑**：在 `<thead>` 的某行 `<tr>` 中，必须同时存在包含"专资编码"和"营业状态"文本的单元格，才匹配成功。

---

## 5. 关键属性

| 属性 | 说明 |
|------|------|
| `head_columns` | 表头列的 `CellSelector` 列表 |
| `body_columns` | 主体列的 `CellSelector` 列表 |
| `head_xpath` | 最终生成的表头定位 XPath（只读） |
| `body_xpath` | 最终生成的主体定位 XPath（只读） |
| `default_head_xpath` | 表头基准 XPath，可修改以适配不同 DOM 结构 |
| `default_body_xpath` | 相对于 `head_xpath` 的主体 XPath，可修改 |
| `all_rows` | 表格所有行元素的快捷属性，等价于 `row({})` |
| `allow_missing_position` | 是否允许列索引缺失（默认 `False`） |
| `cxpaths_for_rebuild` | 列索引到 cxpath 的映射字典，用于 `sync_from_dom` 重建时保留路径信息 |

---

## 6. 关键方法

### 6.1 row() —— 按内容查找行

```python
# 按列标题筛选，返回整行
row_el = table.row({"专资编码": "80002048"}, el_type="row")

# 按列标题筛选，返回指定列的单元格
cell_el = table.row({"专资编码": "80002048"}, title="营业状态")

# 按列索引筛选
cell_el = table.row({2: "80002048"}, by="position", index=4)

# 无筛选条件，获取所有行
all_rows = table.row({})

# 多条件组合（AND 关系）
row_el = table.row({"专资编码": "80002048", "营业状态": "开业"}, el_type="row")
```

> **关键点**：
> - `by="title"` 时，若存在重复标题，仅匹配第一个出现的列，建议改用 `by="position"`
> - `cells` 字典中的值会直接嵌入 XPath 的 `normalize-space()` 条件，注意特殊字符转义

### 6.2 cells() —— 提取行数据

```python
# 提取文本内容（默认）
data = table.cells(row_el)
# => {'序号': '1', '专资编码': '80002048', '影城名称': '影院名称-80002048', ...}

# 返回 Locator 而非文本
data = table.cells(row_el, return_locator=True)

# 以列索引为键
data = table.cells(row_el, title_as_key=False)
# => {1: '1', 2: '80002048', 3: '影院名称-80002048', ...}
```

> **关键点**：被标记为非数据列的单元格不会返回。

### 6.3 cell() —— 获取单个单元格

```python
# 按列标题
cell_el = table.cell(row_el, "营业状态")

# 按列索引
cell_el = table.cell(row_el, 4, by="position")
```

### 6.4 sibling_cell() —— 获取兄弟单元格

从一个已知的单元格出发，获取同行中其他列的单元格。

```python
# 已知"专资编码"单元格，获取同行的"营业状态"单元格
status_cell = table.sibling_cell(code_cell, "营业状态")

# 按列索引
status_cell = table.sibling_cell(code_cell, 4, by="position")
```

### 6.5 header_cells() —— 获取表头单元格

```python
# 获取第1行中标题为"专资编码"的单元格
cell = table.header_cells(title='专资编码', row=1)

# 获取所有行中标题为"营业状态"的单元格
cells = table.header_cells(title='营业状态')

# 在已定位的行元素中查找
row_el = page.locator('//thead/tr[1]')
cell = table.header_cells(row=row_el)
```

### 6.6 标记非数据列

```python
# 按标题标记
table.mark_non_data_columns_by_titles('操作', '序号')

# 按索引标记
table.mark_non_data_columns_by_position(1, 5)

# 链式调用
table.mark_non_data_columns_by_titles('操作').mark_non_data_columns_by_position(1)
```

> **关键点**：标记后，`cells()` 方法会自动跳过这些列，返回纯净的业务数据字典。

### 6.7 set_body_cell_xpath() / set_head_cell_xpath()

批量设置指定列的单元格内容元素相对 XPath。

```python
# "操作"列的按钮嵌套在特殊 div 中
table.set_body_cell_xpath('div[@class="action-btns"]', '操作')

# 链式调用
table.set_body_cell_xpath('div[@class="action-btns"]', '操作') \
     .set_head_cell_xpath('div[@class="special-header"]', '操作')
```

### 6.8 detect_header_titles() —— 自动检测表头

```python
result = table.detect_header_titles()
# 返回:
# {
#     'headers': [['影院信息', '编码'], ['影院信息', '名称']],  # 合并后的列标题层级
#     'merged_cells': [...],                                   # 合并单元格元信息
#     'header_matrix': [...]                                   # 原始表头矩阵
# }
```

### 6.9 sync_from_dom() —— 同步/重建列配置

当表格列顺序可能变化，或初始化时未提供完整列信息时使用。

```python
table = Table(page, '专资编码', '院线', auto_set_position=False)

# 重建模式：完全根据 DOM 重建 body_columns
table.sync_from_dom(mode="rebuild")

# 同步模式：在现有列基础上更新属性
table.sync_from_dom(mode="sync", by="title")

# 重建时清除非数据列标记
table.sync_from_dom(mode="rebuild", clear_non_data_column_marks=True)
```

> **关键点**：
> - `rebuild` 模式会清空并覆盖现有 `body_columns`
> - `sync` 模式仅更新现有列的属性，不销毁重建
> - 重建前，现有的 `body_columns` 的 `cxpath` 会被自动提取到 `cxpaths_for_rebuild` 中保留

---

## 7. 完整示例

### 示例1：基本表格操作

```python
from stest.testobjs.useful.table_locator import Table

# 创建 Table —— 按顺序传入列标题
table = Table(page, '序号', '专资编码', '影城名称', '院线', '影投', '营业状态', '操作')

# 标记非数据列
table.mark_non_data_columns_by_titles('操作', '序号')

# 查找"专资编码"为 "80002048" 的行
row_el = table.row({"专资编码": "80002048"}, el_type="row")

# 提取该行数据（自动排除非数据列）
data = table.cells(row_el)
# => {'专资编码': '80002048', '影城名称': '影院名称-80002048', '院线': '中影院线', '影投': '无', '营业状态': '开业'}

# 获取该行"营业状态"单元格
status_cell = table.cell(row_el, "营业状态")
print(status_cell.text_content())  # => "开业"

# 遍历所有行
for row in table.all_rows.all():
    row_data = table.cells(row)
    print(row_data)
```

### 示例2：固定列表格（Element UI）

Element UI 的固定列会将表格拆分为多个独立的 `<table>` DOM 节点，需要修改默认 XPath。

```python
from stest.testobjs.useful.table_locator import Table

titles = ['序号', '专资编码', '影城名称', '院线', '影投', '营业状态',
          '终端绑定状态', '终端安装状态', '操作']

# 1. 创建 Table
right_table = Table(page, *titles)

# 2. 覆盖默认 XPath，指向固定列所在的 DOM 节点
right_table.default_head_xpath = (
    '//div[@class="el-table__fixed-right"]'
    '/div[contains(@class,"el-table__fixed-header-wrapper")]'
    '/table/thead'
)
right_table.default_body_xpath = (
    './ancestor::table/parent::div'
    '/following-sibling::div[contains(@class,"el-table__fixed-body-wrapper")]'
    '/table/tbody'
)

# 3. 标记非数据列
right_table.mark_non_data_columns_by_titles('操作')

# 4. 正常使用
row_el = right_table.row({"专资编码": "80002048"}, el_type="row")
data = right_table.cells(row_el)
```

### 示例3：不关心列顺序的定位

```python
# 只需表格包含这些列，不要求顺序一致
table = Table(page, '专资编码', '院线', '营业状态', auto_set_position=False)

# 允许 position 为 None 时继续执行（否则会抛出 ValueError）
table.allow_missing_position = True

# 按标题查找行
row_el = table.row({"专资编码": "80002048"}, el_type="row")
```

### 示例4：处理动态列顺序

```python
table = Table(page, '专资编码', '院线', '营业状态', auto_set_position=False)

# 页面列顺序可能变化，手动触发同步
table.sync_from_dom(mode="rebuild")

# 同步后可精确按索引定位
row_el = table.row({"专资编码": "80002048"}, el_type="row")
```

### 示例5：多级表头

```python
# 假设表格有多行表头：
# | 影院信息       | 终端信息       |
# | 编码 | 名称    | 绑定状态 | 安装状态 |

table = Table(page, '影院信息-编码', '影院信息-名称', '终端信息-绑定状态', '终端信息-安装状态')

# 或使用 detect_header_titles 自动检测
result = table.detect_header_titles()
# headers => [['影院信息', '编码'], ['影院信息', '名称'], ...]

# 自定义分隔符
table = Table(page, '影院信息/编码', '影院信息/名称')
table.multi_level_sep = '/'
```

### 示例6：使用 cxpaths_for_rebuild 保留路径信息

```python
table = Table(page, '专资编码', '影城名称', '营业状态',
              body_cell_xpath='div[@class="cell"]')

# 预设 cxpath，确保 sync_from_dom 重建后路径不丢失
table.cxpaths_for_rebuild[1] = 'div[@class="cell"]'
table.cxpaths_for_rebuild[2] = 'div[@class="cell"]'
table.cxpaths_for_rebuild[3] = 'div[@class="cell"]'

# 触发重建，cxpath 会被自动注入
table.sync_from_dom(mode="rebuild")
```

### 示例7：按列索引操作

```python
# 通过列索引初始化（适用于无标题或动态标题的表格）
table = Table(page, *range(1, 10), auto_set_position=False)

# 按列索引查找行
row_el = table.row({2: "80002048", 6: "开业"}, by="position", el_type="row")

# 按列索引获取单元格
cell_el = table.cell(row_el, 4, by="position")

# 按列索引提取数据
data = table.cells(row_el, title_as_key=False)
# => {1: '1', 2: '80002048', 3: '影院名称-80002048', ...}
```

### 示例8：使用字典配置精细控制

```python
table = Table(page,
    {"index": 1, "title": "序号"},
    {"index": 2, "title": "专资编码"},
    {"index": 3, "title": "影城名称", "xpath": 'div[@class="cell"]'},
    {"index": 4, "title": "营业状态", "xpath": 'div[@class="cell"]'},
    {"index": 5, "title": "操作", "xpath": 'div[@class="action-btns"]//button'},
)

table.mark_non_data_columns_by_titles('序号', '操作')

row_el = table.row({"专资编码": "80002048"}, el_type="row")
data = table.cells(row_el)
# => {'专资编码': '80002048', '影城名称': '影院名称-80002048', '营业状态': '开业'}
```

---

## 8. 关键点总结

### 8.1 auto_set_position 的选择

| 场景 | auto_set_position | 说明 |
|------|:-:|------|
| 列顺序固定且已知 | `True`（默认） | 传入标题顺序必须与 DOM 一致 |
| 只关心列是否存在，不关心顺序 | `False` | 定位更灵活，但后续精确操作需配合 `sync_from_dom` |
| 使用整数/字典/元组配置 | 无影响 | 这些配置已显式指定了索引 |

### 8.2 default_head_xpath 与 default_body_xpath 的调整

- **默认值**针对 Element UI 标准表格设计，指向 `#app` 下的 `el-table__header-wrapper`
- **固定列**场景必须修改，因为固定列将表头拆分到独立的 `<table>` 节点
- **标准 HTML 表格**（thead 与 tbody 在同一个 `<table>` 内）可将 `default_body_xpath` 简化为 `./tbody`

### 8.3 allow_missing_position 的使用

当 `auto_set_position=False` 时，列的 `position` 为 `None`，生成的 XPath 会从 `td[1]` 退化为 `td`，可能导致匹配到多个元素。此时：

- 设置 `allow_missing_position = True` 可避免抛出异常，但定位可能模糊
- 更推荐调用 `sync_from_dom()` 让 Table 自动从 DOM 中检测并填充 `position`

### 8.4 非数据列标记

- `mark_non_data_columns_by_titles()` 和 `mark_non_data_columns_by_position()` 支持链式调用
- 标记仅影响 `cells()` 方法，不影响 `row()`、`cell()` 等方法
- `sync_from_dom(mode="rebuild", clear_non_data_column_marks=True)` 重建时会清除标记

### 8.5 cxpaths_for_rebuild 的作用

`sync_from_dom` 重建 `body_columns` 时，DOM 中的表头单元格不包含 `cxpath` 信息，直接重建会导致路径丢失。`cxpaths_for_rebuild` 充当"记忆层"，确保重建后仍能精确定位到单元格内部元素。

### 8.6 重复标题的处理

当表格存在重复列标题时：

- `by="title"` 仅匹配第一个出现的列，可能导致非预期结果
- 推荐使用 `by="position"` 按列索引匹配
- 可通过 `get_duplicate_title_columns()` 检查是否存在重复标题

### 8.7 XPath 注入风险

`row()` 方法的 `cells` 参数中的值会直接嵌入 XPath 的 `normalize-space()` 条件。若值来源于不可信输入，请确保对引号等特殊字符进行转义。

### 8.8 sibling_cell vs cell

- `cell(row, ...)`：从行元素（`<tr>`）出发查找单元格
- `sibling_cell(cell, ...)`：从单元格元素出发，先回溯到行再定位目标单元格

两者功能类似，区别在于起点不同。`sibling_cell` 适用于已有单元格 Locator 但需要获取同行其他列的场景。
