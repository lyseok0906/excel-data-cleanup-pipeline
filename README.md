# excel-data-cleanup-pipeline (Blog B)

Excel Data Cleanup & Transformation 니치 블로그의 콘텐츠·QA 파이프라인 저장소.

이 저장소는 GitHub를 Single Source of Truth(SSoT)로 사용하는 Blog A(`economic-blog-pipeline`) 운영 방식을 그대로 따른다:
`docs/`가 정본(SSoT)이며, Claude Project의 `claude/` 문서는 캐시로만 취급한다.

## 상태

- **Gate**: `FULL GO` (사용자 최종 확정, 2026-09-15)
- Pilot A~G 총 7건 검증 완료, 기술 오류 0건, 재현 성공 7/7
- Site·Domain·Repo·Skill·Publish HOLD 해제됨 (실행은 각 단계별 사용자 승인 후 진행)

## 역할 분담 (Blog A와 동일 원칙 적용)

| 역할 | 담당 |
|---|---|
| 시장 조사·SERP 검증 | Cowork |
| 공식출처 검증 | Cowork |
| 콘텐츠 기획·작성 | Cowork |
| `docs/` 작성·수정 | Cowork |
| `git add` / `git commit` | Cowork (device 접속 시) |
| 최종 `git push` | 사용자 |
| 사실관계·논리·문체 검수 | ChatGPT / 사용자 |

## 디렉터리 구조

```
docs/
  content_operations_playbook.md — 콘텐츠 운영 규칙 정본 (Keyword→Publish 전체 파이프라인, QA 체크리스트, commit 규칙)
  content_status.md              — 키워드별 진행 상태 추적표
  qa_policy.md                   — 3단계 검증 강도 운영모델 + Excel 버전 정책
  pilot_results.md               — Pilot A~G 결과 요약 (상세 원본은 Claude Project 결정 로그)
content/
  pilot_F_numbers_as_text.md
  pilot_G_remove_blank_rows.md
fixtures/
  pilot_FG_fixture_v2.xlsx
evidence/
  (재현 스크린샷 등 필요 시 키워드별 하위 폴더 생성 — docs/content_operations_playbook.md §5 참고)
```

## 콘텐츠 운영 규칙

새 원고를 조사·작성·발행하는 전체 절차(공식 출처 우선순위, 재현 필요/불필요 구분, QA 3종 체크리스트, Human Approval, commit/파일명 규칙)는 [`docs/content_operations_playbook.md`](docs/content_operations_playbook.md)에 정리되어 있다. 실제 Publish는 이 문서의 절차를 따르되 항상 사용자가 직접 실행한다.

## 참고

- 전체 의사결정 히스토리(2026-09-03부터)는 Claude Project 문서 `claude/비즈니스_방향_결정_로그.md`에 남아 있으며, 이 repo가 정식으로 SSoT가 된 이후의 신규 결정은 이 저장소의 `docs/`에 직접 기록한다.
- Pilot A/B/C/D/E의 원본 초안·fixture는 아직 이 저장소로 이관되지 않았다(F/G만 우선 이관). 후속 커밋에서 추가 예정.
