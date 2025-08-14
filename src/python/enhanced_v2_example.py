PURPOSE: Batch filter & process items with contracts, timeout, retry
INPUTS: items:list[int], limiter:int
OUTPUTS: results:list

assert isinstance(items, (list,)), 'TYPE check failed for items: expected list'
assert isinstance(limiter, (int,)), 'TYPE check failed for limiter: expected int'
assert items is not None and len(items) > 0, 'REQUIRES failed: items is not None and len(items) > 0'
assert limiter > 0, 'REQUIRES failed: limiter > 0'

@with_timeout(5)
@with_retry(2, 1.2)
def process_items(items, limiter):
    results = []
    try:
        # PARALLEL FOR EACH item IN items
with ThreadPoolExecutor() as __exec:
    list(__exec.map(lambda __item: __parallel_body(__item), items))
            # __item is the loop variable inside the parallel body
            processed = process(__item)
            if processed.score >= limiter:
                results.append(processed)
                else:
                continue
        except Exception:
        handle_error('processing_failed')
    
    ENSURES: len(results) <= len(items)
    return results
