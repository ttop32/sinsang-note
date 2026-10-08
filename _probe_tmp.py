import re, sys
from collectors import base
from selectolax.parser import HTMLParser

urls = [
 # 삼양 (지주)
 "https://www.samyangroundsquare.com/",
 "https://www.samyangroundsquare.com/kr/news",
 "https://www.samyangroundsquare.com/kor/publicity/press/list.do",
 # CJ 뉴스룸
 "https://cjnews.cj.net/",
 "https://www.cj.net/",
 # 롯데
 "https://www.lotte.co.kr/",
 "https://www.lotte.co.kr/main/pr/newsList.do",
 # 동원그룹
 "https://www.dongwon.com/",
 # 대상홀딩스
 "https://www.daesangholdings.com/",
 # 크라운해태
 "https://www.crownhaitai.com/",
 "https://www.ht.co.kr/",
 # 오리온홀딩스
 "https://www.orionholdings.co.kr/",
 # 매일홀딩스
 "https://www.maeilholdings.com/",
 # 하이트진로
 "https://www.hitejinro.com/",
 # 사조그룹
 "https://www.sajo.co.kr/2026/pr/news.asp",
 # 빙그레
 "https://www.bing.co.kr/",
]
with base.client() as c:
    for u in urls:
        try:
            r = c.get(u)
            t = HTMLParser(r.text)
            title = (t.css_first("title").text().strip() if t.css_first("title") else "")[:60]
            nd = len(re.findall(r"20\d{2}[-.]\s?\d{1,2}[-.]\s?\d{1,2}", r.text))
            print(f"{r.status_code} {len(r.content):>8}B dates={nd:>4}  {u}\n        -> {r.url}\n        {title}")
        except Exception as e:
            print(f"ERR  {u}  {type(e).__name__}: {str(e)[:120]}")
        sys.stdout.flush()
