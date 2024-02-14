from collections import Counter


class DuplicateError(Exception):
    pass


def identify_duplicates(results: list[dict], key: str) -> list[dict]:
    """Identify duplicates for further examination.

    Args:
        results (list): List of results to check for duplicates.
        key (str): Key representing the duplicated key: value pair.

    Returns:
        list[dict]: Duplicated items from input list.
    """    
    url_list = (r.get(key) for r in results)
    c = Counter(url_list)
    dup_items = [r for r in results if r.get(key) in [k for k, v in c.items() if v > 1]]
    return dup_items


def remove_duplicates(results: list[dict], key: str):
    """Filter out duplicates from list[dict] based on a key: value pair 
    ([source](https://www.geeksforgeeks.org/python-remove-duplicate-dictionaries-characterized-by-key/)).

    Args:
        results (list): List of results to filter out duplicates.
        key (str): Key representing the duplicated key: value pair.

    Returns:
        tuple[list, int]: deduplicated list, number of duplicates removed
    """    
    initial_count = len(results)
    
    # remove duplicates
    unique = set()
    res = []
    for r in results:

        # testing for already present value
        if r.get(key) not in unique:
            res.append(r)
            
            # adding to set if new value
            unique.add(r[key])
    
    filtered_count = len(res)
    return res, (initial_count - filtered_count)


def process_duplicates(results: list[dict], key: str, how: str):
    duplicates = identify_duplicates(results, key=key)
    count_dups = len(duplicates)
    # raise, drop, tag
    if count_dups > 0:
        if not isinstance(how, str):
            raise TypeError
        match how:
            case "raise":
                raise DuplicateError(f"Results contain {count_dups} duplicate values based on {key}.")
            case "flag":
                duplicates_list = [doc.get("document_number", "") for doc in duplicates]
                results = [{**doc, **{"duplicate": True}} if doc.get("document_number") in duplicates_list else {**doc, **{"duplicate": False}} for doc in results]
            case "drop":
                results, removed = remove_duplicates(results, key=key)
                print(f"Removed {removed} duplicates")
            case _:
                raise ValueError
    return results
