# Blog B 콘텐츠 상태 추적 (Content Status Tracker)

`docs/content_operations_playbook.md`의 파이프라인(§1) 각 단계 진행 상황을 키워드 단위로 추적하는 표. 새 키워드를 시작하면 행을 추가하고, 단계가 바뀔 때마다 해당 행을 갱신한다.

컬럼 설명:
- **QA(Tech/SEO/EN)**: Technical QA / SEO·Search Intent QA / US English QA 3종의 PASS·FAIL·N/A를 `/`로 구분해 표기 (예: `PASS/PASS/PASS`).
- **Human Approval**: 미요청 / 요청됨 / 승인 / 반려.
- **Publish**: 미발행 / 발행됨(날짜) — 실제 Publish는 항상 사용자가 직접 실행.

## 현재 상태

| Keyword | Search Intent | 등급(QA policy) | Evidence | Draft | QA(Tech/SEO/EN) | Human Approval | Publish | 파일 |
|---|---|---|---|---|---|---|---|---|
| numbers stored as text bulk convert | How-to / Task | Simple Task | 완료 — Pilot F 재현 + 신규 fixture(`fixtures/numbers-stored-as-text-bulk-convert_fixture.xlsx`, 5개 method별 시트, NBSP 실제 문자 포함)로 보강. 스크린샷은 미확보(비차단, 실제 발행 전 필요) | 완료 — 운영 Draft로 전환 (`content/numbers-stored-as-text-bulk-convert.md`) | PASS/PASS/PASS (QA 패키지: `content/numbers-stored-as-text-bulk-convert_qa.md`) | 요청됨 — 이번 운영 전환분은 Pilot 단계의 포괄 승인과 별개로 개별 승인 대기 (CONTENT READY FOR HUMAN APPROVAL) | 미발행 | `content/numbers-stored-as-text-bulk-convert.md` (구 `content/pilot_F_numbers_as_text.md`는 원본 보존용으로 유지) |
| remove blank rows without breaking formulas | Troubleshooting / Fix | Edge-case Guide | 완료 (fixture 결함 2건 수정 후 재현, PASS) | 완료 | PASS/PASS/PASS (Pilot 단계에서 완료) | 승인 (FULL GO에 포함) | 미발행 | `content/pilot_G_remove_blank_rows.md` |
| power query remove duplicates (integrated guide) | Integrated / Reference guide | High-risk Integrated Guide | 완료 (Pilot A, 다중 fixture·독립검증) | 완료 (Pilot 단계 원고) | 완료 (Pilot 단계) | 승인 (FULL GO에 포함) | 미발행 | 아직 repo 미이관 (Claude Project 로그에 원고 있음) |
| excel split comma separated values into rows | Comparison / Method choice | High-risk Integrated Guide | 완료 (Pilot B) | 완료 (Pilot 단계 원고) | 완료 (Pilot 단계) | 승인 (FULL GO에 포함) | 미발행 | 아직 repo 미이관 |
| TRIM vs CHAR(160)/NBSP | Troubleshooting / Fix | Simple Task (실측 개입 높음) | 완료 (Pilot C, UNICHAR(160) 정정 반영) | 완료 (Pilot 단계 원고) | 완료 (Pilot 단계) | 승인 (조건부 — 원고에 UNICHAR 반영 확인 필요) | 미발행 | 아직 repo 미이관 |
| Power Query null vs "" | Edge-case Guide | Edge-case Guide | 완료 (Pilot D) | 완료 (Pilot 단계 원고) | 완료 (Pilot 단계) | 승인 (FULL GO에 포함) | 미발행 | 아직 repo 미이관 |
| Excel 2021 UNIQUE 대체 legacy fallback | Comparison / Method choice | Simple Task | 완료 (Pilot E) | 완료 (Pilot 단계 원고) | 완료 (Pilot 단계) | 승인 (FULL GO에 포함) | 미발행 | 아직 repo 미이관 |

**참고**: Pilot A~E는 원고가 아직 이 repo의 `content/`로 이관되지 않았다(우선순위 낮음, `docs/pilot_results.md` 참고). 이관 시 이 표의 "파일" 컬럼을 갱신한다.

## 다음에 추가할 키워드 (아직 착수 전)

이 표에 아직 행이 없는 새 키워드는 `docs/content_operations_playbook.md` §1의 파이프라인을 따라 진행하면서, 착수 시점에 이 표에 행을 추가한다.

---

*최초 작성: 2026-09-15 (로드맵 5단계). Pilot A~G 초기 상태는 `docs/pilot_results.md`와 Claude Project 결정 로그를 근거로 이 표에 옮겨 적었다.*
