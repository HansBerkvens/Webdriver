from .webdriver import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from threading import Thread
from queue import Queue


def open_drivers(amt_drivers: int, new_driver_startup_time: float = 1.0, **kwargs) -> list[Driver] | Driver:
    print(f'opening {amt_drivers} drivers')

    if amt_drivers == 1:
        return Driver(offset_index=0, **kwargs)
    def create_driver(queue: Queue, index: int):
        sleep((1+index) * new_driver_startup_time)
        driver = Driver(offset_index=index, **kwargs)
        queue.put(driver)
    queue = Queue()
    threads = []

    for i in range(amt_drivers):
        t = Thread(target=create_driver, args=(queue, i))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    drivers = [queue.get() for _ in range(amt_drivers)]

    # check if all instances are independent
    window_handles = set()
    for d in drivers:
        window_handles.add(tuple(d.driver.window_handles))

    # add logic if instances are referring to the same driver
    if len(window_handles) != amt_drivers:
        print(f'Multiple Driver instances are sharing the same driver, retrying with increased stagger time for independence.')
        # kill available drivers
        for d in drivers:
            d.quit()

        # re-try with longer staggering time
        return open_drivers(amt_drivers, new_driver_startup_time+1.5, **kwargs)

    return drivers



