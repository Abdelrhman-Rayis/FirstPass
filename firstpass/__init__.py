"""FirstPass: an agentic first-pass reviewer for standard commercial contracts.

Every contract gets an AI first pass. A human confirms. The queue gets shorter.

Pipeline (the agentic loop) lives in :mod:`firstpass.triage`.
"""

__version__ = "0.3.0"

from .triage import triage_contract, TriageResult, Finding  # noqa: E402,F401
