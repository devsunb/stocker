from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from stocker.bot.wemakeprice_bot import WeMakePriceBot


class WeMakePriceFindBot(WeMakePriceBot):
    site_name = 'WEMAKEPRICEFIND'

    def __init__(self, config, output):
        super().__init__(config, output)

    def buy(self, product_keyword):
        self.driver.get(self.product_url)
        if not self.find(product_keyword):
            self.logger.info('Cannot find product name include {}'.format(product_keyword))
            return 0
        return 1

    def find(self, product_keyword):
        try:
            window_num = len(self.driver.window_handles)
            boxes = self.wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, "box_imagedeal"))).find_elements_by_tag_name('a')
            for box in boxes:
                if product_keyword in box.text:
                    box.click()
                    self.driver.switch_to.window(self.driver.window_handles[window_num])
                    self.log_header_price()
                    self.pay()
                    return True
        except NoSuchElementException:
            return
