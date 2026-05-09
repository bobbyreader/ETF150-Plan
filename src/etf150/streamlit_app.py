from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

import pandas as pd
import streamlit as st

from etf150.cli import get_provider
from etf150.services import get_allocation, get_backtest, get_entry_backtest, get_iopv, get_panel, get_signal, get_valuation


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


@st.cache_resource
def _get_provider(name: str):
    return get_provider(name)


def _render_valuation_tab(provider_name: str, index_code: str) -> None:
    provider = _get_provider(provider_name)
    result = get_valuation(provider, index_code)
    valuation = result["valuation"]

    st.subheader(f"{valuation.index_name} 估值")
    metrics = st.columns(4)
    metrics[0].metric("等权PE均值", valuation.equal_weight_pe_mean)
    metrics[1].metric("等权PE中位数", valuation.equal_weight_pe_median)
    metrics[2].metric("当前PB", valuation.current_pb)
    metrics[3].metric("有效样本数", valuation.valid_sample_size)

    percentiles = st.columns(3)
    percentiles[0].metric("5年分位", f"{valuation.percentile_5y}%")
    percentiles[1].metric("10年分位", f"{valuation.percentile_10y}%")
    percentiles[2].metric("估值区", valuation.valuation_zone)

    st.json(_serialize(result))


def _render_signal_tab(
    provider_name: str,
    index_code: str,
    category: str,
    capital: float,
    rotation_from: str,
    rotation_from_percentile: float,
    rotation_to: str,
    rotation_to_percentile: float,
) -> None:
    provider = _get_provider(provider_name)
    result = get_signal(
        provider=provider,
        index_code=index_code,
        category=category,
        capital=capital,
        rotation_from=rotation_from,
        rotation_from_percentile=rotation_from_percentile,
        rotation_to=rotation_to,
        rotation_to_percentile=rotation_to_percentile,
    )
    signal = result["signal"]

    st.subheader("执行信号")
    metrics = st.columns(4)
    metrics[0].metric("信号", signal.signal)
    metrics[1].metric("目标权益仓位", f"{signal.position.target_equity_pct}%")
    metrics[2].metric("建议份数", signal.units.suggested_units)
    metrics[3].metric("建议金额", signal.units.suggested_amount)

    st.write(signal.position.rationale)
    st.write(signal.units.rationale)
    st.write(signal.worst_case_message)
    if signal.iopv_warning:
        st.warning(signal.iopv_warning)
    if signal.rotation:
        st.info(signal.rotation.rationale)

    st.json(_serialize(result))


def _render_panel_tab(provider_name: str) -> None:
    provider = _get_provider(provider_name)
    result = get_panel(provider)
    st.subheader("多市场面板")
    st.dataframe(pd.DataFrame(_serialize(result["panel"])), use_container_width=True)


def _render_allocation_tab(provider_name: str) -> None:
    provider = _get_provider(provider_name)
    result = get_allocation(provider, include_figure=True)
    st.subheader("资产配置")
    st.pyplot(result["figure"])
    st.dataframe(pd.DataFrame(_serialize(result["allocation"])), use_container_width=True)


def _render_backtest_tab(provider_name: str, index_code: str, years: int) -> None:
    provider = _get_provider(provider_name)
    result = get_backtest(provider, index_code, years)
    backtest = result["backtest"]

    st.subheader("回测结果")
    metrics = st.columns(4)
    metrics[0].metric("起始净值", backtest.start_value)
    metrics[1].metric("结束净值", backtest.end_value)
    metrics[2].metric("累计收益", f"{backtest.cumulative_return_pct}%")
    metrics[3].metric("年化收益", f"{backtest.annualized_return_pct}%")
    st.metric("最大回撤", f"{backtest.max_drawdown_pct}%")
    st.json(_serialize(result))


def _render_entry_backtest_tab(provider_name: str, index_code: str, holding_days: int, history_years: int) -> None:
    provider = _get_provider(provider_name)
    result = get_entry_backtest(provider, index_code, holding_days, history_years)
    entry_backtest = result["entry_backtest"]

    st.subheader("估值起点回测")
    st.dataframe(pd.DataFrame(_serialize(entry_backtest.entries)), use_container_width=True)
    st.json(_serialize(result))


def _render_iopv_tab(provider_name: str, symbol: str) -> None:
    provider = _get_provider(provider_name)
    result = get_iopv(provider, symbol)
    snapshot = result["iopv"]

    st.subheader("IOPV 监控")
    metrics = st.columns(4)
    metrics[0].metric("ETF", snapshot["symbol"])
    metrics[1].metric("现价", snapshot["current_price"])
    metrics[2].metric("IOPV", snapshot["iopv"] if snapshot["iopv"] is not None else "暂无")
    metrics[3].metric("溢价率", f"{snapshot['premium_pct']}%" if snapshot["premium_pct"] is not None else "暂无")
    if snapshot["action"] == "wait":
        st.warning(snapshot["note"])
    elif snapshot["action"] == "unknown":
        st.info(snapshot["note"])
    else:
        st.success(snapshot["note"])
    st.json(result)


def main() -> None:
    st.set_page_config(page_title="ETF150 决策助手", layout="wide")
    st.title("ETF150 决策助手")

    provider_name = st.sidebar.selectbox("数据源", ["mock", "akshare"], index=0)
    provider = _get_provider(provider_name)
    supported_indexes = provider.get_supported_indexes()
    supported_categories = provider.get_supported_categories()
    supported_symbols = provider.get_supported_symbols()
    symbol_labels = provider.get_streamlit_supported_symbol_labels()
    backtest_year_options = provider.get_backtest_year_options()
    index_codes = list(supported_indexes.keys())

    default_index = provider.get_streamlit_default_index()
    default_index_position = index_codes.index(default_index) if default_index in index_codes else 0
    index_code = st.sidebar.selectbox("指数", index_codes, index=default_index_position, format_func=provider.get_index_display_name)
    capital = st.sidebar.number_input("总资金", min_value=1000.0, value=provider.get_streamlit_default_capital(), step=1000.0)
    default_category = provider.get_streamlit_default_category()
    category_index = supported_categories.index(default_category) if default_category in supported_categories else 0
    category = st.sidebar.selectbox("分类", supported_categories, index=category_index)
    default_symbol = provider.get_streamlit_default_symbol()
    symbol_index = supported_symbols.index(default_symbol) if default_symbol in supported_symbols else 0
    symbol = st.sidebar.selectbox(
        "ETF",
        supported_symbols,
        index=symbol_index,
        format_func=lambda item: f"{item} / {symbol_labels[item]}",
    )
    sip_units = st.sidebar.number_input("定投份数", min_value=1, value=provider.get_streamlit_default_sip_units(), step=1)
    default_backtest_years = provider.get_streamlit_default_backtest_years()
    backtest_year_index = backtest_year_options.index(default_backtest_years) if default_backtest_years in backtest_year_options else 0
    backtest_years = st.sidebar.selectbox("回测年限", backtest_year_options, index=backtest_year_index)
    entry_holding_days = st.sidebar.number_input("估值起点持有天数", min_value=1, value=252, step=21)

    rotation_from, rotation_from_percentile, rotation_to, rotation_to_percentile = provider.get_streamlit_default_rotation_inputs()
    rotation_from = st.sidebar.text_input("换马卖出标的", value=rotation_from)
    rotation_from_percentile = st.sidebar.number_input("卖出分位", min_value=0.0, max_value=100.0, value=float(rotation_from_percentile), step=1.0)
    rotation_to = st.sidebar.text_input("换马买入标的", value=rotation_to)
    rotation_to_percentile = st.sidebar.number_input("买入分位", min_value=0.0, max_value=100.0, value=float(rotation_to_percentile), step=1.0)

    st.sidebar.caption(provider.get_streamlit_sidebar_note())
    st.sidebar.caption(provider.get_streamlit_live_data_warning())
    st.sidebar.caption(provider.get_streamlit_market_warning())
    st.sidebar.caption(provider.get_streamlit_footer_note())

    valuation_tab, signal_tab, panel_tab, allocation_tab, backtest_tab, entry_backtest_tab, iopv_tab, sip_tab = st.tabs(
        ["估值", "信号", "面板", "配置", "回测", "估值起点", "IOPV", "定投"]
    )

    with valuation_tab:
        _render_valuation_tab(provider_name, index_code)
    with signal_tab:
        _render_signal_tab(
            provider_name,
            index_code,
            category,
            capital,
            rotation_from,
            rotation_from_percentile,
            rotation_to,
            rotation_to_percentile,
        )
    with panel_tab:
        _render_panel_tab(provider_name)
    with allocation_tab:
        _render_allocation_tab(provider_name)
    with backtest_tab:
        _render_backtest_tab(provider_name, index_code, int(backtest_years))
    with entry_backtest_tab:
        _render_entry_backtest_tab(provider_name, index_code, int(entry_holding_days), int(backtest_years))
    with iopv_tab:
        _render_iopv_tab(provider_name, symbol)
    with sip_tab:
        st.subheader("定投建议")
        st.write(provider.get_sip_suggestion(int(sip_units)))


if __name__ == "__main__":
    main()
