# Blog B 콘텐츠 운영 규칙 (Content Operations Playbook)

이 문서는 CleanSheetHQ(Blog B)를 **AI 대량발행 블로그가 아니라, 검증 가능한 US-English Excel 가이드를 일관되게 생산하는 운영 파이프라인**으로 만들기 위한 정본(SSoT) 운영 규칙이다.

이 문서는 기존 문서를 복제하지 않는다:
- 검증 강도 3단계 모델·알려진 콘텐츠 함정·Excel 버전 정책은 [`docs/qa_policy.md`](./qa_policy.md)가 정본이며, 이 문서는 그것을 파이프라인 단계에 배치하는 방법만 다룬다.
- Pilot A~G 실측 기록과 근거는 [`docs/pilot_results.md`](./pilot_results.md)와 Claude Project `claude/비즈니스_방향_결정_로그.md`가 정본이다.
- 콘텐츠별 현재 상태(어느 단계인지)는 [`docs/content_status.md`](./content_status.md)에서 추적한다. 이 문서를 수정할 필요는 없다.

역할 분담(`README.md`의 표를 그대로 따름): Cowork가 조사·초안·QA·`docs/` 및 `content/` 작성과 `git add`/`commit`을 수행하고, **실제 `git push`와 실제 WordPress 발행(Publish)은 항상 사용자 승인 이후 사용자가 직접 실행**한다. Cowork는 이 두 가지를 절대 자동으로 수행하지 않는다.

---

## 1. 전체 파이프라인

```
Keyword 선정
   ↓
Search Intent 분류
   ↓
Evidence 수집 (공식 문서 우선 + 필요시 실제 재현)
   ↓
Draft 작성 (US English)
   ↓
QA (Technical / SEO·Search Intent / US English, 3종)
   ↓
Human Approval  ← 사용자가 명시적으로 승인해야만 다음 단계로 진행
   ↓
Publish (WordPress) ← 항상 사용자가 직접 실행
```

각 단계의 결과는 [`docs/content_status.md`](./content_status.md)의 해당 키워드 행에 기록한다. 어떤 단계도 건너뛰고 다음 단계로 넘어가지 않는다 — 특히 **QA를 통과하지 않은 원고는 Human Approval 단계로 올리지 않고, Human Approval을 받지 않은 원고는 Publish 단계로 진행하지 않는다.**

### 1.1 Keyword 선정

- 니치 경계: Excel Data Cleanup & Transformation. 미국/영어권 검색자 대상.
- 콘텐츠 전략(확정, 폐기하지 않음): medium-tail task → deep integrated guide → 필요한 edge case만 통합. ultra-specific long-tail(키워드 1개 = 글 1개) 전략은 사용하지 않는다.
- 서로 다른 Search Intent를 억지로 한 글에 통합하지 않는다(T1/T4 분리 결정과 동일한 원칙 — Formula behavior와 Version compatibility는 서로 다른 글로 유지).

### 1.2 Search Intent 분류

키워드마다 아래 중 하나로 분류하고 `content_status.md`에 기록한다:

| Intent 유형 | 설명 | 예 |
|---|---|---|
| **How-to / Task** | "어떻게 하는가"에 대한 단계별 절차 | numbers stored as text bulk convert |
| **Troubleshooting / Fix** | 특정 오류·비정상 동작의 원인과 해결 | TRIM vs CHAR(160)/NBSP |
| **Comparison / Method choice** | 여러 방법·버전 중 무엇을 쓸지 | Excel 2021 UNIQUE 대체 방법 |
| **Integrated / Reference guide** | 여러 서브케이스를 포함하는 종합 가이드 | Power Query remove duplicates |

Search Intent는 제목·구조·QA(§4.2) 기준을 결정하므로 Draft 작성 전에 반드시 확정한다.

### 1.3 Evidence 수집

§2(출처 우선순위)와 §3(재현 필요/불필요 구분)을 따른다.

### 1.4 Draft 작성

- 언어: US English. 어색한 번역투·비영어권 표현 금지(원어민 관점 문체 — Pilot F/G가 이미 이 기준을 통과한 참고 샘플).
- 구조는 Search Intent에 맞춘다(§4.2 SEO/Search Intent QA 체크리스트 참고).
- §2에서 확정한 공식 근거와 §3에서 확정한 재현 결과를 그대로 인용한다 — Draft 단계에서 새로운 기술적 주장을 임의로 추가하지 않는다.

### 1.5 QA

§4(QA 체크리스트) 3종을 모두 통과해야 한다. 통과 여부는 `content_status.md`에 각각 기록한다.

### 1.6 Human Approval

- QA 3종을 통과한 원고만 사용자에게 승인을 요청한다.
- 승인은 매번 명시적으로 받는다 — 과거 승인이나 "전체적으로 진행해도 된다"는 포괄적 발언을 특정 원고의 승인으로 확대 해석하지 않는다.
- 승인/반려/보류 결과를 `content_status.md`에 기록한다.

### 1.7 Publish

- Publish(WordPress에 실제로 올리는 것)는 Human Approval 이후 **사용자가 직접** 실행한다.
- Cowork는 WordPress에 초안을 준비(예: 임시 텍스트 정리, 이미지 alt 제안 등)까지는 요청 시 도울 수 있으나, 최종 "Publish" 버튼 클릭 또는 그에 준하는 발행 확정 동작은 수행하지 않는다.
- 자동발행 파이프라인, 발행 스케줄러, 외부 SNS 연동 등은 이 프로젝트 범위에 포함하지 않는다(§6).

---

## 2. 출처 우선순위 — 공식 Microsoft 문서 우선

### 2.1 우선순위

1. **1순위 (공식, 그대로 인용 가능)**: Microsoft Support (`support.microsoft.com`), Microsoft Learn (`learn.microsoft.com`), Microsoft 공식 함수/기능 문서의 "Applies To"·버전 지원표.
2. **2순위 (보조, 조건부 사용)**: 널리 알려진 Excel 전문 교육 사이트(예: ExcelJet, Ablebits, Contextures, Microsoft MVP 블로그) — 아래 2.2 조건을 만족할 때만 사용.
3. **사용하지 않음**: 출처가 불분명한 커뮤니티 게시글, 포럼 답변, 검증되지 않은 SEO 대행사 글 — 이런 자료가 유일한 근거인 주장은 채택하지 않는다. (예: Pilot E에서 "Excel 2021이 UNIQUE를 지원하지 않는다"는 Microsoft Q&A 게시물을 근거로 채택하지 않기로 확정한 사례.)

### 2.2 2차 출처 사용 조건

2차 출처는 아래 조건을 **모두** 만족할 때만 보조 자료로 사용한다:

1. 공식 문서에 없는 실무 팁·대안 방법을 보충하는 용도로만 사용한다(핵심 기술 주장의 유일한 근거로 사용하지 않는다).
2. 초안에는 해당 문장이 2차 출처 기반임을 내부 노트(`content_status.md`의 Evidence 비고, 또는 Draft 내부 주석)로 남긴다.
3. 재현 가능한 주장(§3)이면, 출처 신뢰도와 무관하게 반드시 실제로 재현해서 확인한다 — 2차 출처가 "믿을 만해서" 재현을 생략하지 않는다.
4. 공식 문서와 상충하면 공식 문서를 따른다.

---

## 3. 재현이 필요한 주장 vs 재현이 필요 없는 주장

| 구분 | 예 | 처리 |
|---|---|---|
| **재현 불필요** | 함수의 버전별 지원 여부(공식 지원표에 명시), 함수 문법·인자 정의, Microsoft가 명시한 표준 동작(예: 기본 Remove Duplicates가 첫 항목을 유지한다는 사실) | 공식 문서를 그대로 인용. 링크·문서명을 Evidence로 기록. |
| **재현 필요** | 특정 버전/로케일/환경에서의 실제 결과, edge case(빈 값·null·중복 키·특수문자) 처리 결과, 여러 함수를 조합했을 때의 실제 출력, "이 방법이 실무에서 통한다"는 주장 | `docs/qa_policy.md`의 등급(Simple/Edge-case/High-risk)에 따라 실제 Excel/Power Query에서 재현하고 스크린샷 또는 fixture 결과를 근거로 남긴다. |

**우선순위 규칙(기존 결정 유지)**: 실측 재현 결과가 과거의 설계 단계 가정이나 공식 문서 해석과 충돌하면, **최신 실측 결과를 우선**한다. 단, 공식 문서 자체가 명시적으로 확정한 사실(예: 버전 지원표)을 근거 없는 커뮤니티 정보로 뒤집지는 않는다.

애매한 경우(재현이 필요한지 판단이 안 서는 경우)에는 재현 필요 쪽으로 판단한다 — 재현 누락으로 발행 후 오류가 발견되는 비용이 재현 1회 비용보다 크다.

---

## 4. QA 체크리스트

QA는 3종을 모두 수행하고 `content_status.md`에 개별로 PASS/FAIL을 기록한다. 하나라도 FAIL이면 Human Approval 단계로 올리지 않는다.

### 4.1 Technical QA

- [ ] 모든 기술적 주장이 §2(출처 우선순위) 기준을 만족하는 근거를 갖고 있다.
- [ ] §3에 따라 재현이 필요한 주장은 실제로 재현되었고, 등급에 맞는 검증 강도(`docs/qa_policy.md`)를 만족한다.
- [ ] `docs/qa_policy.md`의 알려진 함정(CHAR(160) 로케일 버그, null vs `""`, Go To Special→Blanks 범위) 중 해당되는 항목이 있으면 원고에 정확히 반영되어 있다.
- [ ] `docs/qa_policy.md`의 Excel 버전 정책에 따라 버전 지원 여부가 정확하고, 필요한 경우 legacy fallback 섹션이 포함되어 있다.
- [ ] 원고에 등장하는 수식·M코드·단축키가 실제로 실행 가능한 형태로 정확히 표기되어 있다(오타·괄호 누락 없음).
- [ ] 재현에 사용한 스크린샷/fixture가 §5 저장 규칙에 따라 저장되고 원고에서 참조 가능하다.

### 4.2 SEO / Search Intent QA

- [ ] 제목(H1)이 대상 키워드와 §1.2에서 분류한 Search Intent를 명확히 반영한다.
- [ ] 본문 구조(H2/H3)가 Intent 유형에 맞는 형태다 — How-to는 번호 매긴 단계, Troubleshooting은 원인→해결 순서, Comparison은 방법별 비교, Integrated guide는 서브케이스별 섹션.
- [ ] 서로 다른 Search Intent를 한 글에 억지로 통합하지 않았다(§1.1 원칙 확인).
- [ ] 메타 디스크립션 초안이 있다(실제 입력은 발행 단계에서 Rank Math에 사용자가 직접 입력).
- [ ] 경쟁 상위 노출 글이 다루지 않는 실측 기반 차별점(예: 로케일 버그, 실제 실패 사례)이 최소 1개 이상 포함되어 있는지 확인한다(없으면 이유를 기록).
- [ ] 키워드 스터핑 없음 — 자연스러운 빈도로만 등장한다.

### 4.3 US English QA

- [ ] 번역투 표현이 없고, 원어민 관점에서 자연스럽다(Pilot F/G 원고가 이미 통과한 문체 기준을 참고 샘플로 사용).
- [ ] 용어 일관성 — 같은 개념을 문서 내내 같은 용어로 지칭한다(예: "column" vs "field" 혼용 금지, "Power Query" 대소문자·표기 일관).
- [ ] 문법·시제·관사 오류가 없다.
- [ ] 남아있는 한국어·번역 잔재, 또는 어색한 직역 표현이 없다.
- [ ] 문단·문장 길이가 웹 가독성 기준(짧은 문단, 명확한 단계 구분)에 맞는다.

---

## 5. 스크린샷·fixture·증적(Evidence) 저장 규칙

- **Fixture 파일**(`.xlsx` 등 재현용 원본 데이터): `fixtures/`에 저장. 파일명은 `<keyword-slug>_fixture.xlsx` 형식(기존 `pilot_FG_fixture_v2.xlsx`처럼 버전이 여러 번 바뀌면 `_v2`, `_v3` suffix 사용).
- **스크린샷/재현 증적**: `evidence/<keyword-slug>/` 폴더에 저장한다(이 폴더는 필요할 때 새로 만든다). 파일명은 무엇을 보여주는지 알 수 있게 짓는다. 예: `evidence/power-query-remove-duplicates/t2-5-tie-break-result.png`.
- 스크린샷·fixture만 저장하고 끝내지 않는다 — 해당 재현이 무엇을 확인했고 [Designed]/[Observed]/[Decision] 중 어떤 결론에 도달했는지는 `content_status.md`의 Evidence 비고 또는 원고 자체의 근거 섹션에 짧게 남긴다(Pilot 로그처럼 장문으로 남길 필요는 없다 — 그 상세 기록은 필요할 때만 Claude Project 로그에 남긴다).
- 재현이 필요 없는 주장(§3)은 fixture/스크린샷 없이 공식 문서 링크만으로 충분하다 — 불필요한 evidence 파일을 만들지 않는다.

---

## 6. GitHub 파일명·저장·commit 규칙

### 6.1 디렉터리

```
content/   — 발행용 원고 (Markdown)
docs/      — 운영 규칙·정책·상태 추적 (이 문서들)
fixtures/  — 재현용 Excel 파일
evidence/  — 스크린샷 등 재현 증적 (필요 시 생성)
```

### 6.2 파일명 규칙

- **원고(`content/`)**: 이번 5단계부터는 `<keyword-slug>.md` 형식을 기본으로 한다(kebab-case, 영문 키워드 그대로). 예: `content/power-query-remove-duplicates.md`.
  - 기존 `content/pilot_F_numbers_as_text.md`, `content/pilot_G_remove_blank_rows.md`는 Pilot 단계 산물임을 남기기 위해 **그대로 유지**한다(리네임하지 않음 — 불필요한 churn 방지). 새 원고부터 새 규칙을 적용한다.
- **Fixture(`fixtures/`)**: `<keyword-slug>_fixture.xlsx` (필요 시 `_v2` 등 버전 suffix).
- **Evidence(`evidence/`)**: `evidence/<keyword-slug>/<간단한-설명>.png`.

### 6.3 Commit 규칙

- 커밋 메시지는 Blog A와 동일하게 conventional 스타일 접두사를 사용한다: `feat:`(신규 원고/기능), `docs:`(운영 문서), `fix:`(원고 오류 수정), `chore:`(잡다한 정리).
  예: `feat: add power-query-remove-duplicates guide (CONTENT READY)`, `docs: add content operations playbook`.
- 원고 상태(`DRAFT` / `QA PASS` / `CONTENT READY`)를 커밋 메시지에 괄호로 표기하면 히스토리에서 추적하기 쉽다.
- **`git add`/`git commit`은 Cowork가 수행**하고, **`git push`는 항상 사용자가 직접 실행**한다(README 역할 분담표와 동일). Cowork는 어떤 경우에도 자동으로 push하지 않는다.

---

## 7. 상태 추적

콘텐츠별 현재 단계(Keyword 선정 → … → Publish)와 QA 3종 결과, Human Approval 여부는 [`docs/content_status.md`](./content_status.md)에서 표로 추적한다. 새 키워드를 시작할 때 그 문서에 행을 추가하고, 단계가 바뀔 때마다 갱신한다. 이 문서(운영 규칙 자체)는 규칙이 바뀔 때만 수정한다.

---

## 8. 하지 않는 것 (Scope 경계)

이번 5단계 작업 범위에 포함하지 않으며, 별도의 명시적 사용자 지시 없이 추가하지 않는다:

- 불필요한 WordPress 플러그인 추가(현재 설치된 Rank Math SEO / Wordfence / LiteSpeed Cache 외 추가 없음).
- 자동발행(스케줄 발행, 초안 자동 Publish 등).
- 외부 SNS/뉴스레터 등 추가 연동.
- Pilot A~E 원고·fixture의 repo 이관(우선순위 낮음으로 이미 보류 확정 — 별도 지시 시 진행).

---

*최초 작성: 2026-09-15 (로드맵 5단계). 이 문서는 Repo 정본이며, Claude Project의 캐시 문서는 이 내용을 요약해서만 참조한다.*
