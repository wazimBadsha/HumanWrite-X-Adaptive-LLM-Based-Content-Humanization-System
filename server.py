#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Stdio / SSE Server
Enables direct native integration with Claude Desktop, Cursor, and MCP clients.
"""

import sys
import json
import asyncio
from engine import audit_content, humanize_content, compute_stylometrics, build_ticl_exemplar

def handle_mcp_message(message: dict) -> dict:
    method = message.get("method")
    msg_id = message.get("id")
    
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "audit_text",
                        "description": "Conducts a 4-dimensional stylometric audit to detect AI signatures, calculate burstiness (sigma), and assess classifier risk.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Text to audit"}
                            },
                            "required": ["text"]
                        }
                    },
                    {
                        "name": "humanize_text",
                        "description": "Transforms AI text into 100% humanized, undetectable content with jagged sentence cadence and zero RLHF tropes.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string", "description": "Text to mutate and humanize"},
                                "platform": {"type": "string", "description": "Target platform (reddit, medium, linkedin, dev_to, academic, email)"}
                            },
                            "required": ["text"]
                        }
                    },
                    {
                        "name": "generate_ticl_prompt",
                        "description": "Builds a Trial-Error-Explain (TICL) prompt block for in-context learning de-alignment.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "task_objective": {"type": "string", "description": "Task objective"},
                                "ai_trial": {"type": "string", "description": "Negative AI generation"},
                                "human_gold": {"type": "string", "description": "Human reference benchmark"}
                            },
                            "required": ["task_objective", "ai_trial", "human_gold"]
                        }
                    }
                ]
            }
        }
        
    elif method == "tools/call":
        params = message.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "audit_text":
            result = audit_content(args.get("text", ""))
        elif tool_name == "humanize_text":
            result = humanize_content(args.get("text", ""), platform=args.get("platform", "medium"))
        elif tool_name == "generate_ticl_prompt":
            block = build_ticl_exemplar(args.get("task_objective", ""), args.get("ai_trial", ""), args.get("human_gold", ""))
            result = {"ticl_prompt_block": block}
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }
            
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }
        
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "neuro-humanizer-mcp",
                    "version": "4.0.0"
                }
            }
        }
        
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {}
    }

def main():
    """Stdio loop for standard MCP execution."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            response = handle_mcp_message(msg)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
