# Pre-registration: short_interest_alpha_v1

작성일: 2026-09-16
브랜치: experiment/short-interest-v1

이 문서에 적힌 값은 결과를 본 뒤 수정하지 않는다. 수정이 필요하면 결과를 보기 전에
별도 커밋으로 diff를 남긴다.

## 1. Research Question
한국 시장(KOSPI200)에서 종목별 공매도잔고비율의 수준(level)과 변화(momentum)가
각각 향후 수익률의 cross-sectional predictor로 작동하는가?

## 2. Alpha 정의 (2개, 독립적으로 검증)

### Alpha_ShortLevel
- 정의: cross-sectional rank(공매도잔고비율_i,t)
- 기대 방향: 음(-) — 잔고비율 높은 종목일수록 향후 수익률 낮음
- Holding period 후보 (전부 리포트): 5일 / 10일 / 20일

### Alpha_ShortCover
- 정의: -Δ(공매도잔고비율_i,t, K일) — 최근 K일간 잔고비율 감소폭
- 기대 방향: 양(+) — 급격한 감소(숏커버링)일수록 향후 단기 수익률 높음
- K 후보 (전부 리포트): 5 / 10 / 20
- Holding period 후보: 1일 / 3일 / 5일 (Level보다 짧게 — 메커니컬 효과이므로)

> 실제로 탐색한 파라미터 축(K, holding period)은 전부 PBO 검증 대상이다.
> 결과를 보고 "제일 잘 나온 조합"만 골라서 보고하는 건 금지.

## 3. 데이터 및 look-ahead 처리

> **2026-09-10 수정 (결과 확인 전, diff로 남김)**: feature를 shift하는 대신
> forward return을 미루는 방식으로 정렬 컨벤션을 바꿈. 근거: 공매도 데이터가
> 당일 장 마감 후 발표되므로, raw 값을 "당일 저녁 이후 형성되는 신호"로 보고
> 그 신호를 다음날부터의 forward return과 짝지으면 feature를 버리지 않고도
> look-ahead를 피할 수 있음. 정보 누수를 막는 지점이 feature→label로 옮겨간
> 것이며 shift 자체를 없앤 게 아님 — 아래 항목 참고.

- **소스 (2026-09-11 수정)**: `Alpha_ShortLevel`/`Alpha_ShortCover`는 원래 정의(2절)대로
  잔고(stock) 데이터 `get_shorting_balance_by_date`를 쓴다 — 반환 컬럼의 "비중"이
  곧 공매도잔고비율. 처음에 실수로 거래량(flow) 데이터인
  `get_shorting_volume_by_date`를 수집했는데, 이건 "그날 거래된 물량 중 공매도
  비중"이라 잔고와 다른 개념이다(특히 Alpha_ShortCover는 잔고가 줄어드는 걸
  봐야 하는데 거래량으로는 직접 안 보임). 거래량 데이터는 이미 받아뒀으니
  버리지 않고 남겨두되, 이번 alpha 정의에는 쓰지 않는다.
- **정렬 컨벤션**: raw 공매도값(날짜 t)은 shift하지 않는다. 대신 이 값과 짝지을
  수익률은 반드시 forward return이어야 하며, t + `PUBLICATION_LAG_DAYS` 영업일
  시점부터 시작해야 한다 (calendar-day가 아니라 row 기반 오프셋).
- `PUBLICATION_LAG_DAYS`: 거래량은 당일 저녁 발표 가정 → 1. 잔고 데이터는
  아직 미검증 — 실제 공시 스케줄 확인 전까지 동일하게 1을 하한으로 두고,
  확인 후 필요하면 늘린다(줄이는 건 금지). 이 값은 반드시 결과를 보기 전에
  확정한다.
- 유니버스: KOSPI200, `get_index_portfolio_deposit_file(ticker, date)` —
  매 리밸런싱 시점마다 그 시점 기준으로 재조회 (survivorship bias 방지)
- **공매도 전면금지 구간 (2026-09-11 수정, 결과 확인 전 diff로 남김)**: 원래는
  2023-11-06~2025-03-30을 NaN으로 마스킹(기간 절단)할 계획이었으나, 실제 raw
  데이터를 열어보니 이 기간에도 값이 존재함을 확인. 2023-11-06 금융위원회
  보도자료 확인 결과 "시장조성자·유동성공급자 등의 차입공매도는 허용"되어
  있었음 — 즉 이 구간의 공매도 값은 일반 투자자의 정보 기반 매도가 아니라
  LP/시장조성자의 헤지용 물량. 값을 지우지 않고 그대로 두되, `in_ban_period`
  boolean 플래그를 추가해서 이 구간을 구분한다. Alpha_ShortLevel/
  Alpha_ShortCover는 일반 투자자 행동을 가정하므로, 이 구간을 포함해서 백테스트할
  지 국면(11절)으로 따로 떼어 검증할지는 정규화/백테스트 단계에서 `in_ban_period`
  플래그로 제어한다.
- **Alpha_ShortCover 금지경계 델타 제외 (2026-09-12 수정, 결과 확인 후 diff로
  남김)**: 11절 robustness 테스트에서 K∈{5,10,20} × holding∈{1,3,5} 9개 조합
  전부 "국면 의존적"으로 판정됐고, 2025년(금지 해제 직후) log-return 기여도가
  전 조합에서 압도적으로 컸다(최대 116%). K일 lookback이 금지 시작/해제
  경계를 걸치면 잔고가 인위적으로 점프해서 진짜 숏커버링처럼 보이는
  데이터 오염 메커니즘으로 판단, 그 경계를 걸치는 델타 행을 NaN 처리하도록
  `compute_alpha_short_cover`를 수정했다. 결과를 본 뒤의 변경이지만
  "좋아 보이는 파라미터 선택"이 아니라 "명백한 오염 메커니즘 제거"라고
  보고 진행 — 수정 후에도 여전히 국면 의존적으로 나오면 그건 그대로
  받아들인다.
- 결측: 공매도 자체가 없는 종목은 NaN + `is_shortable=False` 플래그. 0으로 채우지 않음.

## 4. 백테스트 방법
- **거래비용 가정 (2026-09-16 확정, 결과 확인 전 — 키움증권 온라인 기준으로
  수정)**: 매수 0.015%(위탁수수료만), 매도 0.215%(위탁수수료 0.015% +
  증권거래세 0.05% + 농어촌특별세 0.15%, 코스피 2026년 기준) — 매수/매도
  비대칭. 슬리피지는 편도 5bp를 출처 없는 보수적 가정으로 추가. turnover
  1단위(비율만큼 종목 교체) 당 매수 1회+매도 1회로 계산.
- Train / Validation / Final Test 기간 분할: (PBO 단계에서 확정, Test는 반복 확인 금지)

## 5. Robustness 축 (전부 사전 고정)
- Parameter: K ∈ {5, 10, 20}
- Time/Regime: bull/bear, high/low vol 구간
- Universe: KOSPI200 내 large/mid/small cap 분위

## 6. PBO
- 실제 탐색한 축(K, holding period)에 대해 PBO 계산 필수
- 단일값 고정 축은 PBO 축에서 제외(탐색을 안 해서이지 신호가 강해서가 아님)

## 7. 실패 판정 기준 (사전 정의)
- Long-short Sharpe가 거래비용 반영 후에도 유의미하게 0보다 크지 않으면 "no edge"
- 연도별 log-return 기여도 50% 초과 시 "국면 의존적" 판정 → 기간 절단 재검증