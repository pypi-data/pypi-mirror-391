# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2024-2025 Felipe Maya Muniz

"""
Command-line interface for AletheionGuard.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .auditor import EpistemicAuditor
from . import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="aletheion-guard",
        description="AletheionGuard - Epistemic Auditor for Large Language Models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit a single response
  aletheion-guard audit --prompt "What is 2+2?" --response "2+2=4"

  # Audit from file
  aletheion-guard audit --file input.json

  # Start API server
  aletheion-guard serve --port 8000

  # Show version
  aletheion-guard --version
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"AletheionGuard {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit LLM responses")
    audit_parser.add_argument("--prompt", type=str, help="Input prompt text")
    audit_parser.add_argument("--response", type=str, help="LLM response text")
    audit_parser.add_argument("--file", type=Path, help="JSON file with prompt/response pairs")
    audit_parser.add_argument("--model-path", type=Path, help="Path to model weights directory")
    audit_parser.add_argument("--output", type=Path, help="Output file for results (JSON)")
    audit_parser.add_argument("--verbose", action="store_true", help="Verbose output")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show package information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "audit":
        return audit_command(args)
    elif args.command == "serve":
        return serve_command(args)
    elif args.command == "info":
        return info_command(args)
    else:
        parser.print_help()
        sys.exit(1)


def audit_command(args):
    """Execute audit command."""
    try:
        # Initialize auditor
        if args.verbose:
            print("Initializing EpistemicAuditor...")

        auditor = EpistemicAuditor(model_dir=args.model_path)

        # Get input data
        if args.file:
            if args.verbose:
                print(f"Reading from {args.file}...")
            with open(args.file, 'r') as f:
                data = json.load(f)

            if isinstance(data, list):
                # Batch audit
                results = []
                for item in data:
                    prompt = item.get("prompt", "")
                    response = item.get("response", "")
                    audit = auditor.audit(prompt, response)
                    results.append(audit.to_dict())
            else:
                # Single audit
                prompt = data.get("prompt", "")
                response = data.get("response", "")
                audit = auditor.audit(prompt, response)
                results = audit.to_dict()

        elif args.prompt and args.response:
            # Single audit from arguments
            if args.verbose:
                print("Auditing single prompt/response...")
            audit = auditor.audit(args.prompt, args.response)
            results = audit.to_dict()

        else:
            print("Error: Either --file or both --prompt and --response must be provided")
            sys.exit(1)

        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            if args.verbose:
                print(f"Results written to {args.output}")
        else:
            print(json.dumps(results, indent=2))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def serve_command(args):
    """Execute serve command."""
    try:
        import uvicorn
        from .api import app

        print(f"Starting AletheionGuard API server on {args.host}:{args.port}")
        print(f"Docs available at http://{args.host}:{args.port}/docs")

        uvicorn.run(
            "aletheion_guard.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )

        return 0

    except ImportError:
        print("Error: FastAPI/Uvicorn not installed. Install with: pip install aletheion-guard[api]")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def info_command(args):
    """Execute info command."""
    from . import __author__, __email__

    print(f"""
AletheionGuard - Epistemic Auditor for LLMs
============================================

Version:     {__version__}
Author:      {__author__}
Email:       {__email__}
License:     AGPL-3.0-or-later

Description:
  AletheionGuard provides tools for quantifying aleatoric (Q1) and
  epistemic (Q2) uncertainty in LLM outputs, enabling hallucination
  detection and calibration assessment.

Features:
  - Q1/Q2 uncertainty quantification
  - Pyramidal epistemic architecture
  - REST API with FastAPI
  - Pre-trained model weights included
  - Batch processing support

Documentation: https://docs.aletheionguard.com
Repository:    https://github.com/AletheionAGI/AletheionGuard
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
