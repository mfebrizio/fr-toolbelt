from collections import Counter


class DuplicateError(Exception):
    """Encountered an error when processing duplicates.
    """
    pass


def _get_keys_as_tuple(document: dict, keys: tuple | list) -> tuple:
    return tuple((document.get(k) for k in keys))


def identify_duplicates(results: list[dict], key: str = None, keys: tuple | list = None) -> list[dict]:
    """Identify duplicates for further examination. Either one key or multiple keys can be provided.

    Args:
        results (list): List of results to check for duplicates.
        key (str, optional): Key representing the duplicated key: value pair. Defaults to None.
        keys (tuple | list, optional): Keys representing the duplicated key: value pairs. Defaults to None.

    Returns:
        list[dict]: Duplicated items from input list.
    """
    if (key is None) and (keys is not None):
        keys_gen = (_get_keys_as_tuple(r, keys) for r in results)
        c = Counter(keys_gen)
        dup_counts = [k for k, v in c.items() if v > 1]
        dup_items = [r for r in results if tuple((r.get(k) for k in keys)) in dup_counts]
    elif (key is not None) and (keys is None):
        key_gen = (r.get(key) for r in results)
        c = Counter(key_gen)
        dup_counts = [k for k, v in c.items() if v > 1]
        dup_items = [r for r in results if r.get(key) in dup_counts]
    else:
        raise ValueError("Must pass values to either 'key' or 'keys'.")
    # return output
    return dup_items


def remove_duplicates(results: list[dict], key: str = None, keys: tuple | list = None):
    """Filter out duplicates from list[dict] based on a key: value pair 
    ([source](https://www.geeksforgeeks.org/python-remove-duplicate-dictionaries-characterized-by-key/)).
    Keeps first instance of duplicated entry.

    Args:
        results (list): List of results to filter out duplicates.
        key (str, optional): Key representing the duplicated key: value pair. Defaults to None.
        keys (tuple | list, optional): Keys representing the duplicated key: value pairs. Defaults to None.

    Returns:
        tuple[list, int]: deduplicated list, number of duplicates removed
    """    
    initial_count = len(results)
    unique = set()
    res = []
    if (key is None) and (keys is not None):  # multiple keys
        for r in results:
            key_tuples = _get_keys_as_tuple(r, keys)
            # testing for already present value
            if key_tuples not in unique:
                res.append(r)
                # adding to set if new value
                unique.add(key_tuples)
    elif (key is not None) and (keys is None):  # one key
        for r in results:
            # testing for already present value
            if r.get(key) not in unique:
                res.append(r)
                # adding to set if new value
                unique.add(r[key])
    else:
        raise ValueError("Must pass values to either 'key' or 'keys'.")
    # return output
    filtered_count = len(res)
    return res, (initial_count - filtered_count)


def flag_duplicates(
        results: list[dict], 
        duplicates: list[dict] = None, 
        key: str = None, 
        keys: tuple | list = None
    ) -> list[dict]:
    """Flag duplicate documents based one or more key: value pairs.
    """
    if duplicates is None:
        duplicates = identify_duplicates(results, key=key, keys=keys)
    if (key is None) and (keys is not None):  # multiple keys
        duplicate_pairs = [_get_keys_as_tuple(doc, keys) for doc in duplicates]
        res = [{**doc, **{"duplicate": True}} if _get_keys_as_tuple(doc, keys) in duplicate_pairs else {**doc, **{"duplicate": False}} for doc in results]
    elif (key is not None) and (keys is None):  # one key
        duplicate_pairs = [doc.get(key) for doc in duplicates]
        res = [{**doc, **{"duplicate": True}} if doc.get(key) in duplicate_pairs else {**doc, **{"duplicate": False}} for doc in results]
    else:
        raise ValueError("Must pass values to either 'key' or 'keys'.")
    # return output
    return res


def process_duplicates(
        results: list[dict], 
        how: str, 
        key: str = None, 
        keys: tuple | list = None, 
        report_drop: bool = False
    ) -> list[dict]:
    """Process duplicates based on one or more key: value pairs. Options include "raise", "flag", and "drop". 
    """
    duplicates = identify_duplicates(results, key=key, keys=keys)
    count_dups = len(duplicates)
    if count_dups > 0:
        if not isinstance(how, str):
            raise TypeError
        match how:  # match options: raise, flag, drop, wildcard
            case "raise":
                raise DuplicateError(f"Results contain {count_dups} duplicate values based on {key}.")
            case "flag":
                res = flag_duplicates(results, duplicates=duplicates, key=key, keys=keys)
            case "drop":
                res, removed = remove_duplicates(results, key=key, keys=keys)
                if report_drop:
                    print(f"Removed {removed} duplicates")
            case _:
                raise ValueError("Invalid input for 'how' parameter.")
    else:
        res = results
    return res
