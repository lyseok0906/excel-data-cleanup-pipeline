> **공유용 사본 (자동 동기화 아님)**
> - 원본: Claude 프로젝트 "블로그 작성하여 수익 창출"의 `claude/Blog_B_PQ_ReplaceValues_후보비교_시험계획_2026-11-17.md` (프로젝트 업로드 2026-11-18 15:28:52 KST). 원본은 프로젝트에 그대로 유지된다.
> - 이 파일은 원본의 §1~4를 옮긴 사본이다. 차이는 두 가지뿐이다: ① 원본 §5(Search Console 점검 대조)는 공개 저장소에 올리지 않으려고 제외했다. ② §2의 수요 문구 한 곳을 외부 문서를 참조하지 않아도 읽히도록 고쳤다(원본: "추정 낮음~중간(2차 후보 문서와 동일 판단, 근거 데이터 없음)" → 사본: "낮음~중간으로 추정(검색 수요는 확인할 자료가 없어 추정)").
> - 원본이 바뀌어도 이 파일은 자동으로 바뀌지 않는다. 대조 기준은 아래 구분선 이후 본문의 SHA-256 앞 16자(`41a7485b965d94c5`)다.
> - 상태: 계획서일 뿐 시험 결과 아님. 발행은 글마다 별도 승인.

---

# Blog B 후보 — Power Query Replace Values 비교·시험 계획 (2026-11-17, 승인 전 제안)
상태: 계획만. 시험·Draft·발행 없음. 발행은 글마다 별도 승인. 대소문자·전체/부분 일치 결과는 **시험 전 단정하지 않음**.

## 1. 기존 글 본문 대조 (공개 본문 읽기, 51편 전수 키워드 검색 + 관련 글 발췌 열람)
Replace Values / Text.Replace / Replacer 언급이 있는 글: WP 371, 262, 84. (411·394는 "match entire"/"case-sensitive" 단어만 1회씩.)
| 글 | Replace Values 사용 | 다루지 않는 것 |
|---|---|---|
| WP 371 PQ Trim·NBSP | NBSP(`#(00A0)`)→일반 공백 1건. "Replace using special characters" 체크. 글자 수 동일 확인 | 일반 텍스트 값 치환, 전체/부분 일치, 대소문자, 체크 해제 상태(글에 "미시험"으로 명시) |
| WP 262 줄바꿈 제거 | `#(lf)`→공백, `#(cr)`→빈칸 2단계, 특수문자 체크 | 일반 단어 치환 동작 |
| WP 84 null vs "" | 코드 예시 한 줄 `Table.ReplaceValue(Source, "", null, Replacer.ReplaceValue, {"Middle"})` (시험 결과 설명 아님, 정규화 용도) | 해당 단계의 결과 비교, 부분 일치 |
| WP 411 UI 찾기/바꾸기 | Excel Ctrl+H 와일드카드. Match entire cell contents 옵션은 미시험이라고 명시 | Power Query 쪽 |
→ 차이: 기존 글은 모두 "보이지 않는 문자 치환"용. **일반 텍스트 값에서 Replace Values가 어떤 셀을 바꾸는지(전체 셀 vs 일부 글자, 대소문자, 공백·NBSP가 붙은 값, null/빈 문자열, 숫자 열)를 비교한 글은 없음.** 이 문장은 공개 본문 키워드 검색과 3편 발췌 열람 기준이며, 나머지 글의 모든 문장을 정독한 것은 아님.
- 아직 읽지 않은 것: Microsoft Learn Replace Values/Table.ReplaceValue/Text.Replace 문서(원문). 인용하려면 시험 후 직접 열람 필요.

## 2. 독자가 겪는 문제 (추정, 검색 수요 자료 없음 → 전부 추정)
1. Replace Values를 했는데 의도한 셀 일부만 바뀌거나 너무 많이 바뀜.
2. 눈으로 같은 값인데 안 바뀜(대소문자 또는 보이지 않는 공백·NBSP가 붙어 있을 수 있음 — 시험 전 단정 안 함, WP 371·34로 연결 가능).
3. null/빈 칸을 다른 값으로 바꾸려는데 동작을 모름.
4. 숫자 열에서 치환.
수요: 낮음~중간으로 추정(검색 수요는 확인할 자료가 없어 추정). 검색어 후보(추정): power query replace values not working, power query replace values partial match, power query replace values case sensitive.

## 3. Excel 2021 시험 계획 (VM, Excel 2021 LTSC 2608, 영어 UI, 한국어 지역 설정)
데이터(Sheet1, From Table/Range): 텍스트 열 Item 14행 — Apple, apple, APPLE, Pineapple, Red Apple, `Apple`+끝 공백, `Apple`+NBSP, `Apple` 사이 이중 공백 변형(Red␠␠Apple), 빈 셀, 수식 `=""`, Apple2, N/A, n/a, 기타 1행. 별도 열 Other(같은 값 일부)로 "선택 열만 바뀌는지" 확인. 숫자 열 Qty: 1, 10, 100, 1.1, 11, 빈 셀.
절차 (각 시험은 새 단계로 하고 단계 수식을 저장 파일 DataMashup에서 읽음):
- T1 Item에서 Value To Find `Apple` → `Fruit`, Advanced 기본 상태. 어떤 행이 바뀌는지 기록.
- T2 같은 조건 + Match entire cell contents 체크(새 단계). T1과 비교.
- T3 `apple`(소문자)로 찾기, T1·T2 조건 각각. 대소문자 결과는 여기서 처음 관찰.
- T4 빈 칸·`""`·null 대상: Value To Find 비움/`null` 입력 시 대화상자 반응과 결과 관찰(입력 가능 여부 포함).
- T5 Qty 숫자 열에서 `1`→`9`, 체크 상태별 결과.
- T6 Item·Other 두 열 선택 후 한 번에 치환(범위 확인).
- T7 보조 비교: 사용자 지정 열 `Text.Replace([Item],"Apple","Fruit")` 결과 vs T1.
- T8 Close & Load, 시트에서 LEN/EXACT로 결과 확인, 저장 파일을 openpyxl로 읽어 대조.
- 반복: T1·T2는 새 복사본에서 1회 더(일치 여부 기록). 나머지는 1회, 글에 "1회 시험"으로 표기.
- 시험하지 않음(글에 명시 예정): 다른 Excel 버전·지역 설정·Mac·웹, 대용량, Comparer 인수, 정규식, 다중 값 목록 치환, "Replace using special characters" 상세(WP 371 참조로 갈음).
- 미확인 후보: 대화상자가 생성하는 M 함수 선택 규칙(시험 후 저장 코드로 확인).

## 4. 화면 캡처 제안 (실제 시험 화면이 도움이 되는 지점)
핵심 3장(사용자 캡처, 시험 후 확정):
① Replace Values 대화상자: Value To Find/Replace With와 Advanced options 펼친 상태(체크 위치 확인용).
② T1 결과 미리보기 + 수식줄(어느 행이 바뀌었는지, 생성된 함수 확인).
③ T2 결과 미리보기 + 수식줄(T1과 나란히 비교 가능한 상태).
선택 1장: 숫자 열 또는 null 처리 결과(차이가 있을 때만). 결과가 표로 충분하면 이미지를 줄일 수 있음. 캡처에는 개인정보 없음(시험 데이터만), 경로·계정 정보 노출 여부는 캡처 후 확인.
