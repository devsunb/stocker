from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from stocker.bot.wemakeprice_find_bot import WeMakePriceFindBot


class WeMakePriceFind2Bot(WeMakePriceFindBot):
    site_name = 'WEMAKEPRICEFIND2'

    def find(self, product_keyword):
        try:
            boxes = self.wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, "box_imagedeal"))).find_elements_by_tag_name('a')
            for box in boxes:
                if product_keyword in box.text:
                    box.click()
                    self.log_header_price()
                    self.pay()
                    return True
        except NoSuchElementException as e:
            self.logger.error(e)
            return
