import json
import subprocess

QUESTION_PREFIX = "QUESTION:"


def claude_command(config, prompt, model, add_dirs, writes, extra=()):
    args = [config.claude_bin, "-p", prompt, "--model", model]
    args += ["--output-format", "stream-json", "--verbose"]
    args += config.claude_write_args if writes else config.claude_read_args
    tools = config.claude_write_tools if writes else config.claude_read_tools
    if tools:
        args += ["--allowedTools", ",".join(tools)]
    for directory in add_dirs:
        args += ["--add-dir", directory]
    return args + list(extra)


def cursor_command(config, prompt, model, add_dirs, writes, cwd):
    args = [config.cursor_bin, "-p", prompt, "--model", model]
    args += ["--output-format", "stream-json", "--workspace", cwd]
    args += config.cursor_write_args if writes else config.cursor_read_args
    for directory in add_dirs:
        args += ["--add-dir", directory]
    return args


def build_command(config, agent, prompt, model, cwd, add_dirs, writes, resume=None):
    if agent == "claude":
        extra = ("--resume", resume) if resume else ()
        return claude_command(config, prompt, model, add_dirs, writes, extra)
    if agent == "cursor":
        return cursor_command(config, prompt, model, add_dirs, writes, cwd)
    raise ValueError(f"unknown agent: {agent}")


def run_logged(command, cwd, log_path, append=False):
    with open(log_path, "a" if append else "w") as log:
        process = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, text=True)
        return process


def _events(log_path):
    for line in log_path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def _message_text(event):
    message = event.get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


def final_result(log_path):
    result = None
    texts = []
    for event in _events(log_path):
        if event.get("type") == "result" and isinstance(event.get("result"), str):
            result = event["result"]
        elif event.get("type") == "assistant":
            text = _message_text(event)
            if text:
                texts.append(text)
    if result:
        return result
    return texts[-1] if texts else ""


def question_text(result):
    question = None
    for line in result.splitlines():
        line = line.strip()
        if line.startswith(QUESTION_PREFIX):
            question = line[len(QUESTION_PREFIX):].strip() or None
    return question


def session_id(log_path):
    found = None
    for event in _events(log_path):
        if event.get("type") in ("system", "result") and event.get("session_id"):
            found = event["session_id"]
    return found


def result_info(log_path):
    info = {
        "subtype": None,
        "is_error": False,
        "permission_denials": [],
        "usage": None,
        "cost": None,
        "models": [],
        "blocked": False,
        "question": None,
        "session_id": None,
        "has_text": False,
        "tool_uses": 0,
    }
    for event in _events(log_path):
        if event.get("type") == "assistant":
            info["has_text"] = info["has_text"] or bool(_message_text(event).strip())
            content = (event.get("message") or {}).get("content")
            info["tool_uses"] += sum(
                1 for block in content if isinstance(block, dict) and block.get("type") == "tool_use"
            ) if isinstance(content, list) else 0
        if event.get("type") == "tool_call" and event.get("subtype") == "started":
            info["tool_uses"] += 1
        if event.get("type") != "result":
            continue
        info["subtype"] = event.get("subtype")
        info["is_error"] = bool(event.get("is_error"))
        info["permission_denials"] = [
            d.get("tool_name", "?") if isinstance(d, dict) else str(d)
            for d in event.get("permission_denials") or []
        ]
        info["usage"] = event.get("usage") if isinstance(event.get("usage"), dict) else None
        cost = event.get("total_cost_usd")
        info["cost"] = float(cost) if isinstance(cost, (int, float)) else None
        usage_by_model = event.get("modelUsage")
        info["models"] = list(usage_by_model) if isinstance(usage_by_model, dict) else []
    result = final_result(log_path)
    info["blocked"] = any(line.startswith("BLOCKED") for line in result.splitlines())
    info["question"] = question_text(result)
    info["session_id"] = session_id(log_path)
    return info


def pretty_lines(log_path):
    for event in _events(log_path):
        kind = event.get("type")
        if kind == "assistant":
            message = event.get("message") or {}
            for block in message.get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text" and block.get("text", "").strip():
                    yield block["text"].strip()
                elif block.get("type") == "tool_use":
                    summary = json.dumps(block.get("input", {}))[:160]
                    yield f"  > {block.get('name')} {summary}"
        elif kind == "tool_call" and event.get("subtype") == "started":
            call = event.get("tool_call") or {}
            key = next((k for k in call if k.endswith("ToolCall")), None)
            if key:
                summary = json.dumps((call[key] or {}).get("args", {}))[:160]
                yield f"  > {key[: -len('ToolCall')]} {summary}"
        elif kind == "result":
            yield f"== result ({event.get('subtype', 'done')})"
