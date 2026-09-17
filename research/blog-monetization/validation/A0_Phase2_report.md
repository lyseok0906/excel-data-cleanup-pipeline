# A0-Phase2 (40개 확장, 누적 50개) 실행 결과

작성일: 2026-09-17 | 근거: `validation_50_v2.csv` (A0-Phase1 10개 + A0-Phase2 40개) + `run_gate_v2.py` 실행 결과 `gate_report_50.txt`

## 실행 범위

사용자 승인에 따라 A0-Phase2(추가 40개, 누적 50개)를 실행했다. 4개 카테고리에 10개씩 분산했다:

- Excel/Spreadsheet & Data Tools: 10개
- Personal Finance: 10개
- Home/DIY & Food/Recipe: 10개
- Product Review/Buying Guides: 10개

기존 100-site pilot(100개) 및 A0-Phase1(10개)과 canonical_root_domain이 중복되지 않도록 사전에 제외 목록을 구성했고, `run_gate_v2.py`의 registrable-domain(eTLD+1) 기준 중복 검사로 50개 전체에서 중복이 없음을 재확인했다(Gate 항목 3 PASS).

모든 새 행은 조사 시점부터 V2 canonical schema(value/evidence/source_url/note 4분리, Rule #8, traffic_scope, contrast_pattern 구조화 등)로 직접 작성했으며 마이그레이션을 거치지 않았다. 스키마 자체는 변경하지 않았다 — 스키마 관련 이슈는 아래 "발견된 schema issues" 섹션에 기록만 하고 코드/문서를 임의 수정하지 않았다.

## Gate 결과 (50개 전체, `run_gate_v2.py ../validation_50_v2.csv`)

**전체 결과: A0-Phase1 FINAL PASS (스크립트 출력 문구는 기존 그대로이며, 50개 데이터 기준 재실행 결과다). Exit code: 0.**

1. **Enum validation:** PASS — boolean/evidence/traffic_scope/contrast_pattern 전 필드가 정의된 값만 사용.
2. **Provenance validation (note fallback 없이, A/B 등급은 전용 source_url 필수):** PASS — A/B 등급 evidence를 가진 모든 필드가 전용 `_source_url` 컬럼에 유효한 http(s) URL을 보유.
3. **Date validation:** PASS — `traffic_research_date`/`revenue_research_date` 전부 ISO 형식 또는 명시적 UNKNOWN.
4. **Duplicate validation (registrable domain 기준):** PASS — 50개 전체가 서로 다른 registrable domain으로 확인됨.
5. **Rule #8 (UNKNOWN 값 → UNKNOWN evidence):** PASS — 위반 사례 없음.
6. **traffic_scope/traffic_tier consistency:** PASS — `WHOLE_DOMAIN_INCLUDES_PRODUCT` 또는 `UNKNOWN` scope인 6개 사이트(zapier.com, coefficient.io, apartmenttherapy.com, seriouseats.com, loveandlemons.com, homegrounds.co) 모두 `traffic_tier=UNKNOWN`으로 강제되었고 raw 트래픽 값은 보존됨.
7. **Denominator automation test:** PASS — affiliate/display_ads/own_product/is_niche_authority/is_contrast_case 전부 컬럼 필터링만으로 분자/분모 자동 계산 가능.
8. **contrast_pattern 구조 확인:** 11개 Contrast Cohort 사이트 모두 `NOT_APPLICABLE`이 아닌 구체적 패턴(shutdown 5건, cadence_drop 4건, traffic_decline 1건, historically_declined 1건, low_traction_despite_age 1건 — 43folders.com 등 A0-Phase1분 포함 12건 표시)을 가지며 `contrast_evidence_period`에 근거가 기록됨.

전체 상세 로그는 `validation/gate_report_50.txt` 참고.

## 카테고리/샘플링 분포 (50개 전체)

**sampling_stratum:**
- Narrow Niche Authority: 15
- Large/Traffic Leader: 12
- Mid-scale Active Site: 12
- Contrast Cohort: 11

(정확히 25%씩은 아니지만 4개 층이 고르게 분포됨 — A0-Phase1 10개가 이미 Productivity/PKM 니치에 특화되어 분포가 약간 치우쳐 있었고, 이번 40개에서 균형을 맞추려 했으나 완벽한 25/25/25/25는 아니다. 이 편차 자체는 Section 12의 미결정 항목 — 950개 확장 시 표본 배분 재검토 필요 — 에 해당한다.)

**traffic_tier (실측 기준):**
- UNKNOWN: 34 (68%) — 대부분 `traffic_scope`가 `WHOLE_DOMAIN_INCLUDES_PRODUCT`/`UNKNOWN`이거나 Similarweb이 소규모 사이트에 대해 절대값을 노출하지 않은 경우
- MID: 13 (26%)
- LOW: 2 (4%)
- HIGH: 1 (2%)

**traffic_scope:**
- UNKNOWN: 27 (54%) — Similarweb 무료 페이지가 다수 소규모 사이트에 대해 명확한 라벨 없는 대시/빈값을 반환한 경우가 다수
- CONTENT_ONLY: 17 (34%)
- WHOLE_DOMAIN_INCLUDES_PRODUCT: 6 (12%)

## Field completion rate (필드별 채움 비율, 50개 기준)

| 필드 | 채움 | 비율 |
|---|---|---|
| canonical_root_domain / site_name / primary_niche / sampling_stratum | 50/50 | 100% |
| contrast_pattern | 50/50 | 100% |
| traffic_research_date / revenue_research_date | 50/50 | 100% |
| is_niche_authority / is_contrast_case | 49/50 | 98% |
| traffic_provider / traffic_metric | 47/50 | 94% |
| traffic_source_period | 46/50 | 92% |
| start_year_value | 41/50 | 82% |
| own_product | 40/50 | 80% |
| traffic_value_raw / traffic_normalization_method | 36/50 | 72% |
| traffic_value_raw_period | 34/50 | 68% |
| traffic_value_monthly_equivalent | 33/50 | 66% |
| course_or_community | 32/50 | 64% |
| display_ads / affiliate | 31/50 | 62% |
| newsletter_email_capture | 30/50 | 60% |
| traffic_scope | 23/50 | 46% |
| contrast_evidence_period | 12/50 | 24% (Contrast Cohort가 아닌 39개 행은 정의상 공란) |
| revenue_value / revenue_figure_period | 4/50 | 8% |

주: "채움"은 UNKNOWN/공란이 아닌 값을 가진 비율이다. `contrast_evidence_period`는 Contrast Cohort가 아닌 행에서는 정의상 비어 있는 것이 정상이므로 39개 비-Contrast 행을 감안하면 사실상 11/11 Contrast 행 중 정보가 있는 것(43folders.com 포함 A0-Phase1 몫도 카운트하면 12/12)에 가깝다.

## UNKNOWN rate 및 evidence tier 분포

전체 `*_evidence` 컬럼(각 evidence-bearing 필드당 1개, 총 11개 필드 x 50행 = 550개 셀) 기준 등급 분포:
- UNKNOWN: 160 (29.1%)
- D (추론): 96 (17.5%)
- C (조사자 직접 관찰): 83 (15.1%)
- A (운영자 직접 진술): 82 (14.9%)
- B (제3자 보도/추정): 79 (14.4%)

**revenue 필드가 압도적으로 UNKNOWN이 높다(92%)** — 이는 100-site pilot과 A0-Phase1에서도 반복 확인된 패턴과 일치한다. 실제 수익 공개가 있는 사이트는 극소수(financialsamurai.com 부분 공개, benlcollins.com 하나만 A등급 완전 공개, consumersearch.com은 인수가만 확인)이며, 이는 Study B(Verified Revenue Cohort)가 별도로 필요한 이유를 재확인시켜준다.

## 발견된 schema issues (자동 수정하지 않고 기록만 함)

사용자 지시("변경 필요성이 발견되면 자동 수정하지 말고 Research Protocol Issue로 기록")에 따라, 스키마/프로토콜을 임의로 수정하지 않고 아래에 이슈만 기록한다.

1. **excelforum.com — 자기보고 트래픽과 제3자 도구 수치의 극단적 불일치.** 사이트 자체가 "~150만 월간 방문자"를 주장하지만 Similarweb은 3개월 합계 23.2만(월 약 7.7만)을 보고해 약 20배 차이가 난다. 현재 스키마는 두 출처를 별개 필드(`traffic_value_raw` 하나만 채택, note에 불일치 기록)로만 처리하며, "자기보고 vs 제3자 도구" 수치를 나란히 비교할 표준 필드는 없다. 950개 확장 시 이런 불일치가 흔하다면 `traffic_self_reported_value` 같은 별도 필드가 필요할 수 있다 — 지금은 note에 기록하는 것으로 충분히 처리되지만, 발생 빈도가 높아지면 재검토 필요.
2. **Similarweb 무료 페이지가 소규모 사이트에 대해 절대값 대신 "insufficient data" 대시만 반환하는 경우가 예상보다 많았다(50개 중 27개가 `traffic_scope=UNKNOWN`, 상당수는 값 자체가 아예 없어서).** Section 4의 "실제 API 접근성 확인 후 provider 확정" 원칙이 옳았음을 재확인 — 무료 웹 페이지 스크래핑 방식으로는 950개 규모에서 절반 가까이가 UNKNOWN이 될 수 있다는 실측 근거. 유료 API 또는 대체 provider 검토가 950개 확장 전 필요할 수 있음을 기록.
3. **`is_contrast_case=UNKNOWN`이 실제로 발생함(excelxor.com 1건).** 기존 스키마는 이를 허용하지만(boolean 필드는 Y/N/UNKNOWN), Contrast Cohort 표본 설계 관점에서 "판정 불가"가 얼마나 자주 나오는지는 950개 확장 전 모니터링이 필요한 지표다.
4. **`contrast_pattern`이 여러 패턴에 걸치는 경우의 처리가 여전히 note 의존적이다.** 예: consumerismcommentary.com은 사실상 매각(2011) → 재인수 → 재폐쇄의 복합 이력을 가지지만 `contrast_pattern=shutdown` 하나로만 기록되고 나머지는 `contrast_evidence_period`/note에 산문으로만 남는다. 43folders.com 사례(A0-Phase1)와 동일한 이미 알려진 한계이며 이번에도 별도 필드 없이 note로 처리했다 — 950개에서 복합 이력이 흔하면 재검토 여지가 있다는 점만 기록.

이상 4가지는 기록만 하며, 이번 태스크의 범위(변경 금지)에 따라 스키마/코드/문서를 수정하지 않았다.

## 요약

50개 전체에 대해 Gate가 모든 항목 PASS, exit code 0으로 확인됐다. 새로운 구조적 결함은 발견되지 않았고, 위 4가지는 "기록"으로만 남기는 관찰 사항이다. Study A 나머지 950개 확장 여부와 Study B 실행 여부는 사용자/GPT의 별도 승인을 기다린다.
