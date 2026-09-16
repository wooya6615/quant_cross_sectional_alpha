# PROJECT_SUMMARY.md

quant_cross_sectional_alpha 연구 기록. 실패한 연구도 지우지 않고 남긴다(12절).

---

## Research: short_interest_alpha_v1

- **Date**: 2026-09-16
- **Pre-registration**: `pre_registration/short_interest_alpha_v1.md`

### Hypothesis
KOSPI200에서 공매도 관련 지표가 향후 수익률의 cross-sectional predictor가
되는지, 서로 다른 시간대의 두 가설로 분리해서 검증:
- **가설 A (Alpha_ShortLevel, persistent)**: 공매도잔고비율이 높을수록
  정보 우위 투자자의 지속적 매도 압력 → 향후 수익률과 음의 상관
- **가설 B (Alpha_ShortCover, short-term reversal)**: 공매도잔고 급감
  (숏커버링) → 단기 매수 압력 → 향후 수익률과 양의 상관

### Alpha 정의
- `Alpha_ShortLevel` = cross-sectional rank(공매도잔고비율), holding 5/10/20일
- `Alpha_ShortCover(K)` = cross-sectional rank(-Δ(공매도잔고비율, K거래일)),
  K∈{5,10,20}, holding 1/3/5일

### 데이터
- 유니버스: KOSPI200, 리밸런싱 시점마다 재조회 (survivorship bias 방지)
- 소스: `get_shorting_balance_by_date`(잔고), `get_market_ohlcv`(수정주가),
  2015-01-01~2025-12-31
- look-ahead: raw는 shift하지 않고 forward return을 `PUBLICATION_LAG_DAYS`
  (=1)만큼 미뤄서 계산
- 공매도 전면금지(2023-11-06~2025-03-30): NaN 마스킹 대신 `in_ban_period`
  플래그 (시장조성자/유동성공급자 헤지 물량이 실제로 존재함을 raw 데이터에서
  확인, 2절 금융위 보도자료 근거)
- 커버리지: 잔고 98.8%(324/328), 가격 100%

### 정규화
Cross-sectional rank(percentile). 극단값에 안 흔들리고 임의 파라미터가
필요 없어서 첫 방법으로 채택.

### Results (IC / Rank IC, MIN_VALID_TICKERS=30 이상인 날짜만)

**Alpha_ShortLevel**
| holding | IC mean | ICIR | Rank IC mean | Rank ICIR |
|---|---|---|---|---|
| 5  | -0.0058 | -0.057 | -0.0074 | -0.066 |
| 10 | -0.0086 | -0.082 | -0.0107 | -0.096 |
| 20 | -0.0112 | -0.104 | -0.0142 | -0.124 |

방향은 가설과 일치(음), holding이 길어질수록 IC가 커지는 패턴 — persistent
가설과 정성적으로 부합. 크기 자체는 약함(ICIR ≪ 0.5).

**Alpha_ShortCover(K)** — 방향은 가설과 일치(양)하지만 Level보다도 약함
(ICIR 0.02~0.07 수준, K가 커질수록 오히려 약해짐 — 9개 조합 전부 IC mean
0.002~0.005 사이).

### Robustness (11절, 연도별 log-return 기여도, 상위/하위 quintile 롱숏 근사)

- **Alpha_ShortLevel**: holding 5/10/20 전부 "국면 의존적이지 않음"
  (최대 연도 기여도 50% 미만). 단, **2017년·2020년만 부호가 일관되게
  반대**로 나옴(다른 8개 연도는 전부 가설과 같은 방향) — 저변동성
  강세장(2017)·코로나 급락&반등(2020) 국면에서 신호가 반대로 작동하는
  패턴으로 보이나, 50% 기준선은 넘지 않아 정식 판정은 "통과".
- **Alpha_ShortCover**: K×holding 9개 조합 **전부 국면 의존적**. 2025년
  (금지 해제 직후) 기여도가 전 조합에서 압도적(최대 161%), 2024년은
  반대로 크게 마이너스인 경우가 많음.

### Failure case: Alpha_ShortCover 폐기

1차 가설: K일 lookback 구간이 금지 시작/해제 경계를 걸치면 잔고가
인위적으로 점프해서 가짜 숏커버링 신호가 생긴다 → `compute_alpha_short_cover`에
경계를 걸치는 델타 행을 NaN 처리하는 수정 적용.

**결과: 가설 기각.** 수정 후에도 9개 조합 전부 국면 의존적 판정 그대로,
2025년 기여도는 오히려 더 커진 조합도 있었음(K=20/holding=5: 116%→161%).
경계 근처 소수 행만 제외한 걸로는 2025년 4월~12월 전체에 퍼진 쏠림을
설명 못 함 — "델타 계산의 경계 오염"이 아니라 **2025년 자체가 통째로
다른 국면**이었을 가능성이 훨씬 큼(원인 미상 — 추가 조사 없이 더 손대는
건 PBO 위반이라 여기서 중단).

**결론**: Alpha_ShortCover는 방향은 가설과 맞지만 신호가 Level보다 약하고,
robustness 실패를 한 번 고쳐보려 했으나 실패 — **폐기**.

### Backtest (거래비용 반영, 키움증권 온라인 기준: 매수 0.015%, 매도 0.215%, 슬리피지 편도 5bp 가정)

방향은 IC가 음수라는 결과에 맞춰 반영(잔고 낮은 종목 롱 / 높은 종목 숏).

| holding | ann_return | ann_vol | sharpe | mdd | calmar | ann_turnover | t-stat(대략) |
|---|---|---|---|---|---|---|---|
| 5  | 0.0094 | 0.1093 | 0.0862 | -0.3748 | 0.0252 | 3.6380 | ≈0.26 |
| 10 | 0.0243 | 0.1111 | 0.2188 | -0.3333 | 0.0729 | 2.6908 | ≈0.67 |
| 20 | 0.0222 | 0.1207 | 0.1835 | -0.2779 | 0.0797 | 1.9813 | ≈0.56 |

세 holding 전부 Sharpe 0.1~0.22, t-stat이 통상 기준(≈2) 근처도 못 감, MDD
-28%~-37%로 큰데 연 수익은 2%대라 Calmar도 0.03~0.08. 연 2~3.6회 회전하는
turnover가 IC 단계에서 보였던 약한 신호를 사실상 비용으로 다 깎아먹음.

### Conclusion

- **Alpha_ShortLevel**: IC 방향 일치, robustness 통과했지만 **실제 거래비용
  반영 백테스트에서 Sharpe가 통계적으로 유의하지 않음** — 사전등록 7절 실패
  기준("Long-short Sharpe가 거래비용 반영 후 유의미하게 0보다 크지 않으면
  no edge")에 해당. **폐기.**
- **Alpha_ShortCover**: robustness 자체 실패 (2025년 국면 집중, 수정 시도도
  실패) — **폐기.**
- PBO는 실행하지 않음 — PBO는 "좋아 보이는 결과가 우연인지" 검증하는
  도구인데, 애초에 좋아 보이는 결과가 없어서(3개 holding 전부 균일하게
  약함) 검증할 대상이 없음.
- `quant_xgboost` 라인의 모멘텀·투자자 flow와 같은 패턴("가설 방향은 맞는데
  강도가 비용을 못 이김")으로 마무리.

### Next experiment

short_interest_alpha_v1 라인 종료. 3절 후보군 중 다음 alpha(모멘텀/투자자
순매수 등)로 새 사전등록 문서를 시작할 것.