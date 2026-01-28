import logging
import os
import sys
from gi.repository import GLib

class StructuredLogger:
    DOMAIN = 'video-downloader'

    @staticmethod
    def setup_file_logging():
        log_dir = GLib.get_user_cache_dir() + '/video-downloader'
        os.makedirs(log_dir, exist_ok=True)
        log_file = log_dir + '/session.log'
        
        # We also want to integrate with GLib logging
        def log_handler(domain, level, message, user_data):
            level_str = {
                GLib.LogLevelFlags.LEVEL_DEBUG: "DEBUG",
                GLib.LogLevelFlags.LEVEL_INFO: "INFO",
                GLib.LogLevelFlags.LEVEL_MESSAGE: "MESSAGE",
                GLib.LogLevelFlags.LEVEL_WARNING: "WARNING",
                GLib.LogLevelFlags.LEVEL_CRITICAL: "CRITICAL",
                GLib.LogLevelFlags.LEVEL_ERROR: "ERROR",
            }.get(level, "UNKNOWN")
            
            with open(log_file, 'a') as f:
                f.write(f"[{level_str}] {domain}: {message}\n")

        GLib.log_set_handler(None, GLib.LogLevelFlags.LEVEL_MASK, log_handler, None)
        return log_file

    @classmethod
    def info(cls, message, **kwargs):
        cls._log(GLib.LogLevelFlags.LEVEL_INFO, message, **kwargs)

    @classmethod
    def warning(cls, message, **kwargs):
        cls._log(GLib.LogLevelFlags.LEVEL_WARNING, message, **kwargs)

    @classmethod
    def error(cls, message, **kwargs):
        cls._log(GLib.LogLevelFlags.LEVEL_ERROR, message, **kwargs)

    @classmethod
    def _log(cls, level, message, **kwargs):
        # Generic PII/Credential masking
        msg_str = str(message)
        # Avoid logging common sensitive patterns
        msg_str = cls._mask_sensitive(msg_str)
        
        fields = {'MESSAGE': GLib.Variant('s', msg_str)}
        for k, v in kwargs.items():
            fields[k.upper()] = GLib.Variant('s', cls._mask_sensitive(str(v)))
        GLib.log_variant(cls.DOMAIN, level, GLib.Variant('a{sv}', fields))
        # Also print to stderr for immediate visibility
        print(f"{msg_str} {kwargs if kwargs else ''}", file=sys.stderr)

    @staticmethod
    def _mask_sensitive(text):
        import re
        # Mask things that look like authorization headers or common tokens
        text = re.sub(r'([Pp]assword|[Tt]oken|[Ss]ecret)[:=]\s*[^\s,]+', r'\1: ***', text)
        return text

def setup_excepthook():
    def excepthook(type, value, tb):
        import traceback
        msg = "".join(traceback.format_exception(type, value, tb))
        StructuredLogger.error("Uncaught exception", traceback=msg)
    sys.excepthook = excepthook
