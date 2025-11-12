# lazy-main

Generalized framework for main loop function.

## Installation

```sh
pip install lazy-main
```

## How to Use

```py
from lazy_main import LazyMain

def main(*args, **kwargs):
    print("Hello World!")

def error_handler(exception):
    print("An error occurred!", exception)

if __name__ == "__main__":
    LazyMain(
        main=main,
        error_handler=error_handler, # This is optional.
        sleep_min=3,
        sleep_max=5,
        print_logs=True,
        loop_count=-1, # -1 Means it will loop infinitely.
    ).run()
```

Some aliases are also provided for `loop_count`.

```py
...

LazyMain(
    ...
    # Sets `loop_count` to 1 if `True`.
    # Sets `loop_count` to -1 if `False`.
    # Does nothing if `None`.
    run_once=True,
    ...
)


# Or...

LazyMain(
    ...
    # Sets `loop_count` to -1 if `True`.
    # Sets `loop_count` to 1 if `False`.
    # Does nothing if `None`.
    run_forever=True,
    ...
)

...
```

You can also pass arguments to the `main` function.

```py
from lazy_main import LazyMain

def main(*args, **kwargs):
    print(kwargs["hello"]) # World!

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run(
        hello="World!",
    )
```

Returning `True` will print the total elapsed time.

```py
from lazy_main import LazyMain

def main():
    return True

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run() # Done in 0.10s.
```

If you don't like the logs, you can disable it.

```py
from lazy_main import LazyMain

...

if __name__ == "__main__":
    LazyMain(
        ...
        print_logs=False,
        ...
    ).run()

...
```

Returning `Terminate` will terminate the loop.

```py
from lazy_main import LazyMain, Terminate

def main():
    return Terminate

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run()

    print("I'm free!")
```

You can also use a generator for the return value.

```py
from lazy_main import LazyMain, Terminate

def main():
    for i in range(10):
        if i == 5:
            yield Terminate

if __name__ == "__main__":
    LazyMain(
        main=main,
    ).run()

    print("I'm free!")
```

You can also provide dynamic kwargs via iteration.

```py
from lazy_main import LazyMain

def main(*args, **kwargs):
    print(kwargs["hello"]) # 0, 1, 2, 3, ...

if __name__ == "__main__":
    i = 0

    for loop in LazyMain(
        main=main,
    ):
        loop(
            hello=i,
        )

        i += 1
```
