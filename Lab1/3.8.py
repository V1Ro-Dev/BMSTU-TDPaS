import inspect


def create_file(param_name):
    frame = inspect.currentframe().f_back
    res = ""
    for name, value in frame.f_locals.items():
        if value is param_name:
            res = name
            break

    if res:
        with open(f"{res}.txt", "w") as file:
            file.write(f"test")


a = 5
create_file(a)
