# ETF150

基于“长赢 150 计划”规则的 ETF 投资决策辅助命令行工具。

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 使用 mock 数据运行

```bash
etf150 valuation --provider mock --index hs300
etf150 signal --provider mock --index hs300 --category broad
etf150 panel --provider mock
etf150 allocation --provider mock --output allocation.png
etf150 sip --units 2
etf150 backtest --provider mock --index hs300 --years 3
etf150 iopv --provider mock --symbol 510300
```

## 运行测试

```bash
pytest
```

## 说明

- 首版以 CLI + 测试为主
- 真实数据优先预留 AkShare provider
- 后续可在此基础上扩展 Streamlit 界面
