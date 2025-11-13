# AletheionGuard

**Epistemic Auditor for Large Language Models**

[![PyPI version](https://img.shields.io/pypi/v/aletheion-guard.svg)](https://pypi.org/project/aletheion-guard/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE.md)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://docs.aletheionguard.com)

AletheionGuard quantifies **aleatoric (Q1)** and **epistemic (Q2)** uncertainty in LLM outputs to detect hallucinations and assess response reliability.

---

## 🚀 Quick Start

### Installation

```bash
# Minimal installation
pip install aletheion-guard

# With API server
pip install aletheion-guard[api]

# Full installation (all features)
pip install aletheion-guard[all]
```

### Basic Usage

```python
from aletheion_guard import EpistemicAuditor

# Initialize auditor (model weights included)
auditor = EpistemicAuditor()

# Audit any LLM response
prompt = "What is the capital of France?"
response = "The capital of France is Paris."
audit = auditor.audit(prompt, response)

print(f"Q1 (aleatoric):  {audit.q1:.3f}")      # Data ambiguity
print(f"Q2 (epistemic):  {audit.q2:.3f}")      # Model ignorance
print(f"Height:          {audit.height:.3f}")   # Proximity to truth
print(f"Verdict:         {audit.verdict}")      # ACCEPT | MAYBE | REFUSED
```

**Output:**
```
Q1 (aleatoric):  0.023
Q2 (epistemic):  0.012
Height:          0.999
Verdict:         ACCEPT
```

### CLI Usage

```bash
# Audit a response
aletheion-guard audit \
  --prompt "What is 2+2?" \
  --response "2+2 equals 4"

# Start API server
aletheion-guard serve --port 8000

# Show package info
aletheion-guard info
```

---

## ✨ Key Features

### 1. **Uncertainty Quantification**
Separates two types of uncertainty:
- **Q1 (Aleatoric)**: Irreducible data noise/ambiguity
- **Q2 (Epistemic)**: Model ignorance/hallucination risk

### 2. **Epistemic Softmax** (New in v1.1.0)
```python
from aletheion_guard import epistemic_softmax

# Uncertainty-aware probability distributions
logits = model.get_logits("What is quantum computing?")
probs, uncertainty = epistemic_softmax(logits, return_uncertainty=True)

print(f"Q1: {uncertainty['q1']:.3f}, Q2: {uncertainty['q2']:.3f}")
```

### 3. **Production-Ready API**
```python
# pip install aletheion-guard[api]
from fastapi import FastAPI
from aletheion_guard.api import app

# Or use CLI
# aletheion-guard serve --host 0.0.0.0 --port 8000
```

**API Endpoints:**
- `POST /v1/audit` - Audit single response
- `POST /v1/batch` - Batch auditing
- `POST /v1/compare` - Compare models
- `GET /health` - Health check

### 4. **Pre-trained Models Included**
Model weights (~2.3MB) are bundled:
- Q1 Gate (aleatoric uncertainty)
- Q2 Gate (epistemic uncertainty)
- Height Gate (proximity to truth)
- Base Forces Network (4-force equilibrium)

---

## 🎯 Use Cases

### Enterprise LLM Safety Gates
```python
audit = auditor.audit(prompt, llm_response)

if audit.verdict == "REFUSED":
    return "I don't have enough confidence to answer this."
elif audit.q2 > 0.5:
    return "This answer may be unreliable. Please verify."
else:
    return llm_response
```

### RAG Enhancement
```python
audit = auditor.audit(query, rag_response)

if audit.q2 > 0.3:
    # High epistemic uncertainty - retrieve more context
    additional_docs = retriever.get_more_context(query)
    improved_response = llm.generate(query, additional_docs)
```

### Model Comparison
```python
from aletheion_guard import EpistemicAuditor

auditor = EpistemicAuditor()

# Compare calibration across models
models = {
    "gpt-4": gpt4_response,
    "claude-3": claude_response,
    "llama-3": llama_response
}

for model_name, response in models.items():
    audit = auditor.audit(prompt, response)
    print(f"{model_name}: Q2={audit.q2:.3f}, ECE={audit.ece:.3f}")
```

---

## 🏗️ Architecture

AletheionGuard implements a **pyramidal architecture** for epistemic equilibrium:

```
┌─────────────────────────────────────┐
│      Epistemic Softmax Layer        │  ← Uncertainty-aware predictions
├─────────────────────────────────────┤
│     Q1 Gate  │  Q2 Gate  │ Height   │  ← Uncertainty quantification
├─────────────────────────────────────┤
│      Base Forces Network            │  ← Memory, Pain, Choice, Exploration
├─────────────────────────────────────┤
│      Input Processor                │  ← Text embeddings
└─────────────────────────────────────┘
```

**Inspired by:** [aletheion-llm](https://github.com/AletheionAGI/aletheion-llm)
**Based on:** ["How to Solve Skynet" research paper](https://docs.aletheionguard.com/paper)

---

## 📦 Installation Options

```bash
# Core package (minimal dependencies)
pip install aletheion-guard

# With API server
pip install aletheion-guard[api]

# With monitoring (Prometheus, OpenTelemetry)
pip install aletheion-guard[monitoring]

# With ML utilities (PyTorch Lightning, Optuna)
pip install aletheion-guard[ml]

# With visualization (Matplotlib, Seaborn)
pip install aletheion-guard[viz]

# Development tools
pip install aletheion-guard[dev]

# All features
pip install aletheion-guard[all]
```

---

## 🔬 Advanced Usage

### Custom Model Weights
```python
auditor = EpistemicAuditor(
    model_dir="/path/to/custom/weights"
)
```

### Batch Processing
```python
from aletheion_guard import EpistemicAuditor

auditor = EpistemicAuditor()

prompts = ["Question 1?", "Question 2?", "Question 3?"]
responses = ["Answer 1", "Answer 2", "Answer 3"]

for prompt, response in zip(prompts, responses):
    audit = auditor.audit(prompt, response)
    print(f"Q2: {audit.q2:.3f}, Verdict: {audit.verdict}")
```

### API Server with Docker
```dockerfile
FROM python:3.11-slim

RUN pip install aletheion-guard[api]

EXPOSE 8000
CMD ["aletheion-guard", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 What Gets Measured

Each audit returns:

| Metric | Range | Description |
|--------|-------|-------------|
| **Q1** | [0, 1] | Aleatoric uncertainty (data ambiguity) |
| **Q2** | [0, 1] | Epistemic uncertainty (model ignorance) |
| **Height** | [0, 1] | Proximity to truth: `h = 1 - √(Q1² + Q2²)` |
| **ECE** | [0, 1] | Expected Calibration Error |
| **Verdict** | enum | `ACCEPT` \| `MAYBE` \| `REFUSED` |

---

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/AletheionAGI/AletheionGuard.git
cd AletheionGuard

# Install for development
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/
isort src/

# Type checking
mypy src/
```

---

## 📚 Documentation

- **Quick Start**: [docs.aletheionguard.com/quickstart](https://docs.aletheionguard.com/quickstart)
- **API Reference**: [docs.aletheionguard.com/api](https://docs.aletheionguard.com/api)
- **Architecture**: [docs.aletheionguard.com/architecture](https://docs.aletheionguard.com/architecture)
- **Examples**: [docs.aletheionguard.com/examples](https://docs.aletheionguard.com/examples)
- **Research Paper**: [docs.aletheionguard.com/paper](https://docs.aletheionguard.com/paper)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/AletheionAGI/AletheionGuard/blob/main/CONTRIBUTING.md).

---

## 📄 License

**Dual Licensed:**

- **AGPL-3.0-or-later** for open source use
- **Commercial License** available for proprietary applications

Contact: [research@aletheionagi.com](mailto:research@aletheionagi.com)

---

## 🔗 Links

- **Website**: [aletheionguard.com](https://aletheionguard.com)
- **Documentation**: [docs.aletheionguard.com](https://docs.aletheionguard.com)
- **GitHub**: [github.com/AletheionAGI/AletheionGuard](https://github.com/AletheionAGI/AletheionGuard)
- **PyPI**: [pypi.org/project/aletheion-guard](https://pypi.org/project/aletheion-guard/)
- **Discord**: [Join our community](https://discord.gg/aletheion)

---

## 🏆 Citation

If you use AletheionGuard in your research, please cite:

```bibtex
@software{aletheionguard2025,
  title = {AletheionGuard: Epistemic Auditor for Large Language Models},
  author = {Aletheion Research Collective},
  year = {2025},
  url = {https://github.com/AletheionAGI/AletheionGuard},
  version = {1.1.0}
}
```

---

## 📈 Project Status

- ✅ **Stable**: Core API is stable and production-ready
- 🚀 **Active Development**: Regular updates and improvements
- 📦 **PyPI**: Official package available
- 🤖 **API**: Hosted API available at [api.aletheionguard.com](https://api.aletheionguard.com)

---

Made with ❤️ by [Aletheion Research Collective](https://aletheionagi.com)
