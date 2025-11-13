
import typing


class Test:
    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter([1, 2, 3])


a = [1, 2, 3]
a += Test()
