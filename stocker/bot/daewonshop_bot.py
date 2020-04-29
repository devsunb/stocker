from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from stocker.bot.bot import Bot


class DaewonshopBot(Bot):
    site_name = 'DAEWONSHOP'

    def __init__(self, config, output):
        super().__init__(config, output)
        daewonshop_config = self.site_config[self.site_name]
        account_config = daewonshop_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        urls = daewonshop_config['URL']
        self.login_url = urls['LOGIN']
        self.product_url = urls['PRODUCT']
        pay_config = daewonshop_config['PAY']
        self.pay_name = pay_config['NAME']

    def login(self):
        self.driver.get(self.login_url)
        self.wait.until(ec.presence_of_element_located((By.ID, 'loginId'))).send_keys(self.user)
        self.driver.find_element_by_id('loginPwd').send_keys(self.password)
        self.driver.find_element_by_id('formLogin').submit()
        try:
            self.wait.until(ec.alert_is_present())
            self.driver.switch_to_alert().accept()
            self.logger.info('출석체크 알림 확인')
        except (TimeoutException, NoAlertPresentException):
            pass
        self.wait.until(ec.presence_of_element_located((By.XPATH, "//a[contains(text(),'로그아웃')]")))

    def buy(self, product_number):
        self.driver.get(self.product_url.format(product_number))
        self.log_header_price()
        if self.is_sold_out():
            self.logger.info('Product {} is sold-out'.format(product_number))
            return 0
        self.pay()
        return 1

    def get_price(self):
        return self.driver.find_element_by_css_selector('#frmView > .info > .item .price > div').text.strip()

    def get_header(self):
        return self.driver.find_element_by_css_selector(
            '#frmView > .info > .goods-header > .top > .tit > h2').text.strip()

    def is_sold_out(self):
        try:
            self.driver.find_element_by_css_selector('.goods > #frmView > .info > .btn > .soldout')
            return True
        except NoSuchElementException:
            return False

    def pay(self):
        self.driver.find_element_by_class_name('btn-add-order').click()
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'final-settlement')))
        self.driver.find_element_by_name('bankSender').send_keys(self.pay_name)
        self.driver.find_element_by_id('settlekind_general').find_element_by_class_name('chosen-container').click()
        self.wait.until(ec.presence_of_element_located((By.XPATH, "//li[contains(text(),'농협')]"))).click()
        self.driver.find_element_by_xpath('//label[@for="receipt_cash"]').click()
        self.driver.find_element_by_xpath('//label[@for="termAgree_orderCheck"]').click()
        self.driver.find_element_by_class_name('order-buy').click()
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'order-completion')))
        self.logger.info('Payment done: {}')
