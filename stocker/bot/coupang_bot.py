from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from stocker.bot.bot import Bot
from stocker.util.coupang_keypad import CoupangKeypad


class CoupangBot(Bot):
    site_name = 'COUPANG'

    def __init__(self, config, output):
        super().__init__(config, output)
        coupang_config = self.site_config[self.site_name]
        account_config = coupang_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        pay_config = coupang_config['PAY']
        self.pay_bank = pay_config['BANK']
        self.pay_password = pay_config['PASSWORD']
        urls = coupang_config['URL']
        self.base_url = urls['BASE']
        self.product_url = urls['PRODUCT']
        data_path_config = coupang_config['DATA_PATH']
        self.screenshot_path = self.get_data_path(data_path_config['SCREENSHOT'])
        ref_keypad_path = self.get_data_path(data_path_config['REF_KEYPAD'])
        self.keypad = CoupangKeypad(ref_keypad_path)

    def login(self):
        self.driver.get(self.base_url)
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'login'))).click()
        self.wait.until(ec.presence_of_element_located((By.ID, 'login-email-input'))).send_keys(self.user)
        self.driver.find_element_by_id('login-password-input').send_keys(self.password)
        self.driver.find_element_by_class_name('_loginSubmitButton').click()
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'today-image')))

    def buy(self, product_number):
        try:
            self.driver.get(self.product_url.format(product_number))
            self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'prod-buy')))
            is_sold_out = self.is_sold_out()
            if is_sold_out:
                self.logger.info('Product {} is sold-out'.format(product_number))
                return 0
            self.log_header_price()
            self.pay()
        except (NoSuchElementException, TimeoutException):
            pass
        return 1

    def is_sold_out(self):
        try:
            self.driver.find_element_by_class_name('restock-notification-style')
            return True
        except NoSuchElementException:
            return False

    def pay(self):
        self.driver.find_element_by_class_name('prod-buy-btn').click()
        keypad_iframe = self.driver.find_element_by_id('callLGPayment')
        sleep(3)
        self.driver.save_screenshot(self.screenshot_path)
        self.driver.switch_to.frame(keypad_iframe)
        key_positions = self.keypad.get_positions(self.screenshot_path)
        for p in self.pay_password:
            self.driver.find_element_by_class_name(
                'rocketpay-keypad-position-{}'.format(key_positions.index(p))).click()
        self.logger.info('Payment done')
        self.driver.switch_to.default_content()

    def get_price(self):
        return self.driver.find_element_by_class_name('total-price').text.strip()

    def get_header(self):
        return self.driver.find_element_by_class_name('prod-buy-header__title').text.strip()
