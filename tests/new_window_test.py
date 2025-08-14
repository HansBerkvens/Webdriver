from Webdriver import Driver, open_drivers
from time import sleep

driver = Driver()

driver.visit('https://www.transfermarkt.co.uk/tobias-werner/profil/spieler/26878')
driver.visit_new_window('https://sofifa.com/player/177100/tobias-werner/190045')

sleep(10)
driver.switch_to_window(0)
sleep(5)
driver.switch_to_window(1)
sleep(5)
driver.switch_to_window(0)
sleep(10)
