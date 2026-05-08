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
etf150 iopv --provider mock --symbol 510300
```

### 使用 AkShare 真实数据

```bash
etf150 valuation --provider akshare --index hs300
etf150 signal --provider akshare --index hs300 --category broad
etf150 panel --provider akshare
etf150 backtest --provider akshare --index hs300 --years 3
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

## 当前能力边界

- CLI 与 Streamlit 共享 `src/etf150/services/app.py` 业务层。
- mock provider 适合离线演示与单元测试。
- AkShare provider 当前优先支持 A 股核心指数的真实估值、回测与 IOPV。
- AkShare 面板里除 A 股外，其余市场仍为实验性占位口径，会在界面中明确标注。
- 若 AkShare 接口缺失、波动或返回空数据，程序会直接报错，不会静默回退到 mock 数据。

## 说明

- 指数估值历史优先基于 AkShare 乐咕乐股接口。
- 回测首版优先使用可稳定获取的指数历史序列。
- Streamlit 界面用于可视化现有策略结果，不额外复制业务逻辑。
