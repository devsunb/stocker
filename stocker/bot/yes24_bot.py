from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from stocker.bot.bot import Bot


class YES24Bot(Bot):
    site_name = 'YES24'

    def __init__(self, config, output):
        super().__init__(config, output)
        yes24_config = self.site_config[self.site_name]
        account_config = yes24_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        urls = yes24_config['URL']
        self.login_url = urls['LOGIN']
        self.product_url = urls['PRODUCT']
        pay_config = yes24_config['PAY']
        self.pay_bank = pay_config['BANK']
        self.pay_name = pay_config['NAME']

    def login(self):
        self.driver.get(self.login_url)
        self.wait.until(ec.presence_of_element_located((By.ID, 'SMemberID'))).send_keys(self.user)
        self.driver.find_element_by_id('SMemberPassword').send_keys(self.password)
        self.driver.find_element_by_id('btnLogin').click()
        self.wait.until(ec.presence_of_element_located((By.ID, "LoginText")))

    def buy(self, product_number):
        self.driver.get(self.product_url.format(product_number))
        self.log_header_price()
        if not self.is_in_stock():
            self.logger.info('Product {} is sold-out'.format(product_number))
            return 0
        self.pay()
        return 1

    def get_price(self):
        return self.driver.find_element_by_class_name('nor_price').text.strip()

    def get_header(self):
        return self.driver.find_element_by_class_name('gd_titArea').find_element_by_tag_name('h2').text.strip()

    def is_in_stock(self):
        return '판매중' in self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'gd_saleState'))).text

    def pay(self):
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "btn_sBlue"))).click()
        self.wait.until(ec.presence_of_element_located((By.XPATH, '//img[@alt="확인"]'))).click()
        self.wait.until(ec.alert_is_present())
        self.driver.switch_to_alert().accept()
        self.wait.until(ec.presence_of_element_located((By.ID, "rdoDeposit"))).click()
        Select(self.driver.find_element_by_id('ddlBank')).select_by_visible_text(self.pay_bank)
        self.driver.find_element_by_id("txtPayerNm").send_keys(self.pay_name)
        self.wait.until(ec.presence_of_element_located((By.ID, "chkSubscribeAgree"))).click()
        self.wait.until(ec.presence_of_element_located((By.ID, "chkPayAgree"))).click()
        self.wait.until(ec.presence_of_element_located((By.XPATH, '//img[@alt="결제하기"]'))).click()
        self.logger.info('Payment done: {}')
