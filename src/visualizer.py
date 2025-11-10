"""
서울시 따릉이 데이터 시각화 유틸리티

다양한 차트를 생성하는 함수들을 포함합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Tuple


# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_style('whitegrid')


def plot_monthly_trend(
    df: pd.DataFrame,
    date_col: str = '대여월_dt',
    value_col: str = '신규가입자수',
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> None:
    """
    월별 신규 가입자 추이를 라인 차트로 시각화합니다.

    Parameters
    ----------
    df : pd.DataFrame
        데이터프레임
    date_col : str
        날짜 컬럼명
    value_col : str
        값 컬럼명
    figsize : tuple
        그래프 크기
    save_path : str, optional
        저장할 파일 경로
    """
    monthly_total = df.groupby(date_col)[value_col].sum()

    plt.figure(figsize=figsize)
    monthly_total.plot(kind='line', marker='o', linewidth=2, markersize=8, color='#4A90E2')
    plt.title('월별 신규 가입자 수 추이', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('월', fontsize=12)
    plt.ylabel('신규 가입자 수', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"그래프 저장 완료: {save_path}")

    plt.show()


def plot_gender_distribution(
    df: pd.DataFrame,
    gender_col: str = '성별',
    value_col: str = '신규가입자수',
    chart_type: str = 'bar',
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> None:
    """
    성별 분포를 시각화합니다.

    Parameters
    ----------
    df : pd.DataFrame
        데이터프레임
    gender_col : str
        성별 컬럼명
    value_col : str
        값 컬럼명
    chart_type : str
        차트 타입 ('bar' 또는 'pie')
    figsize : tuple
        그래프 크기
    save_path : str, optional
        저장할 파일 경로
    """
    gender_total = df.groupby(gender_col)[value_col].sum()

    plt.figure(figsize=figsize)

    if chart_type == 'bar':
        gender_total.plot(kind='bar', color=['#4A90E2', '#E24A90'])
        plt.title('성별 신규 가입자 분포', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('성별', fontsize=12)
        plt.ylabel('신규 가입자 수', fontsize=12)
        plt.xticks(rotation=0)

        # 값 표시
        for i, v in enumerate(gender_total):
            plt.text(i, v, f'{v:,}', ha='center', va='bottom', fontsize=11)

    elif chart_type == 'pie':
        colors = ['#4A90E2', '#E24A90']
        plt.pie(gender_total, labels=gender_total.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        plt.title('성별 신규 가입자 비율', fontsize=16, fontweight='bold', pad=20)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"그래프 저장 완료: {save_path}")

    plt.show()


def plot_age_distribution(
    df: pd.DataFrame,
    age_col: str = '연령대코드',
    value_col: str = '신규가입자수',
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> None:
    """
    연령대별 분포를 시각화합니다.

    Parameters
    ----------
    df : pd.DataFrame
        데이터프레임
    age_col : str
        연령대 컬럼명
    value_col : str
        값 컬럼명
    figsize : tuple
        그래프 크기
    save_path : str, optional
        저장할 파일 경로
    """
    age_order = ['~10대', '20대', '30대', '40대', '50대', '60대', '70대이상', '기타']
    age_total = df.groupby(age_col)[value_col].sum().reindex(age_order)

    plt.figure(figsize=figsize)
    age_total.plot(kind='bar', color='skyblue', edgecolor='black', linewidth=0.5)
    plt.title('연령대별 신규 가입자 분포', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('연령대', fontsize=12)
    plt.ylabel('신규 가입자 수', fontsize=12)
    plt.xticks(rotation=45)

    # 값 표시
    for i, v in enumerate(age_total):
        if pd.notna(v):
            plt.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"그래프 저장 완료: {save_path}")

    plt.show()


def plot_segment_heatmap(
    df: pd.DataFrame,
    index_col: str = '성별',
    columns_col: str = '연령대코드',
    value_col: str = '신규가입자수',
    figsize: Tuple[int, int] = (12, 5),
    save_path: Optional[str] = None
) -> None:
    """
    성별 x 연령대 히트맵을 시각화합니다.

    Parameters
    ----------
    df : pd.DataFrame
        데이터프레임
    index_col : str
        행 인덱스 컬럼명
    columns_col : str
        열 컬럼명
    value_col : str
        값 컬럼명
    figsize : tuple
        그래프 크기
    save_path : str, optional
        저장할 파일 경로
    """
    # 피벗 테이블 생성
    age_order = ['~10대', '20대', '30대', '40대', '50대', '60대', '70대이상', '기타']
    pivot = df.pivot_table(
        values=value_col,
        index=index_col,
        columns=columns_col,
        aggfunc='sum',
        fill_value=0
    )

    # 연령대 순서 정렬
    pivot = pivot[[col for col in age_order if col in pivot.columns]]

    plt.figure(figsize=figsize)
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', linewidths=0.5,
                cbar_kws={'label': '신규 가입자 수'})
    plt.title('성별 × 연령대별 신규 가입자 히트맵', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('연령대', fontsize=12)
    plt.ylabel('성별', fontsize=12)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"그래프 저장 완료: {save_path}")

    plt.show()


def plot_monthly_gender_trend(
    df: pd.DataFrame,
    date_col: str = '대여월_dt',
    gender_col: str = '성별',
    value_col: str = '신규가입자수',
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[str] = None
) -> None:
    """
    월별 성별 추이를 시각화합니다.

    Parameters
    ----------
    df : pd.DataFrame
        데이터프레임
    date_col : str
        날짜 컬럼명
    gender_col : str
        성별 컬럼명
    value_col : str
        값 컬럼명
    figsize : tuple
        그래프 크기
    save_path : str, optional
        저장할 파일 경로
    """
    monthly_gender = df.groupby([date_col, gender_col])[value_col].sum().unstack()

    plt.figure(figsize=figsize)
    monthly_gender.plot(kind='line', marker='o', linewidth=2, markersize=6)
    plt.title('월별 성별 신규 가입자 추이', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('월', fontsize=12)
    plt.ylabel('신규 가입자 수', fontsize=12)
    plt.legend(title='성별', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"그래프 저장 완료: {save_path}")

    plt.show()


if __name__ == '__main__':
    print("시각화 유틸리티 모듈")
    print("사용 예시는 Jupyter 노트북을 참고하세요.")
