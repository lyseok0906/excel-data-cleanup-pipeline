# A0-Phase1 Validation Report (10 sites) — Protocol V2

실행일: 2026-09-16 | 범위: 사이트 10개만 조사, 시장 결론 목적 아님, 스키마 QA 목적. **완료 후 STOP — 추가 40개/1000개/Study B 미실행.**

조사 니치: Productivity Software & Personal Knowledge Management (Notion/Obsidian/PARA/Zettelkasten 등) — 기존 100개 데이터셋과 중복 없는 새 니치로 선정. Contrast Cohort 25% 설계 적용: Large/Traffic Leader 3, Mid-scale 2, Narrow Niche Authority 3, Contrast Cohort 2 (n=10이라 정확히 25%×4는 불가능해 3/2/3/2로 근사).

## 1. Validation Dataset
- `validation_10.csv` (10 rows, 38 columns) — canonical root domain, category_layer, traffic(provider/metric/value/as_of_date/evidence), revenue, display_ads/affiliate/own_product/course_or_community/newsletter_email_capture(각 value/evidence/note 3분리), is_contrast_case, layer 판단 근거.
- `validation_10_notes.md` — 사이트 선정 이유, 기각한 후보(notion.so/blog, todoist.com/blog, productivityist.com, notionmastery.com, redgregory.com, lifehack.org, thesweetsetup.com)와 사유, 스키마 적용 중 발견한 6가지 모호성.

## 2. Enum Validation 결과
자동 스크립트(`run_gate.py`)로 boolean형 필드(display_ads, affiliate, own_product, course_or_community, newsletter_email_capture, is_contrast_case) 전부 검사 → **PASS**: `Y/N/UNKNOWN`, `A/B/C/D/UNKNOWN` 외 값 없음.

단, `start_year` 필드에서 **설계 결함 1건 발견**: `start_year`는 값이 연도 숫자(예: "2010")인데, evidence 컬럼(`start_year_evidence`)이 붙어 있어 제 검증 스크립트가 이를 "boolean 필드"로 오인해 10건 모두 "위반"으로 표시했습니다. 이는 실제 스키마 위반이 아니라 **Section 3 canonical schema가 "값이 Y/N/UNKNOWN이 아닌 숫자/날짜형 필드"(start_year, traffic_value, revenue_value 등)에 대한 규칙을 명시하지 않은 설계 공백**입니다. traffic_value/revenue_value는 문서에서 별도 규칙(Section 3 마지막 문단)으로 이미 다뤘지만, `start_year`류의 다른 숫자형 필드는 빠져 있었습니다.

**→ Protocol V2 수정 필요 항목(신규 발견):** "value/evidence/note 3분리" 규칙을 모든 숫자·날짜형 필드(start_year 포함)에도 명시적으로 확장 적용한다고 Section 3에 한 줄 추가 필요.

## 3. Duplicate Check
`canonical_root_domain` 10개 전부 고유. www/https/trailing slash 없는 clean root form 확인. **PASS.**

## 4. Field Completion Rate (10개 기준)
| 필드 | 비어있지 않음 | 확정(Y/N) | UNKNOWN |
|---|---|---|---|
| display_ads | 10/10 | 9/10 | 1/10 |
| affiliate | 10/10 | 6/10 | 4/10 |
| own_product | 10/10 | 10/10 | 0/10 |
| course_or_community | 10/10 | 10/10 | 0/10 |
| newsletter_email_capture | 10/10 | 9/10 | 1/10 |
| is_contrast_case | 10/10 | 10/10 | 0/10 |

블랭크(공란) 셀은 0건 — 값을 못 찾은 경우 전부 명시적 `UNKNOWN`으로 채워짐. 이는 100개 파일럿 때보다 개선된 지점(그때는 셀이 비어있는 경우와 UNKNOWN 문자열이 혼재).

## 5. UNKNOWN Rate
affiliate 필드가 4/10(40%)로 가장 높음 — keepproductive.com(robots.txt 차단), asianefficiency.com 등에서 발생. 나머지 필드는 0~10%로 낮음. UNKNOWN이 N으로 잘못 계산된 사례는 스크립트 확인 결과 없음(Section 6 결과 PASS).

## 6. Traffic Provider Consistency
10개 전부 `traffic_provider = Similarweb` 단일 사용, 셀 내 provider 혼합 없음. **PASS.** (단, 노트에 기록된 모호성: Similarweb 무료 티어가 "trailing 3-month total"만 제공해 월간 수치로 정규화하는 규칙이 프로토콜에 없었음 — 아래 8번 참고.)

## 7. Denominator Test
`affiliate`, `display_ads`, `own_product` 세 필드에 대해 "값 컬럼만 필터링"으로 분자/분모를 계산 → 문자열 파싱 없이 자동 집계 가능함을 확인. **PASS.** (예: own_product는 confirmed 10개 중 9개가 Y.)

## 8. 발견된 Schema 문제 (총 4건 — QA 목적 달성)
1. **[설계 공백]** `start_year` 등 숫자형 필드에 대한 3분리 규칙이 Section 3에 명시되지 않음 (위 2번 참고).
2. **[정규화 규칙 부재]** Similarweb이 "3개월 합산" 수치만 제공할 때 `traffic_value`를 월간 환산할지, 3개월 합산 그대로 둘지 규칙이 없어 조사자 재량에 맡겨짐 — 데이터셋 간 비교 시 이 처리가 다르면 오염 가능.
3. **[증거 등급 경계 모호]** "운영자가 3자 인터뷰 사이트(Starter Story 등)를 통해 직접 밝힌 수치"를 A로 볼지 B로 볼지 규칙 없음. "사이트에 광고가 없다"는 운영자 자기진술(A)과 직접 관찰(C)이 동시에 성립할 때 우선순위 규칙 없음.
4. **[Contrast Cohort 세분화 부재]** `is_contrast_case`가 단일 Y/N+note라서, "완전 폐쇄"(43folders.com)와 "완만한 쇠퇴"(zenhabits.net)처럼 질적으로 다른 두 대조 유형이 구분 없이 같은 필드에 뭉뚱그려짐 — note로 커버는 됐으나 통계화는 불가능.

## 9. 수정이 필요한가 — 판단
**예, 하지만 스키마를 뒤엎을 정도는 아닙니다.** 핵심 골격(value/evidence/note 3분리, enum 강제, root-domain 유일성, provider 분리, denominator 자동화)은 10개 실측에서 전부 의도대로 작동했습니다. 위 4건은 이번 10개 같은 소규모 QA가 정확히 잡아내야 할 "세부 규칙 누락"이며, 40개로 확대하기 전에 문서에 반영하는 것을 권장합니다:

- (a) 숫자형 필드도 3분리 규칙 적용 대상임을 명문화
- (b) traffic 값의 기간 정규화 규칙 추가(예: "항상 월간 환산값을 traffic_value에, 원본 기간과 raw 값은 traffic_note에")
- (c) A vs B 우선순위 규칙 한 줄 추가(예: "운영자 본인이 직접 말한 수치는 게재처가 3자여도 A")
- (d) `is_contrast_case` 옆에 `contrast_pattern` enum(`shutdown`/`cadence_drop`/`traffic_decline`/`low_traction_despite_age`) 추가 검토

이 4가지는 전부 **문서 수정**으로 해결 가능하며 재조사가 필요하지 않습니다. 40개 추가 진행 여부는 사용자/GPT 승인 후 진행합니다.

---
**STOP.** 추가 40개, 1000개 확장, Study B는 실행하지 않았습니다.
