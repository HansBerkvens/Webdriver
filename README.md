# WebDriver Package

This package provides a custom Selenium-based driver with additional features for managing proxies, handling headless browsing, and automating tasks with greater flexibility. It is specifically designed for use with the **SeleniumBase** driver and includes VPN functionality using **TunnelBear** and support for multiple browser configurations.

## Features

- **Custom Driver**: Extends SeleniumBase `Driver` with enhanced features.
- **Proxy Support**: Supports proxies like TunnelBear and user:pass@host:port type proxies
  - Tunnelbear proxies can be activated calling `driver = Driver(version='bear')`. This requires `TUNNELBEAR_LOGIN` and `TUNNELBEAR_PW` in a `.env` file. These proxies can only run in `uc=False` and `headless=False` instances.
  - Alternatively, a proxy of the form `user:pass@host:port` can be used. This requires a `.env` with `PROXY_USERNAME`, `PROXY_PASSWORD`, `PROXY_HOST` and `PROXY_PORT`. This is called with `Driver(use_proxy=True)`. 
- **Headless Mode**: Can operate in headless mode. `driver = Driver(headless=True)`
- **Tab Handling**: Open and manage browser tabs.
- **Element Interactions**: Functions like `find_element`, `click_element`, `scroll_into_view`, and more.
  - `wait_for` incorporates WebDriverWait and EC. Use `click=True` to click element after it was found. Use `on_error='refresh'` to refresh the page on a timeout and try again.
  - `visit` combines `driver.get(url)` with `wait_for`
  - `click_element` searches for an element and clicks it. If `index` is not None it will use `find_elements(...)` and click the index'th element in the list. If `driver_like_object` is not None it will use `object.find_element(...)` instead of `driver.find_element(...)`. After finding the element it uses JavaScript to scroll the element into view and click.
  - `visit_new_window` allows the driver to open a url in a new window. Especially handy for some troublesome sites.

## Installation

To install the package directly from GitHub, run:

```bash
pip install git+https://github.com/HansBerkvens/Webdriver.git@main
```
# .env example file

# Proxy credentials
- PROXY_USERNAME=your_proxy_username
- PROXY_PASSWORD=your_proxy_password
- PROXY_HOST=proxy_host_address
- PROXY_PORT=proxy_port_number

# Tunnelbear login
- TUNNELBEAR_LOGIN=your_username
- TUNNELBEAR_PW=your_password
