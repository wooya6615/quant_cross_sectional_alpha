# Pre-registration: value_alpha_v1

작성일: 2026-09-16
브랜치: experiment/value-alpha-v1

이 문서에 적힌 값은 결과를 본 뒤 수정하지 않는다. 수정이 필요하면 결과를 보기 전에
별도 커밋으로 diff를 남긴다.

## 1. Research Question
KOSPI200에서 밸류에이션 지표(PER/PBR/배당수익률)가 향후 수익률의
cross-sectional predictor로 작동하는가?

## 2. Hypothesis / Economic Reasoning
저평가(PER 낮음 / PBR 낮음 / 배당수익률 높음) 종목이 향후 수익률이 높다 —
전통적 value premium. 시장이 저평가 기업의 펀더멘털을 과소평가하거나
(행동재무학: 성장주 선호/과잉 비관 편향), 또는 저평가 자체가 재무적
위험(distress risk)에 대한 보상(위험 프리미엄)일 수 있다.

약해질 수 있는 조건: "value trap"(저평가가 구조적 쇠퇴 반영인 경우, 저평가가
아니라 정당한 할인), 성장주 강세장 국면 — Alpha_ShortLevel에서 2017년(저변동성
강세장)에 신호가 반대로 작동했던 것과 같은 국면 리스크가 여기도 있을 수 있음.

## 3. Alpha 정의 (3개, 독립적으로 검증)
지표를 섞지 않고 따로 검증한다(2절 "무작위로 지표 조합 금지" 원칙):

- `Alpha_PER` = cross-sectional rank(-PER) — PER 낮을수록 랭크 높게
- `Alpha_PBR` = cross-sectional rank(-PBR) — PBR 낮을수록 랭크 높게
- `Alpha_DivYield` = cross-sectional rank(배당수익률) — 높을수록 랭크 높게

결합(9절 Alpha Combination)은 세 개 각각 개별 검증이 끝난 뒤에만 고려한다.

Holding period 후보 (전부 리포트): 20 / 60 / 120일 — Short Interest보다 길게
잡는다. 밸류에이션은 펀더멘털 기반 persistent 신호라 짧은 holding에서는
노이즈에 묻힐 가능성이 높다는 판단(가설 2절과 일치하는 선택이지 결과를 보고
정한 게 아님).

## 4. 데이터 및 look-ahead 처리

- 소스: pykrx `get_market_fundamental(start, end, ticker)` — 반환 컬럼
  BPS/PER/PBR/EPS/DIV/DPS
- **Look-ahead 검증 완료 (2026-09-16)**: 삼성전자(005930) 2018~2022년
  EPS/BPS 값이 실제로 바뀌는 날짜를 직접 확인함. 매해 5월 2일~5월 4일에
  변경 — 사업보고서 법정 제출기한(3/31) + KRX 검토기간(~1개월)과 시점이
  일치. 연초나 제출기한 직후에 미리 반영되는 정황 없음 → **shift 불필요
  (기존 가정 확인됨)**.
- **발견한 데이터 quirk**: 액면분할이 있었던 해(예: 삼성전자 2018년 5/4
  50:1 분할)는 사업보고서 반영(5/2, 분할 전 기준)과 분할 조정(5/4)이
  이틀 간격으로 따로 들어와서, 그 사이 하루 EPS/BPS가 극단치로 찍힌다.
  cross-sectional rank 계산 시 이 하루짜리 극단치가 섞이지 않는지 스팟체크
  필요.
- **PER≤0 처리**: 적자 기업은 PER이 NaN이 아니라 0으로 찍혀 나옴(pykrx
  문서 예시로 확인). 13절 교훈 그대로 적용 — PER≤0은 NaN으로 매핑하고
  `is_loss` 플래그를 별도로 둔다. PBR/DIV는 적자와 무관하게 계산되므로
  이 처리가 필요 없음(단, PBR이 음수(자본잠식)인 경우는 별도 확인 필요).
- 유니버스: KOSPI200, 매 리밸런싱 시점마다 재조회(survivorship bias 방지)
- 공매도 전면금지 같은 해당 사항 없음 — 밸류에이션 지표는 그 규제와 무관.

## 5. 백테스트 방법
- 거래비용 가정: short_interest_alpha_v1과 동일(키움증권 온라인 기준,
  매수 0.015% / 매도 0.215% / 슬리피지 편도 5bp)
- Train / Validation / Final Test 기간 분할: (PBO 단계에서 확정)

## 6. Robustness 축 (전부 사전 고정)
- Parameter: holding period ∈ {20, 60, 120}
- Time/Regime: 특히 2017년(성장주 강세장) 별도 확인 — Level 때와 같은
  국면 반전이 있는지
- Universe: KOSPI200 내 large/mid/small cap 분위, 액면분할 발생 종목/연도는
  별도 스팟체크

## 7. PBO
- holding period 축은 실제 탐색한 파라미터이므로 PBO 검증 대상

## 8. 실패 판정 기준 (사전 정의)
- Long-short Sharpe가 거래비용 반영 후에도 유의미하게 0보다 크지 않으면 "no edge"
  (short_interest_alpha_v1과 동일 기준)
- 연도별 log-return 기여도 50% 초과 시 "국면 의존적" 판정