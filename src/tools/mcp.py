"""
MCP Tool Wrapper
----------------
Provides a decorator and helper functions to make tools compatible
with the MCP (Model Context Protocol) style and enable easy logging/tracing.

Usage Example:
--------------
from src.tools.mcp import mcp_tool

@mcp_tool(name="fetch_yfinance_data", description="Get recent candles for a given FX pair.")
def get_candles(pair: str):
    ...
"""

import json
import os
import traceback
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict

# Directory for trace logs
TRACE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "traces")
os.makedirs(TRACE_DIR, exist_ok=True)


def log_tool_trace(tool_name: str, input_data: Dict[str, Any], output_data: Any, success: bool, error_msg: str = ""):
    """Logs each tool call for future evaluation and debugging."""
    trace_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "input": input_data,
        "output": output_data if success else None,
        "success": success,
        "error": error_msg or None,
    }
    trace_path = os.path.join(TRACE_DIR, f"{datetime.now(timezone.utc).strftime('%Y%m%d')}_traces.jsonl")
    with open(trace_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace_entry) + "\n")


def mcp_tool(name: str, description: str = "", fallback: Callable = None):
    """
    Decorator to make a function MCP-compatible.
    Automatically logs calls, captures errors, and returns standardized output.

    Args:
        name (str): Tool name (unique identifier).
        description (str): Short summary of the tool’s purpose.
        fallback (Callable): Optional function to call if the main one fails.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            input_payload = {"args": args, "kwargs": kwargs}
            try:
                result = func(*args, **kwargs)
                log_tool_trace(name, input_payload, result, success=True)
                return {
                    "tool": name,
                    "status": "success",
                    "data": result,
                    "description": description
                }
            except Exception as e:
                error_message = str(e)
                traceback.print_exc()
                log_tool_trace(name, input_payload, {"error": error_message}, success=False, error_msg=error_message)
                if fallback:
                    try:
                        result = fallback(*args, **kwargs)
                        log_tool_trace(name + "_fallback", input_payload, result, success=True)
                        return {
                            "tool": name,
                            "status": "fallback_success",
                            "data": result
                        }
                    except Exception as fe:
                        log_tool_trace(name + "_fallback", input_payload, {"error": str(fe)}, success=False)
                        return {
                            "tool": name,
                            "status": "failed_with_fallback_error",
                            "error": str(fe)
                        }
                return {
                    "tool": name,
                    "status": "failed",
                    "error": error_message
                }
        wrapper.mcp_name = name
        wrapper.mcp_description = description
        return wrapper
    return decorator