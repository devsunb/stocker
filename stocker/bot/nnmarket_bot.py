from time import sleep

from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from stocker.bot.bot import Bot


class NnMarketBot(Bot):
    site_name = 'NNMARKET'

    def __init__(self, config, output):
        super().__init__(config, output)
        nnmarket_config = self.site_config[self.site_name]
        account_config = nnmarket_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        urls = nnmarket_config['URL']
        self.login_url = urls['LOGIN']
        self.cart_url = urls['CART']
        self.product_url = urls['PRODUCT']
        pay_config = nnmarket_config['PAY']
        self.pay_name = pay_config['NAME']
        self.pay_phone_number = pay_config['PHONE_NUMBER']

    def login(self):
        self.driver.get(self.login_url)
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'MS_login_id'))).send_keys(self.user)
        self.driver.find_element_by_class_name('MS_login_pw').send_keys(self.password)
        self.driver.find_element_by_xpath('//img[@alt="로그인"]').click()
        try:
            self.wait.until(ec.alert_is_present())
            self.driver.switch_to_alert().accept()
            self.logger.info('출석체크 알림 확인')
        except (TimeoutException, NoAlertPresentException):
            pass
        self.wait.until(ec.presence_of_element_located((By.XPATH, "//a[contains(text(),'로그아웃')]")))
        self.clear_cart()

    def clear_cart(self):
        self.driver.get(self.cart_url)
        self.driver.find_element_by_class_name('toggle_bt').click()
        for e in self.driver.find_elements_by_xpath('//img[@alt="삭제"]'):
            e.click()
            self.driver.switch_to_alert().accept()

    def buy(self, product_number):
        self.driver.get(self.product_url.format(product_number))
        self.log_header_price()
        if not self.is_in_stock():
            self.logger.info('Product {} is sold-out'.format(product_number))
            return 0
        self.pay()
        return 1

    def get_price(self):
        return self.driver.find_element_by_class_name('selling').text.strip()

    def get_header(self):
        return self.driver.find_element_by_class_name('tit-prd').text.strip()

    def is_in_stock(self):
        return '상품이 품절되었습니다.' not in self.driver.find_element_by_class_name('prd-btns').text

    def pay(self):
        self.driver.find_element_by_xpath('//img[@alt="주문하기"]').click()
        self.driver.find_element_by_id('receiver').send_keys(self.pay_name)
        self.driver.find_element_by_name('emergency21').send_keys(self.pay_phone_number[:3])
        self.driver.find_element_by_name('emergency22').send_keys(self.pay_phone_number[3:7])
        self.driver.find_element_by_name('emergency23').send_keys(self.pay_phone_number[7:])
        window_num = len(self.driver.window_handles)
        self.driver.find_element_by_xpath('//img[@alt="주문하기"]').click()
        while len(self.driver.window_handles) == window_num:
            sleep(1)
        self.driver.switch_to.window(self.driver.window_handles[window_num])
        Select(self.driver.find_element_by_name('paydata1')).select_by_index(1)
        self.driver.find_element_by_name('cashcheck').click()
        self.driver.find_element_by_name('tel1').send_keys(self.pay_phone_number[:3])
        self.driver.find_element_by_name('tel2').send_keys(self.pay_phone_number[3:7])
        self.driver.find_element_by_name('tel3').send_keys(self.pay_phone_number[7:])
        self.driver.find_element_by_name('pay_agree').click()
        self.driver.execute_script('send()')
        self.driver.switch_to_alert().accept()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.wait.until(ec.presence_of_element_located((By.XPATH, '//img[@alt="주문완료"]')))
        self.logger.info('Payment done: {}')
