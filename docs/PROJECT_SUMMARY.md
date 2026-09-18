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

---

## Research: value_alpha_v1

- **Date**: 2026-09-16
- **Pre-registration**: `pre_registration/value_alpha_v1.md`

### Hypothesis
저평가(PER↓/PBR↓/배당수익률↑) 종목이 향후 수익률이 높다 — 전통적 value
premium. 행동재무학적 과잉비관 편향 또는 재무 위험 프리미엄으로 설명.
약해질 조건: value trap, 성장주 강세장 국면.

### Alpha 정의
- `Alpha_PER` = rank(-PER), `Alpha_PBR` = rank(-PBR),
  `Alpha_DivYield` = rank(배당수익률) — 셋 다 독립적으로 검증
- holding 20/60/120일
- PER≤0 → NaN + `is_loss`, PBR<0 → NaN + `is_negative_book`

### 데이터
- 소스: `get_market_fundamental`(밸류에이션), 2015-01-01~2025-12-31
- **look-ahead 검증**: 삼성전자 2018~2022 EPS/BPS 변경일이 매해 5월 초로
  확인 — 사업보고서 제출+KRX 검토 시점과 일치, **shift 불필요 확인됨**
- 발견한 quirk: 액면분할 연도(삼성전자 2018)는 사업보고서 반영(5/2)과
  분할조정(5/4)이 이틀 차이로 따로 들어와 하루짜리 극단치 발생
- 적자(`is_loss`) 17%, 자본잠식(`is_negative_book`) 0%(대형주 유니버스라
  합리적), PBR=0 0.8%(사소, 미처리)

### Results (IC, holding=120 기준 요약 — 셋 다 holding 길수록 Rank IC 강화)
| Alpha | Rank IC mean | Rank ICIR |
|---|---|---|
| PER | 0.0468 | 0.318 |
| PBR | 0.0645 | 0.373 |
| DivYield | 0.0518 | 0.382 |
| Composite(단순평균) | 0.0644 | 0.384 |

**IC(Pearson)은 전부 0 근처거나 음수, Rank IC(Spearman)만 뚜렷하게 양수**
— forward return의 극단값이 Pearson을 왜곡하는 것으로 판단.

### Robustness (11절)
- PER: h=20/120 국면 의존적(2015년, 표본 첫해), h=60 통과
- PBR: 3개 holding 전부 "총합이 0에 가까워 판정 불가"(연도별 방향이
  엇갈리며 상쇄) — Short Interest Cover 때와 다른 종류의 불안정성
- DivYield: h=20 국면 의존적(2020년, 코로나), h=60/120 통과
- **방법론 버그 발견 및 2차 수정**: `yearly_regime_report`의 연도 기여도
  비율이 분모(총합)가 작을 때 발산(-320%/+259%)하는 걸 발견 → 1차
  수정(총합 vs 중앙값 비교)도 불완전 → 최종적으로 "contribution이 100%
  넘으면 판정 불가"로 수정

### Failure case: mean 기반 백테스트가 IC와 정반대로 나옴

1차 백테스트(winsorize 없음): 9개 조합(3 alpha × 3 holding) 전부 Sharpe
마이너스(최저 DivYield h=120: -0.66), IC 단계의 긍정적 패턴과 완전히
모순.

**원인 조사(스팟체크)**: DivYield 바스켓 평균 vs 중앙값 롱숏 수익률 비교 →
평균은 마이너스(-0.65~-1.15)인데 중앙값은 오히려 플러스(+0.29~+1.00),
상관은 0.82~0.90. **소수 극단치 종목이 바스켓 평균을 끌어내리고 있다는
명백한 증거.**

**Winsorize 시도**: 1%는 바스켓 크기(~65종목)상 사실상 안 잘림 확인 →
5%로 재시도(표본 크기 기반 계산값, 임의 튜닝 아님) → 결과 개선됐으나
(PBR은 3개 holding 전부 양전환, PER/DivYield는 부분 개선) 최선의 조합도
t-stat ≈0.70으로 유의성 기준(≈2) 미달.

**합성 알파(단순 평균, 9절)**: PER-PBR-DivYield 상관 0.39~0.57(적당히
겹치면서도 독립적) 확인 후 결합. IC는 개별 알파보다 소폭 개선(Rank ICIR
0.384)됐지만, winsorize 5% 반영 백테스트는 여전히 0 근처~마이너스
(holding 20: 0.008 → holding 120: -0.126).

### Conclusion

- Alpha_PER, Alpha_PBR, Alpha_DivYield, Alpha_ValueComposite **전부 폐기**
  — 거래비용 반영(+winsorize 보정) 후에도 통계적으로 유의한 Sharpe 없음
  (8절 실패 기준 해당)
- **일반 교훈 (cross-alpha, 아래 섹션에도 기록)**: Rank IC가 좋아 보여도
  quantile 평균 롱숏 백테스트 결과가 정반대로 나올 수 있다 — 원인은
  바스켓 평균의 극단치 민감도. 다음 alpha 연구부터 IC 확인 직후 평균 vs
  중앙값 스팟체크를 표준 절차에 넣을 것.

### Next experiment

3절 후보군 중 다음 alpha(Foreign Ownership/모멘텀 재도전 등)로 새 사전등록
문서 시작. 새 라인에서는 처음부터 `winsorize_pct`를 백테스트 기본값으로
켜고 시작할 것.

---

## General Lessons (cross-alpha, 라인 넘어 재사용)

- pykrx는 KRX를 비공식으로 스크래핑하는 라이브러리라 원래 가끔 이유 없이
  깨진다(rate limit이 아니라 라이브러리 자체 불안정성일 수 있음) — 재시도
  +체크포인트를 항상 기본으로 깔고 시작할 것(`pykrx_utils.py`)
- pykrx 최근 버전은 KRX_ID/KRX_PW 환경변수 없이는 import 자체가 실패함
  (`.env` + `load_dotenv()`를 다른 import보다 먼저 실행해야 함)
- `reset_index().rename(columns={"index": "date"})` 패턴은 원래 인덱스에
  이름이 있으면(예: "날짜") 깨진다 — `df.index.name = "date"`로 강제
  통일 후 `reset_index()`할 것
- 연도별 "기여도 비율" 같은 지표는 분모가 0에 가까우면 발산한다 —
  원자료(절대값) 없이 비율만 보고 판단하지 말 것
- **IC/Rank IC가 좋아도 quantile 평균 롱숏 백테스트는 다른 결과를 낼 수
  있다** — 바스켓 평균은 극단치에 취약, 중앙값과 비교해서 괴리가 크면
  winsorize 필요(바스켓 크기 대비 최소 2~3개는 걸리는 강도로)
- 알파 방향(direction)은 IC 부호를 보고 명시적으로 맞춰야 한다 — 안 맞추면
  가설과 반대 포지션을 잡게 됨(Alpha_ShortLevel에서 실제로 있었던 실수)