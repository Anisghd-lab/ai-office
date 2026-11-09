"""Structured logging configuration with automatic secret redaction."""

import logging
import re
import sys
from typing import List, Optional


SECRET_PATTERNS = [
    re.compile(r"(Bearer\s+)[a-zA-Z0-9_\-\.]{10,}", re.IGNORECASE),
    re.compile(r"(api[_\-\s]?key['\"]?\s*[:=]\s*['\"]?)[a-zA-Z0-9_\-\.]{10,}", re.IGNORECASE),
    re.compile(r"(token['\"]?\s*[:=]\s*['\"]?)[a-zA-Z0-9_\-\.]{10,}", re.IGNORECASE),
    re.compile(r"(secret['\"]?\s*[:=]\s*['\"]?)[a-zA-Z0-9_\-\.]{10,}", re.IGNORECASE),
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{36,}", re.IGNORECASE),
    re.compile(r"github_pat_[a-zA-Z0-9_]{50,}", re.IGNORECASE),
]


class SecretRedactionFilter(logging.Filter):
    """Filters out any potential secrets from log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(self.redact(str(arg)) for arg in record.args)
        return True

    @classmethod
    def redact(cls, text: str) -> str:
        res = text
        for pat in SECRET_PATTERNS:
            res = pat.sub(r"\1[REDACTED_SECRET]" if pat.groups else "[REDACTED_SECRET]", res)
        return res


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configures structured logger for AI Office."""
    logger = logging.getLogger("ai_office")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SecretRedactionFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
