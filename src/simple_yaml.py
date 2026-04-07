from __future__ import annotations

import ast


class SimpleYamlError(ValueError):
    """Raised when the limited YAML subset cannot be parsed."""


def safe_load(text: str):
    lines = _prepare_lines(text)
    if not lines:
        return None
    value, index = _parse_block(lines, 0, lines[0].indent)
    if index != len(lines):
        raise SimpleYamlError("unexpected trailing YAML content")
    return value


class _Line:
    __slots__ = ("indent", "content")

    def __init__(self, indent: int, content: str):
        self.indent = indent
        self.content = content


def _prepare_lines(text: str) -> list[_Line]:
    prepared: list[_Line] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        prepared.append(_Line(indent, stripped))
    return prepared


def _parse_block(lines: list[_Line], index: int, indent: int):
    if index >= len(lines):
        raise SimpleYamlError("expected block, found end of file")
    if lines[index].indent != indent:
        raise SimpleYamlError(f"expected indent {indent}, found {lines[index].indent}")
    if lines[index].content.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_mapping(lines, index, indent)


def _parse_mapping(lines: list[_Line], index: int, indent: int):
    result = {}
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent != indent:
            raise SimpleYamlError(f"unexpected indent {line.indent} in mapping")
        if line.content.startswith("- "):
            break

        key, value_text = _split_key_value(line.content)
        if value_text == "":
            next_index = index + 1
            if next_index >= len(lines) or lines[next_index].indent <= indent:
                result[key] = {}
                index = next_index
                continue
            value, index = _parse_block(lines, next_index, lines[next_index].indent)
            result[key] = value
            continue

        result[key] = _parse_scalar(value_text)
        index += 1
    return result, index


def _parse_list(lines: list[_Line], index: int, indent: int):
    result = []
    while index < len(lines):
        line = lines[index]
        if line.indent < indent:
            break
        if line.indent != indent or not line.content.startswith("- "):
            break

        item_text = line.content[2:].strip()
        if item_text == "":
            next_index = index + 1
            if next_index >= len(lines) or lines[next_index].indent <= indent:
                result.append(None)
                index = next_index
                continue
            value, index = _parse_block(lines, next_index, lines[next_index].indent)
            result.append(value)
            continue

        if ":" in item_text:
            key, value_text = _split_key_value(item_text)
            item = {}
            next_indent = indent + 2
            if value_text == "":
                next_index = index + 1
                if next_index < len(lines) and lines[next_index].indent > indent:
                    value, index = _parse_block(lines, next_index, lines[next_index].indent)
                else:
                    value = {}
                    index = next_index
            else:
                value = _parse_scalar(value_text)
                index += 1
            item[key] = value

            if index < len(lines) and lines[index].indent > indent:
                extra, index = _parse_mapping(lines, index, next_indent)
                item.update(extra)
            result.append(item)
            continue

        result.append(_parse_scalar(item_text))
        index += 1
    return result, index


def _split_key_value(content: str) -> tuple[str, str]:
    key, separator, value = content.partition(":")
    if not separator:
        raise SimpleYamlError(f"expected ':' in line: {content}")
    return key.strip(), value.strip()


def _parse_scalar(value_text: str):
    if value_text == "[]":
        return []
    if value_text == "{}":
        return {}
    if value_text == "true":
        return True
    if value_text == "false":
        return False
    if value_text in {"null", "None"}:
        return None
    if value_text.startswith(("'", '"')):
        return ast.literal_eval(value_text)
    if value_text.lstrip("-").isdigit():
        return int(value_text)
    return value_text
