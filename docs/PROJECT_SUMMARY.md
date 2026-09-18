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

## Research: momentum_alpha_v1

- **Date**: 2026-09-18
- **Pre-registration**: `pre_registration/momentum_alpha_v1.md`

### Hypothesis
KOSPI200에서 가격 모멘텀이 향후 수익률의 cross-sectional predictor로 작동하는지,
formation window 길이에 따라 방향이 반대로 나타나는지 분리해서 검증:
- **Alpha_Mom12_1 (장기, persistent)**: 과거 12-1개월 수익률 높을수록 향후
  수익률과 양의 상관 — 정보의 점진적 확산/처분효과/허딩
- **Alpha_MomShort (단기, reversal)**: 과거 1개월 수익률 낮을수록(반전) 향후
  단기 수익률과 양의 상관 — 유동성 충격 과잉반응

### Alpha 정의
- `Alpha_Mom12_1` = rank(price[t-20]/price[t-240] - 1), holding 20/60/120일
- `Alpha_MomShort` = rank(-(price[t]/price[t-20] - 1)), holding 5/10/20일

### 데이터
- 소스: 기존 `price_panel.parquet` 재사용(추가 수집 없음)
- **사전 검증**: 삼성전자 2018-05-04 액면분할 전후 종가 비율로 수정주가 여부
  확인 — 수정주가로 확인됨, shift/조정 로직 불필요

### Results (IC / Rank IC)

**Alpha_Mom12_1**
| holding | IC mean | ICIR | Rank IC mean | Rank ICIR |
|---|---|---|---|---|
| 20  | 0.0242 | 0.155 | 0.0096 | 0.058 |
| 60  | 0.0463 | 0.328 | 0.0191 | 0.124 |
| 120 | 0.0578 | 0.427 | 0.0262 | 0.175 |

세 라인 중 가장 강한 IC/ICIR. 단, **Pearson IC가 Rank IC보다 훨씬 큼** —
value_alpha_v1(Rank IC만 강하고 Pearson은 0 근처/음수)와 정반대 패턴. 극단치가
선형 상관을 끌어올리고 있다는 의심 신호로 판단, 스팟체크로 넘어감.

**Alpha_MomShort** — 전 holding에서 약함(IC mean 0.002~0.006, ICIR 0.02~0.05,
Rank IC도 최대 ICIR 0.18). ShortCover와 유사하게 IC 단계부터 이미 불안한 신호.

### Spotcheck: 평균 vs 중앙값 (winsorize 전)

- **Mom12_1**: 평균 기준 롱숏 누적이 중앙값 기준보다 4~6배 큼(예: h=120
  1.294 vs 0.322), 상관은 0.87~0.93. 소수 극단적 승자 종목이 바스켓 평균을
  끌어올리는 것으로 확인 — IC 단계 의심이 실증됨.
- **MomShort**: 반대로 평균이 중앙값보다 훨씬 작음(예: h=5 0.110 vs 1.450) —
  DivYield 때와 같은 패턴(소수 극단치가 평균을 끌어내림).
- 두 경우 다 사전등록에서 winsorize 5%를 기본값으로 이미 켜둔 게 맞는
  판단이었음(결과를 보고 나서가 아니라 value_alpha_v1 교훈을 반영해 사전에
  결정).

### Robustness (연도별 log-return 기여도)

- **Alpha_Mom12_1**: 3개 holding 전부 "국면 의존적이지 않음"(개별 연도 50%
  미만). 단, **2024+2025 두 해 합산 기여도가 60~68%**(h=20: 61.7%, h=60:
  67.9%, h=120: 60.6%)로 형식적 기준은 통과했지만 최근 2년에 극도로 쏠려
  있음 — 단일 연도 임계값만으로는 못 잡는 종류의 집중.
- **Alpha_MomShort**: 3개 holding 전부 "총합이 0에 가까워 판정 불가"(연도별
  방향이 계속 뒤집히며 상쇄) — ShortCover의 "특정 연도 쏠림"과 다른 종류의
  실패로, 애초에 지속적인 방향성 자체가 없다는 뜻에 가까움.

### Backtest (거래비용 + winsorize 5% 반영, 키움증권 온라인 기준)

**Alpha_Mom12_1**
| holding | sharpe | mdd | ann_turnover | t-stat(대략) |
|---|---|---|---|---|
| 20  | 0.1544 | -0.3156 | 3.098 | ≈0.49 |
| 60  | 0.3009 | -0.1873 | 1.772 | ≈0.95 |
| 120 | 0.3155 | -0.1586 | 1.264 | ≈1.00 |

**Alpha_MomShort**
| holding | sharpe | mdd | ann_turnover | t-stat(대략) |
|---|---|---|---|---|
| 5  | -0.0929 | -0.3710 | 19.494 | ≈-0.29 |
| 10 | -0.0787 | -0.2997 | 13.863 | ≈-0.25 |
| 20 | 0.1390  | -0.2335 | 9.904  | ≈0.44 |

Mom12_1은 지금까지 세 라인 중 t-stat이 가장 높지만(≈1.0) 여전히 유의성
기준(≈2) 미달. MomShort는 h=5/10에서 Sharpe 마이너스, turnover가 연
9.9~19.5회로 극단적으로 높아 신호를 비용이 대부분 상쇄.

### Conclusion

- **Alpha_Mom12_1**: IC/백테스트 모두 지금까지 중 가장 강했지만 (1) 거래비용
  반영 후 Sharpe가 여전히 통계적으로 유의하지 않고(8절 실패 기준 해당), (2)
  그 강도 자체가 소수 극단치 + 최근 2년(2024-2025) 쏠림에 크게 의존하고
  있어 out-of-sample 신뢰도가 낮음 — **폐기**.
- **Alpha_MomShort**: IC 단계부터 약했고, 연도별 방향이 상쇄되는 구조적
  무신호 패턴 + 백테스트 마이너스/극단적 turnover — **폐기**.
- PBO는 실행하지 않음 (기존 라인과 동일 사유 — 좋아 보이는 결과가 없어
  검증할 대상이 없음).

### Next experiment

momentum_alpha_v1 라인 종료. `pre_registration/investor_flow_alpha_v1.md`로
넘어갈 것 — 단, 실행 전에 4절에 남겨둔 미검증 항목(거래대금 데이터 실제
반환 컬럼 확인, 시가총액 정규화, 지수 리밸런싱 패시브 자금 오염 여부)부터
스팟체크로 확정 필요.

---

## General Lessons 추가분

- **Pearson IC ≫ Rank IC로 나오면 극단치/최근 구간 쏠림을 의심할 것** —
  value_alpha_v1(Rank IC≫Pearson)과 반대 방향이지만 원인은 같은 계열(극단값이
  선형 통계를 왜곡). 이 패턴이 보이면 mean-vs-median 스팟체크를 backtest
  전에 먼저 돌릴 것(이번에 실제로 적중).
- **연도별 robustness는 "개별 연도 50% 초과" 기준만으로는 부족할 수 있음** —
  Mom12_1처럼 상위 2개년 합산이 60%를 넘는데도 개별 연도 기준은 통과하는
  경우가 있음. 형식적 판정 외에 상위 N개년 누적 기여도도 같이 볼 것.