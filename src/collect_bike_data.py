# -*- coding: utf-8 -*-
"""
서울시 공공자전거 이용현황 데이터 수집 스크립트
"""
import sys
import io
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# .env 파일에서 API 키 로드
load_dotenv()
API_KEY = os.getenv('KEY')

# API 설정
BASE_URL = "http://openapi.seoul.go.kr:8088"
SERVICE_NAME = "tbCycleUseStatus"
FILE_TYPE = "json"
MAX_RECORDS_PER_REQUEST = 1000

def fetch_bike_data(date_str):
    """
    특정 날짜의 공공자전거 이용현황 데이터를 모두 수집

    Args:
        date_str: 조회할 날짜 (YYYYMMDD 형식)

    Returns:
        DataFrame: 해당 날짜의 모든 데이터
    """
    all_data = []
    start_index = 1

    print(f"[{date_str}] 데이터 수집 시작...")

    while True:
        end_index = start_index + MAX_RECORDS_PER_REQUEST - 1

        # API URL 구성
        url = f"{BASE_URL}/{API_KEY}/{FILE_TYPE}/{SERVICE_NAME}/{start_index}/{end_index}/{date_str}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 응답 확인 (실제 응답 키는 'useStatus')
            if 'useStatus' not in data:
                if SERVICE_NAME in data:
                    result = data[SERVICE_NAME]
                else:
                    print(f"  [{date_str}] API 응답 오류 - 예상하지 못한 응답 구조")
                    break
            else:
                result = data['useStatus']

            # 결과 코드 확인
            if 'RESULT' in result:
                code = result['RESULT']['CODE']
                message = result['RESULT']['MESSAGE']

                if code == 'INFO-200':  # 데이터 없음
                    print(f"  [{date_str}] 수집 완료 (총 {len(all_data)}건)")
                    break
                elif code != 'INFO-000':  # 정상이 아닌 경우
                    print(f"  [{date_str}] 오류: {code} - {message}")
                    break

            # 데이터 추출
            if 'row' in result:
                rows = result['row']
                all_data.extend(rows)
                print(f"  [{date_str}] {start_index}~{start_index + len(rows) - 1}번 수집 완료")

                # 다음 페이지로
                if len(rows) < MAX_RECORDS_PER_REQUEST:
                    print(f"  [{date_str}] 수집 완료 (총 {len(all_data)}건)")
                    break

                start_index = end_index + 1
            else:
                print(f"  [{date_str}] 수집 완료 (총 {len(all_data)}건)")
                break

            # API 요청 간 딜레이
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"  [{date_str}] 요청 오류: {e}")
            break
        except Exception as e:
            print(f"  [{date_str}] 예외 발생: {e}")
            break

    # DataFrame으로 변환
    if all_data:
        df = pd.DataFrame(all_data)
        return df
    else:
        return pd.DataFrame()

def collect_weekly_data(start_date, end_date):
    """
    지정된 기간의 데이터를 날짜별로 수집

    Args:
        start_date: 시작 날짜 (YYYYMMDD)
        end_date: 종료 날짜 (YYYYMMDD)

    Returns:
        DataFrame: 전체 기간의 통합 데이터
    """
    # 날짜 파싱
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')

    all_dataframes = []
    current_date = start

    while current_date <= end:
        # API에는 YYYY-MM-DD 형식으로 전달
        date_str = current_date.strftime('%Y-%m-%d')
        df = fetch_bike_data(date_str)

        if not df.empty:
            all_dataframes.append(df)

        current_date += timedelta(days=1)

    # 모든 데이터 병합
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"\n총 수집 건수: {len(combined_df)}건")
        return combined_df
    else:
        print("\n수집된 데이터가 없습니다.")
        return pd.DataFrame()

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("서울시 공공자전거 이용현황 데이터 수집")
    print("=" * 60)

    if not API_KEY:
        print("오류: .env 파일에 API KEY가 설정되지 않았습니다.")
        return

    # 수집 기간 설정
    START_DATE = "20251006"
    END_DATE = "20251102"

    print(f"수집 기간: {START_DATE} ~ {END_DATE}")
    print(f"API 키: {API_KEY[:10]}...")
    print()

    # 데이터 수집
    df = collect_weekly_data(START_DATE, END_DATE)

    if not df.empty:
        # 데이터 저장
        output_path = "data/raw/bike_weekly.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✓ 데이터 저장 완료: {output_path}")
        print(f"  - 총 레코드 수: {len(df):,}건")
        print(f"  - 컬럼: {', '.join(df.columns.tolist())}")
    else:
        print("\n✗ 수집된 데이터가 없어 파일을 저장하지 않았습니다.")

if __name__ == "__main__":
    main()
