#!/usr/bin/env python3
"""
Universal Soul AI - Full Android APK Entry Point
==============================================

Wrapper that delegates to the full-featured implementation in main_complete.py.
This ensures the complete UI, overlay, voice, and gesture systems are active.
"""

import importlib
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    logger.info("Loading full-featured app from main_complete.py")
    mod = importlib.import_module("main_complete")
    if hasattr(mod, "main"):
        return mod.main()
    # fallback: if module defines an App subclass, run it
    if hasattr(mod, "MDApp") and hasattr(mod.MDApp, "run"):
        logger.info("Running MDApp from main_complete module")
        return mod.MDApp().run()
    if hasattr(mod, "App") and hasattr(mod.App, "run"):
        logger.info("Running App from main_complete module")
        return mod.App().run()
    raise RuntimeError("main_complete.py does not expose a runnable entry point")

if __name__ == "__main__":
    main()