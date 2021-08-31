from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select

from stocker.bot.bot import Bot


class HimartBot(Bot):
    site_name = 'HIMART'

    def __init__(self, config, output):
        super().__init__(config, output)
        himart_config = self.site_config[self.site_name]
        account_config = himart_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        urls = himart_config['URL']
        self.base_url = urls['BASE']
        self.product_url = urls['PRODUCT']

    def login(self):
        self.driver.get(self.base_url)
        window_num = len(self.driver.window_handles)
        self.wait.until(ec.presence_of_element_located((By.XPATH, "//span[contains(text(),'로그인')]"))).click()
        self.driver.switch_to.window(self.driver.window_handles[window_num])
        self.wait.until(ec.presence_of_element_located((By.ID, 'login_id'))).send_keys(self.user)
        self.driver.find_element_by_id('password').send_keys(self.password)
        self.driver.find_element_by_class_name('pop_btn_login').click()
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.wait.until(ec.presence_of_element_located((By.XPATH, "//span[contains(text(),'로그아웃')]")))

    def buy(self, product_number):
        self.driver.get(self.product_url.format(product_number))
        is_sold_out, sold_out_desc = self.is_sold_out()
        if is_sold_out:
            self.logger.info('Product {} is {}'.format(product_number, sold_out_desc))
            return 0
        self.log_header_price()
        self.pay()
        return 1

    def is_sold_out(self):
        btns_purchase = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'btns_purchase')))
        btn_type2_text = btns_purchase.find_element_by_class_name('btn_type2').text.strip()
        return btn_type2_text == '일시품절', btn_type2_text

    def pay(self):
        self.driver.find_element_by_class_name('btns_purchase').find_element_by_class_name('btn_type3').click()
        self.wait.until(ec.presence_of_element_located((By.ID, 'vBank'))).send_keys(Keys.ENTER)
        Select(self.driver.find_element_by_id('vir_acct_bank')).select_by_visible_text(self.pay_bank)
        self.driver.find_element_by_id('cr_issu_type_3').send_keys(Keys.ENTER)
        self.driver.find_element_by_id('cr_issu_mean_no').send_keys(self.pay_phone_number)
        self.driver.find_element_by_id('normalPayment').find_element_by_tag_name('a').send_keys(Keys.ENTER)
        self.driver.switch_to_alert().accept()
        self.driver.switch_to_alert().accept()
        pay_bank_number_selector = '#contents > div.order_wrap > div.order_info > table > tbody > tr:nth-child(4) > td'
        pay_bank_number = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, pay_bank_number_selector))).text.strip().split('\n')[0]
        self.logger.info('Payment done: {}'.format(pay_bank_number))

    def get_price(self):
        return self.driver.find_element_by_class_name('price').find_element_by_class_name(
            'final').find_element_by_class_name('num').text.strip()

    def get_header(self):
        return self.driver.find_element_by_class_name('title_product').find_element_by_class_name('tit').text.strip()
