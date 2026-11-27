import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

import requests

BASE_DIR = Path(__file__).resolve().parent
PAPERS_DIR = BASE_DIR / "papers"
DATA_DIR = BASE_DIR / "data"
QUEUE_FILE = DATA_DIR / "institution_queue.jsonl"

PAPERS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "OLED-DOI-Downloader/0.1 (personal academic literature workflow)"
}

def normalize_doi(doi: str) -> str:
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.strip()

def safe_filename(text: str) -> str:
    text = re.sub(r'[\\/:*?"<>|]+', "_", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:180] if text else "paper"

def get_openalex_work(doi: str) -> dict:
    url = f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='')}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 404:
        raise RuntimeError("OpenAlex 中未找到这个 DOI。")
    r.raise_for_status()
    return r.json()

def collect_pdf_candidates(work: dict):
    candidates = []
    for key in ("best_oa_location", "primary_location"):
        loc = work.get(key) or {}
        if loc.get("pdf_url"):
            candidates.append(loc["pdf_url"])
    for loc in work.get("locations") or []:
        if loc and loc.get("pdf_url"):
            candidates.append(loc["pdf_url"])

    # 去重并保持顺序
    seen = set()
    out = []
    for url in candidates:
        if url and url not in seen:
            seen.add(url)
            out.append(url)
    return out

def download_pdf(url: str, output: Path) -> bool:
    try:
        with requests.get(url, headers=HEADERS, timeout=60, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            ctype = (r.headers.get("Content-Type") or "").lower()
            first = b""
            with open(output, "wb") as f:
                for i, chunk in enumerate(r.iter_content(chunk_size=1024 * 256)):
                    if not chunk:
                        continue
                    if i == 0:
                        first = chunk[:8]
                    f.write(chunk)

            # 简单验证：PDF 文件通常以 %PDF 开头
            if "pdf" not in ctype and not first.startswith(b"%PDF"):
                output.unlink(missing_ok=True)
                return False
            return True
    except Exception:
        output.unlink(missing_ok=True)
        return False

def queue_for_institution(work: dict, doi: str):
    record = {
        "doi": doi,
        "title": work.get("title"),
        "year": work.get("publication_year"),
        "openalex_id": work.get("id"),
        "doi_url": f"https://doi.org/{doi}",
        "status": "institution_required"
    }
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def main():
    if len(sys.argv) >= 2:
        doi = " ".join(sys.argv[1:])
    else:
        doi = input("请输入 DOI：").strip()

    doi = normalize_doi(doi)
    if not doi:
        print("没有输入 DOI。")
        sys.exit(1)

    print(f"\n[1/3] 查询 DOI: {doi}")
    try:
        work = get_openalex_work(doi)
    except Exception as e:
        print(f"查询失败：{e}")
        sys.exit(1)

    title = work.get("title") or doi
    print(f"标题：{title}")

    candidates = collect_pdf_candidates(work)
    if candidates:
        print(f"[2/3] 找到 {len(candidates)} 个开放获取 PDF 候选地址。")
        base_name = safe_filename(f"{work.get('publication_year') or ''} - {title}")
        output = PAPERS_DIR / f"{base_name}.pdf"

        for i, url in enumerate(candidates, 1):
            print(f"尝试 {i}/{len(candidates)}：{url}")
            if download_pdf(url, output):
                print(f"[3/3] 下载成功：{output.relative_to(BASE_DIR)}")
                return

        print("开放获取地址存在，但自动下载均失败。")
    else:
        print("[2/3] OpenAlex 未返回可直接下载的开放获取 PDF。")

    record = queue_for_institution(work, doi)
    print(f"[3/3] 已加入机构权限队列：{QUEUE_FILE.relative_to(BASE_DIR)}")
    print(f"DOI 页面：{record['doi_url']}")
    print("说明：脚本不会绕过 CARSI、CAPTCHA 或出版社反爬；需要机构权限的文献留待后续集中处理。")

if __name__ == "__main__":
    main()
