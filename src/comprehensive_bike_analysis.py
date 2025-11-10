# -*- coding: utf-8 -*-
"""
서울시 따릉이 공공자전거 일별 이용현황 통합 분석
"""
import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 출력 디렉토리 생성
os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/reports", exist_ok=True)

def load_data():
    """데이터 로드"""
    print("=" * 80)
    print("📊 서울시 따릉이 공공자전거 통합 분석")
    print("=" * 80)
    print("\n[1단계] 데이터 로드 중...")

    # 원시 데이터 로드
    df_raw = pd.read_csv("data/raw/bike_daily.csv")
    print(f"  ✓ 원시 데이터 로드 완료: {len(df_raw):,}건")

    # 요약 데이터 로드
    df_sum = pd.read_csv("data/processed/bike_summary.csv")
    print(f"  ✓ 요약 데이터 로드 완료: {len(df_sum):,}건")

    # 기상 데이터 로드 (인코딩 처리)
    try:
        df_temp = pd.read_csv("data/raw/temperature.csv", encoding='cp949')
        print(f"  ✓ 기온 데이터 로드 완료: {len(df_temp):,}건")
    except Exception as e:
        print(f"  ⚠ 기온 데이터 로드 실패: {e}")
        df_temp = None

    try:
        df_rain = pd.read_csv("data/raw/rainfall.csv", encoding='cp949')
        print(f"  ✓ 강수량 데이터 로드 완료: {len(df_rain):,}건")
    except Exception as e:
        print(f"  ⚠ 강수량 데이터 로드 실패: {e}")
        df_rain = None

    return df_raw, df_sum, df_temp, df_rain

def preprocess_data(df_raw, df_sum, df_temp, df_rain):
    """데이터 전처리"""
    print("\n[2단계] 데이터 전처리 중...")

    # 날짜 형식 변환
    df_raw['STAT_DATA'] = pd.to_datetime(df_raw['STAT_DATA'])
    df_raw['RENT_CNT'] = pd.to_numeric(df_raw['RENT_CNT'], errors='coerce')
    df_raw['RTN_CNT'] = pd.to_numeric(df_raw['RTN_CNT'], errors='coerce')

    # 요일 추가
    df_raw['WEEKDAY'] = df_raw['STAT_DATA'].dt.day_name()
    df_raw['IS_WEEKEND'] = df_raw['STAT_DATA'].dt.dayofweek >= 5

    # 요약 데이터에 파생 변수 추가
    df_sum['NET_FLOW'] = df_sum['TOTAL_RENT_CNT'] - df_sum['TOTAL_RTN_CNT']
    df_sum['IMBAL_RATIO'] = (
        abs(df_sum['TOTAL_RENT_CNT'] - df_sum['TOTAL_RTN_CNT']) /
        (df_sum['TOTAL_RENT_CNT'] + df_sum['TOTAL_RTN_CNT'])
    ).fillna(0)

    # 기상 데이터 전처리
    if df_temp is not None:
        # 컬럼명 정리 (공백 제거)
        df_temp.columns = df_temp.columns.str.strip()
        # 일시 컬럼 찾기
        date_col = [col for col in df_temp.columns if '일시' in col or '날짜' in col]
        if date_col:
            df_temp['STAT_DATA'] = pd.to_datetime(df_temp[date_col[0]])
            # 2025-10-06 ~ 2025-11-02 필터링
            df_temp = df_temp[(df_temp['STAT_DATA'] >= '2025-10-06') &
                              (df_temp['STAT_DATA'] <= '2025-11-02')]

    if df_rain is not None:
        df_rain.columns = df_rain.columns.str.strip()
        date_col = [col for col in df_rain.columns if '일시' in col or '날짜' in col]
        if date_col:
            df_rain['STAT_DATA'] = pd.to_datetime(df_rain[date_col[0]])
            df_rain = df_rain[(df_rain['STAT_DATA'] >= '2025-10-06') &
                              (df_rain['STAT_DATA'] <= '2025-11-02')]

    print("  ✓ 데이터 전처리 완료")
    print(f"    - 분석 기간: {df_raw['STAT_DATA'].min()} ~ {df_raw['STAT_DATA'].max()}")
    print(f"    - 총 일수: {df_raw['STAT_DATA'].nunique()}일")
    print(f"    - 대여소 수: {df_raw['RENT_NM'].nunique()}개")
    print(f"    - 행정구 수: {df_raw['STA_LOC'].nunique()}개")

    return df_raw, df_sum, df_temp, df_rain

def analysis_1_daily_trend(df_raw):
    """1️⃣ 일별 수요 트렌드 분석"""
    print("\n" + "=" * 80)
    print("📈 분석 1: 일별 수요 트렌드 분석")
    print("=" * 80)

    # 일별 집계
    daily_agg = df_raw.groupby('STAT_DATA').agg({
        'RENT_CNT': 'sum',
        'RTN_CNT': 'sum',
        'IS_WEEKEND': 'first'
    }).reset_index()

    # 이동평균 계산
    daily_agg['RENT_MA7'] = daily_agg['RENT_CNT'].rolling(window=7, center=True).mean()
    daily_agg['RTN_MA7'] = daily_agg['RTN_CNT'].rolling(window=7, center=True).mean()

    # 통계
    print(f"\n📊 전체 통계:")
    print(f"  - 총 대여건수: {daily_agg['RENT_CNT'].sum():,}건")
    print(f"  - 총 반납건수: {daily_agg['RTN_CNT'].sum():,}건")
    print(f"  - 일평균 대여: {daily_agg['RENT_CNT'].mean():,.0f}건")
    print(f"  - 일평균 반납: {daily_agg['RTN_CNT'].mean():,.0f}건")

    # 평일 vs 주말
    weekday_avg = daily_agg[~daily_agg['IS_WEEKEND']]['RENT_CNT'].mean()
    weekend_avg = daily_agg[daily_agg['IS_WEEKEND']]['RENT_CNT'].mean()
    diff_pct = ((weekday_avg - weekend_avg) / weekday_avg * 100)

    print(f"\n📅 평일 vs 주말:")
    print(f"  - 평일 평균: {weekday_avg:,.0f}건")
    print(f"  - 주말 평균: {weekend_avg:,.0f}건")
    print(f"  - 차이: {diff_pct:.1f}% (주말이 평일 대비 감소)")

    # 이상치 탐지 (±2σ)
    mean_rent = daily_agg['RENT_CNT'].mean()
    std_rent = daily_agg['RENT_CNT'].std()
    anomalies = daily_agg[
        (daily_agg['RENT_CNT'] > mean_rent + 2*std_rent) |
        (daily_agg['RENT_CNT'] < mean_rent - 2*std_rent)
    ]

    if len(anomalies) > 0:
        print(f"\n⚠ 이상치 탐지 (±2σ):")
        for _, row in anomalies.iterrows():
            print(f"  - {row['STAT_DATA'].strftime('%Y-%m-%d')}: {row['RENT_CNT']:,}건")

    # 시각화
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # 일별 대여/반납 추이
    axes[0].plot(daily_agg['STAT_DATA'], daily_agg['RENT_CNT'],
                 label='대여건수', marker='o', linewidth=2, color='#2E86DE')
    axes[0].plot(daily_agg['STAT_DATA'], daily_agg['RTN_CNT'],
                 label='반납건수', marker='s', linewidth=2, color='#EE5A6F')
    axes[0].plot(daily_agg['STAT_DATA'], daily_agg['RENT_MA7'],
                 label='대여 7일 이동평균', linewidth=2, linestyle='--', color='#0652DD')
    axes[0].set_xlabel('날짜', fontsize=12)
    axes[0].set_ylabel('건수', fontsize=12)
    axes[0].set_title('일별 대여/반납 건수 추이', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)

    # 주말 강조
    for _, row in daily_agg.iterrows():
        if row['IS_WEEKEND']:
            axes[0].axvspan(row['STAT_DATA'], row['STAT_DATA'] + pd.Timedelta(days=1),
                           alpha=0.1, color='orange')

    # 요일별 평균
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_avg_df = df_raw.groupby('WEEKDAY')['RENT_CNT'].sum().reindex(weekday_order)
    weekday_labels = ['월', '화', '수', '목', '금', '토', '일']

    axes[1].bar(weekday_labels, weekday_avg_df.values, color='#54A0FF')
    axes[1].set_xlabel('요일', fontsize=12)
    axes[1].set_ylabel('총 대여건수', fontsize=12)
    axes[1].set_title('요일별 총 대여건수', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/01_daily_trend.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 시각화 저장: outputs/figures/01_daily_trend.png")
    plt.close()

    return daily_agg

def analysis_2_station_efficiency(df_sum):
    """2️⃣ 대여소별 효율성 분석"""
    print("\n" + "=" * 80)
    print("🏆 분석 2: 대여소별 효율성 분석")
    print("=" * 80)

    # 상위/하위 10개 대여소
    top10_rent = df_sum.nlargest(10, 'TOTAL_RENT_CNT')
    bottom10_rent = df_sum.nsmallest(10, 'TOTAL_RENT_CNT')

    print(f"\n📊 대여소 통계:")
    print(f"  - 총 대여소 수: {len(df_sum):,}개")
    print(f"  - 평균 대여건수: {df_sum['TOTAL_RENT_CNT'].mean():,.0f}건")
    print(f"  - 중앙값 대여건수: {df_sum['TOTAL_RENT_CNT'].median():,.0f}건")

    # 파레토 분석 (상위 20%)
    df_sum_sorted = df_sum.sort_values('TOTAL_RENT_CNT', ascending=False)
    top20_count = int(len(df_sum) * 0.2)
    top20_sum = df_sum_sorted.head(top20_count)['TOTAL_RENT_CNT'].sum()
    total_sum = df_sum['TOTAL_RENT_CNT'].sum()
    pareto_pct = (top20_sum / total_sum) * 100

    print(f"\n📈 파레토 분석:")
    print(f"  - 상위 20% 대여소 ({top20_count}개)가 전체 대여량의 {pareto_pct:.1f}% 차지")

    print(f"\n🥇 대여건수 상위 10개 대여소:")
    for idx, row in top10_rent.iterrows():
        print(f"  {row['RENT_NM'][:30]:30s} | {row['STA_LOC']:8s} | {row['TOTAL_RENT_CNT']:6,.0f}건")

    print(f"\n🥉 대여건수 하위 10개 대여소:")
    for idx, row in bottom10_rent.iterrows():
        print(f"  {row['RENT_NM'][:30]:30s} | {row['STA_LOC']:8s} | {row['TOTAL_RENT_CNT']:6,.0f}건")

    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 상위 10개
    axes[0].barh(range(10), top10_rent['TOTAL_RENT_CNT'].values, color='#2E86DE')
    axes[0].set_yticks(range(10))
    axes[0].set_yticklabels([name[:20] for name in top10_rent['RENT_NM'].values], fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('총 대여건수', fontsize=12)
    axes[0].set_title('대여건수 상위 10개 대여소', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='x')

    # 하위 10개
    axes[1].barh(range(10), bottom10_rent['TOTAL_RENT_CNT'].values, color='#EE5A6F')
    axes[1].set_yticks(range(10))
    axes[1].set_yticklabels([name[:20] for name in bottom10_rent['RENT_NM'].values], fontsize=9)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('총 대여건수', fontsize=12)
    axes[1].set_title('대여건수 하위 10개 대여소', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig('outputs/figures/02_station_efficiency.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 시각화 저장: outputs/figures/02_station_efficiency.png")
    plt.close()

    return top10_rent, bottom10_rent

def analysis_3_net_flow(df_sum):
    """3️⃣ 순유입 및 불균형 분석"""
    print("\n" + "=" * 80)
    print("⚖ 분석 3: 순유입 및 불균형 분석")
    print("=" * 80)

    # 불균형 상위 10개
    top10_imb = df_sum.nlargest(10, 'IMBAL_RATIO')

    # 순유입/순유출 분류
    inflow = df_sum[df_sum['NET_FLOW'] > 0].sort_values('NET_FLOW', ascending=False).head(10)
    outflow = df_sum[df_sum['NET_FLOW'] < 0].sort_values('NET_FLOW').head(10)

    print(f"\n📊 불균형 통계:")
    print(f"  - 평균 불균형률: {df_sum['IMBAL_RATIO'].mean():.3f}")
    print(f"  - 순유입 대여소: {len(df_sum[df_sum['NET_FLOW'] > 0])}개")
    print(f"  - 순유출 대여소: {len(df_sum[df_sum['NET_FLOW'] < 0])}개")

    print(f"\n⚠ 불균형 상위 10개 대여소:")
    for idx, row in top10_imb.iterrows():
        flow_type = "순유입" if row['NET_FLOW'] > 0 else "순유출"
        print(f"  {row['RENT_NM'][:30]:30s} | {row['STA_LOC']:8s} | 불균형률: {row['IMBAL_RATIO']:.3f} | {flow_type}")

    print(f"\n📤 순유입 상위 10개 대여소 (대여 > 반납):")
    for idx, row in inflow.iterrows():
        print(f"  {row['RENT_NM'][:30]:30s} | {row['STA_LOC']:8s} | +{row['NET_FLOW']:6,.0f}건")

    print(f"\n📥 순유출 상위 10개 대여소 (반납 > 대여):")
    for idx, row in outflow.iterrows():
        print(f"  {row['RENT_NM'][:30]:30s} | {row['STA_LOC']:8s} | {row['NET_FLOW']:6,.0f}건")

    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 불균형 상위 10개
    colors = ['#EE5A6F' if x > 0 else '#2E86DE' for x in top10_imb['NET_FLOW'].values]
    axes[0].barh(range(10), top10_imb['IMBAL_RATIO'].values, color=colors)
    axes[0].set_yticks(range(10))
    axes[0].set_yticklabels([name[:20] for name in top10_imb['RENT_NM'].values], fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('불균형률', fontsize=12)
    axes[0].set_title('불균형 상위 10개 대여소', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='x')

    # 순유입/순유출 분포
    axes[1].hist(df_sum['NET_FLOW'], bins=50, color='#54A0FF', edgecolor='black', alpha=0.7)
    axes[1].axvline(0, color='red', linestyle='--', linewidth=2, label='균형점')
    axes[1].set_xlabel('순유입량 (대여 - 반납)', fontsize=12)
    axes[1].set_ylabel('대여소 수', fontsize=12)
    axes[1].set_title('순유입량 분포', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('outputs/figures/03_net_flow.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 시각화 저장: outputs/figures/03_net_flow.png")
    plt.close()

    # 불균형 데이터 저장
    top10_imb[['STA_LOC', 'RENT_NM', 'TOTAL_RENT_CNT', 'TOTAL_RTN_CNT', 'NET_FLOW', 'IMBAL_RATIO']].to_csv(
        'outputs/reports/top10_imbalance.csv', index=False, encoding='utf-8-sig'
    )
    print(f"✓ 불균형 리포트 저장: outputs/reports/top10_imbalance.csv")

    return top10_imb

def analysis_4_anomaly_detection(df_raw):
    """4️⃣ 이상치 및 이벤트 감지"""
    print("\n" + "=" * 80)
    print("🔍 분석 4: 이상치 및 이벤트 감지")
    print("=" * 80)

    # 일별 집계
    daily_agg = df_raw.groupby(['STAT_DATA', 'IS_WEEKEND']).agg({
        'RENT_CNT': 'sum',
        'RTN_CNT': 'sum'
    }).reset_index()

    # 이동평균 및 표준편차
    daily_agg['RENT_MA7'] = daily_agg['RENT_CNT'].rolling(window=7, center=True).mean()
    daily_agg['RENT_STD7'] = daily_agg['RENT_CNT'].rolling(window=7, center=True).std()

    # 이상치 탐지 (±2σ)
    daily_agg['UPPER_BOUND'] = daily_agg['RENT_MA7'] + 2 * daily_agg['RENT_STD7']
    daily_agg['LOWER_BOUND'] = daily_agg['RENT_MA7'] - 2 * daily_agg['RENT_STD7']
    daily_agg['IS_ANOMALY'] = (
        (daily_agg['RENT_CNT'] > daily_agg['UPPER_BOUND']) |
        (daily_agg['RENT_CNT'] < daily_agg['LOWER_BOUND'])
    )

    anomalies = daily_agg[daily_agg['IS_ANOMALY'] == True]

    print(f"\n⚠ 이상치 탐지 결과:")
    print(f"  - 총 이상치 일수: {len(anomalies)}일")

    if len(anomalies) > 0:
        print(f"\n  이상치 일자:")
        for _, row in anomalies.iterrows():
            deviation = ((row['RENT_CNT'] - row['RENT_MA7']) / row['RENT_MA7'] * 100)
            print(f"  - {row['STAT_DATA'].strftime('%Y-%m-%d')}: {row['RENT_CNT']:,}건 (평균 대비 {deviation:+.1f}%)")

    # 평일 vs 주말 t-test
    weekday_data = daily_agg[~daily_agg['IS_WEEKEND']]['RENT_CNT']
    weekend_data = daily_agg[daily_agg['IS_WEEKEND']]['RENT_CNT']

    t_stat, p_value = stats.ttest_ind(weekday_data, weekend_data)

    print(f"\n📊 평일 vs 주말 t-test:")
    print(f"  - t-통계량: {t_stat:.3f}")
    print(f"  - p-value: {p_value:.4f}")
    print(f"  - 결과: {'유의한 차이 있음' if p_value < 0.05 else '유의한 차이 없음'} (α=0.05)")

    # 시각화
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(daily_agg['STAT_DATA'], daily_agg['RENT_CNT'],
            label='일별 대여건수', marker='o', linewidth=2, color='#2E86DE')
    ax.plot(daily_agg['STAT_DATA'], daily_agg['RENT_MA7'],
            label='7일 이동평균', linewidth=2, linestyle='--', color='#0652DD')
    ax.fill_between(daily_agg['STAT_DATA'],
                     daily_agg['LOWER_BOUND'],
                     daily_agg['UPPER_BOUND'],
                     alpha=0.2, color='gray', label='±2σ 구간')

    # 이상치 표시
    if len(anomalies) > 0:
        ax.scatter(anomalies['STAT_DATA'], anomalies['RENT_CNT'],
                  color='red', s=100, zorder=5, label='이상치', marker='X')

    ax.set_xlabel('날짜', fontsize=12)
    ax.set_ylabel('대여건수', fontsize=12)
    ax.set_title('이상치 탐지 (±2σ)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig('outputs/figures/04_anomaly_detection.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 시각화 저장: outputs/figures/04_anomaly_detection.png")
    plt.close()

    return anomalies

def analysis_5_weather_correlation(df_raw, df_temp, df_rain):
    """5️⃣ 날씨 요인 기반 수요 상관 분석"""
    print("\n" + "=" * 80)
    print("🌤 분석 5: 날씨 요인 기반 수요 상관 분석")
    print("=" * 80)

    if df_temp is None or df_rain is None:
        print("  ⚠ 기상 데이터가 없어 분석을 건너뜁니다.")
        return None

    # 일별 집계
    daily_demand = df_raw.groupby('STAT_DATA').agg({
        'RENT_CNT': 'sum',
        'RTN_CNT': 'sum'
    }).reset_index()

    # 기온 데이터 병합
    temp_col = [col for col in df_temp.columns if '평균기온' in col or '평균' in col]
    if temp_col:
        df_temp_clean = df_temp[['STAT_DATA', temp_col[0]]].copy()
        df_temp_clean.columns = ['STAT_DATA', 'AVG_TEMP']
        df_temp_clean['AVG_TEMP'] = pd.to_numeric(df_temp_clean['AVG_TEMP'], errors='coerce')
        daily_demand = daily_demand.merge(df_temp_clean, on='STAT_DATA', how='left')

    # 강수량 데이터 병합
    rain_col = [col for col in df_rain.columns if '강수량' in col and '1시간' not in col]
    if rain_col:
        df_rain_clean = df_rain[['STAT_DATA', rain_col[0]]].copy()
        df_rain_clean.columns = ['STAT_DATA', 'RAINFALL']
        df_rain_clean['RAINFALL'] = pd.to_numeric(df_rain_clean['RAINFALL'], errors='coerce').fillna(0)
        daily_demand = daily_demand.merge(df_rain_clean, on='STAT_DATA', how='left')
        daily_demand['RAINFALL'] = daily_demand['RAINFALL'].fillna(0)

    # 강수 여부
    daily_demand['IS_RAINY'] = daily_demand['RAINFALL'] > 0

    # 기온 구간
    daily_demand['TEMP_RANGE'] = pd.cut(
        daily_demand['AVG_TEMP'],
        bins=[0, 10, 15, 20, 30],
        labels=['10℃ 미만', '10-15℃', '15-20℃', '20℃ 이상']
    )

    # 상관계수 계산
    if 'AVG_TEMP' in daily_demand.columns:
        corr_temp = daily_demand[['RENT_CNT', 'AVG_TEMP']].corr().iloc[0, 1]
        print(f"\n📈 기온과 대여량 상관계수: {corr_temp:.3f}")

    if 'RAINFALL' in daily_demand.columns:
        corr_rain = daily_demand[['RENT_CNT', 'RAINFALL']].corr().iloc[0, 1]
        print(f"📈 강수량과 대여량 상관계수: {corr_rain:.3f}")

    # 강수일 vs 무강수일 비교
    if 'IS_RAINY' in daily_demand.columns:
        rainy_avg = daily_demand[daily_demand['IS_RAINY']]['RENT_CNT'].mean()
        sunny_avg = daily_demand[~daily_demand['IS_RAINY']]['RENT_CNT'].mean()
        rain_impact = ((rainy_avg - sunny_avg) / sunny_avg * 100)

        print(f"\n☔ 강수 영향 분석:")
        print(f"  - 무강수일 평균: {sunny_avg:,.0f}건")
        print(f"  - 강수일 평균: {rainy_avg:,.0f}건")
        print(f"  - 차이: {rain_impact:+.1f}%")

        # t-test
        rainy_data = daily_demand[daily_demand['IS_RAINY']]['RENT_CNT']
        sunny_data = daily_demand[~daily_demand['IS_RAINY']]['RENT_CNT']
        if len(rainy_data) > 0 and len(sunny_data) > 0:
            t_stat, p_value = stats.ttest_ind(rainy_data, sunny_data)
            print(f"  - t-test p-value: {p_value:.4f} ({'유의함' if p_value < 0.05 else '유의하지 않음'})")

    # 기온 구간별 분석
    if 'TEMP_RANGE' in daily_demand.columns:
        print(f"\n🌡 기온 구간별 평균 대여량:")
        temp_group = daily_demand.groupby('TEMP_RANGE')['RENT_CNT'].mean()
        for temp_range, avg_rent in temp_group.items():
            print(f"  - {temp_range}: {avg_rent:,.0f}건")

    # 시각화
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 기온 vs 대여량
    if 'AVG_TEMP' in daily_demand.columns:
        axes[0, 0].scatter(daily_demand['AVG_TEMP'], daily_demand['RENT_CNT'],
                          alpha=0.6, s=100, color='#FF6B6B')
        axes[0, 0].set_xlabel('평균기온 (℃)', fontsize=12)
        axes[0, 0].set_ylabel('대여건수', fontsize=12)
        axes[0, 0].set_title(f'기온 vs 대여량 (상관계수: {corr_temp:.3f})',
                            fontsize=14, fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)

    # 강수량 vs 대여량
    if 'RAINFALL' in daily_demand.columns:
        axes[0, 1].scatter(daily_demand['RAINFALL'], daily_demand['RENT_CNT'],
                          alpha=0.6, s=100, color='#4ECDC4')
        axes[0, 1].set_xlabel('강수량 (mm)', fontsize=12)
        axes[0, 1].set_ylabel('대여건수', fontsize=12)
        axes[0, 1].set_title(f'강수량 vs 대여량 (상관계수: {corr_rain:.3f})',
                            fontsize=14, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)

    # 강수일 vs 무강수일
    if 'IS_RAINY' in daily_demand.columns:
        rain_data = [
            daily_demand[~daily_demand['IS_RAINY']]['RENT_CNT'],
            daily_demand[daily_demand['IS_RAINY']]['RENT_CNT']
        ]
        axes[1, 0].boxplot(rain_data, labels=['무강수일', '강수일'])
        axes[1, 0].set_ylabel('대여건수', fontsize=12)
        axes[1, 0].set_title('강수일 vs 무강수일 대여량 비교', fontsize=14, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 기온 구간별 평균
    if 'TEMP_RANGE' in daily_demand.columns:
        temp_group_plot = daily_demand.groupby('TEMP_RANGE')['RENT_CNT'].mean()
        axes[1, 1].bar(range(len(temp_group_plot)), temp_group_plot.values, color='#95E1D3')
        axes[1, 1].set_xticks(range(len(temp_group_plot)))
        axes[1, 1].set_xticklabels(temp_group_plot.index, rotation=0)
        axes[1, 1].set_xlabel('기온 구간', fontsize=12)
        axes[1, 1].set_ylabel('평균 대여건수', fontsize=12)
        axes[1, 1].set_title('기온 구간별 평균 대여량', fontsize=14, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('outputs/figures/05_weather_correlation.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 시각화 저장: outputs/figures/05_weather_correlation.png")
    plt.close()

    return daily_demand

def analysis_6_district_summary(df_sum):
    """6️⃣ 행정구별 요약 분석"""
    print("\n" + "=" * 80)
    print("🗺 분석 6: 행정구별 요약")
    print("=" * 80)

    # 행정구별 집계
    gu_summary = df_sum.groupby('STA_LOC').agg({
        'AVG_RENT_CNT': 'mean',
        'AVG_RTN_CNT': 'mean',
        'TOTAL_RENT_CNT': 'sum',
        'TOTAL_RTN_CNT': 'sum',
        'IMBAL_RATIO': 'mean',
        'RENT_NM': 'nunique'
    }).reset_index()

    gu_summary.columns = [
        '행정구', '평균_대여', '평균_반납', '합계_대여', '합계_반납', '평균_불균형', '대여소_수'
    ]

    gu_summary = gu_summary.sort_values('합계_대여', ascending=False)

    print(f"\n📊 행정구별 요약:")
    print(f"{'행정구':10s} | {'대여소':>6s} | {'합계_대여':>10s} | {'합계_반납':>10s} | {'불균형률':>8s}")
    print("-" * 60)
    for _, row in gu_summary.iterrows():
        print(f"{row['행정구']:10s} | {row['대여소_수']:6.0f}개 | {row['합계_대여']:10,.0f}건 | {row['합계_반납']:10,.0f}건 | {row['평균_불균형']:8.3f}")

    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # 행정구별 합계 대여
    axes[0].barh(range(len(gu_summary)), gu_summary['합계_대여'].values, color='#48C9B0')
    axes[0].set_yticks(range(len(gu_summary)))
    axes[0].set_yticklabels(gu_summary['행정구'].values, fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('총 대여건수', fontsize=12)
    axes[0].set_title('행정구별 총 대여건수', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='x')

    # 행정구별 평균 불균형률
    axes[1].barh(range(len(gu_summary)), gu_summary['평균_불균형'].values, color='#F39C12')
    axes[1].set_yticks(range(len(gu_summary)))
    axes[1].set_yticklabels(gu_summary['행정구'].values, fontsize=9)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('평균 불균형률', fontsize=12)
    axes[1].set_title('행정구별 평균 불균형률', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig('outputs/figures/06_district_summary.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 시각화 저장: outputs/figures/06_district_summary.png")
    plt.close()

    # 리포트 저장
    gu_summary.to_csv('outputs/reports/district_summary.csv', index=False, encoding='utf-8-sig')
    print(f"✓ 행정구 요약 저장: outputs/reports/district_summary.csv")

    return gu_summary

def generate_final_report(df_raw, df_sum, daily_agg, top10_rent, top10_imb, gu_summary):
    """최종 리포트 생성"""
    print("\n" + "=" * 80)
    print("📝 최종 리포트 생성")
    print("=" * 80)

    report = []
    report.append("=" * 80)
    report.append("서울시 따릉이 공공자전거 통합 분석 리포트")
    report.append("=" * 80)
    report.append("")
    report.append(f"분석 기간: {df_raw['STAT_DATA'].min()} ~ {df_raw['STAT_DATA'].max()}")
    report.append(f"분석 일수: {df_raw['STAT_DATA'].nunique()}일")
    report.append("")

    report.append("=" * 80)
    report.append("핵심 발견 (Key Findings)")
    report.append("=" * 80)
    report.append("")

    # 1. 수요 집중
    total_rent = df_sum['TOTAL_RENT_CNT'].sum()
    top10_pct = (top10_rent['TOTAL_RENT_CNT'].sum() / total_rent * 100)
    report.append(f"1. 수요 집중")
    report.append(f"   - 상위 10개 대여소가 전체 대여량의 {top10_pct:.1f}% 차지")
    report.append(f"   - 집중 운영 및 우선 보급 대상으로 지정 필요")
    report.append("")

    # 2. 불균형 핫스팟
    report.append(f"2. 불균형 핫스팟")
    report.append(f"   - 상위 10개 불균형 대여소의 평균 불균형률: {top10_imb['IMBAL_RATIO'].mean():.3f}")
    report.append(f"   - 주 2회 이상 점검 및 임시 거치대 운영 권장")
    report.append("")

    # 3. 지역 격차
    report.append(f"3. 지역 격차")
    report.append(f"   - 최고 수요 행정구: {gu_summary.iloc[0]['행정구']} ({gu_summary.iloc[0]['합계_대여']:,.0f}건)")
    report.append(f"   - 최저 수요 행정구: {gu_summary.iloc[-1]['행정구']} ({gu_summary.iloc[-1]['합계_대여']:,.0f}건)")
    report.append(f"   - 출근시간 보급·퇴근시간 회수 루틴 강화 필요")
    report.append("")

    report.append("=" * 80)
    report.append("실행 권고사항 (Action Items)")
    report.append("=" * 80)
    report.append("")

    report.append("단기 (1~2주)")
    report.append("  • 순유입 Top 대여소 AM 보급 강화")
    report.append("  • 불균형 상위 대여소 실시간 모니터링")
    report.append("")

    report.append("중기 (1~3개월)")
    report.append("  • 주말·이벤트 패턴 분리 운영")
    report.append("  • 행정구별 KPI 기반 자전거 배분")
    report.append("")

    report.append("장기 (3개월+)")
    report.append("  • 동적 재배치 최적화 루트 설계")
    report.append("  • AI 기반 수요예측 시스템 구축")
    report.append("")

    report.append("=" * 80)
    report.append("생성 일시: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report.append("=" * 80)

    # 파일 저장
    report_text = "\n".join(report)
    with open('outputs/reports/final_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f"\n✓ 최종 리포트 저장: outputs/reports/final_report.txt")

def main():
    """메인 실행 함수"""
    # 데이터 로드
    df_raw, df_sum, df_temp, df_rain = load_data()

    # 데이터 전처리
    df_raw, df_sum, df_temp, df_rain = preprocess_data(df_raw, df_sum, df_temp, df_rain)

    # 분석 수행
    daily_agg = analysis_1_daily_trend(df_raw)
    top10_rent, bottom10_rent = analysis_2_station_efficiency(df_sum)
    top10_imb = analysis_3_net_flow(df_sum)
    anomalies = analysis_4_anomaly_detection(df_raw)
    daily_weather = analysis_5_weather_correlation(df_raw, df_temp, df_rain)
    gu_summary = analysis_6_district_summary(df_sum)

    # 최종 리포트
    generate_final_report(df_raw, df_sum, daily_agg, top10_rent, top10_imb, gu_summary)

    print("\n" + "=" * 80)
    print("✅ 모든 분석 완료!")
    print("=" * 80)
    print(f"\n📁 결과물:")
    print(f"  - 시각화: outputs/figures/ (6개 그래프)")
    print(f"  - 리포트: outputs/reports/ (3개 CSV + 1개 텍스트)")

if __name__ == "__main__":
    main()
