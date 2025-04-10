from .webdriver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from threading import Thread
from queue import Queue

STARTUP_SECONDS_PER_DRIVER: float = 1.0


def open_drivers(amt_drivers: int, **kwargs) -> list[Driver] | Driver:
    def create_driver(queue: Queue, index: int):
        sleep((1+index) * STARTUP_SECONDS_PER_DRIVER)
        driver = Driver(offset_index=index, **kwargs)
        queue.put(driver)

    print(f'opening {amt_drivers} drivers')

    if amt_drivers == 1:
        return Driver(offset_index=0, **kwargs)

    queue = Queue()
    threads = []

    for i in range(amt_drivers):
        t = Thread(target=create_driver, args=(queue, i))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    drivers = [queue.get() for _ in range(amt_drivers)]
    return drivers



