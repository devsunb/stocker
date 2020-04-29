from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from stocker.bot.bot import Bot


class EMBuyBot(Bot):
    site_name = 'EMBUY'

    def __init__(self, config, output):
        super().__init__(config, output)
        embuy_config = self.site_config[self.site_name]
        account_config = embuy_config['ACCOUNT']
        self.user = account_config['USER']
        self.password = account_config['PASSWORD']
        urls = embuy_config['URL']
        self.login_url = urls['LOGIN']
        self.product_url = urls['PRODUCT']
        self.alert = None

    def login(self):
        self.driver.get(self.login_url)
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'id'))).send_keys(self.user)
        self.driver.find_element_by_class_name('password').send_keys(self.password)
        self.wait.until(ec.element_to_be_clickable((By.XPATH, '//img[@alt="로그인"]'))).click()
        self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, "log")))

    def buy(self, product_number):
        self.driver.get(self.product_url.format(product_number))
        if not self.is_page_exist():
            self.logger.info('Product {} page is not exist'.format(product_number))
            return 0
        self.log_header_price()
        if self.is_sold_out():
            self.logger.info('Product {} is sold-out'.format(product_number))
            return 0
        input_quantity = self.driver.find_element_by_id('quantity')
        input_quantity.clear()
        input_quantity.send_keys('1')
        self.driver.execute_script('product_submit(1, "/exec/front/order/basket/", this)')
        self.wait.until(ec.alert_is_present())
        self.alert = self.driver.switch_to_alert()
        if self.is_in_cart():
            self.logger.info('Product {} is in cart'.format(product_number))
            self.alert.dismiss()
            self.alert = None
        self.pay()
        return 1

    def is_page_exist(self):
        return '페이지를 찾을 수 없습니다' not in self.driver.title

    def get_price(self):
        return self.driver.find_element_by_id('span_product_price_text').text.strip()

    def get_header(self):
        return self.driver.find_element_by_xpath(
            '//*[@id="contents"]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td/span').text.strip()

    def is_sold_out(self):
        return 'displaynone' in self.driver.find_element_by_css_selector(
            '.infoArea .xans-product-action .btnArea .first').get_attribute('class')

    def is_in_cart(self):
        return '동일상품이 장바구니에' in self.alert.text

    def pay(self):
        self.wait.until(ec.alert_is_present())
        self.driver.switch_to_alert().accept()
        self.wait.until(ec.element_to_be_clickable((By.ID, "btn_payment")))
        self.driver.find_element_by_id('addr_paymethod2').click()
        self.driver.find_element_by_id('btn_payment').click()
        self.logger.info('Payment done: {}')
