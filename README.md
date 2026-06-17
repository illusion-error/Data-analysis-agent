# Data Analysis Agent

这是一个基于 LangChain Pandas Agent 的自然语言数据分析项目。用户可以用中文提出数据分析需求，Agent 会读取 CSV 数据，调用大模型生成 Pandas 分析逻辑，并按要求输出 JSON、导出图表、导出表格，最后汇总为 HTML 数据分析报告并发送邮件。

## 项目功能

- 支持自然语言提问，自动分析 CSV 数据。
- 使用 LangChain 的 Pandas DataFrame Agent 操作数据表。
- 使用 DeepSeek Chat 的 OpenAI 兼容接口调用大模型。
- 支持自动生成数据分析结论。
- 支持自动生成图表并保存到 `artifacts/`。
- 支持导出表格结果到 `outputTable/`。
- 支持将多轮分析结果汇总为 HTML 报告。
- 支持使用 `zmail` 将分析报告发送到指定邮箱。

## 项目结构

```text
Data analysis agent/
├── L15.py                         # 项目主程序
├── requirements.txt               # Python 依赖
├── README.md                      # 项目说明
├── chartFont/
│   └── yahei_consola.ttf          # 中文图表字体
├── data/
│   ├── lesson_data.csv            # 课程运营分析示例数据
│   └── 销售数据.csv                # 销售订单分析示例数据
├── artifacts/                     # 图表输出目录
└── outputTable/                   # 表格输出目录
```

## 技术栈

- Python
- Pandas
- Matplotlib
- LangChain
- LangChain OpenAI
- LangChain Experimental
- DeepSeek Chat API
- zmail

## 示例数据说明

### 1. `data/lesson_data.csv`

课程运营数据，字段包括：

- 日期、课程 ID、课程名称、课程分类、课程等级
- PV、UV、自然流量、广告流量、社交流量
- 试用、加购、购买、退款
- 学习次数、活跃学习人数、开课数、完课数
- 平均观看时长、测验分数、NPS
- 订阅收入、企业收入等

适合分析：

- 课程转化漏斗
- 流量来源贡献
- 课程分类表现
- 完课率和学习质量
- 收入结构和用户增长

### 2. `data/销售数据.csv`

销售订单数据，字段包括：

- 订单日期、订单编号、大区、销售员
- 产品编码、品类、单价、数量、折扣
- 折后收入、成本、利润
- 客户细分、支付方式、渠道

适合分析：

- 销售额和利润
- 区域销售表现
- 产品品类贡献
- 销售员业绩
- 渠道和客户细分表现

## 运行方式

1. 克隆仓库

```bash
git clone https://github.com/illusion-error/Data-analysis-agent.git
cd Data-analysis-agent
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置大模型 API Key

当前 `L15.py` 中使用的是 DeepSeek OpenAI 兼容接口：

```python
model = "deepseek-chat"
base_url = "https://api.deepseek.com"
```

运行前需要把代码中的占位符替换为自己的 API Key：

```python
api_key="mock-key-123"
```

建议后续改成环境变量，例如：

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

4. 配置邮箱

当前代码中的邮箱信息是占位符：

```python
server = zmail.server('youremail@yequ.com', 'security_code')
server.send_mail('dest@yequ.com', data)
```

运行前需要替换为自己的发件邮箱、授权码和收件邮箱。

5. 运行项目

```bash
python L15.py
```

运行后，程序会：

1. 读取 `data/lesson_data.csv`。
2. 执行多条数据分析任务。
3. 将每次分析结果保存到 `analysis_log`。
4. 调用大模型生成 HTML 数据分析报告。
5. 通过邮箱发送报告。

## 当前内置分析任务

`L15.py` 中目前内置了 3 个课程运营分析问题：

1. 统计全月 PV、UV、试用、加购、购买、退款，并生成核心漏斗图。
2. 分析自然流量、广告流量、社交流量的贡献度与占比。
3. 按课程分类计算完课率，并生成分组柱形图。

## 输出结果

程序要求 Agent 按统一 JSON 格式返回：

```json
{
  "type": "answer | table | chart | error",
  "input": "用户分析需求",
  "data": {},
  "chart_paths": ["artifacts/example.png"],
  "export_paths": ["outputTable/example.csv"]
}
```

图表会保存到：

```text
artifacts/
```

表格会保存到：

```text
outputTable/
```

## 注意事项

- 当前项目允许 Pandas Agent 执行代码：`allow_dangerous_code=True`，只建议在本地可信环境运行。
- 不要把真实 API Key、邮箱授权码提交到 GitHub。
- 当前主程序是脚本式 Demo，运行后会直接执行内置分析任务。
- 若图表中文乱码，请确认 `chartFont/yahei_consola.ttf` 文件存在。
- 若邮件发送失败，请检查邮箱 SMTP 授权码、收件人地址和网络环境。

## 后续优化方向

- 将 API Key 和邮箱配置改为 `.env` 环境变量。
- 增加 Streamlit 或 Vue 前端，让用户上传 CSV 并输入分析问题。
- 支持多文件、多数据表分析。
- 增加异常处理，避免模型输出非 JSON 时程序中断。
- 增加图表预览页面和报告下载功能。
- 增加分析历史记录，保存每次问题、结果、图表和报告。
- 将 `allow_dangerous_code` 改造成更安全的沙盒执行机制。

## 适合展示的能力

- 自然语言驱动的数据分析 Agent。
- Pandas 数据处理与可视化。
- 大模型 JSON 结构化输出控制。
- 自动化数据分析报告生成。
- 邮件自动发送分析结果。
