import argparse
import logging
import threading

from stocker.bot.bot import BotError
from stocker.bot.coupang_bot import CoupangBot
from stocker.bot.daewonshop_bot import DaewonshopBot
from stocker.bot.embuy_bot import EMBuyBot
from stocker.bot.lotteimall_bot import LotteIMallBot
from stocker.bot.nnmarket_bot import NnMarketBot
from stocker.bot.wemakeprice_bot import WeMakePriceBot
from stocker.bot.wemakeprice_find2_bot import WeMakePriceFind2Bot
from stocker.bot.wemakeprice_find3_bot import WeMakePriceFind3Bot
from stocker.bot.wemakeprice_find_bot import WeMakePriceFindBot
from stocker.bot.yes24_bot import YES24Bot
from stocker.output.influxdb import InfluxDB
from stocker.util.parse import parse_config

logger = logging.getLogger('stocker')

site_bots = {
    CoupangBot.site_name: CoupangBot,
    LotteIMallBot.site_name: LotteIMallBot,
    EMBuyBot.site_name: EMBuyBot,
    YES24Bot.site_name: YES24Bot,
    NnMarketBot.site_name: NnMarketBot,
    DaewonshopBot.site_name: DaewonshopBot,
    WeMakePriceBot.site_name: WeMakePriceBot,
    WeMakePriceFindBot.site_name: WeMakePriceFindBot,
    WeMakePriceFind2Bot.site_name: WeMakePriceFind2Bot,
    WeMakePriceFind3Bot.site_name: WeMakePriceFind3Bot
}
outputs = {
    InfluxDB.output_name: InfluxDB
}


def run():
    option = get_option()
    setup_logger(option.log_level)
    config = parse_config(option.config)

    for r in config['RECIPE']:
        os = [outputs[on](config) for on in r['OUTPUT']]
        b = site_bots[r['SITE']](config, os)
        thread = threading.Thread(target=run_bot, args=(b, r))
        thread.start()


def run_bot(bot, recipe):
    try:
        bot.login()
        bot.loop(recipe)
        bot.quit()
    except BotError as e:
        logger.error('BotError: ({})'.format(e))


def get_option():
    parser = argparse.ArgumentParser(description='Stocker')
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to a configuration file')
    parser.add_argument('-l', '--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Logging level')
    return parser.parse_args()


def setup_logger(log_level):
    logger.setLevel(log_level.upper())
    formatter = logging.Formatter('%(asctime)s %(threadName)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


if __name__ == '__main__':
    run()
