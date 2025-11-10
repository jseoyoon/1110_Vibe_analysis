# 🚲 서울시 따릉이 공공자전거 이용현황 데이터 분석 프로젝트

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8+-orange.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

서울시 공공자전거(따릉이) 이용 데이터를 활용한 **수요 패턴 분석** 및 **운영 최적화 인사이트 도출** 프로젝트입니다.

---

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 및 실행](#-설치-및-실행)
- [데이터 수집](#-데이터-수집)
- [분석 결과](#-분석-결과)
- [핵심 인사이트](#-핵심-인사이트)
- [실행 권고사항](#-실행-권고사항)
- [Jupyter Notebook](#-jupyter-notebook)
- [라이선스](#-라이선스)

---

## 🎯 프로젝트 개요

### 배경
서울시 공공자전거 따릉이는 시민들의 중요한 교통수단으로 자리잡았지만, **대여소별 수요 불균형**, **재배치 비효율**, **날씨에 따른 수요 변화** 등의 운영 과제가 존재합니다.

### 목적
- ✅ **운영 효율화**: 수요 불균형 및 순유입 패턴 분석을 통한 재배치 의사결정 지원
- ✅ **핵심 대여소 식별**: 전체 수요의 중심축이 되는 주요 대여소 파악
- ✅ **지역별 인프라 최적화**: 행정구 단위 이용패턴 비교를 통한 투자/보급 우선순위 수립
- ✅ **이상 패턴 감지**: 특정 일자 또는 지역의 비정상적 수요 급등·급감 탐지
- ✅ **날씨 영향 분석**: 기온 및 강수량이 이용 패턴에 미치는 영향 규명

### 분석 기간
**2025년 10월 6일 ~ 2025년 11월 2일** (28일간)

### 데이터 규모
- **총 데이터**: 76,114건
- **대여소**: 2,764개
- **행정구**: 25개
- **총 대여건수**: 2,978,868건
- **총 반납건수**: 2,962,816건

---

## ⚡ 주요 기능

### 1. 데이터 수집 (Data Collection)
- 서울시 공공데이터 OpenAPI를 통한 일별 이용현황 데이터 자동 수집
- 페이징 처리를 통한 대용량 데이터 수집 (1,000건 단위)
- 기상청 기온 및 강수량 데이터 통합

### 2. 데이터 전처리 (Data Processing)
- 대여소별 일평균/합계 집계
- 순유입(Net Flow) 및 불균형률(Imbalance Ratio) 계산
- 요일별, 주말/평일 분류

### 3. 통합 분석 (Comprehensive Analysis)
#### 📈 일별 수요 트렌드 분석
- 시계열 대여/반납 건수 추이
- 요일별 패턴 분석
- 이동평균 기반 이상치 탐지 (±2σ)

#### 🏆 대여소별 효율성 분석
- 파레토 분석 (상위 20% 대여소의 수요 비율)
- 대여건수 상위/하위 10개 대여소 식별
- 비효율 대여소 재배치 후보군 선정

#### ⚖️ 순유입 및 불균형 분석
- 순유입(대여 > 반납) 및 순유출(반납 > 대여) 대여소 분류
- 불균형률 상위 대여소 식별
- 지리적 패턴 분석 (업무지구 vs 주거지)

#### 🔍 이상치 및 이벤트 감지
- 통계적 이상치 탐지
- 평일 vs 주말 t-test
- 특정 일자 수요 급등/급감 원인 분석

#### 🌤️ 날씨 요인 기반 수요 상관 분석
- 기온과 대여량의 Pearson 상관계수 계산
- 강수량과 대여량의 상관관계 분석
- 강수일 vs 무강수일 비교 (t-test)
- 기온 구간별 (10℃ 미만, 10-15℃, 15-20℃, 20℃ 이상) 이용 패턴

#### 🗺️ 행정구별 요약 분석
- 25개 행정구 수요 비교
- 행정구별 평균 불균형률
- 지역별 투자 우선순위 도출

### 4. 시각화 (Visualization)
- 6개의 고품질 분석 그래프 자동 생성
- Matplotlib/Seaborn 기반 한글 지원
- 300 DPI 해상도 PNG 저장

### 5. 리포트 생성 (Report Generation)
- 자동화된 분석 리포트 생성
- CSV 형식 상세 데이터 저장
- 실행 권고사항 제시

---

## 🛠 기술 스택

### 언어 & 라이브러리
- **Python 3.11**
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Statistical Analysis**: SciPy
- **API Integration**: Requests
- **Environment Management**: python-dotenv

### 데이터 소스
- [서울 열린데이터 광장](https://data.seoul.go.kr/) - 공공자전거 이용현황 API
- 기상청 - 일별 기온 및 강수량 데이터

### 개발 환경
- **IDE**: VSCode
- **Notebook**: Jupyter Notebook
- **Version Control**: Git

---

## 📁 프로젝트 구조

```
woongjin_final_project/
├── data/                           # 데이터 디렉토리
│   ├── raw/                        # 원시 데이터
│   │   ├── bike_daily.csv          # 일별 이용현황 (76,114건)
│   │   ├── temperature.csv         # 기온 데이터
│   │   └── rainfall.csv            # 강수량 데이터
│   └── processed/                  # 전처리 데이터
│       └── bike_summary.csv        # 대여소별 요약 (2,764개)
│
├── src/                            # 소스 코드
│   ├── collect_bike_data.py        # 데이터 수집 스크립트
│   ├── preprocess_bike_data.py     # 데이터 전처리 스크립트
│   └── comprehensive_bike_analysis.py  # 통합 분석 스크립트
│
├── notebooks/                      # Jupyter Notebooks
│   └── comprehensive_bike_analysis.ipynb  # 인터랙티브 분석 노트북
│
├── outputs/                        # 분석 결과물
│   ├── figures/                    # 시각화 결과
│   │   ├── 01_daily_trend.png      # 일별 수요 트렌드
│   │   ├── 02_station_efficiency.png  # 대여소 효율성
│   │   ├── 03_net_flow.png         # 순유입 분석
│   │   ├── 04_anomaly_detection.png   # 이상치 탐지
│   │   ├── 05_weather_correlation.png # 날씨 상관관계
│   │   └── 06_district_summary.png    # 행정구별 요약
│   └── reports/                    # 분석 리포트
│       ├── final_report.txt        # 최종 종합 리포트
│       ├── district_summary.csv    # 행정구별 상세 데이터
│       └── top10_imbalance.csv     # 불균형 상위 10개 대여소
│
├── prompts/                        # 프롬프트 문서
│   ├── import data.txt             # 데이터 수집 가이드
│   └── bike_daily_data_analysis.txt  # 분석 가이드
│
├── .env                            # 환경 변수 (API 키)
├── requirements.txt                # Python 패키지 의존성
└── README.md                       # 프로젝트 문서 (본 파일)
```

---

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd woongjin_final_project
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 생성하고 서울시 OpenAPI 키를 입력합니다:
```env
KEY=your_seoul_openapi_key_here
```

> 📌 API 키는 [서울 열린데이터 광장](https://data.seoul.go.kr/)에서 발급받을 수 있습니다.

---

## 📊 데이터 수집

### 데이터 수집 실행
```bash
python src/collect_bike_data.py
```

**수집 결과:**
- 수집 기간: 2025-10-06 ~ 2025-11-02 (28일)
- 총 76,114건의 데이터 수집
- 저장 경로: `data/raw/bike_daily.csv`

### 데이터 전처리
```bash
python src/preprocess_bike_data.py
```

**전처리 결과:**
- 대여소별 집계 완료 (2,764개 대여소)
- 평균/합계 지표 계산
- 저장 경로: `data/processed/bike_summary.csv`

---

## 📈 분석 결과

### 통합 분석 실행
```bash
python src/comprehensive_bike_analysis.py
```

**생성 결과물:**
- 📊 6개의 시각화 그래프 (`outputs/figures/`)
- 📝 3개의 분석 리포트 (`outputs/reports/`)

### 주요 통계

#### 전체 현황
- **일평균 대여**: 106,388건
- **일평균 반납**: 105,815건
- **평일 평균**: 110,983건
- **주말 평균**: 94,902건
- **주말 감소율**: 14.5%

#### 대여소 분포
- **평균 대여건수**: 1,078건
- **중앙값**: 804건
- **상위 20% 대여소 수요 비중**: 48.0%

#### 불균형 현황
- **순유입 대여소**: 1,438개 (대여 > 반납)
- **순유출 대여소**: 1,283개 (반납 > 대여)
- **평균 불균형률**: 0.072

#### 날씨 영향 (핵심 발견 ⭐)
- **기온 상관계수**: -0.189 (약한 음의 상관)
- **강수량 상관계수**: -0.812 (강한 음의 상관)
- **강수일 수요 감소**: 36.9% ↓ (통계적으로 유의함, p=0.0012)
- **최적 기온 구간**: 10-15℃

---

## 💡 핵심 인사이트

### 1. 수요 집중 패턴
- 상위 10개 대여소가 전체 대여량의 **2.7%** 차지
- **최고 수요 대여소**: 마곡나루역 2번 출구 (12,907건)
- 파레토 법칙: 상위 20% 대여소가 전체의 **48.0%** 처리
- **💼 실행 아이디어**: 상위 10개 대여소 우선 관리 및 보급 강화

### 2. 불균형 핫스팟
- 상위 10개 불균형 대여소의 평균 불균형률: **0.874**
- 최대 순유출: 응암역2번출구 (-1,174건)
- 업무지구는 순유출, 주거지는 순유입 패턴 명확
- **💼 실행 아이디어**: 주 2회 이상 점검 및 임시 거치대 운영

### 3. 지역 격차
- 최고 수요 행정구: **강서구** (360,635건)
- 최저 수요 행정구: **강북구** (35,508건)
- 10배 이상의 수요 격차 존재
- **💼 실행 아이디어**: 출근시간 보급·퇴근시간 회수 루틴 강화

### 4. 날씨의 결정적 영향
- 강수일 대여량이 무강수일 대비 **36.9% 감소**
- 강수량이 대여량에 가장 큰 영향 (상관계수 -0.812)
- 기온 10-15℃ 구간에서 최고 이용량 (123,934건)
- **💼 실행 아이디어**: 날씨 기반 수요 예측 시스템 구축

### 5. 요일별 패턴
- 평일이 주말 대비 **14.5% 높은 수요**
- 금요일 수요 피크 확인
- 주말은 업무지구 수요 급감
- **💼 실행 아이디어**: 평일/주말 분리 운영 전략

---

## 🎯 실행 권고사항

### 단기 (1~2주)
- ✅ 순유입 Top 10 대여소 오전 보급 강화
- ✅ 불균형 상위 대여소 실시간 모니터링 시스템 구축
- ✅ 강수 예보 시 대여소별 사전 재배치

### 중기 (1~3개월)
- ✅ 주말·평일 패턴 분리 운영
- ✅ 행정구별 KPI 기반 자전거 배분
- ✅ 날씨 기반 수요 예측 모델 개발
- ✅ 하위 10개 대여소 거치대 재배치 검토

### 장기 (3개월+)
- ✅ 동적 재배치 최적화 루트 설계
- ✅ AI 기반 수요예측 시스템 구축
- ✅ 실시간 날씨 연동 자동 재배치 시스템
- ✅ 업무지구-주거지 순환 셔틀 운영

---

## 📓 Jupyter Notebook

인터랙티브 분석을 원하시면 Jupyter Notebook을 사용하세요:

```bash
jupyter notebook notebooks/comprehensive_bike_analysis.ipynb
```

**노트북 특징:**
- 셀 단위 실행으로 단계별 분석 가능
- 각 분석마다 상세한 설명 포함
- 시각화 결과 즉시 확인
- 코드 수정 및 실험 용이

---

## 📸 분석 시각화 샘플

### 일별 수요 트렌드
![일별 트렌드](outputs/figures/01_daily_trend.png)

### 대여소별 효율성
![대여소 효율성](outputs/figures/02_station_efficiency.png)

### 순유입 분석
![순유입 분석](outputs/figures/03_net_flow.png)

### 날씨 상관관계
![날씨 상관관계](outputs/figures/05_weather_correlation.png)

---

## 📚 참고 자료

- [서울 열린데이터 광장](https://data.seoul.go.kr/)
- [공공자전거 이용현황 API 문서](http://data.seoul.go.kr/dataList/OA-15493/F/1/datasetView.do)
- [기상청 기상자료개방포털](https://data.kma.go.kr/)

---

## 🤝 기여

프로젝트 개선 아이디어나 버그 리포트는 언제든 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.

---

## 👨‍💻 개발자

**프로젝트 관리 및 데이터 분석**
- Data Collection & Processing
- Statistical Analysis & Visualization
- Insight Generation & Reporting

---

## 📧 문의

프로젝트 관련 문의사항이 있으시면 Issue를 생성해주세요.

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요! ⭐**

Made with ❤️ by Data Analyst

</div>
