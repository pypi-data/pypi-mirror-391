"""
Empathy Healthcare Plugin

Clinical protocol monitoring using the empathy framework.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

__version__ = "1.0.0"

from .monitors.clinical_protocol_monitor import ClinicalProtocolMonitor

__all__ = ["ClinicalProtocolMonitor"]
