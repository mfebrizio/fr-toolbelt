import time
from .tests import ALL_TESTS

if __name__ == "__main__":

    # profile time elapsed
    start = time.process_time()
    
    # run test suite
    for func in ALL_TESTS:
        func()
    print("Tests complete.")

    # calculate time elapsed
    stop = time.process_time()
    print(f"CPU time: {stop - start:0.1f} seconds")
