# pytest-log-filter

![Languate - Python](https://img.shields.io/badge/language-python-blue.svg)
![PyPI - License](https://img.shields.io/pypi/l/pytest-log-filter)
![PyPI](https://img.shields.io/pypi/v/pytest-log-filter)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-log-filter)

屏蔽pytest测试中指定loggers的日志

---

### 如何使用

1. 安装 `pytest-log-filter`

使用pip安装

```sh
pip install pytest-log-filter
```

2. 在pytest命令行参数使用--log-ignore指定要屏蔽的logger模块

```sh
pytest . --log-ignore=urllib3.connectionpool --log-ignore=web3.manager.RequestManager
```

或在pytest.ini中配置
```ini
[pytest]
log_ignore =
    web3.providers.HTTPProvider
    web3._utils.http_session_manager.HTTPSessionManager
```

> 同时使用命令行参数--log-ignore和pytest-ini配置，会屏蔽所有的loggers

