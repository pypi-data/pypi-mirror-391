import os
from datetime import datetime

EXCLUDE_OPTIONS = {
    'allure_epics', 'allure_features', 'allure_ids', 'allure_labels', 'allure_link_pattern',
    'allure_severities', 'allure_stories', 'assertmode', 'attach_capture',
    'basetemp', 'cacheclear', 'cacheshow', 'capture', 'clean_alluredir', 'code_highlight',
    'collect_in_virtualenv', 'collectonly', 'color', 'confcutdir', 'continue_on_collection_errors',
    'css', 'db_uri', 'debug', 'deselect', 'disable_warnings', 'dist', 'distload',
    'doctest_continue_on_failure', 'doctest_ignore_import_errors', 'doctestglob', 'doctestmodules',
    'doctestreport', 'durations', 'durations_min', 'env', 'failedfirst', 'file_or_dir', 'fold_skipped',
    'fulltrace', 'help', 'ignore', 'ignore_glob', 'importmode', 'inifilename', 'inversion',
    'iteration', 'junitprefix', 'keepduplicates', 'keyword', 'last_failed_no_failures', 'lf',
    'log_auto_indent', 'log_cli_date_format', 'log_cli_format', 'log_cli_level', 'log_date_format',
    'log_file_date_format', 'log_file_format', 'log_file_level', 'log_file_mode',
    'log_format', 'log_level', 'logger_disable', 'looponfail', 'markers', 'markexpr', 'maxfail',
    'maxprocesses', 'maxschedchunk', 'maxworkerrestart', 'metadata', 'metadata_from_json',
    'newfirst', 'no_header', 'no_summary', 'no_teamcity', 'noconftest',
    'numprocesses', 'only_rerun', 'override_ini', 'owner', 'pastebin', 'plugins', 'priority', 'pyargs',
    'pythonwarnings', 'quiet', 'reportchars', 'rerun_except', 'reruns', 'reruns_delay', 'rootdir',
    'rsyncdir', 'rsyncignore', 'runxfail', 'self_contained_html', 'session_timeout', 'setuponly',
    'setupplan', 'setupshow', 'show_fixtures_per_test', 'showcapture', 'showfixtures', 'showlocals',
    'status', 'stepwise', 'stepwise_skip', 'strict', 'strict_config', 'strict_markers', 'swapdiff',
    'tbstyle', 'teamcity', 'testrunuid', 'timeout', 'timeout_disable_debugger_detection',
    'timeout_method', 'trace', 'traceconfig', 'tx', 'typeguard_collection_check_strategy',
    'typeguard_debug_instrumentation', 'typeguard_forward_ref_policy', 'typeguard_packages',
    'typeguard_typecheck_fail_callback', 'usepdb', 'usepdb_cls', 'verbose', 'version',
    'xfail_tb', 'log_ignore', 'check_max_fail', 'base_url', 'headed', 'browser_channel',
    'verify_base_url', 'browser', 'xkill', 'device', 'check_max_report', 'xshow', 'tracing',
    'check_max_tb', 'video', 'slowmo', 'asyncio_mode', 'fail_on_flaky', 'full_page_screenshot',
    'screenshot'}

EXCLUDE_INI_CFGS = {
    'addopts', 'console_output_style', 'log_level', 'log_file_date_format', 'log_file_level',
    'log_cli_format', 'log_cli_date_format', 'log_cli_level', 'log_cli', 'markers', 'filterwarnings',
    'timeout', 'log_file_format', 'log_ignore'}


def is_relative(s: str) -> bool:
    return not os.path.isabs(s)


def pytest_configure(config):
    rootdir = config.rootdir
    now = datetime.now()

    # handle relative path in options
    options = [item for item in dir(config.option) if not item.startswith('_')]
    options = list(set(options) - EXCLUDE_OPTIONS)
    ini_cfgs = list(config.inicfg.keys() - EXCLUDE_INI_CFGS)
    for option in options:
        value = config.getoption(option)
        if value is None:
            continue
        if isinstance(value, str) and is_relative(value):
            new_value = os.path.abspath(os.path.join(rootdir, now.strftime(value)))
            setattr(config.option, option, new_value)
        elif isinstance(value, list):
            new_value = []
            for item in value:
                if isinstance(item, str) and item.startswith('.'):
                    new_value.append(os.path.abspath(os.path.join(rootdir, now.strftime(item))))
            setattr(config.option, option, new_value)

    # handle relative path ini configs
    for cfg in ini_cfgs:
        value = config.getini(cfg)
        if is_relative(value):
            new_value = os.path.abspath(os.path.join(rootdir, now.strftime(value)))
            config.inicfg[cfg] = new_value

            if hasattr(config.option, cfg):
                setattr(config.option, cfg, new_value)
