import logging


class Output:
    output_name = ''
    logger = logging.getLogger('stocker')

    def __init__(self, config):
        self.output_config = config['OUTPUT']

    def insert(self, stock_data):
        self.logger.info(stock_data)
        return True
