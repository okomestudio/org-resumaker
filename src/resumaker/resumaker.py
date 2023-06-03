import time
import webbrowser
from datetime import datetime
from importlib import resources
from pathlib import Path
from tempfile import NamedTemporaryFile

import orgparse
from jinja2 import Environment, FileSystemLoader

from . import templates


def _parse_body(body):
    lines = []
    line_buffer = []
    for line in (l for l in body.strip().split("\n") if l):
        if line.startswith("-"):
            line_buffer.append(line.split(maxsplit=1)[1])
        else:
            if line_buffer:
                lines.append(line_buffer)
                line_buffer = []
            lines.append(line)
    if line_buffer:
        lines.append(line_buffer)
    return lines


def _education_item(node):
    d = {
        "degree": node.get_property("degree"),
        "area": node.get_property("area"),
        "organization": node.get_property("organization"),
        "date": node.get_property("date"),
    }
    return d


def _work_item(node):
    d = {
        "job_title": node.get_property("job_title"),
        "organization": node.get_property("organization"),
        "date_from": node.get_property("date_from"),
        "date_to": node.get_property("date_to"),
        "body": _parse_body(node.body),
    }
    return d


def _parse_meta_resume(meta_resume: str, scale: float = 1.0) -> dict:
    page = orgparse.load(meta_resume)

    root = page[1]
    nodes = root.children
    work_items = [_work_item(node) for node in nodes if "work" in node.tags]
    education_items = [
        _education_item(node) for node in nodes if "education" in node.tags
    ]

    context = {
        "name": root.heading,
        "website": root.get_property("website"),
        "email": root.get_property("email"),
        "work_items": work_items,
        "education_items": education_items,
        "scale": scale,
        "icon_size": 16.0 * scale,
        "now": datetime.now(),
    }
    return context


def _render_resume(context: dict) -> str:
    dirpath = Path(templates.__file__).parent
    context["root"] = dirpath

    content = resources.open_text(templates, "content.html.j2").read()

    tmpl = Environment(loader=FileSystemLoader(dirpath)).from_string(content)

    rendered = tmpl.render(context)
    return rendered


def _preview(rendered: str) -> None:
    with NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".html") as f:
        f.write(rendered)
        f.flush()

        webbrowser.open(f.name)
        time.sleep(1)


def resumake(meta_resume: str, scale: float):
    context = _parse_meta_resume(meta_resume, scale)
    rendered = _render_resume(context)
    _preview(rendered)
