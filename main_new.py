import asyncio
from prime_normal import *

async def process_url(url, keyword, semaphore):
    """
    A wrapper to process a single URL with a semaphore to limit concurrency.
    """
    async with semaphore:
        print(f"Processing {url}...")
        # The 'html' function from p_extract_01 is synchronous.
        # To avoid blocking the event loop, we run it in a thread pool executor.
        loop = asyncio.get_running_loop()
        try:
            # The html function returns a tuple (context, date)
            context, date = await loop.run_in_executor(
                None,  # Uses the default ThreadPoolExecutor
                html,
                url,
                keyword
            )
            print(f"Finished processing {url}. Date found: {date}")
            return url, context, date
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
            return url, None, None

async def main():
    """
    Main function to run multiple URL extractions concurrently.
    """
    # Example list of URLs and a keyword to search for
    urls = [
        "https://www.birlasoft.com/services/enterprise-products/aws",
        "https://www.google.com",
        "https://www.python.org",
        "https://www.djangoproject.com/",
        "https://flask.palletsprojects.com/",
        "https://fastapi.tiangolo.com/",
        "https://docs.aiohttp.org/en/stable/",
    ]
    keyword = "AWS"
    concurrency_limit = 5
    semaphore = asyncio.Semaphore(concurrency_limit)

    tasks = [process_url(url, keyword, semaphore) for url in urls]

    results = await asyncio.gather(*tasks)

    print("\n--- All URLs processed ---")
    for url, context, date in results:
        if context and date:
            print(f"\nURL: {url}")
            print(f"Date: {date}")
            print(f"Context found for '{keyword}':")
            for i, chunk in enumerate(context, 1):
                print(f"  Chunk {i}: {chunk[:100]}...") # Print first 100 chars
        else:
            print(f"\nCould not retrieve context or date for {url}")


if __name__ == "__main__":
    # To run the async main function
    asyncio.run(main())
