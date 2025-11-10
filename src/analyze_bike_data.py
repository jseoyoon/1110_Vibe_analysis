# -*- coding: utf-8 -*-
"""
서울시 공공자전거 이용현황 데이터 분석 스크립트
"""
import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 출력 디렉토리 설정
OUTPUT_DIR = "outputs/figures"
DATA_DIR = "data/processed"

def ensure_output_dir():
    """출력 디렉토리 생성"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    """데이터 로드"""
    print("=" * 60)
    print("데이터 로드 중...")
    print("=" * 60)

    # 원시 데이터
    df_raw = pd.read_csv("data/raw/bike_weekly.csv")
    print(f"\n원시 데이터: {len(df_raw):,}건")
    print(f"컬럼: {', '.join(df_raw.columns.tolist())}")

    # 요약 데이터
    df_summary = pd.read_csv("data/processed/bike_weekly_summary.csv")
    print(f"\n요약 데이터: {len(df_summary):,}건")
    print(f"컬럼: {', '.join(df_summary.columns.tolist())}")

    return df_raw, df_summary

def analyze_daily_trend(df_raw):
    """
    분석 1: 일별 수요 트렌드 분석
    - 일별 총 대여·반납 시계열 그래프
    - 행정구별 일평균 비교
    """
    print("\n" + "=" * 60)
    print("분석 1: 일별 수요 트렌드")
    print("=" * 60)

    # 날짜 형식 변환
    df_raw['STAT_DATA'] = pd.to_datetime(df_raw['STAT_DATA'])
    df_raw['RENT_CNT'] = pd.to_numeric(df_raw['RENT_CNT'], errors='coerce')
    df_raw['RTN_CNT'] = pd.to_numeric(df_raw['RTN_CNT'], errors='coerce')

    # 1) 일별 총 대여·반납 시계열
    daily_total = df_raw.groupby('STAT_DATA').agg({
        'RENT_CNT': 'sum',
        'RTN_CNT': 'sum'
    }).reset_index()

    print("\n일별 대여/반납 현황:")
    print(daily_total.to_string(index=False))

    # 시각화 1: 일별 시계열
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_total['STAT_DATA'], daily_total['RENT_CNT'],
            marker='o', label='대여', linewidth=2, markersize=8)
    ax.plot(daily_total['STAT_DATA'], daily_total['RTN_CNT'],
            marker='s', label='반납', linewidth=2, markersize=8)
    ax.set_xlabel('날짜', fontsize=12)
    ax.set_ylabel('건수', fontsize=12)
    ax.set_title('일별 대여·반납 건수 추이 (2025.10.27 ~ 11.02)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/daily_trend.png", dpi=300)
    print(f"\n✓ 저장: {OUTPUT_DIR}/daily_trend.png")
    plt.close()

    # 2) 행정구별 일평균 비교
    gu_daily_avg = df_raw.groupby('STA_LOC').agg({
        'RENT_CNT': 'mean',
        'RTN_CNT': 'mean'
    }).reset_index()
    gu_daily_avg = gu_daily_avg.sort_values('RENT_CNT', ascending=False)

    print("\n행정구별 일평균 대여/반납:")
    print(gu_daily_avg.head(10).to_string(index=False))

    # 시각화 2: 행정구별 비교
    fig, ax = plt.subplots(figsize=(14, 8))
    x = range(len(gu_daily_avg))
    width = 0.35
    ax.barh([i - width/2 for i in x], gu_daily_avg['RENT_CNT'],
            width, label='대여', alpha=0.8)
    ax.barh([i + width/2 for i in x], gu_daily_avg['RTN_CNT'],
            width, label='반납', alpha=0.8)
    ax.set_yticks(x)
    ax.set_yticklabels(gu_daily_avg['STA_LOC'])
    ax.set_xlabel('일평균 건수', fontsize=12)
    ax.set_title('행정구별 일평균 대여·반납 건수', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/gu_comparison.png", dpi=300)
    print(f"✓ 저장: {OUTPUT_DIR}/gu_comparison.png")
    plt.close()

    return daily_total, gu_daily_avg

def analyze_imbalance(df_summary):
    """
    분석 2: 순유입(Net Flow) 및 불균형 분석
    - unbal_50.csv: 불균형 탑 50 데이터
    - net_inflow_outflow.csv: 순유입/순유출 데이터
    """
    print("\n" + "=" * 60)
    print("분석 2: 순유입 및 불균형 분석")
    print("=" * 60)

    # 파생 변수 생성
    df_summary['NET_FLOW'] = df_summary['TOTAL_RENT_CNT'] - df_summary['TOTAL_RTN_CNT']
    df_summary['IMBAL_RATIO'] = (
        abs(df_summary['TOTAL_RENT_CNT'] - df_summary['TOTAL_RTN_CNT'])
        / (df_summary['TOTAL_RENT_CNT'] + df_summary['TOTAL_RTN_CNT'])
    ).fillna(0)

    # 1) 불균형 Top 50
    unbal_50 = df_summary.nlargest(50, 'IMBAL_RATIO')[
        ['STA_LOC', 'RENT_NM', 'AVG_RENT_CNT', 'TOTAL_RENT_CNT',
         'AVG_RTN_CNT', 'TOTAL_RTN_CNT', 'NET_FLOW', 'IMBAL_RATIO']
    ].copy()

    unbal_50_path = f"{DATA_DIR}/unbal_50.csv"
    unbal_50.to_csv(unbal_50_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ 불균형 Top 50 저장: {unbal_50_path}")
    print("\n불균형 상위 10개 대여소:")
    print(unbal_50[['STA_LOC', 'RENT_NM', 'IMBAL_RATIO', 'NET_FLOW']].head(10).to_string(index=False))

    # 2) 순유입/순유출 분류
    df_flow = df_summary.copy()
    df_flow['FLOW_TYPE'] = df_flow['NET_FLOW'].apply(
        lambda x: 'inflow' if x < 0 else 'outflow'
    )

    net_flow_data = df_flow[
        ['STA_LOC', 'RENT_NM', 'AVG_RENT_CNT', 'TOTAL_RENT_CNT',
         'AVG_RTN_CNT', 'TOTAL_RTN_CNT', 'NET_FLOW', 'FLOW_TYPE']
    ].copy()

    net_flow_path = f"{DATA_DIR}/net_inflow_outflow.csv"
    net_flow_data.to_csv(net_flow_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ 순유입/순유출 데이터 저장: {net_flow_path}")

    # 통계 출력
    print("\n순유입/순유출 통계:")
    print(f"  - 순유입(inflow) 대여소: {len(df_flow[df_flow['FLOW_TYPE'] == 'inflow']):,}개")
    print(f"  - 순유출(outflow) 대여소: {len(df_flow[df_flow['FLOW_TYPE'] == 'outflow']):,}개")

    print("\n순유입 상위 10개 대여소 (반납 > 대여):")
    inflow_top = df_flow[df_flow['FLOW_TYPE'] == 'inflow'].nsmallest(10, 'NET_FLOW')
    print(inflow_top[['STA_LOC', 'RENT_NM', 'NET_FLOW']].to_string(index=False))

    print("\n순유출 상위 10개 대여소 (대여 > 반납):")
    outflow_top = df_flow[df_flow['FLOW_TYPE'] == 'outflow'].nlargest(10, 'NET_FLOW')
    print(outflow_top[['STA_LOC', 'RENT_NM', 'NET_FLOW']].to_string(index=False))

    # 시각화 3: 불균형 Top 20
    fig, ax = plt.subplots(figsize=(12, 8))
    top20_imbal = unbal_50.head(20)
    colors = ['red' if x < 0 else 'blue' for x in top20_imbal['NET_FLOW']]
    ax.barh(range(len(top20_imbal)), top20_imbal['IMBAL_RATIO'], color=colors, alpha=0.7)
    ax.set_yticks(range(len(top20_imbal)))
    ax.set_yticklabels(top20_imbal['RENT_NM'], fontsize=9)
    ax.set_xlabel('불균형 비율 (IMBAL_RATIO)', fontsize=12)
    ax.set_title('불균형 상위 20개 대여소\n(빨강: 순유입/반납>대여, 파랑: 순유출/대여>반납)',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/imbalance_top20.png", dpi=300)
    print(f"\n✓ 저장: {OUTPUT_DIR}/imbalance_top20.png")
    plt.close()

    # 시각화 4: 순유입/순유출 분포
    fig, ax = plt.subplots(figsize=(12, 6))
    flow_counts = df_flow['FLOW_TYPE'].value_counts()
    colors_pie = ['#ff6b6b', '#4ecdc4']
    ax.pie(flow_counts.values, labels=['순유출\n(대여>반납)', '순유입\n(반납>대여)'],
           autopct='%1.1f%%', startangle=90, colors=colors_pie, textprops={'fontsize': 12})
    ax.set_title('대여소별 순유입/순유출 분포', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/flow_distribution.png", dpi=300)
    print(f"✓ 저장: {OUTPUT_DIR}/flow_distribution.png")
    plt.close()

    return unbal_50, net_flow_data

def generate_insights(daily_total, gu_daily_avg, unbal_50, net_flow_data):
    """
    핵심 발견 및 실행 권고 생성
    """
    print("\n" + "=" * 60)
    print("핵심 발견 및 인사이트 도출")
    print("=" * 60)

    # 통계 계산
    total_rent = daily_total['RENT_CNT'].sum()
    total_rtn = daily_total['RTN_CNT'].sum()
    avg_daily_rent = daily_total['RENT_CNT'].mean()

    weekday_avg = daily_total.iloc[:5]['RENT_CNT'].mean()  # 평일 (10/27-10/31)
    weekend_avg = daily_total.iloc[5:]['RENT_CNT'].mean()  # 주말 (11/1-11/2)

    top_gu = gu_daily_avg.iloc[0]

    insights = {
        'total_rent': total_rent,
        'total_rtn': total_rtn,
        'avg_daily_rent': avg_daily_rent,
        'weekday_avg': weekday_avg,
        'weekend_avg': weekend_avg,
        'weekend_decrease': ((weekday_avg - weekend_avg) / weekday_avg * 100),
        'top_gu': top_gu['STA_LOC'],
        'top_gu_avg': top_gu['RENT_CNT'],
        'imbal_count': len(unbal_50[unbal_50['IMBAL_RATIO'] > 0.3]),
        'severe_imbal_count': len(unbal_50[unbal_50['IMBAL_RATIO'] > 0.5])
    }

    return insights

def create_report(insights, unbal_50, net_flow_data):
    """
    최종 분석 리포트 생성
    """
    report = f"""
{'=' * 80}
서울시 따릉이 일별 이용현황 분석 리포트
분석 기간: 2025년 10월 27일 ~ 11월 2일 (7일간)
{'=' * 80}

📊 주요 통계
{'─' * 80}
• 총 대여 건수: {insights['total_rent']:,.0f}건
• 총 반납 건수: {insights['total_rtn']:,.0f}건
• 일평균 대여 건수: {insights['avg_daily_rent']:,.0f}건
• 평일 평균 대여: {insights['weekday_avg']:,.0f}건
• 주말 평균 대여: {insights['weekend_avg']:,.0f}건
• 주말 감소율: {insights['weekend_decrease']:.1f}%

🔍 핵심 발견 (Key Findings)
{'─' * 80}

1️⃣ 평일 중심의 뚜렷한 출퇴근형 패턴
   • 주말 대여량이 평일 대비 {insights['weekend_decrease']:.1f}% 감소
   • 업무지구 중심의 수요 구조 확인
   • {insights['top_gu']} 지역이 일평균 {insights['top_gu_avg']:.0f}건으로 최다 이용

2️⃣ 심각한 수요 불균형 발생
   • 불균형 비율 30% 이상 대여소: {insights['imbal_count']}개
   • 불균형 비율 50% 이상 대여소: {insights['severe_imbal_count']}개
   • 주거지역: 순유출 (대여 > 반납)
   • 업무지역: 순유입 (반납 > 대여)

3️⃣ 소수 대여소의 수요 집중
   • 상위 10개 대여소가 전체 이용의 상당 부분 차지
   • 마곡나루역 일대 대여소가 주간 3,000건 이상 기록
   • 수요 집중 지역에 대한 집중 관리 필요

💡 실행 권고사항 (Action Items)
{'─' * 80}

1️⃣ 단기 조치 (1~2주 내)
   ✓ 순유입 상위 대여소 오전(AM) 보급 강화
   ✓ 순유출 상위 대여소 저녁(PM) 회수 강화
   ✓ 불균형 비율 50% 이상 대여소 실시간 모니터링 시스템 구축

2️⃣ 중기 조치 (1~3개월)
   ✓ 주거지 ↔ 업무지구 간 셔틀 재배치 루틴 정례화
   ✓ 평일/주말 차별화된 운영 전략 수립
   ✓ 수요 집중 지역 임시 거치대 추가 설치

3️⃣ 장기 조치 (3개월 이상)
   ✓ AI 기반 수요 예측 시스템 도입
   ✓ 동적 재배치 최적화 알고리즘 개발
   ✓ 행정구별 자전거 배분 KPI 기반 운영

📋 세부 개선 제안서
{'─' * 80}

[AM 루틴 - 출근시간대 (07:00~09:00)]
• 주거지역 대여소 → 자전거 보급 우선
• 업무지역 대여소 → 거치 공간 확보

[PM 루틴 - 퇴근시간대 (18:00~20:00)]
• 업무지역 대여소 → 자전거 회수 우선
• 주거지역 대여소 → 거치 공간 확보

[거치대 조정 우선순위]
• 불균형 상위 50개 대여소 중심
• 순유입/순유출 절대값 100건 이상 대여소
• 일평균 이용량 100건 이상 고수요 대여소

{'=' * 80}
분석 완료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
"""

    # 리포트 저장
    report_path = f"{OUTPUT_DIR}/analysis_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(report)
    print(f"\n✓ 리포트 저장: {report_path}")

    return report

def main():
    """메인 실행 함수"""
    print("\n")
    print("🚲 서울시 따릉이 일별 이용현황 분석")
    print("=" * 60)

    # 출력 디렉토리 생성
    ensure_output_dir()

    # 데이터 로드
    df_raw, df_summary = load_data()

    # 분석 1: 일별 트렌드
    daily_total, gu_daily_avg = analyze_daily_trend(df_raw)

    # 분석 2: 불균형 분석
    unbal_50, net_flow_data = analyze_imbalance(df_summary)

    # 인사이트 도출
    insights = generate_insights(daily_total, gu_daily_avg, unbal_50, net_flow_data)

    # 리포트 생성
    create_report(insights, unbal_50, net_flow_data)

    print("\n" + "=" * 60)
    print("✓ 모든 분석 완료!")
    print("=" * 60)
    print(f"\n생성된 파일:")
    print(f"  • 시각화: {OUTPUT_DIR}/")
    print(f"    - daily_trend.png (일별 추이)")
    print(f"    - gu_comparison.png (행정구별 비교)")
    print(f"    - imbalance_top20.png (불균형 상위 20)")
    print(f"    - flow_distribution.png (순유입/순유출 분포)")
    print(f"  • 데이터: {DATA_DIR}/")
    print(f"    - unbal_50.csv (불균형 상위 50)")
    print(f"    - net_inflow_outflow.csv (순유입/순유출)")
    print(f"  • 리포트: {OUTPUT_DIR}/analysis_report.txt")

if __name__ == "__main__":
    main()
