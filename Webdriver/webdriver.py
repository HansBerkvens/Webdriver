import atexit
from contextlib import suppress
from datetime import datetime
from dotenv import load_dotenv
import os
import importlib.resources
import selenium.common.exceptions as exceptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from seleniumbase import Driver as SelBaseDriver
from time import sleep

NEW_TAB_WAIT = 1.5
TIMEOUT_RETRY = 60
DRIVER_WAIT_TIMEOUT = 60
Bet365_NEW_TAB_SLEEP_BACKUP = NEW_TAB_WAIT + 2

POST_ACTION_SLEEP: float = 0.  # for slower operating systems: add a sleep after finding/clicking an element


def now() -> str:
    return f'{datetime.now().strftime("%H:%M:%S")}\t\t'


def specify_version(version) -> tuple[bool, bool, bool]:
    version = version.lower()
    if version == 'headless':
        return True, True, False
    if version == 'tunnelbear' or version == 'tunnel' or version == 'bear':
        return False, False, True
    if version == 'smartproxy':
        return True, True, True
    if version == 'u' or version == 'undetected' or version == 'uc':
        return True, False, False
    raise ValueError(f'Driver init function was called with {version = }, but this is not a recognized value')


class Driver:

    def __init__(
            self,
            version: str | None = None,  # string representing a default version; see specify_version function
            *,
            uc: bool = True,  # open in undetected mode
            headless: bool = False,  # open in headless mode
            use_proxy: bool = False,  # use a proxy; requires credentials
            offset_index: int = 0,  # offset when opening multiple browsers, index browsers 0, 1, 2, etc.
            offset_amount: int = 20,  # pixels to offset different drivers by
            offset_right: bool = False,  # offset new windows to the right or left
            dotenv_file_name: str = '.env',  # where to find proxy credentials
            save_bet365_fails: bool = True,  # save an image of the page when bet365 fails to load twice
            monitor: int = 0,  # monitor to open the window on, -1 for left, 0 for main monitor, 1 for right
            vpn_country: str = 'Mexico',  # country to let tunnelbear vpn to
    ):
        atexit.register(self.printquit)

        self.save_bet365_fails = save_bet365_fails
        if version is not None:
            uc, headless, use_proxy = specify_version(version)

        print(f'opening {"'uc' " if uc else ""}{"'headless' " if headless else ""}{"'with proxy' " if use_proxy else ""} driver (idx={offset_index})')

        if use_proxy and not uc and not headless:
            load_dotenv(dotenv_file_name)
            extension_path = importlib.resources.path("Webdriver", "TunnelBear.crx")
            with extension_path as path:
                self.driver = SelBaseDriver(
                    headless=False,
                    uc=False,
                    extension_zip=str(path),
                    block_images=True
                )
            if offset_right:
                offset_amount *= -1
            self.reposition(offset_index, offset_amount)
            self.log_in_to_proxy()
        else:
            if use_proxy:
                load_dotenv(dotenv_file_name)
                proxy = (f'{os.getenv('PROXY_USERNAME')}:{os.getenv('PROXY_PASSWORD')}@'
                         f'{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}')
            else:
                proxy = None
            self.driver = SelBaseDriver(
                headless=headless,
                uc=uc,
                proxy=proxy,
                block_images=True
            )

            if offset_right:
                offset_amount *= -1
            self.reposition(offset_index, offset_amount)

    def reposition(self, offset_index: int = 0, offset_amount: int = 20):
        try:
            self.driver.maximize_window()
        except:
            pass
        x, y = self.driver.get_window_position().values()
        width, height = self.driver.get_window_size().values()
        self.driver.set_window_size(width=width, height=height)
        self.driver.set_window_position(x=x - offset_index * offset_amount,
                                        y=y + abs(offset_index * offset_amount))

    def find_element(self, *args, **kwargs):
        result = self.driver.find_element(*args, **kwargs)
        sleep(POST_ACTION_SLEEP)
        return result

    def find_elements(self, *args, **kwargs):
        result = self.driver.find_elements(*args, **kwargs)
        sleep(POST_ACTION_SLEEP)
        return result

    def log_in_to_proxy(self, country: str = 'Mexico'):
        # go to tunnelbear login
        self.visit('https://www.tunnelbear.com/account/signup?v=3.6.2', (By.XPATH, '//button[@class="plain link"]'), new_window=True)
        self.wait_for((By.XPATH, '//button[@class="plain link"]'), click=True)

        # enter credentials
        self.find_element(By.XPATH, '//input[@name="email"]').send_keys(os.getenv('TUNNELBEAR_LOGIN'))
        sleep(0.1)
        self.find_element(By.XPATH, '//input[@name="password"]').send_keys(os.getenv('TUNNELBEAR_PW'))
        sleep(0.1)
        self.find_element(By.XPATH, '//button[@type="submit"]').click()

        # wait for login to complete
        self.wait_for((By.XPATH, '//button[@type="submit"]/div[@class="button-state checkmark"]'))
        sleep(3)
        self.refresh()
        sleep(1.5)
        self.wait_for((By.XPATH, '//div[@class="table-row"]/div[@class="item"]'))
        sleep(2)

        # access extension as website
        self.visit(r'chrome-extension://omdakjcmkglenbhjadbccaookpfjihpa/popup.html', new_window=False)
        sleep(1)
        # self.visit(r'chrome-extension://omdakjcmkglenbhjadbccaookpfjihpa/popup.html', new_window=True)
        # sleep(0.5)

        # click country selection
        self.find_element(By.ID, 'country-container').click()
        sleep(0.5)

        # click desired country
        for c in self.find_elements(By.XPATH, '//ul[@class="menu-list"]/li'):
            if country in c.text:
                c.click()
                break

        # click button to activate the VPN
        self.wait_for((By.ID, 'on-off-toggle-container'), click=True)
        sleep(0.5)

    def refresh(self):
        return self.driver.refresh()

    def page_source(self):
        return self.driver.page_source

    def scroll_up(self):
        self.driver.execute_script('window.scrollBy(0, -20000)')
        sleep(0.5)
        self.driver.execute_script('window.scrollBy(0, -20000)')

    def execute_script(self, s: str, element: WebElement = None):
        try:
            return self.driver.execute_script(s)
        except exceptions.JavascriptException:
            return self.driver.execute_script(s, element)

    def assert_element(self, element) -> WebElement:
        if isinstance(element, WebElement):
            return element
        if isinstance(element, tuple):
            return self.find_element(*element)

    def wait_for(self, element: tuple[str, str], wait_seconds: float = 10, click: bool = False, on_error: str = 'raise', wait_interactable=False) -> None:
        try:
            if wait_interactable:
                element_present = EC.element_to_be_clickable(element)
            else:
                element_present = EC.presence_of_element_located(element)
            WebDriverWait(self.driver, wait_seconds).until(element_present)
            sleep(POST_ACTION_SLEEP)
            if click:
                self.click_element(element)
                sleep(POST_ACTION_SLEEP)
                # self.find_element(*element).click()
        except (TimeoutError, exceptions.TimeoutException):
            if on_error == 'raise':
                raise exceptions.TimeoutException
            if on_error == 'refresh':
                self.refresh()
                sleep(POST_ACTION_SLEEP)
                self.wait_for(element, wait_seconds, click, on_error='raise')

    def execute_script_and_click(self, script, element: WebElement) -> bool:
        if script:
            self.execute_script(script, element)
            sleep(POST_ACTION_SLEEP)
        with suppress(Exception):
            element.click()
            sleep(POST_ACTION_SLEEP)
            return True
        return False

    def click_element(self, element=None, driver_like_object=None, print_stuff: bool = False, index=None) -> bool:
        if print_stuff:
            try:
                print('clicking', element.text.split('\n'))
            except:
                print('clicking', element)

        if isinstance(element, tuple):
            try:
                if driver_like_object:
                    if index:
                        element = driver_like_object.find_elements(*element)[index]
                    else:
                        element = driver_like_object.find_element(*element)
                else:
                    if index:
                        element = self.find_elements(*element)[index]
                    else:
                        element = self.find_element(*element)
            except Exception as e:
                return False

        for script in ['',
                       'window.scrollBy(0, -2000)',
                       'window.scrollBy(0, 3000)',
                       "arguments[0].scrollIntoView();"]:
            if self.execute_script_and_click(script, element):
                return True

        return False

    def visit_new_window(self, url):
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        sleep(NEW_TAB_WAIT)
        if len(self.driver.window_handles) > 3:
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])
        sleep(NEW_TAB_WAIT)

    def visit_365_url(self, url: str,
                      wait_element: tuple[str, str] = None,
                      bet365sleep: float = NEW_TAB_WAIT,
                      on_error: str = 'retry') -> bool:

        # bet 365 returns an empty page when using driver.get(url), opening a new tab seems to gets around this problem
        self.visit_new_window(url)
        sleep(bet365sleep)

        try:
            self.wait_for((By.CLASS_NAME, 'gl-MarketGroup '))

        except:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            if on_error == 'retry':
                print(f'bet365 url would not load, retrying {url}')
                return self.visit_365_url(url, wait_element, Bet365_NEW_TAB_SLEEP_BACKUP, 'raise')
            if on_error == 'raise':
                if self.save_bet365_fails:
                    try:
                        self.driver.save_screenshot(f"bet365fail {datetime.now().strftime("%Y%m%d %H%M%S")}.png")
                    except:
                        pass  # no big deal if the screenshot fails
                print('bet365 url would not load again, returning False', url)
                return False
        return True

    def visit(
            self,
            url: str,
            wait_element: tuple[str, str] = None,
            wait_timeout: float | int | None = None,
            new_window: bool = False
    ) -> bool:
        # go to site, either directly or through new window
        print(f'{now()}visiting {url}')
        if 'bet365.' in url:
            return self.visit_365_url(url, wait_element)
        else:
            if new_window:
                self.visit_new_window(url)
            else:
                self.driver.get(url)

        # if there is no wait element, return True and quit function
        if wait_element is None:
            return True

        try:
            self.wait_for(wait_element, DRIVER_WAIT_TIMEOUT if wait_timeout is None else wait_timeout, on_error='refresh')
            return True
        except exceptions.TimeoutException:
            print('loading page timed out', url)
        return False

    def scroll_into_view(self, element):
        self.execute_script("arguments[0].scrollIntoView();", element)
        sleep(0.3)
        self.execute_script("arguments[0].scrollIntoView();", element)

    def signalquit(self, signum, frame):
        print(f'Driver instance was interrupted, closing instance.')
        self.quit()
        raise KeyboardInterrupt

    def printquit(self):
        print('Driver instance was not closed in code, closing using atexit.')
        self.driver.quit()

    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    driver = Driver(uc=True, use_proxy=True)
