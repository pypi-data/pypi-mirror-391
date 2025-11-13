# MediCafe/network_route_helpers.py
"""
Route mismatch remediation helpers for MediCafe.
Keeps XP/DNS-specific logic out of core request handling paths.

COMPATIBILITY: Python 3.4.4 and Windows XP compatible
"""

import os
import json
import platform

try:
    from MediCafe.core_utils import get_shared_config_loader, run_cmd  # type: ignore
    MediLink_ConfigLoader = get_shared_config_loader()
except ImportError:
    try:
        from .core_utils import get_shared_config_loader, run_cmd  # type: ignore
        MediLink_ConfigLoader = get_shared_config_loader()
    except ImportError:
        run_cmd = None  # type: ignore
        try:
            from MediCafe.MediLink_ConfigLoader import MediLink_ConfigLoader  # type: ignore
        except ImportError:
            MediLink_ConfigLoader = None  # type: ignore

ROUTE_404_HINT = "Hint: verify endpoint configuration and rerun after DNS flush (ipconfig /flushdns on Windows XP)."


def handle_route_mismatch_404(status_code, response_content, method, url, console_flag=False):
    """
    Run lightweight remediation when we see 404 'no route matched' behaviour.

    Returns:
        bool: True if the caller should retry the request, False otherwise.
    """
    if not MediLink_ConfigLoader:
        return False
    if not _is_route_mismatch_404(status_code, response_content):
        return False

    log = MediLink_ConfigLoader.log
    log(
        "Detected 404 'no route matched' for {} {}. Evaluating DNS remediation.".format(method, url),
        level="WARNING",
        console_output=console_flag
    )

    if not _is_windows_host():
        log(
            "DNS flush automation skipped: host OS is not Windows.",
            level="INFO",
            console_output=console_flag
        )
        return True

    if not _is_windows_xp_family():
        log(
            "DNS flush automation skipped: host release {} is outside Windows XP/2003 lineage.".format(_get_platform_release()),
            level="INFO",
            console_output=console_flag
        )
        return True

    if run_cmd is None:
        log(
            "DNS flush automation skipped: command runner unavailable in this runtime.",
            level="WARNING",
            console_output=console_flag
        )
        return True

    rc, stdout_text, stderr_text = run_cmd(['ipconfig', '/flushdns'])
    stdout_sanitized = _sanitize_log(stdout_text)
    stderr_sanitized = _sanitize_log(stderr_text)

    if rc == 0:
        log(
            "DNS cache flushed (ipconfig /flushdns). stdout: {}".format(stdout_sanitized or "<<empty>>"),
            level="WARNING",
            console_output=console_flag
        )
        log(
            "Retry the provider call to confirm route restoration.",
            level="INFO",
            console_output=console_flag
        )
    else:
        log(
            "DNS flush returned {}. stdout: {} stderr: {}".format(
                rc,
                stdout_sanitized or "<<empty>>",
                stderr_sanitized or "<<empty>>"
            ),
            level="ERROR",
            console_output=console_flag
        )

    return True


def _is_route_mismatch_404(status_code, response_content):
    try:
        if int(status_code) != 404:
            return False
    except Exception:
        return False
    body_text = _normalize_text(response_content)
    if not body_text:
        return False
    if "no route matched" in body_text:
        return True
    return "no route" in body_text and "matched" in body_text


def _normalize_text(value):
    try:
        if isinstance(value, (dict, list)):
            return json.dumps(value).lower()
    except Exception:
        pass
    try:
        return str(value).strip().lower()
    except Exception:
        return ""


def _is_windows_host():
    try:
        system_name = platform.system()
        if system_name:
            return system_name.lower().startswith('win')
    except Exception:
        pass
    return os.name == 'nt'


def _get_platform_release():
    try:
        release = platform.release()
    except Exception:
        release = ''
    try:
        version = platform.version()
    except Exception:
        version = ''
    if release and version:
        return "{} ({})".format(release, version)
    return release or version or "unknown"


def _is_windows_xp_family():
    if not _is_windows_host():
        return False
    release = ''
    version = ''
    try:
        release = (platform.release() or '').lower()
    except Exception:
        release = ''
    try:
        version = (platform.version() or '').lower()
    except Exception:
        version = ''
    if any(token in release for token in ('xp', '5.1', '5.2', '2003')):
        return True
    if version.startswith('5.1') or version.startswith('5.2'):
        return True
    return False


def _sanitize_log(value, limit=300):
    text = _normalize_text(value)
    if not text:
        return ''
    text = text.replace('\r', ' ').replace('\n', ' ')
    if len(text) > limit:
        text = text[:limit] + '...'
    return text


__all__ = (
    'handle_route_mismatch_404',
    'ROUTE_404_HINT',
)
