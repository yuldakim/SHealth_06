# Agents

## Activities Stage Delivery

README **Activities 1~6단계**를 마칠 때마다 Report·대화 transcript(Prompt)·Git push를 수행한다.

### 사용법

Cursor 채팅에서:

```
@activities-stage-delivery 1단계 완료
```

또는:

```
Activities 2단계 끝났어. Report 작성하고 transcript export해서 Git에 올려줘
```

### 산출물

| Stage | Report / Prompt 파일명 |
|-------|-------------------------|
| 1 | `stage01-code-analysis.md` |
| 2 | `stage02-first-refactoring.md` |
| 3 | `stage03-unit-test.md` |
| 4 | `stage04-feature-improvement.md` |
| 5 | `stage05-retrospective.md` |
| 6 | `stage06-remaining-improvements.md` |

- `Report/` — 단계 작업 보고서
- `Prompt/` — Export Transcript (Markdown, Report와 동일 파일명)

### 수동 실행 (스크립트)

```bash
python .cursor/skills/activities-stage-delivery/scripts/finalize_stage.py --stage 1
```

옵션: `--no-push`, `--skip-git`, `--transcript path/to/session.jsonl`

스킬 상세: [.cursor/skills/activities-stage-delivery/SKILL.md](.cursor/skills/activities-stage-delivery/SKILL.md)
