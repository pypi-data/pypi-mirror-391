# pytest-relative-path

![Languate - Python](https://img.shields.io/badge/language-python-blue.svg)
![PyPI - License](https://img.shields.io/pypi/l/pytest-relative-path)
![PyPI](https://img.shields.io/pypi/v/pytest-relative-path)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-relative-path)

处理Pytest参数及配置中的相对路径，将相对于执行目录改为项目项目根目录，支持时间戳。

---

### 如何使用

1. 安装 `pytest-relative-path`

使用pip安装

```sh
pip install pytest-relative-path
```

2. 在pytest命令行参数或pytest.ini配置中，路径以'.'开头，支持时间戳

```sh
pytest . --log-file=./logs/%Y%m%d%H%M%S.log
```

或在pytest.ini中配置
```ini
[pytest]
log_file=./logs/%Y%m%d%H%M%S.log
```
并执行 
```sh
pytest .
```
无论执行路径，将固定在项目根目录按时间戳生成日志，例如 (rootdir)/logs/20240830122250.log

3. 支持插件pytest-html、allure-pytest、pytest-data-file、pytest-variables等，例如

```sh
pytest . --html=./reports/TestReport-%Y%m%d%H%M%S.html --alluredir=./reports/allure_data  --data-file=./data/a.json --variables=./data/b.json
```
无论执行路径如何，报告会固定生成在项目/reports目录下，数据会固定从项目/data目录下寻找