import asyncio
import time
from asyncio.coroutines import iscoroutinefunction


def cost_time(func):
    def wrapper(*args, **kwargs):
        timeStart = time.perf_counter()
        result = func(*args, **kwargs)
        print(f'func {func.__name__} cost time:{time.perf_counter() - timeStart:.8f} s')
        return result

    async def wrapper_async(*args, **kwargs):
        timeStart = time.perf_counter()
        result = await func(*args, **kwargs)
        print(f'func {func.__name__} cost time:{time.perf_counter() - timeStart:.8f} s')
        return result

    if iscoroutinefunction(func):
        return wrapper_async
    else:
        return wrapper


@cost_time
def test():
    print('func start')
    time.sleep(1)
    print('func end')


@cost_time
async def test_async():
    print('async func start')
    await asyncio.sleep(1)
    print('async func end')


if __name__ == '__main__':
    test()
    asyncio.get_event_loop().run_until_complete(test_async())
