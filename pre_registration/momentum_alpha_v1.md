# Pre-registration: momentum_alpha_v1

작성일: 2026-09-18
브랜치: experiment/momentum-alpha-v1

이 문서에 적힌 값은 결과를 본 뒤 수정하지 않는다. 수정이 필요하면 결과를 보기 전에
별도 커밋으로 diff를 남긴다.

## 1. Research Question
KOSPI200에서 가격 모멘텀(과거 수익률)이 향후 수익률의 cross-sectional predictor로
작동하는가? 특히 formation window 길이에 따라 방향이 반대로 나타나는지
(장기 모멘텀 vs 단기 반전)를 분리해서 검증한다.

## 2. Hypothesis / Economic Reasoning
**장기(12-1개월류) 모멘텀**: 과거 승자가 단중기적으로 계속 승자 — 정보의 점진적
확산(underreaction), 처분효과(disposition effect), 허딩이 메커니즘으로 제시됨
(Jegadeesh & Titman). 최근 1개월을 formation에서 제외하는 건 문헌상 표준 컨벤션 —
초단기 구간에는 반전이 섞여 신호를 훼손한다는 이유.

**단기(1개월 이하) 반전**: 위와 반대 메커니즘 — 유동성 충격에 대한 과잉반응,
마켓메이커의 재고 리스크 프리미엄 등으로 단기적으로는 승자가 오히려 향후
수익률이 낮다는 문헌이 있음. 두 효과를 하나의 alpha로 섞지 않고 별도 정의로
분리해서 검증한다(기존 원칙 2절 유지).

약해질 수 있는 조건: 모멘텀 크래시(급락 후 급반등 국면에서 과거 루저가 오히려
급등 — 국내 사례로는 short_interest_alpha_v1에서 확인된 2020년 코로나 반등
국면과 유사한 패턴 가능성), 한국 시장은 개인 투자자 비중이 높아 단기 반전
효과가 문헌 평균보다 강하게 나타날 수 있다는 가설.

## 3. Alpha 정의 (2개, 독립적으로 검증)

### Alpha_Mom12_1
- 정의: cross-sectional rank(과거 약 12개월(240영업일) 수익률, 단 최근
  1개월(20영업일)은 formation에서 제외 — 즉 `price[t-20]/price[t-240] - 1`)
- 기대 방향: 양(+) — 과거 승자가 향후에도 상대적으로 우수
- Holding period 후보 (전부 리포트): 20 / 60 / 120일 — Value 라인과 동일한
  스케일(persistent 신호로 가정)

### Alpha_MomShort
- 정의: cross-sectional rank(-과거 1개월(20영업일) 수익률) — 최근 급등 종목의
  랭크를 낮게(반전 가정)
- 기대 방향: 양(+, 즉 랭크값 자체는 반전 방향을 이미 내장) — 최근 급락 종목이
  향후 단기 수익률 높음
- Holding period 후보: 5 / 10 / 20일 — ShortCover와 동일한 논리로, 단기 효과이므로
  짧게 잡음

> 두 alpha 모두 실제 탐색한 파라미터 축(holding period)은 전부 PBO 검증 대상이다.
> "제일 잘 나온 조합"만 골라서 보고하는 건 금지.

## 4. 데이터 및 look-ahead 처리

- 소스: `get_market_ohlcv` — 이미 수집된 `data/raw/price_panel.parquet` 재사용,
  추가 수집 불필요
- **수정주가 여부 확인 필요 (미검증)**: `get_market_ohlcv`가 액면분할/유상증자
  등 corporate action을 반영한 수정주가를 반환하는지 결과를 보기 전에 확인한다.
  value_alpha_v1에서 삼성전자 2018년 액면분할 시 EPS/BPS가 이틀 간격으로 따로
  반영되며 하루짜리 극단치가 생긴 quirk를 발견한 바 있음 — 가격 데이터에도
  유사한 분할 경계 극단치가 formation window(특히 Mom12_1의 240일 lookback)에
  섞일 가능성이 있으므로, 분할 이벤트가 있었던 종목·연도는 스팟체크 항목으로
  둔다.
- look-ahead: formation window는 전부 t 시점 이전 과거 가격만 사용하므로
  feature 자체의 shift는 불필요. 다만 formation window의 끝 시점(t)과 forward
  return의 시작 시점(lag)이 겹치지 않는지 확인 — `lag=0`으로 두되
  `compute_forward_returns`가 t 시점 가격을 entry로 쓰는 것과 Alpha_Mom12_1이
  t-20 시점 가격까지만 쓰는 것 사이에 순서 상 누수가 없는지 코드 리뷰 단계에서
  재확인한다.
- 유니버스: KOSPI200, `get_index_portfolio_deposit_file` — 매 리밸런싱 시점마다
  재조회 (survivorship bias 방지, 기존 컨벤션 유지)
- 결측: formation window 내 가격이 일부라도 없는 종목은 해당 시점 alpha를
  NaN으로 둔다(상장 초기 종목 등). 0으로 채우지 않음.

## 5. 백테스트 방법
- 거래비용 가정: 기존과 동일 (키움증권 온라인 기준 — 매수 0.015%, 매도 0.215%,
  슬리피지 편도 5bp)
- **winsorize 5% 기본 적용 (사전 확정)**: value_alpha_v1에서 얻은 일반 교훈
  ("IC 좋아도 quantile 평균 롱숏 백테스트는 극단치 때문에 반대로 나올 수 있다")을
  반영해, 처음부터 `winsorize_pct=0.05`를 기본값으로 켜고 시작한다. 결과를 보고
  나중에 추가하는 방식(value 라인에서 했던 것)은 반복하지 않는다.
- Train / Validation / Final Test 기간 분할: (PBO 단계에서 확정, Test는 반복 확인 금지)

## 6. Robustness 축 (전부 사전 고정)
- Parameter: holding period (Mom12_1: {20,60,120}, MomShort: {5,10,20})
- Time/Regime: 모멘텀 크래시로 알려진 급반등 국면 별도 확인 (2020년 코로나
  반등 구간을 최우선으로, short_interest 라인에서 이미 이상 신호가 확인된
  구간이므로)
- Universe: KOSPI200 내 large/mid/small cap 분위, 액면분할 발생 종목/연도는
  별도 스팟체크

## 7. PBO
- holding period 축(두 alpha 각각)에 대해 PBO 계산 필수
- 단일값 고정 축은 PBO 축에서 제외

## 8. 실패 판정 기준 (사전 정의)
- Long-short Sharpe가 거래비용 반영 후에도 유의미하게 0보다 크지 않으면 "no edge"
  (기존 라인과 동일 기준)
- 연도별 log-return 기여도 100% 초과 시 "판정 불가"(총합 발산), 50% 초과 시
  "국면 의존적" — `yearly_regime_report`의 2차 수정 기준을 그대로 사용, 재발
  가능성 있는 버그이므로 수치 이상해 보이면 원자료(절대값)부터 먼저 확인할 것