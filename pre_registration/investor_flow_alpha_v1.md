# Pre-registration: investor_flow_alpha_v1

작성일: 2026-09-18
브랜치: experiment/investor-flow-alpha-v1

이 문서에 적힌 값은 결과를 본 뒤 수정하지 않는다. 수정이 필요하면 결과를 보기 전에
별도 커밋으로 diff를 남긴다.

## 1. Research Question
KOSPI200에서 외국인/기관 투자자의 순매수가 향후 수익률의 cross-sectional
predictor로 작동하는가?

## 2. Hypothesis / Economic Reasoning
정보 우위가 있다고 여겨지는 투자자 그룹(외국인/기관)의 순매수를 따라가면
초과수익을 낼 수 있다는 "smart money" 가설. 메커니즘: 외국인/기관이 개인
대비 정보 접근·분석 역량에서 우위가 있어, 이들의 매매가 아직 가격에 반영되지
않은 정보를 선행 반영한다고 가정.

Short Interest Level 때(정보 우위 투자자의 지속적 압력 → persistent 신호)와
논리 구조는 유사하지만, 다음 지점에서 차이가 있고 이게 약화 요인이 될 수
있다:
- 외국인/기관 순매수는 이미 시장 참여자 대부분이 실시간으로 확인 가능한
  잘 알려진 지표라, Short Interest보다 arb-out(신호 소진)됐을 가능성이 높음
- 지수 리밸런싱에 따른 패시브 자금 편입/편출은 정보와 무관한 기계적 순매수를
  발생시켜 신호를 오염시킬 수 있음 — Short Interest의 공매도 전면금지 구간
  (LP/시장조성자 헤지물량)과 유사한 종류의 오염 가능성으로, 사전에 플래그
  처리를 고려한다(4절 참고)

## 3. Alpha 정의 (2개, 독립적으로 검증)

### Alpha_ForeignNetBuy
- 정의: cross-sectional rank(외국인 순매수대금 누적(K거래일) / 시가총액)
- 기대 방향: 양(+) — 외국인 순매수 많을수록 향후 수익률 높음
- K 후보 (전부 리포트): 5 / 10 / 20

### Alpha_InstNetBuy
- 정의: cross-sectional rank(기관 순매수대금 누적(K거래일) / 시가총액)
- 기대 방향: 양(+) — 기관 순매수 많을수록 향후 수익률 높음
- K 후보 (전부 리포트): 5 / 10 / 20

Holding period 후보 (두 alpha 공통, 전부 리포트): 5 / 10 / 20일 — Short
Interest와 동일한 논리로, flow 기반 신호라 persistent보다는 단중기 효과로
가정하고 짧게 잡는다.

> K와 holding 둘 다 실제 탐색한 파라미터 축이므로 전부 PBO 검증 대상이다.

## 4. 데이터 및 look-ahead 처리

- **소스 확정 필요 (미검증, 최우선 확인 항목)**: pykrx
  `get_market_trading_value_by_date`(투자자별 거래대금) 계열 함수 후보 —
  실제 반환 컬럼명(외국인/기관/개인 구분, 순매수 vs 순매수대금 등)과 인자
  순서를 코드 작성 전에 먼저 `src/scripts/`에 스팟체크 스크립트로 직접
  확인한다. Short Interest 라인에서 거래량(flow) 데이터를 잔고(stock)
  데이터로 착각해 수집한 전례(pre_registration/short_interest_alpha_v1.md
  3절)가 있으므로, "순매수" 정의가 누적 flow인지 잔고 change인지 문서만
  보고 판단하지 않고 실제 반환값을 직접 확인 후 alpha 정의를 코드로 옮긴다.
- **시가총액 데이터 신규 필요**: 순매수 금액을 시가총액으로 정규화해야 하므로
  `get_market_cap` 계열 데이터를 추가 수집해야 함. 정규화 없이 순매수
  금액 자체를 쓰면 대형주 편향이 생기므로 반드시 시가총액 대비 비율로 변환.
- **패시브 리밸런싱 오염 가능성**: KOSPI200 정기 변경(6월/12월) 편입·편출
  종목은 편입/편출 발표 후 수 거래일간 기계적 순매수/순매도가 발생함.
  Short Interest의 `in_ban_period` 플래그와 같은 방식으로 `near_index_rebal`
  같은 플래그를 추가할지, 아니면 편입 발표일 전후 N거래일을 아예 alpha
  계산에서 제외할지는 raw 데이터를 실제로 열어보고(편입 종목의 순매수
  스파이크가 실제로 관측되는지) 결과를 보기 전에 결정한다.
- **PUBLICATION_LAG_DAYS 미검증**: 투자자별 거래대금은 당일 장 마감 후
  발표된다고 가정 — Short Interest의 거래량 데이터와 동일한 가정(=1)을
  하한으로 두되, 실제 공시 스케줄 확인 전까지는 동일하게 적용하고 확인 후
  필요하면 늘린다(줄이는 건 금지).
- 유니버스: KOSPI200, 매 리밸런싱 시점마다 재조회 (survivorship bias 방지)
- 결측: 거래 자체가 없었던 날은 순매수 0이 아니라 NaN으로 구분해야 하는지
  (거래 정지 등) raw 데이터 확인 후 처리 방식을 사전에 확정한다.

## 5. 백테스트 방법
- 거래비용 가정: 기존과 동일 (키움증권 온라인 기준)
- **winsorize 5% 기본 적용 (사전 확정)**: value_alpha_v1의 교훈을 반영해
  처음부터 `winsorize_pct=0.05`를 기본값으로 켠다.
- Train / Validation / Final Test 기간 분할: (PBO 단계에서 확정)

## 6. Robustness 축 (전부 사전 고정)
- Parameter: K ∈ {5, 10, 20}
- Time/Regime: KOSPI200 정기 변경 시점(6월/12월) 전후 별도 확인 — 패시브
  자금 오염 여부 검증
- Universe: KOSPI200 내 large/mid/small cap 분위 — 외국인/기관 수급은
  대형주에 쏠릴 가능성이 높아 시가총액 분위별로 신호 강도가 다를 수 있음

## 7. PBO
- K × holding period 조합 전부 PBO 검증 대상

## 8. 실패 판정 기준 (사전 정의)
- Long-short Sharpe가 거래비용 반영 후에도 유의미하게 0보다 크지 않으면 "no edge"
  (기존 라인과 동일 기준)
- 연도별 log-return 기여도 50% 초과 시 "국면 의존적" 판정 (100% 초과 시
  판정 불가 — `yearly_regime_report` 기존 수정 기준 재사용)