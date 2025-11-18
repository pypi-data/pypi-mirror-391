#!/usr/bin/env python3
"""
MCP Server: mcp-cloud-azure

Read-only wrapper for the Azure CLI with a subscription search helper.
"""

import json
import logging
import os
import shlex
import subprocess
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP  # type: ignore[import]


cloud_logger = logging.getLogger("mcp.cloud.azure")
cloud_logger.setLevel(logging.INFO)


def _parse_command(command: str) -> List[str]:
    operators = ["|", "&&", "||", ";"]
    result: List[str] = []
    current_cmd = ""
    i = 0
    while i < len(command):
        for op in operators:
            if command[i:].startswith(op):
                if current_cmd.strip():
                    result.append(current_cmd.strip())
                current_cmd = ""
                i += len(op)
                break
        else:
            current_cmd += command[i]
            i += 1
    if current_cmd.strip():
        result.append(current_cmd.strip())
    return result


def _extract_positional(parts: List[str], tool_name: str) -> List[str]:
    positional: List[str] = []
    try:
        tool_index = parts.index(tool_name)
    except ValueError:
        return positional

    i = tool_index + 1
    skip_next_value = False
    while i < len(parts):
        token = parts[i]
        if skip_next_value:
            skip_next_value = False
            i += 1
            continue
        if token.startswith("-"):
            if "=" not in token and i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                skip_next_value = True
            i += 1
            continue
        positional.append(token)
        i += 1
    return positional


def _validate_and_run(command: str, allowed: List[str], disallowed_opts: List[str]) -> Dict[str, Any]:
    try:
        full_command = command if command.strip().startswith("az") else f"az {command}"

        for sub_cmd in _parse_command(full_command):
            parts = shlex.split(sub_cmd)
            positional = _extract_positional(parts, "az")
            if not positional:
                raise ValueError("Invalid az command: missing target resource or action")
            verb = positional[-1]
            if not any(verb == a or verb.startswith(a) for a in allowed):
                raise ValueError(f"Only read-only az verbs allowed: {', '.join(allowed)}")
            if any(opt in parts for opt in disallowed_opts):
                raise ValueError(f"Disallowed options detected: {', '.join(disallowed_opts)}")

        proc = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()

        if proc.returncode != 0:
            if not err.strip():
                return {"output": "Command executed successfully but returned no output."}
            return {"error": f"Error running az command: {err}"}

        if out.strip():
            return {"output": out}
        if err.strip():
            return {"output": err}
        return {"output": "Command executed successfully but returned no output."}
    except Exception as exc:
        return {"error": f"Error executing az command: {exc}"}


def _ensure_azure_login() -> None:
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        cloud_logger.info(
            "Azure service principal env vars not fully set; skipping automatic login."
        )
        return

    try:
        check = subprocess.run(
            ["az", "account", "show"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if check.returncode == 0:
            return
    except FileNotFoundError as exc:
        cloud_logger.error("Azure CLI not found: %s", exc)
        return

    login_cmd = [
        "az",
        "login",
        "--service-principal",
        "--tenant",
        tenant_id,
        "--username",
        client_id,
        "--password",
        client_secret,
    ]
    cloud_logger.info("Performing Azure CLI login with service principal")
    proc = subprocess.run(login_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        cloud_logger.error("Azure CLI login failed: %s", proc.stderr.strip())
    else:
        cloud_logger.info("Azure CLI login succeeded")


def _subscription_required(positional: List[str]) -> bool:
    if not positional:
        return False
    exempt_groups = {"account", "configure", "extension", "feedback", "find", "help", "login", "logout", "version"}
    if positional[0] in exempt_groups:
        return False
    return True


def create_server() -> FastMCP:
    _ensure_azure_login()

    mcp = FastMCP("mcp-cloud-azure")

    allowed_verbs = [
        "check",
        "describe",
        "estimate",
        "export",
        "find",
        "get",
        "inspect",
        "list",
        "preview",
        "query",
        "retrieve",
        "search",
        "show",
        "summarize",
        "validate",
        "view",
    ]

    @mcp.tool()
    def az(command: str) -> str:
        """Execute a read-only Azure CLI command. Requires --subscription."""
        if not command:
            return "No Azure CLI command provided"

        full_command = command if command.strip().startswith("az") else f"az {command}"
        positional = _extract_positional(shlex.split(full_command), "az")

        if _subscription_required(positional) and "--subscription" not in command:
            return "Error: The --subscription option is required to specify which Azure subscription to use. Format: '<group> <resource> <action> [parameters] --subscription <subscription_id>'"

        res = _validate_and_run(
            command,
            allowed=allowed_verbs,
            disallowed_opts=["--yes", "--force", "--delete", "--remove"],
        )
        return res.get("output") if "output" in res else res.get("error", "Unknown error")

    @mcp.tool()
    def search_context(command: str) -> str:
        """Search Azure subscriptions by substring(s)."""
        account_res = _validate_and_run(
            "account list --output json",
            allowed=allowed_verbs,
            disallowed_opts=["--yes", "--force", "--delete", "--remove"],
        )
        if "error" in account_res:
            return f"Failed to list Azure subscriptions: {account_res['error']}"

        try:
            subscriptions = json.loads((account_res.get("output") or "[]").strip() or "[]")
        except json.JSONDecodeError as exc:
            return f"Failed to parse Azure subscriptions: {exc}"

        search_terms = [(command or "").strip().lower()]
        terms = [term for term in " ".join(search_terms).split() if term]

        def matches(sub: Dict[str, Any]) -> bool:
            if not terms:
                return True
            haystack = [
                str(sub.get("name") or "").lower(),
                str(sub.get("id") or "").lower(),
                str(sub.get("tenantId") or "").lower(),
            ]
            return all(any(term in h for h in haystack if h) for term in terms)

        filtered = [sub for sub in subscriptions if matches(sub)]

        result = [
            {
                "name": sub.get("name"),
                "id": sub.get("id"),
                "tenantId": sub.get("tenantId"),
                "state": sub.get("state"),
                "isDefault": sub.get("isDefault"),
            }
            for sub in filtered
        ]

        return json.dumps({"subscriptions": result}, indent=2)

    return mcp


if __name__ == "__main__":
    create_server().run()


def main():
    create_server().run()


