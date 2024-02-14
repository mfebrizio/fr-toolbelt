from collections import Counter


class DuplicateError(Exception):
    pass


def identify_duplicates(results: list[dict], key: str) -> list[dict]:
    """Identify duplicates for further examination. If no key is provided, check for duplicate dictionaries.

    Args:
        results (list): List of results to check for duplicates.
        key (str, optional): Key representing the duplicated key: value pair. Defaults to None.

    Returns:
        list[dict]: Duplicated items from input list.
    """    
    if key is None:
        pass
        #res_list = (tuple(r) for r in results)
        #c = Counter(res_list)
        #dup_items =  [k for k, v in c.items() if v > 1]
    else:
        key_list = (r.get(key) for r in results)
        c = Counter(key_list)
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
    if key is None:  # duplicate dictionaries
        pass
        #unique = set(tuple(r.items()) for r in results)
        #print(unique)
        #res = [dict(r) for r in unique]
    else:  # duplicate keys
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


def process_duplicates(results: list[dict], how: str, key: str):
    """Process duplicates. Options include "raise", "flag", and "drop". 
    If no key is provided, process duplicate dictionaries.

    Args:
        results (list[dict]): _description_
        how (str): _description_
        key (str, optional): _description_. Defaults to None.

    Raises:
        TypeError: _description_
        DuplicateError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    """
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


if __name__ == "__main__":
     
    test_list = [{"a": d[0], "b": d[1]} for d in zip("abcdefghij", range(10))]
    test_list += test_list[0:2]
    #print(test_list)
    #print(set(tuple(r.items()) for r in test_list))
    
    res_a, count = remove_duplicates(test_list, key = "a")
    print("Removing dup key = a", res_a, count)
    
    res_all, count = remove_duplicates(test_list)
    print("Removing dup all", res_all, count)

    def sort_list_dict(results, key):
        return sorted(results, key=lambda d: d[key])
    
    print(sort_list_dict(res_a, "a") == sort_list_dict(res_all, "a"))

    test_list += [{'a': 'g', 'b': 100}]
    
    res_a, count = remove_duplicates(test_list, key = "a")
    print("Removing dup key = a", res_a, count)
    
    res_all, count = remove_duplicates(test_list)
    print("Removing dup all", res_all, count)
    
    print(sort_list_dict(res_a, "a") == sort_list_dict(res_all, "a"))
