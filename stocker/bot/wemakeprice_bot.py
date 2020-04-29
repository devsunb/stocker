from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from stocker.bot.bot import Bot


class WeMakePriceBot(Bot):
    site_name = 'WEMAKEPRICE'

    def __init__(self, config, output):
        super().__init__(config, output)
        wemakeprice_config = self.site_config[self.site_name]
        account_config = wemakeprice_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        urls = wemakeprice_config['URL']
        self.login_url = urls['LOGIN']
        self.product_url = urls['PRODUCT']
        self.product_number = None

    def login(self):
        self.driver.get(self.login_url)
        self.wait.until(ec.presence_of_element_located((By.ID, '_loginId'))).send_keys(self.user)
        self.driver.find_element_by_id('_loginPw').send_keys(self.password)
        self.driver.find_element_by_id('_userLogin').click()
        self.wait.until(ec.presence_of_element_located((By.XPATH, "//strong[contains(text(),'이*석')]")))

    def buy(self, product_number):
        self.product_number = product_number
        self.driver.get(self.product_url.format(product_number))
        self.log_header_price()
        if not self.is_in_stock():
            self.logger.info('Product {} is sold-out'.format(product_number))
            return 0
        self.pay()
        return 1

    def is_in_stock(self):
        try:
            self.driver.find_element_by_class_name("button_box").find_element_by_class_name('buy')
            return True
        except NoSuchElementException:
            return

    def get_price(self):
        return self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "sale_price"))).text.strip()

    def get_header(self):
        return self.driver.find_element_by_class_name('deal_tit').text.strip()

    def pay(self):
        url = self.driver.current_url
        while self.driver.current_url == url:
            self.logger.debug('Click buy button')
            self.driver.find_element_by_class_name('buy').click()
            sleep(0.5)
        self.wait.until(ec.presence_of_element_located((By.ID, "btnPaymentSubmit"))).click()
        sleep(1000)
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'order_finish_tit')))
        self.logger.info('Payment done: {}')
