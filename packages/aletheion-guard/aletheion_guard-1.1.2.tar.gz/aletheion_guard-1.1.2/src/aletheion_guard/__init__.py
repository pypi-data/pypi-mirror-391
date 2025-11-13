# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
AletheionGuard - Epistemic Auditor for Large Language Models

This package provides tools for quantifying aleatoric (Q1) and epistemic (Q2)
uncertainty in LLM outputs, enabling hallucination detection and calibration assessment.

Architecture inspired by aletheion-llm: https://github.com/AletheionAGI/aletheion-llm
Based on the research paper "How to Solve Skynet: A Pyramidal Law for Epistemic Equilibrium".
"""

from .auditor import EpistemicAuditor, EpistemicAudit
from .q1q2_gates import Q1Gate, Q2Gate, UncertaintyNetwork
from .pyramidal import PyramidalArchitecture
from .input_processor import InputProcessor
from .epistemic_softmax import (
    epistemic_softmax,
    EpistemicSoftmaxLayer,
    LocalUncertaintyGate,
    CrossContextGate,
    compare_softmax,
    apply_epistemic_sampling,
    create_epistemic_softmax_from_gates
)

__version__ = "1.1.0"
__author__ = "Aletheion Research Collective"
__email__ = "research@aletheionagi.com"

__all__ = [
    # Core auditor
    "EpistemicAuditor",
    "EpistemicAudit",
    # Q1/Q2 Gates
    "Q1Gate",
    "Q2Gate",
    "UncertaintyNetwork",
    # Pyramidal architecture
    "PyramidalArchitecture",
    # Input processing
    "InputProcessor",
    # Epistemic Softmax (from aletheion-llm)
    "epistemic_softmax",
    "EpistemicSoftmaxLayer",
    "LocalUncertaintyGate",
    "CrossContextGate",
    "compare_softmax",
    "apply_epistemic_sampling",
    "create_epistemic_softmax_from_gates",
]
