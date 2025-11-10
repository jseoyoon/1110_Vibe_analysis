# -*- coding: utf-8 -*-
"""
서울시 공공자전거 이용현황 데이터 전처리 스크립트
"""
import sys
import io
import pandas as pd
import os

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def preprocess_bike_data(input_path, output_path):
    """
    수집된 자전거 데이터를 전처리하고 집계

    Args:
        input_path: 원본 데이터 파일 경로
        output_path: 전처리 결과 저장 경로
    """
    print("=" * 60)
    print("서울시 공공자전거 이용현황 데이터 전처리")
    print("=" * 60)

    # 데이터 로드
    print(f"\n데이터 로드 중: {input_path}")
    df = pd.read_csv(input_path)
    print(f"  - 원본 데이터: {len(df):,}건")
    print(f"  - 컬럼: {', '.join(df.columns.tolist())}")

    # 기본 정보 출력
    print("\n데이터 기본 정보:")
    print(f"  - 기준일자 범위: {df['STAT_DATA'].min()} ~ {df['STAT_DATA'].max()}")
    print(f"  - 행정구 수: {df['STA_LOC'].nunique()}개")
    print(f"  - 대여소 수: {df['RENT_NM'].nunique()}개")

    # 데이터 타입 변환
    print("\n데이터 타입 변환 중...")
    df['RENT_CNT'] = pd.to_numeric(df['RENT_CNT'], errors='coerce')
    df['RTN_CNT'] = pd.to_numeric(df['RTN_CNT'], errors='coerce')

    # 결측치 확인
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        print("\n결측치 확인:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"  - {col}: {count}건")

    # 대여소별 집계
    print("\n대여소별 집계 처리 중...")
    summary = df.groupby(['STA_LOC', 'RENT_NM']).agg({
        'RENT_CNT': ['mean', 'sum'],
        'RTN_CNT': ['mean', 'sum']
    }).reset_index()

    # 컬럼명 정리
    summary.columns = [
        'STA_LOC',          # 행정구
        'RENT_NM',          # 대여소명
        'AVG_RENT_CNT',     # 평균 대여건수
        'TOTAL_RENT_CNT',   # 대여건수 합계
        'AVG_RTN_CNT',      # 평균 반납건수
        'TOTAL_RTN_CNT'     # 반납건수 합계
    ]

    # 소수점 반올림
    summary['AVG_RENT_CNT'] = summary['AVG_RENT_CNT'].round(2)
    summary['AVG_RTN_CNT'] = summary['AVG_RTN_CNT'].round(2)

    # 정렬 (대여건수 합계 기준 내림차순)
    summary = summary.sort_values('TOTAL_RENT_CNT', ascending=False).reset_index(drop=True)

    # 결과 출력
    print(f"\n집계 결과:")
    print(f"  - 대여소 수: {len(summary):,}개")
    print(f"  - 총 대여건수: {summary['TOTAL_RENT_CNT'].sum():,.0f}건")
    print(f"  - 총 반납건수: {summary['TOTAL_RTN_CNT'].sum():,.0f}건")
    print(f"  - 평균 대여건수 (대여소당): {summary['AVG_RENT_CNT'].mean():.2f}건")
    print(f"  - 평균 반납건수 (대여소당): {summary['AVG_RTN_CNT'].mean():.2f}건")

    # 상위 10개 대여소
    print("\n대여건수 상위 10개 대여소:")
    print(summary[['RENT_NM', 'STA_LOC', 'TOTAL_RENT_CNT']].head(10).to_string(index=False))

    # 파일 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    summary.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✓ 전처리 완료: {output_path}")

    return summary

def main():
    """메인 실행 함수"""
    input_path = "data/raw/bike_weekly.csv"
    output_path = "data/processed/bike_weekly_summary.csv"

    if not os.path.exists(input_path):
        print(f"오류: {input_path} 파일이 존재하지 않습니다.")
        print("먼저 collect_bike_data.py를 실행하여 데이터를 수집해주세요.")
        return

    preprocess_bike_data(input_path, output_path)

if __name__ == "__main__":
    main()
