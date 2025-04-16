from .webdriver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from threading import Thread
from queue import Queue


def open_drivers(amt_drivers: int, new_driver_startup_time: float = 1.0, **kwargs) -> list[Driver] | Driver:
    def create_driver(queue: Queue, index: int):
        sleep((1+index) * new_driver_startup_time)
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



