---
name: activities-stage-delivery
description: >-
  SHealth Activities 1~6단계 완료 시 Report/Prompt Markdown 작성, 대화
  transcript export, README 체크박스 갱신, Git commit/push까지 수행. Use when
  the user finishes an Activities stage, says "N단계 완료", "stage N done",
  requests stage report, Export Transcript, or Git upload for Report/Prompt.
---

# Activities Stage Delivery Agent

README.md **생성형AI를 활용한 Activities** 1~6단계가 끝날 때마다 아래를 수행한다.

## 산출물 규칙

| 항목 | 경로 | 파일명 |
|------|------|--------|
| Report | `Report/` | `stage{NN}-{slug}.md` |
| Transcript (Prompt) | `Prompt/` | Report와 **동일 파일명** |
| Git | 현재 브랜치 → `origin` push | — |

단계별 `slug`는 [scripts/stages.json](scripts/stages.json) 참고.

| Stage | slug | 제목 |
|-------|------|------|
| 1 | `code-analysis` | 문제 코드 분석 및 코드 스멜 찾기 |
| 2 | `first-refactoring` | 1차 리펙토링 |
| 3 | `unit-test` | UnitTest 작성 |
| 4 | `feature-improvement` | 기능 개선 |
| 5 | `retrospective` | 회고 및 발표 |
| 6 | `remaining-improvements` | 남은 단점 및 개선 |

예: 1단계 → `Report/stage01-code-analysis.md`, `Prompt/stage01-code-analysis.md`

## 워크플로 (단계 완료 시 필수)

사용자가 **N단계(1~6) 완료**를 알리면 다음 순서를 따른다.

### 1. Report 작성

`Report/stage{NN}-{slug}.md`에 아래 섹션을 **실제 작업 내용**으로 채운다.

- 목표
- 수행 내용
- 결과 및 산출물
- 이슈 및 해결
- 다음 단계

스크립트가 만든 빈 템플릿이 있으면 덮어써서 완성한다.

### 2. Transcript export → Prompt

대화 전체를 Markdown으로 `Prompt/`에 저장한다. **Report와 동일한 basename**.

1. **우선**: Cursor 메뉴 **Export Transcript**로보낸 Markdown이 있으면, 그 내용을 `Prompt/stage{NN}-{slug}.md`에 반영(가장 완전함).
2. **자동**: 아래 스크립트로 agent jsonl을 변환한다.

```bash
python .cursor/skills/activities-stage-delivery/scripts/finalize_stage.py --stage N --repo-root .
```

`--transcript`로 특정 `.jsonl` 경로 지정 가능.  
환경변수 `CURSOR_AGENT_TRANSCRIPTS_DIR`에 transcript 폴더를 지정할 수 있다.

### 3. README 체크박스

해당 단계의 `1. []` / `- []`를 `[x]`로 갱신한다.  
`finalize_stage.py`가 자동 처리한다.

### 4. Git 업로드

같은 스크립트가 `Report/`, `Prompt/`, `README.md`를 add → commit → **push**한다.

- 커밋 메시지: `docs(stageNN): {제목} — Report 및 Prompt transcript 추가`
- push 실패 시 원인을 보고하고 사용자에게 인증/네트워크 확인 요청
- 사용자가 push를 원하지 않으면 `--no-push` 사용

Report를 먼저 직접 작성한 뒤 transcript·git만 실행:

```bash
python .cursor/skills/activities-stage-delivery/scripts/finalize_stage.py --stage N --overwrite-report
```

Git 없이 파일만:

```bash
python .cursor/skills/activities-stage-delivery/scripts/finalize_stage.py --stage N --skip-git
```

### 5. 사용자에게 보고

- 생성된 Report / Prompt 경로
- 커밋 해시·push된 브랜치
- README에서 체크된 항목 요약

## 트리거 문구 예시

- `@activities-stage-delivery 2단계 완료`
- `Activities 3단계 끝났어. Report랑 Prompt 만들고 Git에 올려줘`
- `stage 4 delivery`

## 주의

- **한 번에 한 단계**만 처리한다.
- Report 본문은 스크립트가 생성하지 않는다 — **에이전트가 반드시 작성**한다.
- transcript jsonl에 `[REDACTED]`가 많으면 Export Transcript 본문을 Prompt에 넣을 것.
- `Refactoring` 브랜치에서 작업 중이면 그 브랜치에 push한다.

## 추가 자료

- Report 상세 템플릿: [reference.md](reference.md)
