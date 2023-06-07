import io
import time
import webbrowser
from datetime import datetime
from importlib import resources
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO
from typing import List
from typing import Union

import orgparse
from dateutil.parser import parse as dtparse
from jinja2 import Environment
from jinja2 import FileSystemLoader
from orgparse.node import OrgNode
from orgparse.node import OrgRootNode

from . import templates


def _parse_org_body(body: str) -> List[Union[str, List[str]]]:
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


def _parse_datetime(s: Union[str, None]) -> datetime:
    t = dtparse(s) if s else None
    return t


def _education_item(edu_node: OrgNode) -> dict:
    degrees = []
    for node in edu_node.children:
        date_from = node.get_property("date_from")

        degree = {
            "degree": node.heading,
            "area": node.get_property("area"),
            "date_from": _parse_datetime(node.get_property("date_from")),
            "date_to": _parse_datetime(node.get_property("date_to")),
        }
        degrees.append(degree)

    edu_item = {
        "degrees": degrees,
        "organization": edu_node.heading,
    }
    return edu_item


def _work_item(work_node: OrgNode) -> dict:
    positions = []
    for node in work_node.children:
        position = {
            "title": node.heading,
            "date_from": _parse_datetime(node.get_property("date_from")),
            "date_to": _parse_datetime(node.get_property("date_to")),
            "body": _parse_org_body(node.body),
        }
        positions.append(position)

    work_item = {
        "organization": work_node.heading,
        "positions": positions,
    }
    return work_item


def _load_from_org(arg: Union[str, Path, IO]) -> OrgRootNode:
    arg = str(arg) if isinstance(arg, Path) else arg
    if isinstance(arg, io.TextIOBase) or (isinstance(arg, str) and Path(arg).exists()):
        parsed = orgparse.load(arg)
    elif isinstance(arg, str):
        parsed = orgparse.loads(arg)
    else:
        raise TypeError("arg is file path, org-formatted str, or file-like object")
    return parsed


def _find_resume_trees(
    node: OrgNode, resume_trees: List[OrgNode] = None
) -> List[OrgNode]:
    resume_trees = [] if resume_trees is None else resume_trees
    for child_node in node.children:
        if "resume" in child_node.tags:
            resume_trees.append(child_node)
        else:
            resume_trees.extend(_find_resume_trees(child_node))
    return resume_trees


def _resume_tree_to_context(resume_node: OrgNode) -> dict:
    nodes = resume_node.children

    work_items = [_work_item(node) for node in nodes if "work" in node.tags]
    education_items = [
        _education_item(node) for node in nodes if "education" in node.tags
    ]

    context = {
        "name": resume_node.heading,
        "website": resume_node.get_property("website"),
        "email": resume_node.get_property("email"),
        "work_items": work_items,
        "education_items": education_items,
        "now": datetime.now(),
        "root": Path(templates.__file__).parent,
    }
    return context


def _parse_context_from_org(org: Union[str, Path, IO]) -> dict:
    page = _load_from_org(org)
    resume_trees = _find_resume_trees(page[0])
    context = _resume_tree_to_context(resume_trees[0])
    return context


def _render_resume(
    meta_resume: str, scale: float = 1.0, template: str = "console"
) -> str:
    context = _parse_context_from_org(meta_resume)
    context["style"] = {"scale": scale, "icon_size": 16.0 * scale}

    content = resources.open_text(templates, f"{ template }.html.j2").read()

    tmpl = Environment(loader=FileSystemLoader(context["root"])).from_string(content)
    rendered = tmpl.render(context)
    return rendered


def _preview_html(rendered: str) -> None:
    with NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".html") as f:
        f.write(rendered)
        f.flush()

        webbrowser.open(f.name)
        time.sleep(1)


def resumake(
    org_resume: str, scale: float = 1.0, template: str = "console", ftype: str = "html"
):
    rendered = _render_resume(org_resume, scale, template)

    if ftype == "html":
        _preview_html(rendered)
    else:
        raise NotImplementedError
