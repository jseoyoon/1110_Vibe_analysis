"""
Pokemon 데이터를 PokeAPI에서 가져와 Notion 데이터베이스에 추가하는 스크립트
"""

import requests
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# 환경 변수 로드
load_dotenv()


class PokemonToNotion:
    """Pokemon 데이터를 Notion에 추가하는 클래스"""

    def __init__(self, notion_token: str, database_id: str):
        """
        초기화

        Args:
            notion_token: Notion API Integration Token
            database_id: Notion Database ID
        """
        self.notion_token = notion_token
        self.database_id = database_id
        self.notion_api_url = "https://api.notion.com/v1"
        self.pokeapi_url = "https://pokeapi.co/api/v2"

        # Notion API 헤더 설정
        self.notion_headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def get_pokemon_data(self, pokemon_name: str) -> Dict[str, Any]:
        """
        PokeAPI에서 Pokemon 데이터 가져오기

        Args:
            pokemon_name: 포켓몬 이름 (예: pikachu)

        Returns:
            Pokemon 데이터 딕셔너리
        """
        url = f"{self.pokeapi_url}/pokemon/{pokemon_name.lower()}"

        print(f"🔍 PokeAPI에서 '{pokemon_name}' 데이터를 가져오는 중...")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            print(f"✅ '{pokemon_name}' 데이터를 성공적으로 가져왔습니다!")
            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ 오류 발생: {e}")
            raise

    def format_pokemon_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PokeAPI 데이터를 Notion 형식으로 변환

        Args:
            raw_data: PokeAPI에서 가져온 원본 데이터

        Returns:
            Notion 형식으로 변환된 데이터
        """
        print("📝 데이터를 Notion 형식으로 변환 중...")

        # 능력치 추출
        stats = {}
        for stat in raw_data['stats']:
            stat_name = stat['stat']['name']
            stat_value = stat['base_stat']
            stats[stat_name] = stat_value

        # 타입 추출
        types = [t['type']['name'] for t in raw_data['types']]

        # 변환된 데이터
        formatted_data = {
            'pokemon_name': raw_data['name'],
            'hp': stats.get('hp', 0),
            'attack': stats.get('attack', 0),
            'defense': stats.get('defense', 0),
            'special_attack': stats.get('special-attack', 0),
            'special_defense': stats.get('special-defense', 0),
            'speed': stats.get('speed', 0),
            'types': types,
            'weight': raw_data['weight'],
            'height': raw_data['height'],
            'image': raw_data['sprites']['front_default']
        }

        print("✅ 데이터 변환 완료!")
        return formatted_data

    def create_notion_page(self, pokemon_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notion 데이터베이스에 Pokemon 페이지 추가

        Args:
            pokemon_data: 변환된 Pokemon 데이터

        Returns:
            Notion API 응답
        """
        url = f"{self.notion_api_url}/pages"

        # Notion 페이지 데이터 구조
        notion_page = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": pokemon_data['pokemon_name'].capitalize()
                            }
                        }
                    ]
                },
                "HP": {
                    "number": pokemon_data['hp']
                },
                "Attack": {
                    "number": pokemon_data['attack']
                },
                "Defense": {
                    "number": pokemon_data['defense']
                },
                "Special Attack": {
                    "number": pokemon_data['special_attack']
                },
                "Special Defense": {
                    "number": pokemon_data['special_defense']
                },
                "Speed": {
                    "number": pokemon_data['speed']
                },
                "Types": {
                    "multi_select": [{"name": t.capitalize()} for t in pokemon_data['types']]
                },
                "Weight": {
                    "number": pokemon_data['weight']
                },
                "Height": {
                    "number": pokemon_data['height']
                },
                "Image": {
                    "url": pokemon_data['image']
                }
            }
        }

        print(f"📤 Notion에 '{pokemon_data['pokemon_name']}' 페이지를 추가하는 중...")

        try:
            response = requests.post(url, headers=self.notion_headers, json=notion_page)
            response.raise_for_status()
            result = response.json()

            print(f"✅ Notion 페이지가 성공적으로 생성되었습니다!")
            print(f"🔗 페이지 URL: {result.get('url', 'N/A')}")

            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Notion API 오류: {e}")
            if hasattr(e.response, 'text'):
                print(f"상세 오류: {e.response.text}")
            raise

    def add_pokemon_to_notion(self, pokemon_name: str) -> Dict[str, Any]:
        """
        Pokemon 데이터를 가져와서 Notion에 추가하는 전체 프로세스

        Args:
            pokemon_name: 포켓몬 이름

        Returns:
            Notion API 응답
        """
        print(f"\n{'='*60}")
        print(f"🚀 '{pokemon_name.upper()}' 데이터를 Notion에 추가 시작")
        print(f"{'='*60}\n")

        # 1. PokeAPI에서 데이터 가져오기
        raw_data = self.get_pokemon_data(pokemon_name)

        # 2. 데이터 변환
        formatted_data = self.format_pokemon_data(raw_data)

        # 3. Notion에 페이지 추가
        result = self.create_notion_page(formatted_data)

        print(f"\n{'='*60}")
        print(f"🎉 작업 완료!")
        print(f"{'='*60}\n")

        return result


def main():
    """메인 함수"""

    # Notion 설정 (환경 변수 또는 직접 입력)
    NOTION_TOKEN = os.getenv("NOTION_TOKEN", "YOUR_NOTION_INTEGRATION_TOKEN")
    DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "YOUR_NOTION_DATABASE_ID")

    # 토큰과 데이터베이스 ID 확인
    if NOTION_TOKEN == "YOUR_NOTION_INTEGRATION_TOKEN" or DATABASE_ID == "YOUR_NOTION_DATABASE_ID":
        print("⚠️  경고: .env 파일에 NOTION_TOKEN과 NOTION_DATABASE_ID를 설정해주세요!")
        print("\n.env 파일 예시:")
        print("NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxx")
        print("NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxx")
        return

    # PokemonToNotion 인스턴스 생성
    pokemon_to_notion = PokemonToNotion(NOTION_TOKEN, DATABASE_ID)

    # 피카츄 데이터 추가
    try:
        pokemon_to_notion.add_pokemon_to_notion("pikachu")

        # 피카츄 능력치 출력
        print("\n📊 피카츄 능력치 정보:")
        print("-" * 40)
        pikachu_data = pokemon_to_notion.get_pokemon_data("pikachu")
        formatted = pokemon_to_notion.format_pokemon_data(pikachu_data)

        print(f"이름: {formatted['pokemon_name'].capitalize()}")
        print(f"타입: {', '.join([t.capitalize() for t in formatted['types']])}")
        print(f"HP: {formatted['hp']}")
        print(f"공격: {formatted['attack']}")
        print(f"방어: {formatted['defense']}")
        print(f"특수공격: {formatted['special_attack']}")
        print(f"특수방어: {formatted['special_defense']}")
        print(f"스피드: {formatted['speed']}")
        print(f"무게: {formatted['weight']}")
        print(f"키: {formatted['height']}")
        print(f"이미지: {formatted['image']}")

    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        print("\n문제 해결 방법:")
        print("1. .env 파일에 NOTION_TOKEN과 NOTION_DATABASE_ID가 올바르게 설정되어 있는지 확인")
        print("2. Notion Integration이 데이터베이스에 연결되어 있는지 확인")
        print("3. 데이터베이스 속성 이름이 정확히 일치하는지 확인")
        print("   (Name, HP, Attack, Defense, Special Attack, Special Defense, Speed, Types, Weight, Height, Image)")


if __name__ == "__main__":
    main()
