from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from prewire.schemas import MemoOutput


def render_html(memo: MemoOutput, template_dir: Path) -> str:
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape())
    template = env.get_template("memo.html")
    return template.render(memo=memo)


def export_json(memo: MemoOutput, output_path: Path) -> None:
    output_path.write_text(json.dumps(memo.model_dump(), indent=2), encoding="utf-8")


def export_html(memo: MemoOutput, output_path: Path, template_dir: Path) -> None:
    output_path.write_text(render_html(memo, template_dir), encoding="utf-8")


def export_pdf(memo: MemoOutput, output_path: Path, template_dir: Path) -> None:
    html = render_html(memo, template_dir)
    HTML(string=html).write_pdf(str(output_path))


def export_all(
    memo: MemoOutput,
    output_dir: Path,
    template_dir: Path,
) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "json": output_dir / f"memo_{memo.run_id}.json",
        "html": output_dir / f"memo_{memo.run_id}.html",
        "pdf": output_dir / f"memo_{memo.run_id}.pdf",
    }
    export_json(memo, outputs["json"])
    export_html(memo, outputs["html"], template_dir)
    export_pdf(memo, outputs["pdf"], template_dir)
    return outputs
