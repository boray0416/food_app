from duckduckgo_search import DDGS

try:
    print("Testing DDGS...")
    with DDGS() as ddgs:
        results = list(ddgs.text("麥當勞 優惠", max_results=2))
        print(f"Results found: {len(results)}")
        for r in results:
            print(r)
except Exception as e:
    print(f"Error: {e}")
