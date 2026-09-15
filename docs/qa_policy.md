# Blog B 검증 강도 3단계 운영모델

(2026-09-15 확정, `claude/비즈니스_방향_결정_로그.md`에서 이관)

Pilot A/B에 들었던 전수 검증(다중 fixture, 다중 screenshot, Cowork 독립검증, edge case 전수 재현)은 콘텐츠 제작 비용이 아니라 **Blog B 생산 시스템/QA 기준 자체를 만드는 비용**이었다. 이 강도를 모든 키워드에 기본 적용하는 것은 비효율적이므로, 콘텐츠 위험도에 따라 검증 강도를 차등화한다.

| 콘텐츠 유형 | 검증 강도 | 예 |
|---|---|---|
| **Simple Task** | 공식문서 확인 + 빠른 실제 재현 1회 | TRIM, UNIQUE, 기본 Split, 숫자→텍스트 변환 |
| **Edge-case Guide** | 실제 데이터 재현 + 핵심 edge case만 QA | null 처리, composite key, 부분 빈 행 삭제 |
| **High-risk Integrated Guide** | 다중 fixture, 다중 screenshot, 독립검증, edge case 전수 재현 | deterministic dedupe, 버전/데이터 손실 위험이 있는 통합 가이드 |

## 기본 운영 흐름 (Simple / Edge-case 등급)

```
Keyword 선정 → 공식 근거 확인 → 필요한 경우에만 실제 재현 → Draft → Technical spot-check → English QA → 완료
```

전체 fixture 제작·다중 screenshot·독립검증은 **High-risk Integrated Guide 등급에만** 적용한다.

## 핵심 원칙: 불일치 시에만 확대

Simple/Edge-case 등급에서는 **새로운 불일치(증적이 기대값과 어긋나는 경우)가 발견될 때만** 더 깊은 재검증으로 확대한다. Pilot C(TRIM vs CHAR(160))에서 이 원칙이 실제로 작동해 로케일 버그(`CHAR(160)` ≠ NBSP on 한국어 Windows)를 발견했고, Pilot D/E/F는 1회 재현만으로 종료되었다.

## 알려진 함정 (콘텐츠 작성 시 반드시 반영)

1. **`CHAR(160)` 로케일 문제**: 일부 Windows 로케일(한국어 등)에서 `CHAR(160)`이 유니코드 NBSP가 아니라 일반 공백(코드 32)을 반환한다. NBSP 관련 수식에는 항상 `UNICHAR(160)`을 사용한다.
2. **`null` vs `""` (빈 문자열)**: Power Query `Text.Combine` 등에서 `null`은 스킵되지만 `""`는 스킵되지 않아 구분자가 중복 삽입된다. Excel의 Go To Special → Blanks도 `""`가 채워진 셀을 "빈 셀"로 인식하지 않는다 — fixture를 만들 때 진짜 blank(`None`)와 빈 문자열(`""`)을 혼동하지 않도록 주의(Pilot G에서 이 문제로 fixture 재작업 발생).
3. **Go To Special → Blanks → Delete Entire Row**: 블랭크 "셀"을 선택하는 것이지 블랭크 "행"을 선택하는 게 아니다. 부분적으로만 빈 행도 삭제될 수 있고, 삭제된 행을 명시적으로 참조하는 수식은 `#REF!`가 된다. 안전한 대안은 `COUNTA` 헬퍼 열로 완전히 빈 행만 필터링하는 것이다.
