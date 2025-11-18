"""
Notion API를 사용하여 페이지를 생성하는 모듈
"""
import os
import json
from typing import Dict, List, Optional
import requests


class NotionAPI:
    """Notion API를 사용하기 위한 클래스"""
    
    def __init__(self, api_key: str, database_id: str = None):
        """
        Args:
            api_key: Notion API 토큰
            database_id: Notion 데이터베이스 ID (선택사항)
        """
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def create_page_in_database(
        self,
        database_id: str,
        title: str,
        properties: Dict = None,
        content: List[Dict] = None
    ) -> Optional[Dict]:
        """
        데이터베이스에 페이지를 생성합니다.
        
        Args:
            database_id: Notion 데이터베이스 ID
            title: 페이지 제목
            properties: 페이지 속성 (데이터베이스 필드)
            content: 페이지 콘텐츠 (블록)
            
        Returns:
            생성된 페이지 정보 또는 None
        """
        # properties 기본값 설정
        if properties is None:
            properties = {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        
        # 페이지 데이터 구성
        page_data = {
            "parent": {
                "database_id": database_id
            },
            "properties": properties
        }
        
        if content:
            page_data["children"] = content
        
        try:
            response = requests.post(
                f"{self.base_url}/pages",
                headers=self.headers,
                json=page_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"페이지 생성 실패: {e}")
            if hasattr(e.response, 'text'):
                print(f"응답: {e.response.text}")
            return None
    
    def create_block(self, parent_id: str, blocks: List[Dict]) -> Optional[Dict]:
        """
        페이지에 블록(콘텐츠)을 추가합니다.
        
        Args:
            parent_id: 부모 페이지 또는 블록 ID
            blocks: 추가할 블록 리스트
            
        Returns:
            생성된 블록 정보 또는 None
        """
        try:
            response = requests.patch(
                f"{self.base_url}/blocks/{parent_id}/children",
                headers=self.headers,
                json={"children": blocks}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"블록 추가 실패: {e}")
            if hasattr(e.response, 'text'):
                print(f"응답: {e.response.text}")
            return None
    
    @staticmethod
    def create_heading_block(text: str, level: int = 2) -> Dict:
        """제목 블록을 생성합니다 (level: 1-3)"""
        return {
            "object": "block",
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": text
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def create_paragraph_block(text: str) -> Dict:
        """문단 블록을 생성합니다"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": text
                        }
                    }
                ]
            }
        }
    
    @staticmethod
    def create_image_block(image_url: str, caption: str = "") -> Dict:
        """이미지 블록을 생성합니다"""
        return {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                },
                "caption": [
                    {
                        "type": "text",
                        "text": {
                            "content": caption
                        }
                    }
                ]
            }
        }


def main():
    """예제 사용법"""
    # 환경변수에서 API 키와 데이터베이스 ID 가져오기
    # api_key = os.getenv("NOTION_API_KEY")
    api_key = "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"
    database_id = "29a798defb7f8031a0addd830e26c534"
    
    if not api_key:
        print("오류: NOTION_API_KEY 환경변수가 설정되지 않았습니다.")
        print("사용법: NOTION_API_KEY='your_key' NOTION_DATABASE_ID='your_db_id' python create_notion.py")
        return
    
    if not database_id:
        print("오류: NOTION_DATABASE_ID 환경변수가 설정되지 않았습니다.")
        print("사용법: NOTION_API_KEY='your_key' NOTION_DATABASE_ID='your_db_id' python create_notion.py")
        return
    
    # Notion API 클래스 초기화
    notion = NotionAPI(api_key, database_id)
    
    # 콘텐츠 블록 생성
    blocks = [
        NotionAPI.create_heading_block("새로운 페이지", level=1),
        NotionAPI.create_paragraph_block("이것은 Python을 사용하여 생성된 페이지입니다."),
        NotionAPI.create_paragraph_block("Notion API를 사용하여 자동으로 작성되었습니다.")
    ]
    
    # 데이터베이스에 페이지 생성
    result = notion.create_page_in_database(
        database_id=database_id,
        title="테스트 페이지",
        content=blocks
    )
    
    if result:
        print("페이지가 성공적으로 생성되었습니다!")
        print(f"페이지 ID: {result.get('id')}")
        print(f"페이지 URL: {result.get('url', 'URL을 찾을 수 없습니다.')}")
    else:
        print("페이지 생성에 실패했습니다.")


if __name__ == "__main__":
    main()