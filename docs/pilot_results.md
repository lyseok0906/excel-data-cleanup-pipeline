# Pilot A~G 결과 요약

전체 상세 근거([Designed]/[Observed]/[Decision] 형식)는 Claude Project 문서 `claude/비즈니스_방향_결정_로그.md`의 2026-09-15 절들을 참고. 이 문서는 이관용 요약본이다.

| Pilot | 주제 | 등급 | 최종 상태 |
|---|---|---|---|
| A | Power Query remove duplicates (통합 가이드) | High-risk Integrated Guide | CONTENT READY |
| B | excel split comma separated values into rows | High-risk Integrated Guide | CONTENT READY |
| C | TRIM vs CHAR(160)/NBSP | Simple Task (실측 결과 예외적으로 높은 개입) | PASS (조건부, UNICHAR 반영 필수) |
| D | Power Query null vs "" | Edge-case Guide | PASS |
| E | Excel 2021 UNIQUE 대체 legacy fallback | Simple Task | PASS |
| F | numbers stored as text bulk convert | Simple Task | CONTENT READY |
| G | remove blank rows without breaking formulas | Edge-case Guide | CONTENT READY (fixture 결함 2건 수정 후) |

## Gate 이력

1. 2026-09-10: `APPROVE FOR LIVE TEST`
2. 2026-09-15 (Pilot A/B 종결 후): Cowork 잠정 `CONDITIONAL GO CONTINUE`
3. 2026-09-15 (사용자 확정): `CONDITIONAL GO CONTINUE` (Pilot C/D/E 추가 후에도 유지)
4. 2026-09-15 (Pilot F/G 종결, 사용자 최종 확정): **`FULL GO`**

## 생산성 데이터 (스크린샷 왕복 / 추가 진단)

| Pilot | 스크린샷 왕복 | 추가 진단 | 비고 |
|---|---:|---:|---|
| C | 6회 | 다수 | 로케일 버그 근본원인 규명 비용 |
| D | 1회 | 없음 | 설계대로 경량 |
| E | 1회 | 없음 | 설계대로 경량 |
| F | 1회 | 없음 | 설계대로 경량 |
| G | 2회 | fixture 재조사 1건 | 콘텐츠 문제 아닌 fixture 제작 결함 |

## 이관 상태

- Pilot F, G의 원고·fixture는 이 저장소(`content/`, `fixtures/`)로 이관 완료.
- Pilot A~E의 원고·fixture는 아직 이 저장소에 없음 — 후속 커밋에서 이관 예정.
