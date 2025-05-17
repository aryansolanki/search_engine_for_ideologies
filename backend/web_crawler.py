import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.parse
import json
import time
from lxml import html as lxml_html

class WebCrawler:
    def __init__(self, seeds, max_pages=100000, concurrent_tasks=50, incremental_interval=1000):
        """
        Initialize the web crawler.
        """
        self.frontier = asyncio.Queue()
        for seed in seeds:
            self.frontier.put_nowait(seed)

        self.visited = set()
        self.web_graph = {}
        self.seen_titles = set()

        self.max_pages = max_pages
        self.concurrent_tasks = concurrent_tasks
        self.pages_crawled = 0
        self.incremental_interval = incremental_interval
        self.session = None

    def is_english(self, html_text):
        """
        Return False if the page explicitly declares a non-English language
        via <html lang="..."> or meta http-equiv/content-language or meta[name=language].
        Otherwise True.
        """
        soup = BeautifulSoup(html_text, "lxml")
        # 1) <html lang="...">
        if soup.html and soup.html.has_attr("lang"):
            lang = soup.html["lang"].strip().lower()
            if not lang.startswith("en"):
                return False
        # 2) <meta http-equiv="content-language" content="...">
        meta_http = soup.find("meta", attrs={"http-equiv": "content-language"})
        if meta_http and meta_http.get("content"):
            lang = meta_http["content"].split(",")[0].strip().lower()
            if not lang.startswith("en"):
                return False
        # 3) <meta name="language" content="...">
        meta_name = soup.find("meta", attrs={"name": "language"})
        if meta_name and meta_name.get("content"):
            lang = meta_name["content"].strip().lower()
            if not lang.startswith("en"):
                return False
        return True

    async def fetch(self, url):
        """
        Asynchronously fetch a web page.
        """
        try:
            async with self.session.get(url, timeout=10) as resp:
                ct = resp.headers.get("content-type", "")
                if resp.status == 200 and "text/html" in ct:
                    return await resp.text()
        except:
            pass
        return None

    def extract_links(self, doc, base_url):
        """
        Normalize and filter outgoing HTTP(S) links.
        """
        links = []
        for href in doc.xpath("//a[@href]/@href"):
            if href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            absu = urllib.parse.urljoin(str(base_url), href)
            absu = urllib.parse.urldefrag(absu)[0]
            p = urlparse(absu)
            if p.scheme not in ("http", "https"):
                continue
            norm = urllib.parse.urlunparse((
                p.scheme, p.netloc.lower(), p.path.rstrip("/"),
                "", p.query, ""
            ))
            links.append(norm)
        # dedupe preserving order
        seen = set()
        unique = []
        for u in links:
            if u not in seen:
                seen.add(u)
                unique.append(u)
        return unique

    def extract_metadata(self, html_text, base_url):
        """
        Extract title, description, and keywords with robust fallbacks.
        """
        soup = BeautifulSoup(html_text, "lxml")

        # --- Title ---
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # --- Description meta fallbacks ---
        description = ""
        # 1) <meta name="description">
        m = soup.find("meta", {"name": "description"})
        if m:
            desc = m.get("content", "").strip()
            if len(desc) >= 30 and " " in desc:
                description = desc

        # 2) Open Graph
        if not description:
            og = soup.find("meta", property="og:description")
            if og:
                desc = og.get("content", "").strip()
                if len(desc) >= 30 and " " in desc:
                    description = desc

        # 3) Twitter
        if not description:
            tw = soup.find("meta", {"name": "twitter:description"})
            if tw:
                desc = tw.get("content", "").strip()
                if len(desc) >= 30 and " " in desc:
                    description = desc

        # 4) Wikipedia-specific fallback
        if not description and "wikipedia.org" in base_url:
            container = soup.find("div", class_="mw-parser-output")
            if container:
                for p in container.find_all("p"):
                    text = p.get_text().strip()
                    if len(text) >= 80 and not text.startswith(("Coordinates", "This is", "[")):
                        description = text
                        break

        # 5) Generic <p> scan ≥80 chars
        if not description:
            for p in soup.find_all("p"):
                text = p.get_text().strip()
                if len(text) >= 80:
                    description = text
                    break

        # 6) Final fallback
        if not description and (p := soup.find("p")):
            description = p.get_text().strip()

        # --- Keywords fallbacks ---
        keywords = ""
        kw = soup.find("meta", {"name": "keywords"})
        if kw and kw.get("content", "").strip():
            keywords = kw["content"].strip()
        elif nk := soup.find("meta", {"name": "news_keywords"}):
            keywords = nk.get("content", "").strip()
        elif ogk := soup.find("meta", property="og:keywords"):
            keywords = ogk.get("content", "").strip()
        elif twk := soup.find("meta", {"name": "twitter:keywords"}):
            keywords = twk.get("content", "").strip()
        elif "wikipedia.org" in base_url:
            # Wikipedia categories
            cat_div = soup.find("div", id="mw-normal-catlinks")
            if cat_div:
                cats = [a.get_text().strip() for a in cat_div.find_all("a")[1:]]
                keywords = ", ".join(cats)
        if not keywords and title:
            keywords = title

        return {"title": title, "description": description, "keywords": keywords}

    async def process_page(self, url):
        """
        Fetch, parse, enforce English + unique-title + non-empty metadata, then add to graph.
        """
        if url in self.visited:
            return

        html_text = await self.fetch(url)
        if not html_text:
            return

        # Skip non-English pages
        if not self.is_english(html_text):
            self.visited.add(url)
            return

        self.visited.add(url)
        self.pages_crawled += 1

        # Parse for links
        try:
            doc = lxml_html.fromstring(html_text)
        except:
            return

        # Extract metadata
        meta = self.extract_metadata(html_text, url)
        title = meta["title"]

        # Enforce unique titles
        if title and title in self.seen_titles:
            # still enqueue links
            for link in self.extract_links(doc, url):
                if link not in self.visited and self.pages_crawled < self.max_pages:
                    await self.frontier.put(link)
            return

        if title:
            self.seen_titles.add(title)

        # Extract & enqueue links
        links = self.extract_links(doc, url)
        for link in links:
            if link not in self.visited and self.pages_crawled < self.max_pages:
                await self.frontier.put(link)

        # Only add pages with some metadata
        if title or meta["description"] or meta["keywords"]:
            self.web_graph[url] = {"metadata": meta, "links": links}

        # Periodic save
        if self.pages_crawled % self.incremental_interval == 0:
            self.incremental_update()

    def incremental_update(self):
        """
        Save an incremental JSON snapshot.
        """
        data = {
            "pages_crawled": self.pages_crawled,
            "web_graph": self.web_graph
        }
        with open("incremental_update.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[update] pages_crawled={self.pages_crawled}, graph_size={len(self.web_graph)}")

    async def worker(self):
        while self.pages_crawled < self.max_pages:
            url = await self.frontier.get()
            try:
                await self.process_page(url)
            except:
                pass
            finally:
                self.frontier.task_done()

    async def crawl(self):
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as self.session:
            tasks = [asyncio.create_task(self.worker()) for _ in range(self.concurrent_tasks)]
            await self.frontier.join()
            for t in tasks:
                t.cancel()

def main():
    seeds = [
        "https://byjus.com/free-ias-prep/political-ideologies-types-definitions/",
        "https://en.wikipedia.org/wiki/Ideology",
        # Liberalism (15)
        "https://en.wikipedia.org/wiki/Liberalism",
        "https://en.wikipedia.org/wiki/Classical_liberalism",
        "https://en.wikipedia.org/wiki/Social_liberalism",
        "https://en.wikipedia.org/wiki/Economic_liberalism",
        "https://en.wikipedia.org/wiki/Neoliberalism",
        "https://en.wikipedia.org/wiki/Neoclassical_liberalism",
        "https://en.wikipedia.org/wiki/History_of_liberalism",
        "https://plato.stanford.edu/entries/liberalism/",
        "https://www.liberal-international.org/",
        "https://www.britannica.com/topic/liberalism",
        "https://en.wikipedia.org/wiki/Liberalism_in_the_United_States",
        "https://en.wikipedia.org/wiki/Modern_liberalism_in_the_United_States",
        "https://en.wikipedia.org/wiki/Liberalism_in_Europe",
        "https://en.wikipedia.org/wiki/Liberal_democracy",
        "https://en.wikipedia.org/wiki/Cultural_liberalism",
        # Conservatism (15)
        "https://en.wikipedia.org/wiki/Conservatism",
        "https://en.wikipedia.org/wiki/Fiscal_conservatism",
        "https://en.wikipedia.org/wiki/Social_conservatism",
        "https://en.wikipedia.org/wiki/Cultural_conservatism",
        "https://en.wikipedia.org/wiki/Traditionalist_conservatism",
        "https://en.wikipedia.org/wiki/Neoconservatism",
        "https://en.wikipedia.org/wiki/Paleoconservatism",
        "https://en.wikipedia.org/wiki/Libertarian_conservatism",
        "https://en.wikipedia.org/wiki/Liberal_conservatism",
        "https://en.wikipedia.org/wiki/Authoritarian_conservatism",
        "https://en.wikipedia.org/wiki/National_conservatism",
        "https://en.wikipedia.org/wiki/Conservatism_in_the_United_States",
        "https://en.wikipedia.org/wiki/Conservatism_in_the_United_Kingdom",
        "https://plato.stanford.edu/entries/conservatism/",
        "https://www.britannica.com/topic/conservatism",
        # Socialism (15)
        "https://en.wikipedia.org/wiki/Socialism",
        "https://en.wikipedia.org/wiki/History_of_socialism",
        "https://en.wikipedia.org/wiki/Democratic_socialism",
        "https://en.wikipedia.org/wiki/Social_democracy",
        "https://en.wikipedia.org/wiki/Communism",
        "https://en.wikipedia.org/wiki/Marxism",
        "https://en.wikipedia.org/wiki/Libertarian_socialism",
        "https://en.wikipedia.org/wiki/Utopian_socialism",
        "https://en.wikipedia.org/wiki/Leninism",
        "https://en.wikipedia.org/wiki/Marxism%E2%80%93Leninism",
        "https://en.wikipedia.org/wiki/Trotskyism",
        "https://en.wikipedia.org/wiki/Maoism",
        "https://www.socialistinternational.org/",
        "https://plato.stanford.edu/entries/socialism/",
        "https://www.britannica.com/topic/socialism",
        # Libertarianism (15)
        "https://en.wikipedia.org/wiki/Libertarianism",
        "https://en.wikipedia.org/wiki/History_of_libertarianism",
        "https://en.wikipedia.org/wiki/Right-libertarianism",
        "https://en.wikipedia.org/wiki/Left-libertarianism",
        "https://en.wikipedia.org/wiki/Minarchism",
        "https://en.wikipedia.org/wiki/Anarcho-capitalism",
        "https://en.wikipedia.org/wiki/Objectivism_(Ayn_Rand)",
        "https://en.wikipedia.org/wiki/Libertarianism_in_the_United_States",
        "https://en.wikipedia.org/wiki/Voluntaryism",
        "https://en.wikipedia.org/wiki/Anarchism",
        "https://www.libertarianism.org/",
        "https://plato.stanford.edu/entries/libertarianism/",
        "https://www.britannica.com/topic/libertarianism",
    ]

    crawler = WebCrawler(
        seeds=seeds,
        max_pages=1000,
        concurrent_tasks=50,
        incremental_interval=1000
    )
    start = time.time()
    asyncio.run(crawler.crawl())
    print(f"Finished crawling {crawler.pages_crawled} pages in {(time.time()-start)/60:.2f} mins")

if __name__ == "__main__":
    main()