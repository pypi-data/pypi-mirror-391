## Function that we'll run and unit test on
def sample_func(x: str):
    y = x[::-1]
    print("The new value is: ", y)
    return y

## Run it
if __name__ == "__main__":
    sample_func("sample")