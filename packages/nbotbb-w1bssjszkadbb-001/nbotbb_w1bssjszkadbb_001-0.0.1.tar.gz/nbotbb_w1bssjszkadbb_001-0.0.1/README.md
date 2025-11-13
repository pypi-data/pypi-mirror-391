# NBotbb MCP Server
一个基于 Model Context Protocol（MCP）的上下文服务器，提供农资商品查询与收货地址提取能力。该服务器使大语言模型（LLM）能够理解用户关于农药、化肥等农资产品的自然语言查询（包括有效成分、品牌、规格等），并从本地数据库实时检索库存信息；同时可从任意消息中精准解析结构化收货地址，并内置对文本、图片、语音等多模态输入的透明支持。

🔗 [Model Context Protocol 官网](https://modelcontextprotocol.io/)

---

## 🧰 核心能力（MCP Tools）

### 1. `agro_product_search`：农资商品查询与推荐   
从用户输入中自动识别农药/化肥产品信息，并查询本地库存。
- **适用场景**：用户询问“有没有草甘膦？”、“滨农金特200ml有货吗？”
- **识别字段**：
  - 产品名称（如“烯草酮”）
  - 有效成分（如“烟嘧磺隆+莠去津”）
  - 品牌（如“滨农”、“先正达”）
  - 规格（如“200毫升”、“1公斤”）
  - 用途（如“玉米田除草”、“水稻防虫”）
- **数据源**：本地 SQLite 数据库 products.db
- **支持偏好**：
  - 价格最低（`cheapest`）
  - 生产日期最新（`recent`）
  - 折扣优先（`discount`）
- **输出**：结构化商品列表（含价格、库存、生产日期、折扣信息）

---
### 2. `agro_product_recommend`：智能农资推荐  
基于作物类型、病虫害、地区气候等上下文，推荐最合适的农资产品组合。

- **适用场景**：用户说“山东小麦得了锈病怎么办？”、“南方水稻防虫用什么药？”
- **输入解析**：
  - 作物（如“小麦”、“水稻”）
  - 病害/虫害（如“锈病”、“稻飞虱”）
  - 地区（如“山东”、“华南”）
  - 生长期（可选）
- **推荐逻辑**：
  - 匹配农业知识库 + 当地用药习惯
  - 排除禁用/高毒产品（符合国家法规）
  - 优先推荐低毒、高效、登记作物匹配的产品
- **输出**：
  - 推荐商品列表（含使用剂量、安全间隔期）
  - 简明使用建议（如“亩用30ml，兑水30kg喷雾”）

> 💡 此工具可与 `agro_product_search` 联动：先推荐，再查库存。

---

### 3. `extract_delivery_address`：收货地址智能提取
从任意用户消息中(文本/图片/语音)精准解析完整收货信息。
- **适用场景**：用户发消息“李四 13912345678 上海浦东陆家嘴环路1000号”
- **识别字段**：
  - 姓名、手机号
  - 省、市、区（自动补全层级，如“浦东” → “上海市 浦东新区”）
  - 详细地址、邮编（可选）
- **智能清洗**：
  - 去重（如“北京市 北京市” → “北京市”）
  - 纠错（如“浦東” → “浦东”）
  - 标准化（统一“路/街/巷”格式）
- **输出**：标准化 JSON 地址对象，供下单或确认使用

---

💡 多模态输入（文本/图片/语音）由服务器内部统一处理，LLM 无需额外调用 OCR 或 ASR 工具。
图片 → 调用 Qwen-VL 识别农药包装
语音 → 调用通义千问 ASR 转写为文本
所有输入最终转化为结构化上下文，供上述两个工具使用

## 编译
```bash
conda create env -n uvx python=3.10 -y
conda activate uvx
pip install build twine
cd ~/autodl-tmp/servers/src/nbotbb/
python -m build .
twine upload dist/*
pypi-AgEIcHlwaS5vcmcCJGEwNjVkOTA4LTBlODAtNDViZC1hOTI4LWI4ZWJhMTZhYmEyYwACKlszLCI4NWJmOWE2My0wNDdkLTQ0MjItODAzNS1iZTRlMjUxN2VhNTciXQAABiBdbXlpoANY0MFUeL2BaG6jI6-UfoLiWMfODOpdyUXTMA
```

## 🚀 百炼部署
- 使用 uvx

```bash
# 安装当前项目（可编辑模式）
pip install -e .

# 测试命令是否可用
mcp-server-nbotbb --local-name "测试"
pip install -i http://mirrors.aliyun.com/pypi/simple/ mcp-server-nbotbb==0.0.1
```

```json
{
  "mcpServers": {
    "NBotbb": {
    "command": "uvx",
    "args": ["mcp-server-nbotbb"]
    }
  }
}
```

## 🌐 多模态输入自动处理（透明化）
| 输入类型 | 处理方式 |
|---------|----------|
| 文本 | 纯文本输入，无需处理 |
| 图片 | 调用 Qwen-VL 识别包装，返回结构化结果 |
| 语音 | 调用通义千问 ASR 转写为文本，返回结构化结果 |
最终，所有工具接收的都是**干净的结构化文本上下文**。

---


# 🛠️ MCP 工具定义（供 LLM 调用）
- agro_product_search
```json
{
  "name": "agro_product_search",
  "description": "根据用户描述查询农资商品库存、价格与规格",
  "parameters": {
    "type": "object",
    "properties": {
      "query_text": { "type": "string", "description": "用户原始输入（已含多模态解析结果）" },
      "preferences": {
        "type": "object",
        "properties": {
          "price_preference": { "enum": ["cheapest", "default"] },
          "date_preference": { "enum": ["recent", "default"] }
        }
      }
    }
  }
}
```
- extract_delivery_address
```json
{
  "name": "extract_delivery_address",
  "description": "从用户消息中提取并标准化收货地址信息",
  "parameters": {
    "type": "object",
    "properties": {
      "message": { "type": "string", "description": "用户原始消息（已转为文本）" }
    },
    "required": ["message"]
  }
}
```

# 💬 示例对话

```bash
用户：
有滨农金特200毫升的烯草酮吗？想要最近生产日期的。

AI 调用 agro_product_search 后回复：
老板，为您查询到
🔍 关键词: 烯草酮
🛒 烯草酮 200ml
🏪 店铺：劲牛农资旗舰店
💰 规格和价格：
• 200ml：¥35.00 (🟢 有货:12) 生产日期：2025-10-01 折扣活动：无
`

用户：
李四，手机号13912345678，地址：上海市浦东新区陆家嘴环路1000号

AI 调用 extract_delivery_address 后回复：
📦 已为您提取地址信息：
👤 姓名：李四
📞 手机：13912345678
📍 地址：上海市 浦东新区
🏠 详细：陆家嘴环路1000号

请确认地址信息是否正确？
```
🐞 调试

使用 MCP Inspector 实时查看工具调用：

bash
npx @modelcontextprotocol/inspector uvx jinniu-mcp-server

📦 项目结构
```bash
nbotbb/
├── src/
│   └── nbotbb_mcp_server/
│       ├── __init__.py          # main() 入口
│       ├── __main__.py          # 支持 python -m
│       ├── server.py            # MCP Server 初始化
│       └── tools/
│           ├── product_search.py     # agro_product_search
│           ├── product_recommend.py  # agro_product_recommend
│           └── address_extract.py    # extract_delivery_address
├── products.db                  # 农资商品数据库（需自行准备）
├── .env                         # DASHSCOPE_API_KEY 等
├── pyproject.toml
├── Dockerfile
└── README.md
```

