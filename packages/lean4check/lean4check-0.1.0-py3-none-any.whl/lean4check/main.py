"""
lean4check MCP Server - A Lean 4 build wrapper MCP server
"""

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import json


@dataclass
class CLIResult:
    """Result of executing a CLI command."""
    stdout: str = ""
    stderr: str = ""
    returncode: int | None = None
    timed_out: bool = False
    error: str | None = None


def execute_command(
    args: list[str],
    cwd: Path | None = None,
    timeout: int = 300
) -> CLIResult:
    """
    Execute a CLI command and capture its output.

    Args:
        args: Command and arguments as a list
        cwd: Working directory for the command
        timeout: Timeout in seconds

    Returns:
        CLIResult containing the command output and status
    """
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return CLIResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode
        )

    except subprocess.TimeoutExpired:
        return CLIResult(timed_out=True)
    except FileNotFoundError:
        return CLIResult(error=f"Command not found: {args[0]}")
    except Exception as e:
        return CLIResult(error=f"Error running command: {e}")


class Lean4Project:
    """Represents a Lean 4 project and provides operations on it."""

    def __init__(self, root: Path):
        """
        Initialize a Lean 4 project.

        Args:
            root: Root directory of the Lean 4 project
        """
        self.root = root

    def check_file(self, filepath: str) -> CLIResult:
        """
        Check a Lean 4 file using lake lean with JSON output.

        Args:
            filepath: The file path to check (e.g., "Semantic/Fsub/Soundness.lean")

        Returns:
            CLIResult containing the check output and status
        """
        if not self.root.exists():
            return CLIResult(error=f"Project root {self.root} does not exist.")

        if not (self.root / "lakefile.lean").exists() and not (self.root / "lakefile.toml").exists():
            return CLIResult(error=f"No lakefile found in {self.root}. Not a valid Lean 4 project.")

        return execute_command(
            ["lake", "lean", filepath, "--", "--json"],
            cwd=self.root,
            timeout=300
        )

    def render_result(self, result: CLIResult, filename: str) -> str:
        if result.stderr and not result.stdout:
            builder = []
            builder.append(f"Lake produces the following messages when checking the dependencies of this module:\n")
            builder.append(result.stderr)
            builder.append("\n")
            builder.append("These may indicate errors in the dependencies that need to be resolved before checking this file.")
            builder.append("Or they may be informational message that can be ignored. You need to figure out which.")
            return "\n".join(builder)

        if result.timed_out:
            return f"I tried to check the file, but it took too long and timed-out."

        if result.error:
            builder = []
            builder.append(f"I failed to check the file due to an unexpected error. Error:")
            builder.append(result.error)
            return "\n".join(builder)

        try:
            lines = result.stdout.splitlines()
            diagnostics = []
            for line in lines:
                if line.strip():
                    diag = json.loads(line)
                    if diag:
                      diagnostics.append(diag)
            if not diagnostics:
                return "No issues found."

            # Sort diagnostics by position
            # Diagnostics without position go to the end (lowest priority)
            def get_sort_key(diag):
                pos = diag.get('pos')
                if pos is None or not isinstance(pos, dict):
                    # No position - put at end with very large line number
                    return (float('inf'), float('inf'))
                line_num = pos.get('line', float('inf'))
                col_num = pos.get('column', float('inf'))
                return (line_num, col_num)

            diagnostics.sort(key=get_sort_key)

            # Limit to first 8 diagnostics
            total_count = len(diagnostics)
            diagnostics = diagnostics[:8]

            builder = []
            builder.append(f"I found the following issues in {filename}:\n")
            for diag in diagnostics:
                if diag is not None:
                    builder.append(self.render_message(diag))

            # Show count if there are more diagnostics
            if total_count > 8:
                builder.append(f"\n... and {total_count - 8} more diagnostic(s) not shown.")

            if result.stderr.strip():
                builder.append("\nAdditionally, there were some infos/warnings/errors from lake:\n")
                builder.append(result.stderr)
            return "\n".join(builder)
        except json.JSONDecodeError:
            return f"I failed to parse output from lean as JSON. The raw output was:\n{result.stdout}"

    def render_message(self, message: dict) -> str:
        """
        Render a Lean diagnostic message in a human-readable format.

        Args:
            message: A diagnostic message dictionary

        Returns:
            Formatted diagnostic string with context and annotations
        """
        severity = message.get('severity', 'info')
        pos = message.get('pos')
        end_pos = message.get('endPos')
        filename = message.get('fileName', '')
        data = message.get('data', '')

        # Handle case where position information is not available
        if pos is None:
            return f"{severity.upper()}: {filename}\n{data}"

        # Ensure pos is a dict
        if not isinstance(pos, dict):
            return f"{severity.upper()}: {filename}\n{data}"

        line_num = pos.get('line', 0)
        col_num = pos.get('column', 0)

        # Handle end_pos being None or not a dict
        if end_pos is None or not isinstance(end_pos, dict):
            end_pos = pos

        end_line = end_pos.get('line', line_num)
        end_col = end_pos.get('column', col_num)

        # Read the file
        try:
            filepath = Path(filename)
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except Exception:
            # Fallback if file can't be read
            return f"{severity.upper()} at {filename}:{line_num}:{col_num}\n{data}"

        # Validate line number
        if line_num < 1 or line_num > len(lines):
            return f"{severity.upper()} at {filename}:{line_num}:{col_num}\n{data}"

        # Extract context (5 lines before and after)
        context_before = 5
        context_after = 5
        start_line = max(1, line_num - context_before)
        end_line_ctx = min(len(lines), line_num + context_after)

        # Calculate line number width for alignment
        line_num_width = len(str(end_line_ctx))

        # Build the output
        builder = []

        # Header
        builder.append(f"{severity.upper()}: {filename}:{line_num}:{col_num}")
        builder.append("")

        # Show context lines
        for i in range(start_line, end_line_ctx + 1):
            line_content = lines[i - 1].rstrip('\n')
            line_prefix = f"{i:>{line_num_width}} | "
            builder.append(f"{line_prefix}{line_content}")

            # Add marker and error message if this is the error line
            if i == line_num:
                # Calculate marker position (column is 0-indexed within content)
                marker_length = 1
                if end_line == line_num and end_col > col_num:
                    marker_length = end_col - col_num

                # Create the marker line with proper gutter prefix
                gutter = " " * line_num_width + " | "
                marker_line = gutter + " " * col_num + "^" * marker_length
                builder.append(marker_line)

                # Add blank line for spacing
                builder.append(" " * line_num_width + " │")

                # Frame the error message in a beautiful box
                box_prefix = " " * line_num_width + " "
                error_lines = data.split('\n')

                # Top border
                builder.append(f"{box_prefix}╭─────────────────────────────────────────────")

                # Error content with left border
                for error_line in error_lines:
                    builder.append(f"{box_prefix}│ {error_line}")

                # Bottom border
                builder.append(f"{box_prefix}╰─────────────────────────────────────────────")

        return "\n".join(builder)

    def check_file_rendered(self, filepath: str) -> str:
        """
        Check a Lean 4 file and return rendered diagnostics.

        Args:
            filepath: The file path to check (e.g., "Semantic/Fsub/Soundness.lean")

        Returns:
            Rendered diagnostics as a string
        """
        result = self.check_file(filepath)
        return self.render_result(result, filepath)


# Global project instance
PROJECT: Lean4Project | None = None

# Initialize the MCP server
mcp = FastMCP("lean4check")


@mcp.tool()
def check(filepath: str) -> str:
    """
    Check a Lean 4 file for type errors and proof failures.

    Executes the Lean 4 compiler via lake and presents diagnostics in a
    human-readable format. Each error includes the offending code with
    surrounding context, precise column markers, and detailed error
    explanations in a visually distinct frame.

    Args:
        filepath: Relative path from project root (e.g., "Semantic/Fsub/Soundness.lean")

    Returns:
        Formatted diagnostics with source context, or "No issues found." if successful.
        Returns error message if project structure is invalid or compilation fails.
    """
    if PROJECT is None:
        return "Error: No Lean 4 project root specified. Use --root argument."

    return PROJECT.check_file_rendered(filepath)


def main():
    """Main entry point for the lean4check MCP server."""
    global PROJECT

    parser = argparse.ArgumentParser(
        description="Lean 4 build wrapper MCP server"
    )
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory of the Lean 4 project"
    )

    args = parser.parse_args()
    PROJECT = Lean4Project(args.root.resolve())

    # Run the server with stdio transport
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
