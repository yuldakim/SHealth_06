#!/usr/bin/env python3
"""
Finalize an Activities stage: export transcript, scaffold report, mark README, git commit/push.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STAGES_PATH = SCRIPT_DIR / "stages.json"


def load_stages() -> dict[str, dict[str, str]]:
    with STAGES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def repo_root_from_args(path: Path | None) -> Path:
    if path:
        return path.resolve()
    return Path.cwd().resolve()


def base_name(stage: int, slug: str) -> str:
    return f"stage{stage:02d}-{slug}"


def report_template(stage: int, title: str, slug: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Stage {stage:02d} Report — {title}

- **Completed**: {now}
- **Transcript**: `Prompt/{base_name(stage, slug)}.md`

## 목표

<!-- README Activities {stage}단계 목표 요약 -->

## 수행 내용

<!-- 이번 단계에서 한 작업 (코드 변경, 분석, 테스트 등) -->

## 결과 및 산출물

<!-- 생성/수정된 파일, 테스트 결과, 주요 수치 -->

## 이슈 및 해결

<!-- 막혔던 점, AI 활용 방식, 해결 방법 -->

## 다음 단계

<!-- 다음 Activities 단계에서 할 일 -->
"""


def mark_readme_stage_done(readme: Path, stage: int, stages: dict[str, dict[str, str]]) -> bool:
    text = readme.read_text(encoding="utf-8")
    original = text

    stage_header = f"{stage}. [ ]"
    stage_done = f"{stage}. [x]"
    if stage_header not in text:
        if stage_done in text:
            return False
        raise ValueError(f"README Activities header not found: {stage_header!r}")

    start = text.index(stage_header)
    if stage < 6:
        end = text.find(f"{stage + 1}. ", start)
    else:
        end = text.find("## Activities 단계 완료 시", start)
    if end == -1:
        end = len(text)

    block = text[start:end]
    block = block.replace(stage_header, stage_done, 1)
    block = re.sub(r"- \[ \]", "- [x]", block)
    text = text[:start] + block + text[end:]

    if text == original:
        return False
    readme.write_text(text, encoding="utf-8")
    return True


def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def git_upload(repo_root: Path, stage: int, title: str, paths: list[Path], push: bool) -> None:
    run(["git", "add", "--"] + [str(p.relative_to(repo_root)) for p in paths], cwd=repo_root)
    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_root,
        capture_output=True,
    )
    if status.returncode == 0:
        print("Nothing to commit (files unchanged).")
        return

    msg = f"docs(stage{stage:02d}): {title} — Report 및 Prompt transcript 추가"
    run(["git", "commit", "-m", msg], cwd=repo_root)
    print(f"Committed: {msg}")

    if push:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        run(["git", "push", "-u", "origin", branch], cwd=repo_root)
        print(f"Pushed to origin/{branch}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize Activities stage delivery.")
    parser.add_argument("--stage", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--transcript", type=str, default=None)
    parser.add_argument("--skip-readme", action="store_true")
    parser.add_argument("--skip-git", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--overwrite-report", action="store_true")
    args = parser.parse_args()

    repo_root = repo_root_from_args(args.repo_root)
    stages = load_stages()
    info = stages[str(args.stage)]
    slug = info["slug"]
    title = info["title"]
    name = base_name(args.stage, slug)

    report_dir = repo_root / "Report"
    prompt_dir = repo_root / "Prompt"
    report_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / f"{name}.md"
    prompt_path = prompt_dir / f"{name}.md"

    export_script = SCRIPT_DIR / "export_transcript.py"
    export_cmd = [
        sys.executable,
        str(export_script),
        "--stage",
        str(args.stage),
        "--repo-root",
        str(repo_root),
        "--stage-title",
        title,
        "--base-name",
        name,
        "--output",
        str(prompt_path),
    ]
    if args.transcript:
        export_cmd.extend(["--transcript", args.transcript])

    subprocess.run(export_cmd, check=True)

    if not report_path.exists() or args.overwrite_report:
        report_path.write_text(
            report_template(args.stage, title, slug),
            encoding="utf-8",
        )
        print(f"Wrote report scaffold: {report_path}")
    else:
        print(f"Report exists (kept): {report_path}")

    readme = repo_root / "README.md"
    if not args.skip_readme and readme.is_file():
        if mark_readme_stage_done(readme, args.stage, stages):
            print(f"Marked README Activities stage {args.stage} as done.")
        else:
            print("README checkboxes: no changes (already marked or pattern mismatch).")

    if not args.skip_git:
        git_upload(
            repo_root,
            args.stage,
            title,
            [report_path, prompt_path, readme],
            push=not args.no_push,
        )

    print(f"\nStage {args.stage} delivery complete.")
    print(f"  Report:  {report_path.relative_to(repo_root)}")
    print(f"  Prompt:  {prompt_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
