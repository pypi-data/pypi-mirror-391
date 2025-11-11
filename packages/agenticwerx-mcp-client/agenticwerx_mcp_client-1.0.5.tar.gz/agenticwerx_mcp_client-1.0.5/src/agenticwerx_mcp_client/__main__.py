#!/usr/bin/env python3
"""
AgenticWerx MCP Client - Entry point for uvx execution

This module serves as the main entry point when the package is executed
via uvx or python -m agenticwerx_mcp_client.
"""

import argparse
import asyncio
import json
import logging
import os
import sys

from .api import AgenticWerxAPI
from .client import AgenticWerxMCPClient


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def get_api_key(args_api_key: str | None) -> str:
    """Get API key from arguments or environment variables."""
    api_key = args_api_key or os.getenv("AGENTICWERX_API_KEY")

    if not api_key:
        print(
            "Error: API key required via --api-key argument or AGENTICWERX_API_KEY environment variable",
            file=sys.stderr,
        )
        print(
            "Get your API key at: https://agenticwerx.com/dashboard/api-keys",
            file=sys.stderr,
        )
        sys.exit(1)

    return api_key


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="AgenticWerx MCP Client - Universal code analysis for all IDEs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # MCP Server Mode (for IDEs)
  export AGENTICWERX_API_KEY=your_key_here
  agenticwerx-mcp-client

  # CLI Mode - Get rules
  agenticwerx-mcp-client --api-key your_key get-rules
  agenticwerx-mcp-client --api-key your_key get-rules --package-id pkg_123

  # CLI Mode - Analyze code
  agenticwerx-mcp-client --api-key your_key analyze-code --code "print('hello')"
  agenticwerx-mcp-client --api-key your_key analyze-code --file script.py --language python

For more information, visit: https://docs.agenticwerx.com/mcp-client
        """,
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="AgenticWerx API key (can also use AGENTICWERX_API_KEY env var)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--version",
        action="version",
        version=f"agenticwerx-mcp-client {__import__('agenticwerx_mcp_client').__version__}",
    )

    # Subcommands for CLI mode
    subparsers = parser.add_subparsers(dest="command", help="CLI commands")

    # get-rules command
    get_rules_parser = subparsers.add_parser(
        "get-rules", help="Get AgenticWerx rules"
    )
    get_rules_parser.add_argument(
        "--package-id", type=str, help="Optional package ID to filter rules"
    )

    # analyze-code command
    analyze_parser = subparsers.add_parser(
        "analyze-code", help="Analyze code using AgenticWerx rules"
    )
    code_group = analyze_parser.add_mutually_exclusive_group(required=True)
    code_group.add_argument("--code", type=str, help="Code snippet to analyze")
    code_group.add_argument("--file", type=str, help="File path to analyze")
    analyze_parser.add_argument(
        "--language", type=str, help="Programming language (auto-detected if omitted)"
    )
    analyze_parser.add_argument(
        "--package-ids",
        type=str,
        nargs="+",
        help="Package IDs to use for analysis",
    )

    return parser


# Maximum code size before chunking (in characters)
# Lambda server has a limit around 10KB, so we chunk at 8KB to be safe
MAX_CODE_SIZE = 8000


def detect_language_from_file(filepath: str) -> str | None:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "zsh",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".r": "r",
        ".R": "r",
    }

    import os

    _, ext = os.path.splitext(filepath)
    return ext_map.get(ext.lower())


def smart_chunk_code(code: str, max_size: int = MAX_CODE_SIZE) -> list[str]:
    """
    Split code into chunks intelligently, trying to break at logical boundaries.

    Args:
        code: The code to chunk
        max_size: Maximum size per chunk in characters

    Returns:
        List of code chunks
    """
    if len(code) <= max_size:
        return [code]

    chunks = []
    lines = code.split("\n")
    current_chunk = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1  # +1 for newline

        # If adding this line would exceed max_size, save current chunk
        if current_size + line_size > max_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0

        current_chunk.append(line)
        current_size += line_size

    # Add remaining lines
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def aggregate_analysis_results(results: list[dict]) -> dict:
    """
    Aggregate multiple analysis results into a single result.

    Args:
        results: List of analysis results from chunks

    Returns:
        Aggregated result
    """
    if not results:
        return {"summary": {}, "suggestions": [], "warnings": []}

    # Start with first result as base
    aggregated = {
        "summary": {
            "language": results[0].get("summary", {}).get("language"),
            "totalChunks": len(results),
            "totalCodeSize": sum(
                r.get("summary", {}).get("codeSize", 0) for r in results
            ),
            "totalRulesApplied": sum(
                r.get("summary", {}).get("rulesApplied", 0) for r in results
            ),
            "totalIssues": sum(
                r.get("summary", {}).get("totalIssues", 0) for r in results
            ),
            "totalProcessingTime": sum(
                r.get("summary", {}).get("processingTime", 0) for r in results
            ),
        },
        "suggestions": [],
        "warnings": [],
    }

    # Collect all suggestions and warnings
    for result in results:
        aggregated["suggestions"].extend(result.get("suggestions", []))
        aggregated["warnings"].extend(result.get("warnings", []))

    # Update counts
    aggregated["summary"]["returned"] = len(aggregated["suggestions"])

    return aggregated


async def run_cli_command(args: argparse.Namespace, api_key: str) -> None:
    """Run CLI command mode."""
    async with AgenticWerxAPI(api_key) as api:
        if args.command == "get-rules":
            # Get rules
            result = await api.get_rules(args.package_id)
            print(json.dumps(result, indent=2))

        elif args.command == "analyze-code":
            # Read code from file if specified
            language = args.language
            logger = logging.getLogger(__name__)

            if args.file:
                try:
                    with open(args.file, "r") as f:
                        code = f.read()
                    # Auto-detect language from file extension if not provided
                    if not language:
                        language = detect_language_from_file(args.file)
                        if language:
                            logger.info(f"Auto-detected language: {language}")
                except Exception as e:
                    print(f"Error reading file: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                code = args.code

            # Check if code needs to be chunked
            if len(code) > MAX_CODE_SIZE:
                logger.info(
                    f"Code size ({len(code)} chars) exceeds limit ({MAX_CODE_SIZE} chars), chunking..."
                )
                chunks = smart_chunk_code(code, MAX_CODE_SIZE)
                logger.info(f"Split code into {len(chunks)} chunks")

                # Analyze each chunk
                results = []
                for i, chunk in enumerate(chunks, 1):
                    logger.info(
                        f"Analyzing chunk {i}/{len(chunks)} ({len(chunk)} chars)..."
                    )
                    try:
                        result = await api.analyze_code(
                            code=chunk,
                            language=language,
                            package_ids=args.package_ids,
                        )
                        results.append(result)
                    except Exception as e:
                        logger.warning(f"Chunk {i} analysis failed: {e}")
                        # Continue with other chunks

                # Aggregate results
                if results:
                    aggregated = aggregate_analysis_results(results)
                    logger.info(
                        f"Analysis complete: {aggregated['summary']['totalIssues']} total issues found"
                    )
                    print(json.dumps(aggregated, indent=2))
                else:
                    print(
                        json.dumps(
                            {"error": "All chunks failed to analyze"}, indent=2
                        ),
                        file=sys.stderr,
                    )
                    sys.exit(1)
            else:
                # Single request for small code
                result = await api.analyze_code(
                    code=code, language=language, package_ids=args.package_ids
                )
                print(json.dumps(result, indent=2))


async def async_main() -> None:
    """Async main function."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)

    # Get API key
    api_key = get_api_key(args.api_key)

    # Check if running in CLI mode (subcommand provided)
    if args.command:
        logger.debug(f"Running CLI command: {args.command}")
        try:
            await run_cli_command(args, api_key)
        except Exception as e:
            logger.error(f"Command failed: {e}")
            if args.debug:
                logger.exception("Full traceback:")
            sys.exit(1)
        return

    # MCP Server mode (default)
    logger.info("Starting AgenticWerx MCP Client in server mode...")
    logger.debug("Debug logging enabled")

    try:
        # Create and run the MCP client
        client = AgenticWerxMCPClient(api_key=api_key, debug=args.debug)

        await client.run()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
