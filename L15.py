import json
from langchain_openai import ChatOpenAI
# 从langchain_experimental.agents中导入用于构建Pandas Agent的类
from langchain_experimental.agents import create_pandas_dataframe_agent
# 导入pandas模块，将其命名为pd
import pandas as pd
# 导入 zmail 库
import zmail

'''Part1 - 构建数据分析Agent'''

# Agent 输出提示词
PROMPT_TEMPLATE = '''
你扮演“数据分析助理”。仅可对已注入的 Pandas DataFrame `df` 进行只读分析与绘图：
- 严禁修改 `df` 原始数据；如需派生请使用副本（例如 `tmp = df.copy()`）。

- 任何图表必须使用 matplotlib 并保存到本地目录 `artifacts/`。
- 制作图表时，需要强制从 `chartFont/yahei_consola.ttf` 目录中加载yahei_consola字体。
- 除了源数据的字段名、数据内容外，所有描述内容均使用中文作答。
- 最终仅返回**一个合法 JSON**，不可有额外文本或符号。


【统一返回 JSON 结构】
{
  "type": "answer" | "table" | "chart" | "error",
  "input": <简述用户的需求>,
  "data": <根据 type 的载荷>,
  "chart_paths": ["artifacts/<file>.png"],       // 若无图表可为空数组,若目录不存在则创建该目录
  "export_paths": ["outputTable/<file>.csv"],      // 表格/数据片段导出,若目录不存在则创建该目录
}

【各 type 的 data 结构】
- type="answer":
  "data": {"answer": "<先写1行小标题总结，再给要点式答案；包含关键口径/数值>"} 

- type="table":
  "data": {
    "columns": ["<严格使用真实列名或映射后的列名>", "..."],
    "rows": [
      ["<与 columns 对齐的值>", ...],
      ...
    ],
    "sort": {"by": "<列名>", "order": "asc|desc"}
  }
  规则：
  * 最多返回 100 行；超过时按与问题最相关的排序截断，并在 warnings 说明“已截断为100行”。
  * 将生成的表格导出到"export_paths"中的目录中

- type="chart":
  "data": {
    "chart_type": "line|bar|scatter|box|hist",
    "summary": "<生成数据分析报告，以及对可视化图的中文解读，不能包含占位符>"
  }
  说明：
  * 绘图时加载中文字体（chartFont/yahei_consola.ttf）。
  * 图片导出并保存在目录`artifacts/`中。
  * 导出统一规范：dpi=144，bbox_inches="tight"。
  * summary 中不能出现占位符。

- type="error":
  "data": {
    "message": "<错误原因：缺失字段/筛选不合法/无数据/不确定等>",
    "missing_columns": ["<列名>", "..."],
    "invalid_filters": {"列名": "提供的值"},
    "suggestions": ["<如何改写查询/替代列/放宽筛选>", "..."]
  }

【图表自动选择（当用户未指定）】
- 有时间字段 + 序列 → "line"
- 类别字段 + 聚合值 → "bar"
- 两个连续数值字段 → "scatter"
- 其余无法判断 → 返回 type="error"，说明原因并给出建议

【JSON 规范】
- 仅双引号；不得出现 NaN/Infinity（请转为 null 或实际数值）
- 所有列名必须存在于 df（若使用映射，请先在说明中给出映射关系）
- 仅返回一个 JSON；不要附加解释性文字'''


def data_analyze_agent(csv_path, user_query):
    '''1.初始化模型'''
    model = ChatOpenAI(
        api_key='mock-key-123',
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        response_format={'type': 'json_object'}
    )

    '''2.数据准备阶段'''

    # 存储所有df数据
    df = pd.read_csv(csv_path)


    '''3.创建支持使用Pandas的Agent工具'''
    # 创建包含数据分析工具的客户端：
    agent = create_pandas_dataframe_agent(
        # 指定用于生成回答的聊天模型
        llm=model,
        # 指定需要操作的df文档
        df=df,
        # 直接使用pandas工具，不做其他思考
        agent_type="tool-calling",
        # 容许 AI 编写敏感代码
        allow_dangerous_code=True,
    )

    '''4.使用Agent解决数分问题'''
    # 调用Agent的invoke：约定输入键为 "input"
    raw = agent.invoke({"input": PROMPT_TEMPLATE + user_query})

    '''5.将答案内容转换为JSON字典'''
    answer = json.loads(raw.get('output', {}))
    return answer


analysis_log = []

csv_path = 'data/lesson_data.csv'
user_query = "给出全月规模与转化概况，按月汇总 PV/UV/Trial/Add/Pay/Refunds，生成并导出核心漏斗图表与转换率标注。"
answer = data_analyze_agent(csv_path, user_query)
analysis_log.append(answer)

user_query = "分析自然/广告/社媒贡献度与效率？给出 自然流量pv_organic/广告流量pv_ads/社媒流量pv_social 的总计与占比，生成并导出堆叠柱形或玫瑰图。"
answer = data_analyze_agent(csv_path, user_query)
analysis_log.append(answer)

user_query = "英语/IT/AI/通识哪类更强？按 category 聚合 ，计算完课率：sum(completions)/sum(starts)，生成并导出分组柱形图"
answer = data_analyze_agent(csv_path, user_query)
analysis_log.append(answer)

'''Part2 - 生成数据分析报告'''

# 从 langchain.prompts 模块中导入 ChatPromptTemplate，用于构造提示词模板
from langchain.prompts import ChatPromptTemplate

# 初始化一个新的 ChatOpenAI 实例，配置调用参数
llm = ChatOpenAI(
    api_key="mock-key-123",
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    # 指定返回结果的格式为 JSON 对象
    response_format={'type': 'json_object'},
)

# 定义一个长字符串作为 system 提示，说明模型的角色和任务
prompt = """
你是一名资深数据分析报告专家。你的任务是：  
根据用户传入的 **json 列表**（每个元素包含数据分析结果），将信息汇总并撰写成一份 **结构化报告**。  

【输入说明】  
- 输入是一个由多个 json 组成的列表；  
- 每个 json 至少包含：  
  - type：数据类型（例如 chart、table）  
  - input：用户任务描述  
  - data：包含 summary、指标、分析结论等  
  - chart_paths：图表文件路径（可选）  
  - export_paths：导出的数据表路径（可选）  

【输出要求】  
输出必须是一个 JSON 对象，严格符合以下结构：  
{{
    "subject": "<报告的总标题>",  
    "content_html": "<报告的完整HTML内容>", 
    "attachments": ["<附件地址1>", "<附件地址2>", ...]
}}

【content_html 生成规则】  
必须严格按照以下 HTML 层次生成：  

<h1> [总标题] </h1>

<h2> [小标题] </h2>  
<p> [内容概括，来自该 json 的 summary] </p>  

<h3>数据标题1</h3>  
<table>
  <tbody>
    [逐行列出核心指标及其数值]
  </tbody>
</table>  

<h3>数据标题2</h3>  
<table>
  <tbody>
    [逐行列出核心指标及其数值]
  </tbody>
</table>  

<h3>分析结论</h3>  
<p>[简明总结趋势、问题与亮点]</p>  

<h3>附件</h3>  
<p>[列出该 json 对应的 chart_paths 和 export_paths]</p>  

【参考示例】  
输入 json：  
{{
 "type": "chart",
 "input": "给出全月规模与转化概况，按月汇总 PV/UV/Trial/Add/Pay/Refunds，生成并导出核心漏斗图表与转换率标注",
 "data": {{
   "chart_type": "bar",
   "summary": "2024年6月核心转化漏斗显示，总页面浏览量（PV）为359,167，独立访客（UV）为237,082..."
 }},
 "chart_paths": ["artifacts/funnel_chart.png"],
 "export_paths": ["outputTable/monthly_funnel_data.csv"]
}}  

输出示例（content_html）：  
<h1>2024年6月数据分析报告</h1>  

<h2>核心转化漏斗分析</h2>  
<p>2024年6月平台总PV为359,167，UV为237,082，用户在试用、加购、购买及退款环节逐级递减。</p>  

<h3>核心数据</h3>  
<table>
  <tbody>
    <tr><th>试用用户数</th><td>103784</td></tr>
    <tr><th>加购用户数</th><td>25589</td></tr>
    <tr><th>购买用户数</th><td>12535</td></tr>
    <tr><th>退款用户数</th><td>381</td></tr>
  </tbody>
</table>  

<h3>转化率表现</h3>  
<table>
  <tbody>
    <tr><th>UV/PV</th><td>65.98%</td></tr>
    <tr><th>试用/UV</th><td>43.77%</td></tr>
    <tr><th>加购/试用</th><td>24.66%</td></tr>
    <tr><th>购买/加购</th><td>48.99%</td></tr>
    <tr><th>退款/购买</th><td>3.04%</td></tr>
  </tbody>
</table>  

<h3>分析结论</h3>  
<p>整体转化链路表现良好，加购到购买环节效率较高，退款率较低，表明转化质量较佳。</p>  

<h3>附件</h3>  
<p>artifacts/funnel_chart.png，outputTable/monthly_funnel_data.csv</p>  

【注意事项】  
- 每个 json 对应一个 <h2> 小节；  
- 所有表格必须使用 <table> 标签；  
- 内容要专业、简洁、结构清晰；  
- 输出的 JSON 必须严格符合规定的键名和层次。  
"""

# 构建一个 ChatPromptTemplate 对象
# from_messages 表示对话的多角色提示：
#   system 用于定义整体任务角色
#   user   用于提供输入数据和具体任务
report_prompt = ChatPromptTemplate.from_messages([
    # 系统消息，传入上面定义的 prompt
    ("system", prompt),
    # 用户消息，插入变量 {json_list}
    ("user", "输入的 json 列表如下：{json_list}请生成报告。")
])

# 调用模型生成结果
# 使用 report_prompt.invoke({"json_list":analysis_log}) 将用户输入的数据填充到提示模板中
pmt = report_prompt.invoke({"json_list":analysis_log})

# llm.invoke 执行调用，返回模型生成的结果
ret = llm.invoke(pmt)
# 将模型返回的内容（字符串形式）转为 Python 字典对象，便于后续操作
data = json.loads(ret.content)


'''Part3 - 将报告发送到指定邮箱'''


# 创建一个邮件服务器对象，传入邮箱账号和授权码（不是邮箱登录密码）
server = zmail.server('youremail@yequ.com', 'security_code')

# 调用 send_mail 方法发送邮件:
# 收件人邮箱为：'dest@yequ.com'
# 邮件为 AI 生成的数据 data
server.send_mail('dest@yequ.com', data)