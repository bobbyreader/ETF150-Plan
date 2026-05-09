#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="${PYTHONPATH:-src}"

pytest
python -m etf150.cli --help >/dev/null
python -m etf150.cli panel --provider mock >/dev/null
python -m etf150.cli entry-backtest --provider mock --index hs300 --holding-days 20 >/dev/null
