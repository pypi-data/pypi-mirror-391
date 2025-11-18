from .core import M8taim
from .dec import time_protected, require_license, track_usage, retry_on_failure, rate_limit
from .hk import HookSystem, EventLogger, PluginManager
from .lic import LicenseManager
from .cfg import ConfigManager
from .ana import AnalyticsEngine
from .adv import AdvancedTimeManager
from .ut import SystemUtils, CryptoUtils, TimeUtils, FileUtils
from .tm import get_remaining, calc_expiry

__version__ = "1.0.0"
__author__ = "MERO (@Qp4rm)"
__all__ = [
    "M8taim",
    "time_protected",
    "require_license",
    "track_usage",
    "retry_on_failure",
    "rate_limit",
    "HookSystem",
    "EventLogger",
    "PluginManager",
    "LicenseManager",
    "ConfigManager",
    "AnalyticsEngine",
    "AdvancedTimeManager",
    "SystemUtils",
    "CryptoUtils",
    "TimeUtils",
    "FileUtils",
    "get_remaining",
    "calc_expiry"
]
