"""
서울시 따릉이 데이터 로더 유틸리티

데이터를 로딩하고 기본 전처리를 수행하는 함수들을 포함합니다.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def load_seoulbike_data(
    file_path: str,
    encoding: str = 'cp949',
    parse_dates: bool = True
) -> pd.DataFrame:
    """
    서울시 공공자전거 신규가입자 데이터를 로딩합니다.

    Parameters
    ----------
    file_path : str
        데이터 파일 경로
    encoding : str, default='cp949'
        파일 인코딩
    parse_dates : bool, default=True
        대여월을 datetime으로 변환할지 여부

    Returns
    -------
    pd.DataFrame
        로딩된 데이터프레임

    Examples
    --------
    >>> df = load_seoulbike_data('data/raw/서울시 공공자전거 신규가입자 정보(월별).csv')
    >>> print(df.shape)
    (192, 5)
    """
    # 데이터 로딩
    df = pd.read_csv(file_path, encoding=encoding)

    # 날짜 파싱
    if parse_dates and '대여월' in df.columns:
        df['대여월_dt'] = pd.to_datetime(df['대여월'], format='%Y%m')

    return df


def get_basic_stats(df: pd.DataFrame) -> dict:
    """
    데이터프레임의 기본 통계를 반환합니다.

    Parameters
    ----------
    df : pd.DataFrame
        분석할 데이터프레임

    Returns
    -------
    dict
        기본 통계 정보
    """
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'date_range': (df['대여월'].min(), df['대여월'].max()) if '대여월' in df.columns else None,
        'total_subscribers': df['신규가입자수'].sum() if '신규가입자수' in df.columns else None,
        'missing_values': df.isnull().sum().to_dict()
    }

    return stats


def aggregate_by_month(df: pd.DataFrame, value_col: str = '신규가입자수') -> pd.DataFrame:
    """
    월별로 데이터를 집계합니다.

    Parameters
    ----------
    df : pd.DataFrame
        원본 데이터프레임
    value_col : str, default='신규가입자수'
        집계할 값 컬럼

    Returns
    -------
    pd.DataFrame
        월별 집계 결과
    """
    if '대여월_dt' in df.columns:
        date_col = '대여월_dt'
    else:
        date_col = '대여월'

    monthly = df.groupby(date_col)[value_col].sum().reset_index()
    monthly.columns = ['month', 'total_subscribers']

    return monthly


def aggregate_by_gender(df: pd.DataFrame, value_col: str = '신규가입자수') -> pd.DataFrame:
    """
    성별로 데이터를 집계합니다.

    Parameters
    ----------
    df : pd.DataFrame
        원본 데이터프레임
    value_col : str, default='신규가입자수'
        집계할 값 컬럼

    Returns
    -------
    pd.DataFrame
        성별 집계 결과
    """
    gender = df.groupby('성별')[value_col].sum().reset_index()
    gender.columns = ['gender', 'total_subscribers']

    return gender


def aggregate_by_age(df: pd.DataFrame, value_col: str = '신규가입자수') -> pd.DataFrame:
    """
    연령대별로 데이터를 집계합니다.

    Parameters
    ----------
    df : pd.DataFrame
        원본 데이터프레임
    value_col : str, default='신규가입자수'
        집계할 값 컬럼

    Returns
    -------
    pd.DataFrame
        연령대별 집계 결과 (순서 정렬됨)
    """
    age_order = ['~10대', '20대', '30대', '40대', '50대', '60대', '70대이상', '기타']

    age = df.groupby('연령대코드')[value_col].sum().reset_index()
    age.columns = ['age_group', 'total_subscribers']

    # 연령대 순서대로 정렬
    age['age_group'] = pd.Categorical(age['age_group'], categories=age_order, ordered=True)
    age = age.sort_values('age_group').reset_index(drop=True)

    return age


def create_segment_pivot(
    df: pd.DataFrame,
    index: str = '성별',
    columns: str = '연령대코드',
    values: str = '신규가입자수',
    aggfunc: str = 'sum'
) -> pd.DataFrame:
    """
    세그먼트별 피벗 테이블을 생성합니다.

    Parameters
    ----------
    df : pd.DataFrame
        원본 데이터프레임
    index : str, default='성별'
        행 인덱스로 사용할 컬럼
    columns : str, default='연령대코드'
        열로 사용할 컬럼
    values : str, default='신규가입자수'
        집계할 값 컬럼
    aggfunc : str, default='sum'
        집계 함수

    Returns
    -------
    pd.DataFrame
        피벗 테이블
    """
    pivot = df.pivot_table(
        values=values,
        index=index,
        columns=columns,
        aggfunc=aggfunc,
        fill_value=0
    )

    # 연령대 순서 정렬
    age_order = ['~10대', '20대', '30대', '40대', '50대', '60대', '70대이상', '기타']
    pivot = pivot[[col for col in age_order if col in pivot.columns]]

    return pivot


if __name__ == '__main__':
    # 예제 사용법
    data_path = Path('../data/raw/서울시 공공자전거 신규가입자 정보(월별).csv')

    if data_path.exists():
        df = load_seoulbike_data(data_path)
        print("데이터 로딩 완료!")
        print(f"데이터 크기: {df.shape}")

        stats = get_basic_stats(df)
        print(f"\n기본 통계:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print(f"데이터 파일을 찾을 수 없습니다: {data_path}")
