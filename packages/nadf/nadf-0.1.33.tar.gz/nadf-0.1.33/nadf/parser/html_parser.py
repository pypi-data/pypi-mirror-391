import os
from typing import List, Tuple
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

class HtmlParser:
    def __init__(self, html: BeautifulSoup, url: str):
        self.soup = html
        self.url = url
        self.content_target = os.getenv("NAMUWIKI_CONTENT_TARGET")

    async def extract_small_topics(self) -> List[Tuple[str, str, str]]:  # 레벨 추가
        small_topics = self.soup.find_all(['h2', 'h3', 'h4'])
        small_topics_list = []


        for topic in small_topics:
            level = topic.name  # 'h2', 'h3', 'h4'
            span = topic.find('span')
            small_topics_title = span.get_text().replace("[편집]", "")

            if (link := span.find('a')):
                small_topic = (small_topics_title, link.get("href"), level)
                small_topics_list.append(small_topic)
        return small_topics_list

    async def extract_content(self) -> List[str]:
        """
        콘텐츠 추출 - 구조 기반 접근 (동적 클래스명 대응)
        """
        import re

        headings = self.soup.find_all(['h2', 'h3', 'h4'])
        result = []

        for heading in headings:
            content_text = ""

            # 1️⃣ h2/h3/h4의 부모 다음 형제 우선 탐색
            if heading.parent:
                next_sibling = heading.parent.find_next_sibling()
                if next_sibling and next_sibling.name == "div":
                    content_text = next_sibling.get_text(separator=" ", strip=True)

            # 2️⃣ 텍스트가 없거나 짧으면: self.content_target 클래스 기반 탐색
            if (not content_text or len(content_text) < 20) and self.content_target:
                for sibling in heading.find_next_siblings(limit=10):
                    if sibling.name != "div":
                        continue

                    classes = sibling.get("class", [])
                    # 환경변수에서 가져온 클래스명 직접 비교
                    if self.content_target in classes:
                        text = sibling.get_text(separator=" ", strip=True)
                        if len(text) > 20:
                            content_text = text
                            break

            # 3️⃣ 그래도 못 찾으면 fallback: 기존 정규식 해시 탐색
            if not content_text or len(content_text) < 20:
                for sibling in heading.find_next_siblings(limit=10):
                    if sibling.name != "div":
                        continue
                    classes = sibling.get("class", [])
                    has_hash_class = any(
                        re.fullmatch(r"[A-Za-z0-9]{6,10}", cls)
                        for cls in classes
                    )
                    if has_hash_class:
                        text = sibling.get_text(separator=" ", strip=True)
                        if len(text) > 20:
                            content_text = text
                            break

            result.append(content_text)

        return result
