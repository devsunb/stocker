import logging
import os
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait

from stocker.util.stock_data import StockData
from stocker.util.timer import Timer


class BotError(RuntimeError):
    pass


class Bot:
    site_name = ''
    logger = logging.getLogger('stocker')

    def __init__(self, config, outputs):
        self.config = config
        self.outputs = outputs
        general_config = self.config['GENERAL']
        chromedriver_config = general_config['CHROMEDRIVER']
        self.chromedriver_path = chromedriver_config['PATH']
        self.timeout = chromedriver_config['TIMEOUT']
        self.window_size = chromedriver_config['WINDOW_SIZE']
        self.chrome_options = chromedriver_config['OPTION']
        self.init_scripts = chromedriver_config['INIT_SCRIPT']
        self.driver, self.wait = self.init_chromedriver()
        self.data_path = general_config['DATA_PATH']
        self.site_config = self.config['SITE']

    def init_chromedriver(self):
        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"
        caps["pageLoadStrategy"] = "eager"
        # caps["pageLoadStrategy"] = "none"

        options = webdriver.ChromeOptions()
        for o in self.chrome_options:
            options.add_argument(o)

        driver = webdriver.Chrome(self.chromedriver_path, desired_capabilities=caps, chrome_options=options)
        wait = WebDriverWait(driver, self.timeout)

        for s in self.init_scripts:
            driver.execute_script(s)
        driver.set_window_size(*self.window_size)
        return driver, wait

    def get_data_path(self, path):
        return os.path.join(self.data_path, path)

    def login(self):
        return

    def loop(self, recipe):
        product_number = recipe['PRODUCT_NUMBER']
        product_name = recipe['PRODUCT_NAME']
        term = recipe['TERM']
        timeout = recipe['TIMEOUT']
        stock_data = StockData(self.site_name, product_number, product_name)
        t = Timer(timeout)
        t.start()
        while not t.is_timeout():
            stock_data['time'] = datetime.utcnow()
            in_stock = self.buy(product_number)
            stock_data['in_stock'] = in_stock
            for o in self.outputs:
                o.insert(stock_data)
            if in_stock:
                self.logger.info('Buy success')
                return
            self.logger.info('Buy failed. Sleep in term: {} second(s)'.format(term))
            sleep(term)

    def buy(self, product_number):
        return 0

    def is_sold_out(self):
        return True

    def pay(self):
        return

    def get_price(self):
        return ''

    def get_header(self):
        return ''

    def log_header_price(self):
        price = self.get_price()
        header = self.get_header()
        self.logger.info('Buy {}: {}'.format(header, price))

    def quit(self):
        self.driver.quit()
        for o in self.outputs:
            o.close()
