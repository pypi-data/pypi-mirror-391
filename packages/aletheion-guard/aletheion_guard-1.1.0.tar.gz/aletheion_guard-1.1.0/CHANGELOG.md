# Changelog

All notable changes to AletheionGuard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-12

### Added
- **PyPI Package Release** - First official PyPI distribution
- **CLI Tool** (`aletheion-guard` command)
  - `audit` command for auditing LLM responses
  - `serve` command to start API server
  - `info` command for package information
- **Pre-trained Model Weights** included in package
  - Q1 Gate (aleatoric uncertainty)
  - Q2 Gate (epistemic uncertainty)
  - Height Gate (proximity to truth)
  - Base Forces Network (4-force equilibrium)
- **Modular Installation Options**
  - Core package with minimal dependencies
  - Optional extras: `api`, `monitoring`, `ml`, `viz`, `tracking`, `dev`, `docs`
- **Modern Packaging**
  - PEP 621 compliant `pyproject.toml`
  - Type hints support (`py.typed`)
  - Comprehensive package metadata

### Changed
- Reorganized model weights to be included in package distribution
- Optimized dependency requirements (core vs optional)
- Improved documentation for PyPI distribution

### Fixed
- Model weight loading paths for packaged installation
- Import paths for CLI entry point

## [1.0.0] - 2024-12-15

### Added
- **Core Epistemic Auditor**
  - Q1/Q2 uncertainty quantification
  - Pyramidal architecture implementation
  - Epistemic softmax layer
  - Base forces network (Memory, Pain, Choice, Exploration)
- **REST API Server**
  - FastAPI-based API with `/v1/audit`, `/v1/batch`, `/v1/compare` endpoints
  - API key authentication
  - Rate limiting with Redis
  - Prometheus metrics
  - OpenTelemetry tracing
  - Managed mode (hosted HuggingFace endpoints)
  - BYO-HF mode (Bring Your Own HuggingFace)
- **Input Processing**
  - Sentence Transformers embeddings
  - Context-aware text processing
- **Security Features**
  - Input validation
  - Rate limiting
  - API key management
- **Monitoring & Observability**
  - Structured logging with structlog
  - Prometheus metrics
  - OpenTelemetry distributed tracing
  - Health check endpoints
- **Documentation**
  - Comprehensive API reference
  - Quick start guide
  - Architecture deep-dive
  - Deployment guide
  - Research paper
  - Examples and tutorials

### Technical Details
- **Architecture**: Pyramidal epistemic architecture
- **ML Framework**: PyTorch 2.0+
- **Embeddings**: sentence-transformers
- **API Framework**: FastAPI
- **Supported Python**: 3.8+

## [0.1.0] - 2024-11-01

### Added
- Initial research prototype
- Basic Q1/Q2 heuristic estimator
- Proof of concept implementation

---

## Release Notes

### Version 1.1.0 - PyPI Release Highlights

This is the first official PyPI release of AletheionGuard! 🎉

**Quick Install:**
```bash
# Minimal installation
pip install aletheion-guard

# With API server
pip install aletheion-guard[api]

# Full installation
pip install aletheion-guard[all]
```

**What's Included:**
- Pre-trained model weights (~2.3MB)
- Command-line interface
- Python library with type hints
- Optional REST API server
- Comprehensive documentation

**Breaking Changes from Pre-release:**
- Model weights now bundled with package
- CLI entry point changed from script to console command
- Import paths remain the same

**Upgrade Path:**
If you were using the development version from git:
```bash
pip uninstall aletheion-guard  # Remove git version
pip install aletheion-guard    # Install PyPI version
```

---

## Upcoming Features (Roadmap)

### Version 1.2.0 (Planned)
- [ ] JavaScript/TypeScript SDK
- [ ] Improved batch processing performance
- [ ] Additional pre-trained models
- [ ] Enhanced calibration metrics
- [ ] WebSocket support for streaming

### Version 2.0.0 (Future)
- [ ] Multi-language support (Go, Rust clients)
- [ ] Fine-tuning utilities
- [ ] Model compression options
- [ ] Enhanced visualization tools
- [ ] Integration with popular LLM frameworks (LangChain, LlamaIndex)

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/AletheionAGI/AletheionGuard/blob/main/CONTRIBUTING.md).

## License

AletheionGuard is dual-licensed:
- **AGPL-3.0-or-later** for open source use
- **Commercial License** available - contact research@aletheionagi.com

---

**Full Changelog**: https://github.com/AletheionAGI/AletheionGuard/blob/main/CHANGELOG.md
