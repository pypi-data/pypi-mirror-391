from clockitpy import measure_time, timeit

@measure_time
def test_slow_func():
    sum([i for i in range(1000000)])

test_slow_func()

# Or directly
duration, result = timeit(test_slow_func)
print(f"Duration: {duration:.5f} sec")
