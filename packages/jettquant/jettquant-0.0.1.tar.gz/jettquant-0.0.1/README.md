# jettquant

[![PyPI - Version](https://img.shields.io/pypi/v/jettquant.svg)](https://pypi.org/project/jettquant)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jettquant.svg)](https://pypi.org/project/jettquant)

-----

## Table of Contents

- [Installation](#installation)
- [Introduction](#project-structure)
- [License](#license)

## Installation

```console
pip install jettquant
```

## Introduction

示例1：订阅全市场数据
from pandas import DataFrame

from jettquant import MarketEngine

market_engine = MarketEngine(is_verbose=True)

def on_all_tick(df: DataFrame):
"""每3秒推送一次截面数据"""
print(df.head(5))

market_engine.subscribe_all(on_all_tick)

market_engine.start()
market_engine.run_forever()

示例2：订阅单只标的
from jettquant import MarketEngine

market_engine = MarketEngine()

def func(data_dict: dict):
"""订阅单只标的"""
print(data_dict)

xt_symbol = ["300750.SZ"]
market_engine.subscribe(xt_symbol, func)

market_engine.start()
market_engine.run_forever()

## License

`jettquant` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
