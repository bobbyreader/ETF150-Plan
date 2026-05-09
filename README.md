# ETF150

基于“长赢 150 计划”规则的 ETF 投资决策辅助工具，支持 CLI 与 Streamlit 界面，并可在 mock / AkShare 两种数据源间切换。

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## CLI 示例

### 使用 mock 数据

```bash
etf150 valuation --provider mock --index hs300
etf150 signal --provider mock --index hs300 --category broad
etf150 panel --provider mock
etf150 allocation --provider mock --output allocation.png
etf150 sip --provider mock --units 2
etf150 backtest --provider mock --index hs300 --years 3
etf150 entry-backtest --provider mock --index hs300 --holding-days 252
etf150 iopv --provider mock --symbol 510300
```

### 使用 AkShare 真实数据

```bash
etf150 valuation --provider akshare --index hs300
etf150 signal --provider akshare --index hs300 --category broad
etf150 panel --provider akshare
etf150 backtest --provider akshare --index hs300 --years 3
etf150 entry-backtest --provider akshare --index hs300 --holding-days 252 --history-years 10
etf150 iopv --provider akshare --symbol 510300
```

## 启动 Streamlit

```bash
streamlit run src/etf150/streamlit_app.py
```

## 运行测试

```bash
pytest
```

## 一键验证

```bash
scripts/verify.sh
```

该脚本会运行完整测试套件，并 smoke test CLI help、mock 多市场面板和估值起点回测。

## 当前能力边界

- CLI 与 Streamlit 共享 `src/etf150/services/app.py` 业务层。
- mock provider 适合离线演示与单元测试。
- AkShare provider 当前优先支持 A 股核心指数的真实估值、回测、估值起点回测与 IOPV。
- A 股指数估值优先使用指数成分股与全 A 股 TTM PE 明细合并后做等权计算，并剔除负 PE 与 PE > 150 样本。
- 多市场面板已接入 AkShare 真实历史行情；A 股为估值分位，港股、美股、德国、黄金、原油为价格分位代理，界面与数据 note 会明确标注。
- AkShare 数据会缓存在 `.cache/etf150/akshare/`；接口短暂失败时优先使用本地缓存，无缓存或返回空数据才报错。
- `entry-backtest` 会把历史估值起点分为低估、正常、高估三组，对比固定持有天数后的收益表现。

## 说明

- 指数估值历史优先基于 AkShare 乐咕乐股接口。
- 成分股严格等权 PE 优先基于 AkShare `stock_a_ttm_lyr` 与中证指数成分股列表合并；若成分股 PE 明细完全缺失，会退回指数等权 PE 代理并在有效样本数上体现。
- 回测首版优先使用可稳定获取的指数历史序列。
- Streamlit 界面用于可视化现有策略结果，不额外复制业务逻辑。

## 数据口径

| 模块 | AkShare 数据口径 | 说明 |
| --- | --- | --- |
| A 股估值 | 乐咕乐股指数 PE/PB + 成分股 TTM PE | 当前估值使用严格等权样本；历史分位使用乐咕等权 PE 序列 |
| 多市场面板 | A 股估值分位；其他市场历史价格分位 | 非 A 股暂作为跨市场温度计，不等同 PE/PB 估值 |
| IOPV | 东方财富 ETF 实时行情 | 现价高于 IOPV 时输出等待提示 |
| 普通回测 | 指数或 ETF 历史收盘价 | 买入持有收益、年化收益、最大回撤 |
| 估值起点回测 | 历史价格 + 历史等权 PE | 比较低估/正常/高估起点的固定持有期收益 |

## 缓存与容错

- 缓存目录：`.cache/etf150/akshare/`。
- 缓存对象：AkShare 返回的 DataFrame，包括指数估值、指数行情、ETF 行情、成分股 PE 和多市场行情。
- 容错策略：优先请求实时接口；成功后刷新缓存；失败时读取旧缓存；无缓存时抛出明确错误。
- 设计原则：不会静默切换到 mock 数据，避免把演示数据误当真实行情。
