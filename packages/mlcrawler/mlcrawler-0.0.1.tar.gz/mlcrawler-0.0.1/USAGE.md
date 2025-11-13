# Example usage scenarios

## URL fetcher

- URLs to fetch are in a Queue (with metadata like tries, last-try)
- Async-based workers pick individual items from the queue for processing
  - Record the URL in a shared Registry as in-progress to avoid duplication
  - Cache-aware fetch
  - Extract outbound links (feed back into the Queue)
  - Filter and save in the output format
  - On error
    - if tries is exceeded mark in the Registry as failed
    - else return the URL into the Queue and remove from the Registry
  - On success mark as completed in the Registry 
- Once the Queue is empty and no workers are running -> exit

## Cache-aware URL fetch

- Single URL processing with caching
- Fetched URLs cached unmodified in .cache/{host}/{cache-path}
  where {cache-path} is a sha256-based hash of the URL formatted as {hash[0]}/{hash[1]}/{hash[2:]}
- Metadata are cached in the same .cache/{host}/{cache-path}.meta.json and must include the requested URL, date, response headers, etc
- Responses without a body (e.g. 300-class redirects or 400-class errror) should still be cached as Metadata-only,
  500-class internal error responses should not be cached
- Requests to fetch URLs must consult the cache first
- Two modes are supported:
  - exists - if a matching cached file exists it is returned to the caller directly from the cache (incl metadata)
  - conditional - use the cached headers (etag, last-modified, etc) to run a
    conditional GET, if a new version is returned update the cache and return to
    the caller, otherwise return the cached data to the caller.
- All is async for parallel operation

## Extract outbound links

- Extract links from the document ("a href"-only)
- Prepend the host name or base-url where required, resolve relative ones
- Filter out unwanted ones (e.g. cross-host, cross-domain, dynamic with "?..", "#anchor")
- For each URL consult the Registry if it's a new URL
- If yes insert into the Queue and mark as Queued in the Registry

## Output processing

- Output files are saved under ./output/{host}/{path}/{path}/{file}.{ext}
- With metadata in ./output/{host}/{path}/{path}/{file}.meta.json
- Convert non-UTF-8 to UTF-8
- Apply input filters based on the input format:
  - html - remove <script>, <style>, <svg>, <nav> tags from source html
- Convert to output format:
  - markdown - use markdownify

## URL Registry

- Keep track of URLs:
  - queued / in-progress / completed / failed
  - additional metadata like number of tries remaining
  - last-try timestamp for implementing exponential backoff
- Shared data structure for all workers
- push() must fail if the URL already exists in the registry (in any state)
- pop() should return a queued URL
- update() should be used to change between states
- Must be thread safe / concurrency safe

## Sitemap processing

- Extract URLs from sitemap.xml and linked sub-sitemaps
- Push them to the Registry

## Download specified pages

mlcrawler --url https://httpbin.org --url https://httpbin.org/anything/data.json

Effects:
- Download and cache the two URLs

## Crawl from specified page

mlcrawler --url https://httpbin.org --crawl [--max-depth N] [--max-pages N]

Effects:
- Download the URL provided
- Extract a list of links into the queue

## Crawl from a sitemap

mlcrawler --sitemap https://httpbin.org/sitemap.xml

Effects:
- 