# 1000-Site Research Protocol V2 — 설계 문서 (실행 아님)

작성일: 2026-09-16 (개정) | 근거: 100-site 파일럿 결과(sites.csv/methodology.md/findings.md) + 사후 QA에서 발견된 데이터 품질 문제 + 사용자 결정사항 반영

**이 문서는 설계만 한다. 이 문서 작성 자체는 새로운 웹 리서치, 사이트 검증, 서브에이전트 실행, Similarweb/Semrush 등 API 호출을 포함하지 않는다. A0 Validation 10개조차 이 문서 승인 전에는 실행하지 않는다.**

## 핵심 원칙 (신규)

**1000개를 빨리 채우는 것보다, 통계적으로 다시 집계 가능한 깨끗한 구조화 데이터를 만드는 것이 우선이다.** 이 문서의 모든 결정(스키마, 표본 설계, 실행 순서, gate)은 이 원칙에 종속된다. 규모 확장은 데이터 품질이 검증된 뒤에만 진행한다.

## 0. 왜 V2가 필요한가 — 100개 파일럿에서 발견된 3가지 결함

1. **필드 오염(value/evidence/note 미분리).** `sites.csv`의 여러 boolean성 필드에 `Y`, `N`, `UNKNOWN`, `Y (C)`, `N (D)`, `UNKNOWN (possible, D)` 같은 자유문자 값이 섞여 들어갔다. `findings.md`의 일부 분모(예: display_ads 75/92)는 이런 혼합 표기를 사람이 다시 정규화해서 나온 숫자이고, 그 정규화 규칙이 문서화되어 있지 않다. 1000개 규모에서는 이 방식이 통계를 조용히 왜곡한다.
2. **중복 도메인 실시간 감지 부재.** 10개 배치가 병렬로 실행되면서 thespruce.com/bobvila.com/thepointsguy.com이 서로 다른 카테고리에서 중복 샘플링됐다. 100개에서는 사후 수작업으로 잡았지만, 1000개에서는 배치 시작 전에 자동으로 막아야 한다.
3. **성공 편향 표본만 구성됨(대조군 없음).** 100개는 전부 "성공 사례 후보"였다. 그래서 "성공한 사이트에 X가 있다"는 관찰은 나오지만 "X가 없으면 성공하지 못한다"는 비교는 애초에 불가능하다. 이게 이번 findings.md 전체에서 상관관계/원인 구분을 반복해서 명시해야 했던 근본 원인이다.

## 1. 실행 순서 — 바로 1000개로 가지 않는다 (수정)

이전 버전은 Study A 1,000개를 단일 목표로 제시했다. 이번 개정에서는 실행을 3단계로 쪼갠다. 각 단계는 이전 단계 통과 후에만 시작한다.

```
A0-Phase1: V2 스키마로 10개 사이트 실행
   ↓
   schema / enum / evidence / dedupe / denominator 계산 검증 (Section 7 Gate)
   ↓ (이상 없을 때만)
A0-Phase2: 40개 추가 실행 (누적 50개)
   ↓
   50개 전체 기준으로 Section 7 Gate 재검증 + 결과 보고
   ↓
   STOP — 사용자/GPT 검토
   ↓ (승인 시에만)
Study A 나머지 950개 확장 (+ Study B Verified Revenue Cohort 병행 가능)
```

10개와 40개를 나눈 이유: 10개 단계에서 스키마 자체의 구조적 결함(enum 위반, 중복 감지 실패 등)을 저비용으로 먼저 잡고, 40개 단계에서 그 수정된 스키마가 실제 규모에서도 버티는지 확인한다. 50개를 처음부터 한 번에 실행하지 않는다.

## 2. Study A / Study B 정의

### Study A — Broad Structure Dataset (목표 1,000 unique domains, 3단계로 도달)
목적: 이 사업 형태들이 시장에 얼마나, 어떤 조합으로 존재하는지의 구조적 지도를 그린다. 매출 숫자를 억지로 찾지 않는다.

수집 필드(자동화 가능 위주):
- domain(canonical root domain — Section 6 참조), category, sub_category, as_of_date(조사 시점 — 트래픽 수치의 시점 고정을 위해 필수, 누락 금지)
- traffic 관련 필드는 Section 4의 provider 원칙을 따른다.
- content_scale_proxy(사이트맵/구글 색인 수 등 자동 수집 가능한 대리지표)
- 아래 "canonical schema"(Section 3)를 따르는 모든 boolean 필드

### Study B — Verified Revenue Cohort (목표 100~200개) — Study A의 부분집합으로 제한하지 않음 (수정)
목적: 실제 수익 증거(A등급: 운영자 자체 공개, 또는 신뢰할 수 있는 B등급: 날짜가 있는 인터뷰/광고네트워크 케이스스터디/공시)가 있는 사이트만 골라서 "무엇이 실제로 돈이 됐는가"를 본다.

포함 조건: income report, founder interview(날짜·구체 수치 포함), SEC/공시, ad-network case study, 검증 가능한 인수 보도 중 최소 1개.

**Study B는 다음 두 그룹을 모두 포함한다(이전 버전의 "Study A의 부분집합" 제약을 제거):**
- Study A 표본에 포함되어 있으면서 수익 증거가 확인된 사이트
- Study A 표본에는 없지만 신뢰할 수 있는 수익 증거가 존재하는 사이트

이를 구분하기 위해 신규 필드를 추가한다: `in_study_a = Y / N`. 좋은 수익 증거를 "Study A 표본 바깥"이라는 이유만으로 버리지 않는다. Study A처럼 UNKNOWN이 70~80% 채워지는 걸 방지하기 위해, 애초에 "수익 증거가 있는 사이트"만 후보로 넣는다는 원칙은 유지한다.

## 3. Canonical Schema — value / evidence / source / note 4분리 (전면 개정, A0-Phase1 QA 반영)

100개 파일럿과 A0-Phase1(10개) 실측에서 나온 문제를 모두 반영해 스키마를 4개 컬럼 세트로 확정한다. **모든** evidence-bearing 필드(boolean이든 숫자든 날짜든) 예외 없이 이 구조를 따른다.

```
{field}            → 필드 고유 타입의 값만 (boolean형은 Y/N/UNKNOWN, 숫자형은 숫자 또는 UNKNOWN, 자유문자 금지, enum/타입 검증)
{field}_evidence   → A / B / C / D / UNKNOWN 만 허용
{field}_source_url → 출처 URL, 없으면 명시적으로 UNKNOWN (boolean 필드도 예외 없음 — A0-Phase1에서 boolean 필드에 source_url이 없어 출처를 note 안 자유텍스트에 숨기게 되는 문제가 실제로 발견됨)
{field}_note       → 자유 텍스트 (관찰 내용, 애매함 설명, 판단 근거는 전부 여기로 — 등급이나 출처를 여기 숨기지 않는다)
```

예:
```
affiliate = Y
affiliate_evidence = C
affiliate_source_url = https://example.com/disclosure-page
affiliate_note = "Amazon Associates 배너 관찰됨"
```
`Y (D)`처럼 값 컬럼에 등급을 섞어 넣는 것, 또는 출처 URL을 note 자유텍스트 안에만 적고 `_source_url` 컬럼을 비워두는 것 모두 V2에서 금지한다. 통계 스크립트가 `{field}` 컬럼만 보고 집계할 수 있어야 하며, 사람이 문자열을 다시 파싱해서 재분류하는 단계가 없어야 한다.

### 3-1. Evidence 등급 정의 (확정, pre-950 하드닝 라운드에서 판단 예시 보강 — 2026-09-17)
- **A** = 운영자의 직접 진술 — 본인 소유 페이지의 자기공개(예: 본인 About 페이지의 "2012년 시작") 뿐 아니라, 신뢰할 수 있는 제3자 Q&A/인터뷰에서 운영자 본인이 직접 한 발언도 포함한다(게재처가 3자여도, 발언 주체가 운영자 본인이면 A). 예: 제3자 기사에 인용된 "창립년도에 대한 제3자의 보도"는 A가 아니라 B (아래) — 운영자 본인의 직접 인용문일 때만 A.
- **B** = 제3자의 보도·요약·추정(트래픽 추정 도구, 언론 보도, 창립년도를 다룬 제3자 기사 등 — 운영자 본인의 발언이 아닌 모든 제3자 주장/추정).
- **C** = 조사자 본인의 직접 사이트 관찰(예: 광고 유닛이 실제로 떠 있는 것을 직접 확인, 결제/가입 폼이나 제품 판매 페이지를 직접 확인 등 — 조사자가 그 자리에서 직접 본 것).
- **D** = 간접 근거를 이용한 추론(예: 광고 유닛의 부재로부터 "광고 없는 것으로 보임"을 추론), 항상 근거를 note에 명시.
- **UNKNOWN** = 확인 불가.

**Gate 강제 규칙(pre-950 하드닝, run_gate_v2.py Section 11–13에 구현됨):**
1. `{field} != UNKNOWN`인데 `{field}_evidence == UNKNOWN`이면 FAIL — 값이 확정되어 있는데 근거등급이 없는 경우는 있을 수 없다(Rule #8의 방향 반대 보완).
2. `evidence ∈ {A, B, C}`이면 그 필드 전용 `{field}_source_url`이 반드시 실제 URL이어야 한다(note에 URL을 적어두는 것으로 대체 불가). **자동 홈페이지 URL 보완 전면 금지(2026-09-17 "remove auto-fabrication" 패치로 수정, 이전 문구 폐기):** 이전 버전은 "C등급은 조사자 본인 관찰이므로 URL이 없으면 사이트 홈페이지 URL로 자동 보완 가능"이라고 명시했으나, 이는 조사자가 실제로 확인하지 않은 URL을 자동 생성하는 것이므로 fabrication의 일종으로 판단해 삭제했다. A/B/C 등급 모두 예외 없이 실제 출처 URL을 생성 스크립트가 직접 공급해야 하며(`evidence_harden.py`는 자동 보완을 전혀 수행하지 않고 누락 시 `EvidenceHardenError`만 raise한다), 확인이 안 되면 등급을 낮추거나 값을 UNKNOWN으로 되돌린다.
3. `evidence == D`이면 `{field}_note`가 반드시 비어있지 않아야 한다(추론의 근거를 항상 note에 남긴다).

### 3-2. Rule #8 — UNKNOWN 값은 반드시 UNKNOWN 증거등급을 동반한다
`{field} = UNKNOWN`이면 `{field}_evidence`도 반드시 `UNKNOWN`이어야 한다. "아마 D등급 정도의 추론은 가능하다"는 판단은 값을 UNKNOWN이 아닌 실제 추정치(N 등)로 채우고 evidence=D로 기록하거나, 값을 UNKNOWN으로 유지하고 그 추론 내용은 `_note`에만 적어야 한다 — evidence 컬럼에 D를 남겨두면 안 된다. (A0-Phase1에서 fortelabs.com/affiliate, asianefficiency.com/affiliate 2건이 `UNKNOWN, D`로 기록되어 있던 실제 위반 사례가 발견되어 이 규칙으로 수정됨 — Section 7-A 참조.)

### 3-3. 숫자·날짜형 필드도 동일 구조 적용 (A0-Phase1에서 발견된 설계 공백 수정)
`start_year`, `traffic_value`, `revenue_value`처럼 값이 Y/N/UNKNOWN이 아닌 필드도 예외 없이 value/evidence/source_url/note 4분리를 적용한다. 이전 개정판은 이 규칙을 revenue에만 명시했으나, A0-Phase1 실측에서 `start_year`가 빠져 있어 검증 스크립트가 이를 boolean 필드로 오인하는 문제가 실제로 발생했다. 예: `start_year_value / start_year_evidence / start_year_source_url / start_year_note`.

### 3-4. 날짜 필드: ISO 값과 설명문을 분리 (신규)
날짜가 필요한 모든 곳에서 "언제 조사했는가"(ISO 형식, 예: `2026-09-16`)와 "수치가 어떤 기간을 나타내는가"(자유 텍스트 기간 설명)를 별도 필드로 둔다. 하나의 날짜 필드에 `"2026-09-16 (Similarweb snapshot dated August 2026)"`처럼 값과 설명을 섞지 않는다.
```
traffic_research_date      → ISO (조사 시점)
traffic_source_period      → 자유 텍스트 (원본 데이터가 커버하는 기간, 예: "Similarweb snapshot dated August 2026")
traffic_value_raw_period   → 자유 텍스트 (raw 수치 자체의 집계 기간, 예: "trailing_3_months")
revenue_research_date      → ISO (조사 시점)
revenue_figure_period      → 자유 텍스트 (매출 수치가 커버하는 기간, 예: "2023" 또는 "recent as of 2023 interview")
```

### 3-5. Similarweb 등 "N개월 합산" 수치의 정규화 (신규)
raw 값을 절대 덮어쓰지 않는다. 다음 3개 필드로 분리 보존한다.
```
traffic_value_raw               → 원본 그대로의 숫자 (예: 3개월 합산치)
traffic_value_raw_period        → 그 원본이 커버하는 기간
traffic_value_monthly_equivalent → 정규화 계산값 (예: raw/3)
traffic_normalization_method    → 계산 방법 설명 (예: "raw_3mo_total / 3, rounded to nearest integer") 또는 정규화 불필요/불가 시 그 사유
```

### 3-6. traffic_scope enum (재정의 — pre-950 하드닝 라운드, 2026-09-17)
**중요한 의미 수정:** `traffic_scope`는 트래픽 **수치를 실제로 구했는지 여부**가 아니라, 이 도메인의 **구조 자체**가 무엇인지를 나타낸다. 즉 "Similarweb에서 숫자가 안 나왔다"는 `traffic_value`가 UNKNOWN이 되는 이유일 뿐, 그 자체로 `traffic_scope`를 UNKNOWN으로 만드는 근거가 아니다. A0-Phase2 초안에서 정확히 이 혼동이 실제로 발생했다 — 27개 사이트가 "숫자를 못 구했다"는 이유만으로 `traffic_scope=UNKNOWN`으로 잘못 기록되어 있었고(실제로는 명백한 콘텐츠 퍼블리셔 도메인), apartmenttherapy.com/seriouseats.com/loveandlemons.com/homegrounds.co 등 4개 사이트는 반대로 "부수적인 쇼핑/광고/도서 판매 링크가 있다"는 이유만으로 `WHOLE_DOMAIN_INCLUDES_PRODUCT`로 과잉 분류되어 있었다. 이번 라운드에서 50개 전체를 도메인 구조 기준으로 재검토하여 수정했다(Section 7-C 참조).

`traffic_value`가 UNKNOWN인 것과 `traffic_scope`가 UNKNOWN인 것은 서로 별개의 축이다:
```
CONTENT_ONLY                    → 이 루트 도메인은 본질적으로 콘텐츠 퍼블리셔다(부수적인 쇼핑/광고/도서
                                   판매 링크 정도는 이 분류를 막지 않는다). 트래픽 숫자를 실제로 구했는지와
                                   무관하게, 도메인 구조가 "콘텐츠 단독"이면 CONTENT_ONLY다.
WHOLE_DOMAIN_INCLUDES_PRODUCT   → zapier.com/coefficient.io처럼, SaaS/앱 제품이 도메인 트래픽에 실질적으로
                                   섞여 있어 도메인 전체 수치가 콘텐츠만의 규모를 대표하지 못하는 구조.
SUBDIRECTORY_ESTIMATE           → 콘텐츠 서브디렉토리만 별도로 추정된 수치인 구조.
UNKNOWN                         → 도메인 구조 자체를 판단할 수 없는 경우에만 사용한다(트래픽 숫자를 못
                                   구했다는 이유만으로는 UNKNOWN을 쓰지 않는다 — 그 경우 traffic_scope는
                                   도메인 구조상 판단 가능한 값(대개 CONTENT_ONLY)으로 채우고,
                                   traffic_value 쪽만 UNKNOWN으로 둔다). 폐쇄/리다이렉트된 옛 도메인처럼
                                   현재 구조 자체를 특정할 수 없는 경우가 진짜 UNKNOWN 사례다
                                   (예: consumerismcommentary.com, consumersearch.com).
```
`traffic_scope`가 다른 두 사이트의 `traffic_value`를 직접 비교하지 않는다.

## 4. Traffic Provider 원칙 (수정 — Similarweb 단일 확정 아님)

이전 버전은 "Similarweb 단일 도구로 통일"을 사실상 기본값처럼 서술했다. 이를 다음 원칙으로 대체한다.

- 단일 traffic provider를 전체 1000개에 사용하는 것을 **우선 목표**로 하되, 실행 전에 실제 API 접근 가능성, 요금제, 호출 제한(rate limit)을 확인한 뒤에 provider를 확정한다. 이 확인 자체가 A0 단계 이전에 필요한 준비 작업이며, 이 문서 승인만으로 provider가 정해지는 것은 아니다.
- 여러 provider를 함께 사용해야 하는 경우, **서로 다른 provider의 수치를 같은 컬럼에 절대 섞지 않는다.** provider별로 독립된 필드를 둔다:
  ```
  similarweb_visits
  semrush_organic_traffic
  ```
- 공통 메타 필드(모든 traffic 관련 행에 필수, Section 3-4/3-5/3-6 반영 최종본):
  ```
  traffic_provider
  traffic_metric
  traffic_scope                     (Section 3-6 enum)
  traffic_value_raw
  traffic_value_raw_period
  traffic_value_monthly_equivalent
  traffic_normalization_method
  traffic_research_date             (ISO)
  traffic_source_period             (자유 텍스트)
  traffic_evidence
  traffic_source_url
  traffic_note
  ```
- **서로 다른 provider가 낸 숫자는 동일 척도로 직접 비교하지 않는다**는 점을 데이터셋과 분석 문서 양쪽에 명시한다(예: Similarweb의 "월 방문수"와 Semrush의 "오가닉 트래픽"은 정의가 달라 같은 줄에서 대소 비교하면 안 됨).

### 4-1. traffic_scope별 traffic_tier 산출 규칙 (신규 — A0-Phase1 zapier.com 사례 기반 확정)

`traffic_scope`(Section 3-6) 값에 따라 `traffic_tier`(Section 5-1)를 아래처럼 다르게 계산한다. **raw 트래픽 값(`traffic_value_raw`, `traffic_value_monthly_equivalent`)은 어떤 scope든 항상 그대로 보존**하며, scope에 따라 달라지는 것은 오직 "이 raw 값을 콘텐츠 단위 `traffic_tier`로 인정할지"이다.

- **CONTENT_ONLY** → raw 값을 그대로 사용해 `traffic_tier` 계산 가능(Section 5-1의 HIGH/MID/LOW 임계값 적용).
- **SUBDIRECTORY_ESTIMATE** → 계산은 가능하나, `traffic_tier`를 다른 scope의 값과 같은 통계 줄에 직접 합산/비교하지 않고 scope별로 별도 분석한다(서브디렉토리 추정치는 방법론이 CONTENT_ONLY와 다르므로).
- **WHOLE_DOMAIN_INCLUDES_PRODUCT** → 콘텐츠 단위 `traffic_tier`는 **강제로 UNKNOWN**으로 둔다(도메인 전체 수치에는 제품/앱 트래픽이 섞여 있어 콘텐츠만의 규모를 대표하지 못하기 때문). raw 값 자체는 삭제하지 않고 그대로 남긴다 — "이 사이트의 콘텐츠가 이 정도로 크다"는 잘못된 결론을 통계에서 방지하는 것이 목적이지, 데이터를 버리는 것이 목적이 아니다.
- **UNKNOWN** → `traffic_tier` = UNKNOWN.

A0-Phase1의 zapier.com이 이 규칙 확정의 실제 계기였다: `traffic_scope=WHOLE_DOMAIN_INCLUDES_PRODUCT`인데도 최초 마이그레이션 때는 raw 5.3M/3mo 수치를 그대로 넣어 `traffic_tier=HIGH`로 계산되어 있었다 — 이는 이 규칙 위반 사례였고, 이번 개정에서 `traffic_tier=UNKNOWN`으로 교정했다(raw 값은 유지).

## 5. 표본 설계 — Contrast Cohort 25% 확정 + 샘플링 차원과 분석 특성의 분리 (수정)

100개 파일럿은 카테고리당 10개를 전부 "강한 후보"로 채웠다. V2는 카테고리당 표본을 4개 층으로 나누고, 각 층을 **25%씩** 고정 배분한다.

- Large / Traffic Leader — 25%
- Mid-scale Active Site — 25%
- Narrow Niche Authority — 25%
- **Contrast Cohort — 25%**

**명칭 주의: "Failed Site"라는 표현은 사용하지 않는다.** 이 층은 "Contrast Cohort"로만 부른다.

Contrast Cohort에 포함하려면 아래 중 **최소 하나 이상의 명확한 근거**가 있어야 하며, 근거는 `{field}_note`에 구체적으로 기록한다. 단순히 "작아 보인다"는 인상만으로는 포함하지 않는다.

- verified traffic decline (검증 가능한 트래픽 하락 추세)
- materially reduced publishing cadence (발행 빈도의 뚜렷한 감소)
- very low traffic despite long operating age (오래 운영됐음에도 매우 낮은 트래픽)
- monetization structure exists but visible traction is low (수익화 구조는 있으나 가시적 반응이 낮음)
- historically strong but clearly declined (과거엔 강했으나 명백히 쇠퇴)

Contrast Cohort가 있어야 findings.md에서 계속 반복했던 "이 패턴이 성공의 원인인지, 성공한 사이트에서 흔히 관찰되는 동반 현상인지"를 조금이라도 구분할 수 있다. 대조군 없이는 이 구분이 원천적으로 불가능하다는 점이 100개 결과의 가장 중요한 방법론적 교훈이다.

### 5-1. 샘플링 층(sampling_stratum)과 분석 특성을 별도 필드로 분리 (신규, A0-Phase1에서 실제 필요성 확인)

"Large / Niche Authority / Contrast"는 서로 다른 차원의 개념인데도 이전 버전은 이를 하나의 배타적 `category_layer`로 합쳐 놓았다. A0-Phase1 실측에서 asianefficiency.com이 정확히 이 문제를 드러냈다: 표본 설계상 Large/Traffic Leader 층에 배정했지만 실제 측정 트래픽은 이 표본에서 가장 낮은 축에 속했다. 이런 모순을 통계에 반영하려면 다음 4개 필드를 독립적으로 둔다.

```
sampling_stratum   → Large/Traffic Leader | Mid-scale Active Site | Narrow Niche Authority | Contrast Cohort (표본 설계 시점의 배정, 배타적 1개)
traffic_tier       → HIGH | MID | LOW | UNKNOWN (실측 트래픽 기준 분류, sampling_stratum과 독립적으로 계산됨)
is_niche_authority → Y / N / UNKNOWN (+evidence/source_url/note) — 특정 방법론/서브니치의 대표 사이트인지 여부. sampling_stratum이 Contrast Cohort여도 역사적으로는 Y일 수 있다(예: 과거 Top 25 블로그였던 사이트가 지금은 쇠퇴 중인 경우).
is_contrast_case   → Y / N / UNKNOWN (+evidence/source_url/note) — 이미 존재하던 필드, sampling_stratum과 별도로 유지.
```
`traffic_tier` 구간(잠정, 1000개 착수 전 재검토 필요): HIGH ≥ 200,000/월, MID 20,000~199,999/월, LOW < 20,000/월, 데이터 없으면 UNKNOWN. 이 임계값은 니치별 트래픽 분포 차이를 반영하지 못하는 잠정치이며, Section 12 미결정 항목에 재검토 필요 사항으로 남긴다.

### 5-2. contrast_pattern 구조화 (신규, A0-Phase1에서 필요성 확인)

`is_contrast_case`만으로는 "완전 폐쇄"와 "완만한 쇠퇴"처럼 질적으로 다른 유형을 구분할 수 없다는 게 A0-Phase1에서 실측으로 확인됐다(43folders.com=완전 폐쇄 vs zenhabits.net=측정 가능한 쇠퇴세이나 여전히 운영 중). 다음 구조를 추가한다.

```
contrast_pattern        → shutdown | traffic_decline | cadence_drop | low_traction_despite_age | historically_declined | NOT_APPLICABLE (Contrast Cohort가 아니면 NOT_APPLICABLE)
contrast_evidence_period → 자유 텍스트 — 어떤 근거로, 어떤 기간에 걸쳐 이 패턴을 판정했는지 명시 (예: "trailing 3 months ending Sept 2026, Similarweb 기준 global rank #133,150→#142,017 악화")
```
여러 패턴이 동시에 해당하는 경우(예: 43folders.com은 cadence_drop이 먼저 있었고 이후 shutdown으로 귀결) 가장 최종적/결정적인 패턴을 `contrast_pattern`에 넣고, 선행 패턴은 `contrast_evidence_period` 또는 `is_contrast_case_note`에 시간순으로 기록한다.

## 6. 중복 도메인 방지 — Root-Domain Canonicalization + Reservation (강화)

이전 버전의 "공유 CSV로 exclude" 방식만으로는 불충분하다. 다음 2단계를 추가한다.

### 6-1. Root-domain canonicalization을 조사 전에 먼저 수행
아래는 모두 동일한 도메인으로 정규화되어야 한다:
```
www.thespruce.com
garden.thespruce.com
https://thespruce.com/...
→ thespruce.com (canonical_root_domain)
```
서브도메인/프로토콜/www 접두어 차이로 같은 사이트가 다른 행으로 중복 등록되는 것을 막는다. "동일 모기업이 소유한 여러 버티컬 사이트"(예: The Spruce 계열)를 몇 개 버티컬까지 별도 행으로 허용할지는 조사 착수 전에 규칙으로 정한다(100개 때는 사후에야 발견된 문제).

### 6-2. Domain Reservation 흐름
완전 병렬 환경에서 두 개의 조사 흐름이 동시에 같은 신규 도메인을 잡는 race condition을 방지하기 위해, 다음 흐름을 원칙으로 한다:
```
canonical_root_domain 확정
   → RESERVE (레지스트리에 등록)
   → research (실제 조사 수행)
   → COMMIT (결과 확정 및 레지스트리 최종화)
```
**Reservation 메커니즘 구현이 어려운 경우**, 다음 대안으로 대체한다:
- 2~3개 배치씩 wave 단위로 실행
- 각 wave 종료 후 레지스트리를 즉시 갱신
- 갱신된 레지스트리를 다음 wave의 제외 목록으로 사용
- 전체 완료 후 100개 때처럼 사후 전수 도메인 대조를 1회 더 수행(이중 안전장치)

### 6-3. 중복 판정은 registrable domain(eTLD+1) 기준으로 한다 (신규, GPT 독립검토 반영)

`canonical_root_domain` 문자열을 단순 lower()/strip()해서 비교하는 것만으로는 `www.example.com`, `https://example.com/path`, `blog.example.com`이 서로 다른 문자열로 남아 중복이 감지되지 않을 수 있다. 이를 막기 위해 중복 판정은 항상 **registrable domain(eTLD+1)** 단위로 한다. 다만 `example.co.uk`처럼 2단계 public suffix가 있는 도메인은 단순히 "마지막 두 라벨"로 자르면 `co.uk`를 등록 가능 도메인으로 오판하므로, Public Suffix List(PSL) 개념을 반영해야 한다.

이 프로젝트의 실행 환경은 PyPI/publicsuffix.org 등 외부 네트워크에 접근할 수 없어 `tldextract` 같은 표준 라이브러리를 설치/사용할 수 없었다. 따라서 `validation/scripts/domain_utils.py`는 co.uk, com.au, co.jp 등 흔히 등장하는 multi-label suffix를 수십 개 curated 목록으로 내장하고, 목록에 없는 suffix는 "마지막 두 라벨" 일반 규칙으로 처리하는 경량 구현을 쓴다. **알려진 한계**: 목록에 없는 드문 multi-label suffix(예: 일부 국가의 3단계 이상 suffix)는 잘못 판정될 수 있다. 향후 네트워크/의존성 설치가 가능해지면 `domain_utils.registrable_domain()`을 `tldextract.extract(...).registered_domain` 호출로 그대로 교체 가능하도록 함수 시그니처를 맞춰뒀다.

## 7. V2 Validation Gate (1000개 확장 전 필수 통과 조건, A0-Phase1 실측 반영 개정)

**Study A 950개 확장은 아래 gate를 통과하고 사용자/GPT가 승인하기 전에는 실행하지 않는다. A0-Phase2(추가 40개)도 마찬가지로 사용자/GPT 승인 전에는 실행하지 않는다.**

A0 (10개 → 50개) 단계에서 다음 항목을 확인한다(3-6번은 A0-Phase1에서 새로 추가됨):

1. boolean/enum field는 정의된 값만 존재하는가 (`Y/N/UNKNOWN`, `A/B/C/D/UNKNOWN`, `traffic_scope` enum, `contrast_pattern` enum — 다른 값 없음)
2. value/evidence 혼합 표기가 하나도 없는가 (예: `Y (D)` 형태 금지 위반 여부)
3. root-domain 기준 duplicate가 없는가 (Section 6 canonicalization 적용 후 재확인)
4. **모든** evidence-bearing 필드(boolean 포함, traffic/revenue만이 아니라)에 `_source_url`이 A/B 등급일 때 채워져 있는가 (Section 3 4분리 반영). **note fallback 금지**: evidence가 A/B인데 전용 `_source_url` 컬럼이 비어 있고 URL이 `_note` 자유텍스트 안에만 적혀 있는 경우는 PASS로 인정하지 않는다 — validator는 반드시 전용 컬럼만 검사한다(GPT 독립검토로 발견, `run_gate_v2.py`에서 note fallback 로직 제거됨).
5. 날짜 필드가 ISO(`YYYY-MM-DD`) 또는 명시적 `UNKNOWN`이며, 기간 설명문이 섞여 있지 않은가 (Section 3-4)
6. Rule #8 — `{field}=UNKNOWN`인데 `{field}_evidence≠UNKNOWN`인 행이 없는가 (Section 3-2)
7. traffic provider/scope가 정상적으로 분리되어 있는가 (provider·scope 혼입 없음, whole-domain 수치가 content-only 수치와 직접 비교되지 않는가)
8. `sampling_stratum` / `traffic_tier` / `is_niche_authority` / `is_contrast_case`가 서로 독립적으로 기록되어 있는가 (하나의 배타적 라벨로 뭉개지지 않았는가)
9. denominator 계산이 스크립트로 자동화 가능한가 (사람이 문자열을 다시 파싱해야 하는 경우가 없는가)
10. enum validation(스키마 검증 스크립트)이 전체 통과하는가
11. **Gate 실행 자체가 machine-detectable해야 한다**: 검증 스크립트(`run_gate_v2.py`)는 하나라도 FAIL이 있으면 반드시 비정상 종료코드(exit code ≠ 0, 권장 1)로 끝나야 하며, 문자열 출력에 "FAIL"이 있는지 사람이 눈으로 확인하는 방식에 의존하지 않는다(CI/자동화 파이프라인에서 그대로 게이트로 쓸 수 있어야 함). 전체 PASS 시 exit code 0.

**50개 완료 후 보고 항목** (950개 확장 여부를 사용자/GPT가 판단하기 위한 자료):
- enum validation 결과
- provenance/source validation 결과 (신규)
- date-format validation 결과 (신규)
- duplicate 결과
- field completion rate (필드별 채움 비율)
- UNKNOWN rate (필드별)
- traffic provider/scope consistency
- denominator test 결과
- 발견된 스키마 문제점 목록

이 보고 후 **STOP**하며, 950개 확장은 사용자/GPT의 명시적 승인 후에만 실행한다.

## 7-A. A0-Phase1 (10개) 실행 결과 — 스키마 패치의 근거 (완료, 2026-09-16)

A0-Phase1은 Productivity Software & PKM 니치에서 10개 사이트를 실제 조사해 스키마 골격(enum, root-domain 유일성, provider 분리, denominator 자동화)이 PASS함을 확인했다. 이 과정에서 아래 4가지 결함이 실측으로 발견되어 본 문서(Section 3, 5, 7)에 반영됐다:
1. 숫자형 필드(`start_year`)에 3분리 규칙이 없었던 설계 공백 → Section 3-3에서 수정.
2. Similarweb "3개월 합산" 수치의 정규화 규칙 부재 → Section 3-5에서 수정.
3. 3자 인터뷰를 통한 운영자 자기진술의 A/B 등급 경계 모호 → Section 3-1 evidence 정의에서 "발언 주체가 운영자면 게재처가 3자여도 A"로 확정.
4. `is_contrast_case`가 "완전 폐쇄"와 "완만한 쇠퇴"를 구분 못함 → Section 5-2 `contrast_pattern` enum으로 수정.

추가로 사용자 지시에 따른 스키마 패치(이번 개정) 이후, 기존 10개 데이터를 새 스키마로 마이그레이션(`validation_10_v2.csv`, 새 웹 리서치 없이 기존 자료만 재구조화)하고 Gate를 재실행한 결과는 다음과 같다.

**최종 결과 (targeted repair 이후 재실행, 2026-09-16 두 번째 패치):**

**Enum validation:** PASS — boolean/evidence/traffic_scope/contrast_pattern 전 필드 정의된 값만 존재.

**Provenance/source validation:** **PASS** — 최초 실행에서 FAIL 7건(zapier.com/asianefficiency.com/keepproductive.com/linkingyourthinking.com/43folders.com/zenhabits.net의 `start_year_source_url`, zenhabits.net의 `display_ads_source_url`)이 있었으나, **동일 근거를 그대로 유지한 채 정확한 출처 URL만 targeted repair로 확정**(새 주장·새 사이트 조사 없음):
- zapier.com → https://zapier.com/blog/erratic-effective-story-behind-zapier-blog-2013/ (Wade Foster 본인 글, "이번 6월부터 진지하게 시작" 확인)
- asianefficiency.com → https://www.asianefficiency.com/about/ ("2011년 passion project로 시작" 원문 확인)
- keepproductive.com → https://theplus.so/who/francesco-dalessio (기존에 기록된 인용문 "We started Keep Productive in late 2017..." 원문 그대로 확인)
- linkingyourthinking.com → https://medium.com/@nickmilo22/reflecting-on-the-age-of-the-linked-note-ff13945d6af4 (Obsidian beta 2020년 4월, LYT Kit 2020년 5월, 첫 워크숍 2020년 7월 — 기존 기록된 3개 날짜 모두 원문에서 정확히 확인)
- 43folders.com → https://en.wikipedia.org/wiki/Merlin_Mann ("2004년 9월 설립" 확인)
- zenhabits.net (start_year + display_ads) → https://en.wikipedia.org/wiki/Zen_Habits (2007년 2월 설립, 2009·2010 Time Top 25 확인) / https://zenhabits.net/about/ ("I don't take guest posts, advertising..." 원문 그대로 확인)

**Date-format validation:** PASS — `traffic_research_date`/`revenue_research_date` 전부 ISO 또는 UNKNOWN, 기간 설명문은 별도 필드(`traffic_source_period` 등)로 분리됨.

**Duplicate validation:** PASS — 10개 canonical_root_domain 전부 고유.

**Rule #8 (UNKNOWN→UNKNOWN evidence):** PASS — 원본에서 `UNKNOWN, D`로 기록되어 있던 fortelabs.com/affiliate, asianefficiency.com/affiliate 2건을 `UNKNOWN, UNKNOWN`으로 교정(추론 내용은 note에 보존).

**traffic_scope/traffic_tier consistency (Section 4-1):** PASS — zapier.com(`traffic_scope=WHOLE_DOMAIN_INCLUDES_PRODUCT`)의 `traffic_tier`를 최초 마이그레이션 때 잘못 계산됐던 `HIGH`에서 규칙에 맞게 `UNKNOWN`으로 교정. raw 트래픽 값(5,300,000/3mo)은 삭제하지 않고 그대로 보존.

**Denominator test:** PASS — affiliate/display_ads/own_product/is_niche_authority/is_contrast_case 전부 값 컬럼 필터링만으로 분자/분모 자동 계산 확인.

**A0-Phase1 FINAL PASS.**

**남은 문제(추후 A0-Phase2/1000개 확장 시 검토 필요, 이번 gate 통과에는 영향 없음):** `traffic_tier` 임계값(HIGH/MID/LOW 구간)이 잠정치라 니치별 검증 필요, `is_niche_authority`/`contrast_pattern` 판정이 현재 D등급 추론 위주라 대규모에서는 판정 기준을 더 구체화할 필요, `SUBDIRECTORY_ESTIMATE` scope는 이번 10개 표본에 실례가 없어 규칙만 정의되고 실측 검증은 아직 안 됨.

## 7-B. GPT 독립 코드 리뷰 반영 — Validator/Migration 하드닝 (완료, 2026-09-17)

commit `40732be`(pilot-100, protocol, A0-Phase1 validation 데이터/스크립트 최초 커밋) 이후 GPT가 GitHub 저장소를 독립적으로 리뷰해, **데이터(`validation_10_v2.csv`)는 Gate PASS이지만 validator/migration 코드 자체에 5건의 blocking issue**가 있다고 지적했다. 40개 확장 전에 반드시 고쳐야 하는 이유는, 코드에 결함이 있으면 40개·1000개로 늘어났을 때 결함도 함께 배로 늘어나기 때문이다. 이번 라운드는 코드/문서 정합화만 수행했고 **새 사이트 조사, 새 수치 확인, 추가 표본 확장은 전혀 하지 않았다.**

**GPT가 발견한 5건과 조치:**

1. **Provenance note-fallback 금지 (검증 누락 수정).** 기존 `run_gate_v2.py`는 A/B 등급 evidence인데 전용 `_source_url` 컬럼이 비어 있어도, URL 문자열이 `_note` 자유텍스트 안에 들어있으면 PASS로 인정하는 허점이 있었다. 이는 실질적으로 provenance 검증을 무력화한다. `check_provenance()`를 재작성해 A/B 등급은 **전용 `_source_url` 컬럼에 `http(s)://`로 시작하는 값이 있을 때만 PASS**로 엄격화했다(note fallback 로직 완전 제거). Section 7 Gate 체크리스트 4번 항목에 "note fallback 금지" 문구를 명시했다.
2. **`migrate_schema.py` 재현성 복구.** 기존 스크립트를 그대로 재실행해도 커밋된 `validation_10_v2.csv`(zapier.com traffic_tier 교정, 7건 provenance URL 패치 등)를 재생성하지 못했다 — 그 패치들이 스크립트 밖에서 1회성 수작업으로 적용됐기 때문이다. 모든 patch를 `SOURCE_URL_OVERRIDES` 딕셔너리와 `traffic_tier_for()` 함수 등 **스크립트 코드 안으로 흡수**해, `validation_10.csv` + `migrate_schema.py` → `validation_10_v2.csv`가 항상 동일한 결과를 재현하도록 고쳤다. 검증 방법: 별도 임시 파일에 재생성 → 필드 단위 diff → 결과는 아래 "재현성 검증 결과" 참고. 행 순서도 고정 리스트(`expected_order`)와 대조해 어긋나면 스크립트가 즉시 에러를 내도록 했다.
3. **환경 종속 절대경로 제거.** 스크립트에 박혀 있던 `/home/claude/...` 식 절대경로를 전부 제거하고, `pathlib.Path(__file__).resolve().parent` 기준 상대경로를 기본값으로 쓰되 `argparse`로 CLI 인자(`--src`, `--dst`, 위치 인자 `csv_path`, `--report`)를 받도록 고쳤다. 이제 저장소를 어느 OS/환경에 clone해도(Windows, Linux, Cowork) 동일하게 동작한다. 새로운 환경 종속 경로는 추가하지 않았다.
4. **Registrable domain(eTLD+1) 기반 중복 판정 구현.** 기존 중복 판정은 `lower()/strip()` 단순 문자열 비교였다. 신규 `domain_utils.py` 모듈(의존성/네트워크 없음 — 이 환경은 PyPI·publicsuffix.org에 대한 아웃바운드 네트워크 접근이 차단되어 있어 `tldextract` 설치 불가, 별도 확인됨)이 `example.co.uk`류 복수 라벨 공용 접미사를 인식하는 큐레이션된 목록 기반으로 registrable domain을 계산한다. 상세는 아래 6-3 신설 절 참고. `check_duplicates()`는 이제 원본 `canonical_root_domain` 포맷 검증과 registrable-domain 기준 중복 검사를 모두 수행한다.
5. **Gate의 machine-detectable exit code.** 기존 `run_gate_v2.py`는 FAIL이 있어도 텍스트만 출력하고 프로세스는 항상 exit code 0으로 끝났다. 이제 모든 체크 결과를 집계한 `all_passed` boolean을 기준으로 **전체 PASS일 때만 exit code 0, 하나라도 FAIL이면 exit code 1**로 종료하도록 고쳤다(`sys.exit(0 if all_passed else 1)`). Section 7 Gate 체크리스트에 11번 항목으로 명시했다.

**회귀 테스트 (신규 `test_validation_tooling.py`, stdlib `unittest`만 사용, 이 저장소의 "추가 의존성 없음" 원칙 준수):**
- Case A: A등급 evidence + `_source_url` 비어있음 + URL이 note에만 있음 → FAIL 확인
- Case B: A등급 evidence + 전용 `_source_url` 존재 → PASS 확인
- Case C: `traffic_scope=WHOLE_DOMAIN_INCLUDES_PRODUCT` → `traffic_tier=UNKNOWN` 강제 확인
- Case D: `traffic_scope=UNKNOWN` → `traffic_tier=UNKNOWN` 강제 확인
- Case E: `example.com`/`www.example.com`/`blog.example.com` → 동일 도메인으로 판정 확인
- Case F: `example.co.uk`/`www.example.co.uk` → 동일 도메인으로 판정 확인(및 `.co.uk`가 `.com`과 혼동되지 않음을 별도 확인)
- Case G: 의도적으로 결함(중복 도메인 + `Y (D)` 혼합 포맷)을 주입한 fixture로 실제 서브프로세스 실행 → exit code ≠ 0 확인
- Case H: 정상 데이터로 실제 서브프로세스 실행 → exit code == 0 확인
- Case I: `migrate_schema.py`를 재실행해 커밋된 `validation_10_v2.csv`와 필드 단위로 완전히 일치하는지 확인

**결과: 12/12 테스트 전부 PASS.**

**재현성 검증 결과:** `migrate_schema.py`를 재실행해 생성한 CSV와 기존 커밋된 `validation_10_v2.csv`를 diff한 결과, 차이는 정확히 3건이며 모두 **의도적으로 공개된 정밀도 개선**이다 — keepproductive.com의 `affiliate_source_url`/`own_product_source_url`/`course_or_community_source_url`이 기존의 일반 URL(`https://www.theplus.so`)에서, 이전 targeted-repair 라운드에서 이미 확인했던 더 정확한 원문 페이지(`https://theplus.so/who/francesco-dalessio`, 동일 출처·새 조사 없음)로 갱신됐다. 그 외 57개 필드 × 10행 전체가 완전히 일치한다.

**Gate 재실행 결과:** `validation_10_v2.csv`에 대해 `run_gate_v2.py`를 재실행한 결과 전체 체크리스트 PASS, **"A0-Phase1 FINAL PASS"**, 프로세스 exit code **0** 확인. 의도적으로 결함을 주입한 fixture에 대해서는 exit code가 **0이 아님**(1)을 별도로 확인했다(Case G).

이번 라운드는 코드/문서 정합화만 수행했으며, A0-Phase2(40개 확장), Study B, 950개 확장은 실행하지 않았다. 다음 단계는 사용자/GPT의 별도 승인 후에만 진행한다.

## 7-C. 950개 확장 전 마지막 pre-scale 하드닝 (완료, 2026-09-17)

GPT가 누적 50-site 커밋(`baac63d`)을 독립 검토해 PASS로 승인한 뒤, 950개 확장 착수 **직전** 마지막 정합화 라운드로 사용자가 지시한 9개 항목을 처리했다. **이번 라운드에서도 새 사이트 조사는 0건이며, 950개 확장/Study B는 실행하지 않았다.**

1. **`traffic_scope` 재정의 및 50개 전체 재분류** — Section 3-6 참고. 27개 사이트의 잘못된 `UNKNOWN` 분류와 apartmenttherapy.com/seriouseats.com/loveandlemons.com/homegrounds.co 4개 사이트의 잘못된 `WHOLE_DOMAIN_INCLUDES_PRODUCT` 분류를 도메인 구조 기준으로 교정. consumerismcommentary.com/consumersearch.com(폐쇄·리다이렉트로 구조 자체 불확정)만 진짜 UNKNOWN으로 유지, zapier.com/coefficient.io는 진짜 SaaS 혼합 구조로 `WHOLE_DOMAIN_INCLUDES_PRODUCT` 유지.
2. **Traffic Provider 전략 (950개 규모) — 결정 아닌 권고안 제시.** 유료 구매/API 등록은 금지 지시에 따라 실행하지 않았으며, 조사 결과만 기록한다:
   - Similarweb 무료/공개 티어: API 없음(전부 수동 조회), 익명 사용자 하루 약 10~15개 도메인 소프트 제한, 결과는 화면 캡처만 가능(CSV 내보내기 없음), 데이터 이력은 최근 약 3개월로 제한. 950개를 이 티어만으로 조사하면 매우 큰 수작업 부담과 높은 UNKNOWN 비율(현재 50개 기준 `traffic_value_raw` UNKNOWN 28%, `traffic_tier` UNKNOWN 38%)이 계속될 것으로 예상된다.
   - Semrush API: API 이용에는 최상위 "Advanced" 플랜(월 $549 최소)이 필요하고, 그 구독만으로는 API 유닛이 자동 지급되지 않으며 별도 유닛 패키지를 구매해야 한다. 유닛당 단가는 공개되어 있지 않아 영업팀에 직접 문의해야 확인 가능하다.
   - **권고:** 950개 확장에서도 현재와 같이 Similarweb 무료 티어를 1차 provider로 유지하되(원칙 4의 "다른 provider 수치를 같은 컬럼에서 섞지 않는다"는 원칙은 그대로 유지), 높은 `traffic_value`/`traffic_tier` UNKNOWN 비율을 950개 규모에서 정상적으로 예상되는 결과로 명시적으로 받아들이는 것을 권고한다. Semrush 등 유료 provider 도입은 실제 예산 승인이 있을 때만 검토할 별도 의사결정 사항으로 남겨둔다.
3. **Study A `revenue_value` 필드 정리** — Study A는 매출 연구가 아니므로, 인수가(acquisition price)나 부분적/과거 시점 수치, 서술형 텍스트는 `revenue_value`에 넣지 않고 `revenue_note`로만 옮긴다. `revenue_value`는 이제 항상 `UNKNOWN`이거나 단일하고 깔끔한 구조화 수치 중 하나만 허용한다(Gate Section 13, `check_revenue_value_format`으로 강제). 이번 라운드에서 4건 교정: thomasjfrank.com/benlcollins.com/financialsamurai.com(서술형·복합기간 값 → UNKNOWN, 상세는 note로 이동), consumersearch.com($33M 인수가 → UNKNOWN, 인수가는 note에 URL과 함께 보존). Study B의 매출 스키마는 이번 라운드에서 설계하지 않았다(user 지시대로 보류).
4. **Evidence A/B/C/D 판정 규칙 명확화 및 Gate 강화** — Section 3-1 참고. `evidence_harden.py` 신규 모듈로 "값이 있으면 evidence도 있어야 한다"(Rule #8 방향 보완), "A/B/C는 전용 source_url 필요(C는 홈페이지 URL 자동 보완 가능)", "D는 note 필수"의 3개 규칙을 모든 생성 스크립트에 공통 적용. Gate에 대응하는 3개 신규 체크(Section 11~13)를 추가.
5. **Full PSL 기반 root-domain 처리 — 시도 결과: 차단(blocker)으로 보고.** `WebFetch` 도구로는 `raw.githubusercontent.com`의 Public Suffix List 원본에 접근이 가능함을 확인했으나, 이 도구는 내용을 AI 모델이 요약/가공해서 반환하는 방식이라 10,000줄 이상의 정확한 바이트 단위 데이터 파일(도메인 판정의 정확성이 직접 걸린 파일)을 안전하게 그대로 옮겨오는 용도로는 부적합하다고 판단했다. 이 세션의 `Bash`(curl, pip)에서는 여전히 조직 egress 정책으로 `raw.githubusercontent.com`, `pypi.org` 모두 403으로 차단된 것을 재확인했다(`tldextract` 설치 불가). 사용자 지시("불가능하면 매뉴얼 목록을 더 확장하지 말고 STOP하고 blocker로 보고")에 따라 매뉴얼 목록은 확장하지 않았다. **후속 조치 필요:** 사용자 본인 환경(로컬 PC, 네트워크 제한 없음)에서 `pip install tldextract` 또는 공식 PSL 스냅샷 파일을 직접 받아 저장소에 커밋하면, `domain_utils.py`의 `registrable_domain()` 시그니처만 유지한 채 내부 구현을 교체하는 것은 이후 세션에서 바로 가능하다.
6. **Domain Registry + wave 아키텍처 설계 및 구현** — `research/blog-monetization/registry/domain_registry.csv`(컬럼: `canonical_root_domain, registrable_domain, source_group, category, sampling_stratum, status, batch_id`)와 이를 관리하는 `validation/scripts/build_domain_registry.py`(`reserve_domains`/`commit_domains`/`reject_domains`/`merge_wave_into_master`/`check_duplicate` 함수 제공)를 신설했다. 사용자 기기에 연결된 `pilot-100/sites.csv`(pre-V2 스키마, `domain` 컬럼)를 세션 중 확보하여 `--pilot-csv` 옵션으로 시딩까지 완료: 현재 A0 누적 50개는 `COMMITTED`, 원본 100개 파일럿 스터디는 중복 3건(thepointsguy.com/thespruce.com/bobvila.com, 각 2개 카테고리에서 독립 샘플링됨)을 1개 registry row로 합쳐 97개 고유 도메인이 `EXCLUDED_PRIOR_PILOT`으로 시딩됨. 총 147행, `COMMITTED`∩`EXCLUDED_PRIOR_PILOT` 교집합 0건(중복 없음)을 스크립트 자체 검증으로 확인.
7. **자동 요약 스크립트 신설** — `validation/scripts/summarize_dataset.py`. row count/category/sampling_stratum/`is_contrast_case`(를 `sampling_stratum=Contrast Cohort`와 명시적으로 분리 표기)/`traffic_scope`·`traffic_tier`/필드별 UNKNOWN율/필드 완성률/evidence 등급 분포(및 "10개 필드 × N행 = 예상 총합"과 "실제 계산된 총합"을 나란히 출력해 자체 검증)를 CSV에서 직접 계산한다. 이전 `A0_Phase2_report.md`의 "11 fields × 50 = 550" 산술 오류와 `sampling_stratum=Contrast Cohort`/`is_contrast_case=Y` 혼동을 재발 방지하기 위해 신설했다.
8. **Gate 최종 메시지 데이터셋 중립화** — 항상 "A0-Phase1 FINAL PASS"로 고정 출력되던 메시지를 `f"VALIDATION GATE PASS -- rows={len(rows)}"`(실패 시 `FAILED`)로 교체.
9. **완료 기준 이행 결과:** (a) 기존 50개 재검증 — Gate 13개 섹션 전부 PASS, exit code 0 확인. (b) 위 (a)와 동일. (c) 자동 요약 생성 — `summarize_dataset.py` 신설 및 실행 확인(evidence 등급 총합 500=500 MATCH). (d) Registry 시딩 — COMMITTED 50건 + EXCLUDED_PRIOR_PILOT 97건, 총 147건, 교집합 0건으로 완료. (e) 재현성 확인 — `migrate_schema.py` → `build_a0_phase2.py` → `run_gate_v2.py` 파이프라인 재실행으로 확인. (f) 테스트 실행 — 기존 회귀 테스트 12/12 PASS(변경 없이 그대로 통과, 이번 라운드가 기존 동작을 깨지 않았음을 확인). 이번 라운드의 모든 변경은 커밋 1건으로 묶되 push하지 않으며, **950개 확장은 사용자/GPT의 다음 별도 승인 전까지 시작하지 않는다.**

## 7-D. 950개 확장 직전 마지막 engineering patch (완료, 2026-09-17, commit 8dffb08 GPT 후속검토 반영)

GPT가 commit `8dffb08`를 코드 수준까지 검토한 뒤, 950개 확장을 승인하기 **전** 마지막 pre-scale engineering patch로 7개 항목을 지시했다. **이번 라운드도 새 사이트 리서치 0건, Study B 미착수, 950개 확장 미실행이며, 현재 50개에 대해서만 schema/tooling을 정리했다.**

1. **Study A production schema 누락 필드 실제 추가.** Protocol Section 2가 정의만 해두고 실제 canonical schema에는 없었던 `category`(고정 5-value enum, `primary_niche` 자유텍스트와 분리) / `sub_category`(예약, 현재는 전부 UNKNOWN) / `as_of_date`(ISO, UNKNOWN 불허) / `content_scale_proxy_value·method·evidence·source_url·note`(신규 5-필드 evidence-bearing 그룹, 현재 50개 전부 UNKNOWN — 새 리서치 없이 필드만 추가) 를 `schema_extend.py` 신규 모듈로 구현해 `migrate_schema.py`/`build_a0_phase2.py` 양쪽에 적용했다. `category`는 이미 알려진 배치 설계(A0-Phase1=Productivity/PKM 10개, A0-Phase2=Excel/Spreadsheet·Personal Finance·Home DIY & Food·Product Review 각 10개)에서만 배정했다. `summarize_dataset.py`도 `primary_niche`가 아니라 실제 `category` 필드를 집계하도록 수정하고, `primary_niche`는 "참고용 자유텍스트"로 별도 표기했다. 최종 production schema는 총 **65개 컬럼**이다(Section 8-A 참고).
2. **evidence_harden.py의 자동 fabrication 2건 제거.** 기존에는 C등급인데 `_source_url`이 비어있으면 홈페이지 URL을 자동 backfill하고, D등급인데 `_note`가 비어있으면 일반 placeholder 문구를 자동 삽입했다. 두 동작 모두 "조사자가 실제로 확인하지 않은 내용을 자동 생성"하는 것이므로 제거했다 — 이제 두 경우 모두 `EvidenceHardenError`를 raise한다(Section 3-1 Gate 강제 규칙 2·3 문구도 이에 맞춰 갱신). 이미 커밋되어 있던 50개 데이터의 기존 자동-backfill 35건(C-tier 홈페이지 URL)과 9건(D-tier placeholder note)을 전부 재검토해, 원본 조사 note를 근거로 실제 홈페이지 관찰이 명확한 26건은 명시적 `SOURCE_URL_OVERRIDES` 항목으로 유지(KEEP)하고, 애매한 9건은 새 리서치 없이 UNKNOWN으로 되돌렸다(REVERT, 각 건마다 왜 확정할 수 없는지 note에 기록). D-tier 9건은 각 행에 이미 기록된 정보(니치/business model 등)만 근거로 실제 추론 문장을 채워 넣었다.
3. **Full PSL(tldextract) 구현 — 재확인 결과: 여전히 blocker.** 클라우드 샌드박스(`pip install tldextract`, `pip download`, PyPI 직접 접근 전부 403)와 사용자 로컬 Windows 환경(`device_bash`가 2026년 9월 8일 Windows 업데이트발 Plan9-mount 문제로 계속 기동 실패, 재확인함) 양쪽 경로 모두 막혀 있음을 재확인했다. 사용자의 명시적 지시("설치가 불가능하면 임의 구현을 계속하지 말고 blocker로 보고한다")에 따라 `domain_utils.py`의 `COMMON_MULTI_LABEL_SUFFIXES` curated 목록은 전혀 확장하지 않았고 그대로 유지했다. `test_KNOWN_LIMITATION_blogspot_subdomains_incorrectly_collapse` 테스트를 신설해, 현재 known-wrong 동작(`foo.blogspot.com`과 `bar.blogspot.com`이 잘못 동일 도메인으로 collapse됨)을 의도적으로 assert함으로써, 향후 Full PSL이 실제로 적용되면 이 테스트가 즉시 실패해 갱신이 필요함을 스스로 알리도록 했다. **후속 조치 필요 사항은 Section 6-3과 동일**: 사용자 본인 네트워크 제한 없는 환경에서 `pip install tldextract` 또는 공식 PSL 스냅샷을 직접 받아 커밋하면, `registrable_domain()` 시그니처만 유지한 채 내부 구현 교체가 가능하다.
4. **Domain Registry를 single-coordinator wave 구조로 hardening.** 기존에는 상태 전환 규칙이 문서화만 되어 있고 코드로 강제되지 않았다. `build_domain_registry.py`에 `IMMUTABLE_STATUSES = {EXCLUDED_PRIOR_PILOT, COMMITTED}`와 공유 `_transition()` 헬퍼, `RegistryStateError`를 신설해, `commit_domains`/`reject_domains`가 (a) 레지스트리에 없는 도메인, (b) 이미 immutable 상태인 도메인, (c) `RESERVED`가 아닌 도메인, (d) 다른 `batch_id`가 예약한 도메인에 대한 시도를 실제로 raise하며 거부하도록 만들었다. 레지스트리 seed 시점의 A0/prior-pilot registrable-domain 중복은 기존 WARNING에서 **non-zero exit(FAIL)**로 강화했다. `merge_wave_into_master`도 raw canonical 문자열 중복 검사에 더해 `domain_utils.registrable_domain()` 기준 중복 검사를 추가했다. 실제 950-site 리서치를 실행하지 않은 채, 이 상태 머신 전체를 end-to-end로 검증하는 `wave_coordinator.py`(신규, `run_wave()` + `--demo` 모드)를 작성해 synthetic placeholder 도메인 3개로 RESERVE→research→Gate→COMMIT→merge 전체 흐름과 상태 전환 거부 케이스(재-COMMIT, 잘못된 batch_id, immutable 전환)를 실제로 실행/검증했다.
5. **회귀 테스트 16건 신규 추가** (기존 12건 유지, 총 28건): non-UNKNOWN value + UNKNOWN evidence FAIL, C등급 no-source_url FAIL, D등급 empty-note FAIL, D등급 real-note PASS, revenue_value에 acquisition-price/자유텍스트 FAIL, revenue_value clean-figure/UNKNOWN PASS, summary evidence-cell 총합 자체검증, summary가 `primary_niche`가 아니라 `category`를 사용하는지 확인, registry duplicate reserve 거부, `EXCLUDED_PRIOR_PILOT`→`COMMITTED` 전환 거부, `COMMITTED`→`RESERVED` 전환 거부, wrong-batch_id commit 거부, registrable-domain 기준 merge 중복 거부, 그리고 Full PSL 관련 known-limitation 테스트(blogspot 서브도메인 오분류를 의도적으로 assert).
6. **50개 데이터셋 전체 재검증 완료.** row count 50, Gate 13개 섹션 전부 PASS(exit 0), `summarize_dataset.py` 자동 생성(evidence 셀 총합 self-check 일치), Registry = `COMMITTED` 50 + `EXCLUDED_PRIOR_PILOT` 97 = 147행·교집합 0, 회귀 테스트 28/28 PASS, `migrate_schema.py`→`build_a0_phase2.py` 파이프라인 재실행으로 재현성 확인. **950개는 실행하지 않았다.**
7. 이번 라운드의 모든 변경은 커밋 1건으로 묶고 push하지 않는다(사용자 지시). 남은 blocker는 정확히 1건(Item 3, Full PSL)이며, 그 외 항목은 전부 완료됐다.

### 7-D-1. 65-column production schema (최종, 이번 라운드 기준)

```
canonical_root_domain, site_name, primary_niche, category, sub_category, as_of_date,
sampling_stratum, traffic_tier,
is_niche_authority(+evidence/source_url/note),
is_contrast_case(+evidence/source_url/note),
contrast_pattern, contrast_evidence_period,
start_year_value(+evidence/source_url/note),
traffic_provider, traffic_metric, traffic_scope,
traffic_value_raw, traffic_value_raw_period, traffic_value_monthly_equivalent, traffic_normalization_method,
traffic_research_date, traffic_source_period, traffic_evidence, traffic_source_url, traffic_note,
revenue_value, revenue_figure_period, revenue_research_date, revenue_evidence, revenue_source_url, revenue_note,
display_ads(+evidence/source_url/note),
affiliate(+evidence/source_url/note),
own_product(+evidence/source_url/note),
course_or_community(+evidence/source_url/note),
newsletter_email_capture(+evidence/source_url/note),
content_scale_proxy_value(+method/evidence/source_url/note)
```

## 7-E. GPT 코드 리뷰 반영 — production blocker 6건 수정 (완료, 2026-09-17, commit 13a383d 후속)

GPT가 commit `13a383d`를 코드 수준까지 검토해 6건의 production blocker를 지적했다. **이번 라운드도 새 사이트 리서치 0건, Study B 미착수, 950개 확장 미실행이다.**

1. **content_scale_proxy를 evidence_harden 공통 group에 편입.** 스키마에는 `content_scale_proxy_*` 5개 필드가 있었지만 `evidence_harden.ALL_GROUPS`에는 빠져 있어, evidence-tier 검증/집계에서 조용히 누락되고 있었다. `CONTENT_SCALE_PROXY_GROUP`을 `ALL_GROUPS`에 편입해 evidence-bearing group 총수가 **10개 → 11개**로 늘었고, 50개 기준 evidence cell 총수는 **11 × 50 = 550**이 됐다(`summarize_dataset.py`는 `len(evidence_harden.ALL_GROUPS)`를 동적으로 참조하므로 코드 변경 없이 자동 반영). `content_scale_proxy_value != UNKNOWN`이면 `content_scale_proxy_method`도 UNKNOWN이면 안 된다는 규칙을 `evidence_harden.harden_row()`와 `run_gate_v2.py`(Section 15) 양쪽에 추가했다. 또한 "canonical schema의 모든 `*_evidence` 컬럼이 정확히 하나의 evidence group에 속하는지" 자동 검증하는 `evidence_harden.verify_group_coverage()`를 신설하고 Gate Section 14로 추가했다(누락/중복 모두 FAIL) — 이번처럼 새 evidence-bearing 필드가 스키마에는 추가됐는데 `ALL_GROUPS`에는 빠지는 실수가 다시 발생하면 침묵하지 않고 Gate가 즉시 잡아낸다.
2. **Protocol 3-1의 오래된 문구 삭제.** "C등급은 URL이 없으면 홈페이지 URL로 자동 보완 가능"이라는, 이미 코드에서는 제거됐지만 문서에는 남아있던 문구를 삭제했다(Section 3-1 참고). 최종 규칙: A/B/C 등급 모두 예외 없이 전용 `_source_url`이 있어야 하고, 자동 홈페이지 보완이나 D등급 generic placeholder note는 전면 금지다. 코드와 Protocol이 이제 동일하다.
3. **Production category taxonomy 확정 — 11개 카테고리.** 기존 pilot-100(100개 파일럿)이 이미 10-category broad-market 설계였다는 점(Career/Education, Excel/Spreadsheet/Productivity, Food/Recipe, Gardening/Outdoor, Home/DIY, Other Strong Niche, Personal Finance, Product Review/Buying Guides, Software/Tech Tutorials, Travel)과, A0가 Productivity/PKM을 Excel/Spreadsheet와 이미 별도 10-site 배치로 분리 실행했다는 점을 근거로, **pilot의 10개 카테고리에서 "Excel/Spreadsheet/Productivity"를 "Productivity / PKM"과 "Excel / Spreadsheet"로 분리한 11개**를 최종 production taxonomy로 확정했다(`schema_extend.CATEGORY_ENUM`). 새 웹 조사 없이, 기존 A0-Phase2의 "Home / DIY & Food" 배치(10개)를 각 사이트에 이미 기록된 `primary_niche`만 근거로 "Food / Recipe"(5개: seriouseats.com/101cookbooks.com/loveandlemons.com/theperfectloaf.com/afarmgirlsdabbles.com)와 "Home / DIY"(5개: apartmenttherapy.com/designsponge.com/shanty-2-chic.com/tinyhousetalk.com/thewoodwhisperer.com)로 재분류했다(`schema_extend.DOMAIN_CATEGORY_OVERRIDES`). pilot-100 자체의 "Excel/Spreadsheet/Productivity" 10개 행은 새 리서치 없이는 개별 사이트를 다시 확인해야 정확히 분리할 수 있으므로, 강제로 양분하지 않고 `schema_extend.PRIOR_PILOT_CATEGORY_MAP`에 명시적 legacy pass-through 값으로 남겼다(EXCLUDED_PRIOR_PILOT 레지스트리 행에만 쓰이며 실제 Study A 데이터셋에는 나타나지 않는다).
4. **Domain Registry의 category 컬럼 수정.** 기존에는 `category` 컬럼에 `primary_niche`(자유텍스트)를 넣고 있었다. 이제 A0(COMMITTED) 행은 실제 production `category` 컬럼 값을, prior-pilot(EXCLUDED_PRIOR_PILOT) 행은 pilot CSV 자체의 broad `category` 컬럼을 `PRIOR_PILOT_CATEGORY_MAP`으로 변환한 값을 사용한다(`build_domain_registry.py`의 `_seed_from_study_csv`에 `category_field`/`category_map` 파라미터 추가). 레지스트리 재생성 후 재확인: 총 147행, COMMITTED 50, EXCLUDED_PRIOR_PILOT 97, registrable-domain 교집합 0. 신규 `validate_registry_categories()`가 COMMITTED 행은 `CATEGORY_ENUM`, EXCLUDED_PRIOR_PILOT 행은 `PRIOR_PILOT_CATEGORY_MAP`의 값 집합에 속하는지 검사해, `primary_niche` 같은 자유텍스트가 category 컬럼에 섞여 들어가면 hard FAIL(non-zero exit)한다.
5. **Wave transaction 순서 수정 — Gate 통과 전 COMMITTED 저장 금지.** 기존 `run_wave()`는 "wave Gate PASS → registry COMMITTED 저장 → master merge" 순서였다. merge가 실패하면 registry는 COMMITTED인데 master에는 반영되지 않는 불일치 상태가 될 수 있었다. 새 순서: RESERVE → research → wave Gate → (파일에 쓰지 않고 메모리 상에서만) merge 검증(`build_domain_registry.compute_merge()`) → 병합된 전체 데이터셋에 대해 Gate 재실행 → **두 Gate 모두 통과한 뒤에만** master 파일 기록(`write_rows_csv()`) → **master 기록이 성공한 뒤에만** registry COMMIT. 두 Gate 중 하나라도 실패하면 `WaveAbortedError`를 raise하고 도메인은 RESERVED 상태로 남으며 master 파일은 전혀 건드리지 않는다. 또한 `commit_domains`/`reject_domains`가 공유하는 `_transition()`을 "전체 대상 먼저 검증 → 이후 전체 mutation" 2단계로 재작성해, 여러 도메인 중 하나라도 전환이 불가능하면 그 앞 도메인들도 mutate되지 않도록(부분 상태 변경 방지) 고쳤다.
6. **신규 테스트 6건 추가**(기존 28건 유지, 총 34건): wave Gate PASS + merge 실패 시 registry가 RESERVED로 남고 master가 변경되지 않는지(Test A), wave Gate PASS이지만 병합된 전체 데이터셋 Gate가 실패하면 master 파일이 전혀 기록되지 않고 registry도 RESERVED로 남는지(Test B), 모든 단계가 통과하면 master row가 늘고 registry가 COMMITTED로 바뀌는지(Test C), `commit_domains`에 여러 도메인을 넘겼을 때 하나라도 불법 전환이면 나머지 도메인도 mutate되지 않는지(Test D), `evidence_harden.verify_group_coverage()`가 누락/중복 evidence 컬럼을 실제로 잡아내는지, `content_scale_proxy_value≠UNKNOWN`인데 `method=UNKNOWN`이면 raise/FAIL하는지.
7. **Full PSL — blocker 유지, 테스트를 desired-behavior 방식으로 전환.** 환경 제약(클라우드 샌드박스·사용자 로컬 `device_bash` 모두 재확인 결과 여전히 차단)은 변함이 없어 수동 suffix 목록을 확장하지 않았다. 기존에 "현재의 잘못된 동작"(`foo.blogspot.com == bar.blogspot.com`)을 PASS로 assert하던 테스트를, 이제 **desired 동작**(`foo.blogspot.com != bar.blogspot.com`)을 명시하고 `@unittest.expectedFailure`로 표시하는 테스트로 교체했다 — 현재는 예상대로 실패하지만(테스트 실행 결과 자체에 "expected failure"로 드러남), Full PSL이 실제로 구현되면 이 테스트가 예상 밖의 성공(unexpected success)으로 표시되어 `expectedFailure` 데코레이터 제거가 필요함을 스스로 알린다. **950개 확장 승인 전에는 이 `expectedFailure`가 반드시 제거되어야 한다.**

**완료 조건 확인:** 새 사이트 조사 0건. 50개 데이터 재생성 후 row count 50, production schema(65 컬럼) 일치, Gate 15개 섹션 전부 PASS, evidence coverage 11 groups × 50 rows = 550 cells(자체 검증 MATCH), category distribution이 11-카테고리 taxonomy 기준으로 정상 출력, registry 147행(COMMITTED 50 + EXCLUDED_PRIOR_PILOT 97, 교집합 0) 정상, wave transaction 신규 테스트 전부 PASS, 기존 회귀 테스트 전부 PASS(총 34/34) 확인했다. 이번 라운드도 커밋 1건으로 묶고 push하지 않는다. **950개 확장은 여전히 사용자/GPT의 별도 승인 전까지 시작하지 않는다.**

## 8. 자동화 가능한 필드 vs 사람 판단이 필요한 필드 (100개 경험 기반 분류)

**자동화/API로 확장 가능:**
- 트래픽 프록시 수치(확정된 provider의 API)
- 사이트 생성 연도(WHOIS, Wayback Machine 첫 스냅샷)
- 광고 네트워크 존재 여부(페이지 소스 내 ad-tech 태그 스캔)
- 대략적 콘텐츠 규모(사이트맵 URL 개수)
- 뉴스레터 존재 여부(페이지 내 폼/서비스 스크립트 탐지)

**사람(또는 정교한 서브에이전트) 판단이 필요, 자동화 어려움:**
- 수익 실제 확인 여부와 등급(A/B/C/D) 판정 — 인터뷰/공시 문서 해석 필요
- "왜 통하는가"(why_it_works), 핵심 성공요인 서술
- CleanSheetHQ 전이가능성 같은 정성적 판단
- 소유권/제휴 관계 확인(예: Guiding Tech의 Zoho 소유설처럼 출처 검증이 필요한 주장)
- Contrast Cohort 포함 근거의 타당성 판단(Section 5의 5가지 기준 중 실제 해당 여부)

이 구분에 따라 1000개 확장 시 자동화 가능한 필드는 스크립트/API로 선처리하고, 서브에이전트는 판단이 필요한 필드에만 시간을 쓰도록 설계하면 토큰·시간 비용을 크게 줄일 수 있다.

## 9. 애매했던 필드 정의 재정리 필요 항목

100개에서 배치마다 판단이 갈렸던 필드들 — V2 착수 전 정의를 명문화해야 함:
- `winner_type`: 복합 라벨("NICHE AUTHORITY (financially fragile, contrast case)")을 허용할지, 단일 라벨 + 별도 `is_contrast_case` boolean으로 분리할지 결정 필요. (Section 5에서 Contrast Cohort를 별도 층으로 분리했으므로, `is_contrast_case` boolean으로 통일하는 쪽을 권장.)
- `evergreen_vs_news`: "혼합"의 기준(뉴스 비중 몇 %부터 혼합으로 볼지)이 배치마다 달랐음.
- `content_scale`: "수백 개", "수천 개" 같은 구간 표현 대신 사이트맵 기반 실수치로 통일 가능한지 검토.
- `time_to_monetization`: 100개 중 대부분 UNKNOWN이었던 필드 — 수집 가능성이 낮으므로 Study B(Verified Revenue Cohort)에서만 수집하고 Study A에서는 제외하는 것을 권장.

## 10. 제외 대상 (100개와 동일하게 유지)
개인 일기형 블로그, 대형 언론사(참고용 제외), Amazon/마켓플레이스, 리테일러 블로그.

## 11. CleanSheetHQ 발행과 시장조사는 병행 (신규 — Track 구조)

1000사이트 연구 완료까지 CleanSheetHQ 실제 발행을 기다리지 않는다. 두 트랙을 동시에 진행한다.

**Track 1 — CleanSheetHQ**
- 사이트 기본 구축
- 실제 콘텐츠 발행 (10개 → 30개)
- Search Console 실측
- 반응 좋은 cluster 확대

**Track 2 — Research**
- V2 Validation 10개 → QA → 추가 40개 (누적 50개) → STOP
- 사용자/GPT 승인 후 Study A 나머지 950개 확장
- Study B Verified Revenue Cohort는 Study A와 병행 가능 (Section 2 참조)

**우선순위 원칙:** 실제 CleanSheetHQ의 Search Console/전환 데이터가 확보되기 시작하면, 그 시점부터는 외부 시장조사(Track 2)보다 자사 실측 데이터(Track 1)를 더 높은 우선순위로 본다.

## 12. 실행 전 아직 미결정인 항목 (설계자가 임의로 정하지 않음)
- Traffic provider 최종 확정 (Similarweb 단일 vs 복수 provider 병행) — 실제 API 접근성/요금제 확인 후 결정 필요.
- Contrast Cohort의 5가지 포함 근거 중 실제 우선순위(여러 근거가 동시에 있는 사이트를 우선할지, 근거 유형별로 쿼터를 둘지).
- Study B 목표 100~200개 중 정확한 목표치(예: 150개)와, `in_study_a = Y`와 `N` 비율을 어느 정도로 볼지.
- A0 50개 완료 후 950개 확장을 승인할 기준선(예: field completion rate 최소 몇 % 이상이어야 통과로 볼지)의 구체적 수치.
- **(신규, A0-Phase1에서 발견)** `traffic_tier`의 HIGH/MID/LOW 임계값(현재 잠정: ≥200K/월, 20K~200K/월, <20K/월)을 니치별로 다르게 둘지, 전체 공통으로 유지할지.
- **(신규)** A0-Phase1에서 미해결로 남은 6개 사이트의 `start_year_source_url` 등 provenance 공백을 A0-Phase2 승인 시 재조사로 채울지, 아니면 evidence 등급을 B→D로 하향 조정해 채우지 않고 넘어갈지.

## 결론
100개 파일럿은 "무엇을 물어야 하는지"를 확정하는 역할을 이미 끝냈다. 1000개는 규모를 키우는 문제가 아니라, 이 문서가 정의한 gate(Section 7)를 통과하는 깨끗한 구조화 데이터를 만드는 문제다. A0(10→50개) 실행과 그 결과 보고까지만 다음 단계이며, 950개로의 확장은 그 이후 사용자/GPT 승인을 별도로 받는다.
