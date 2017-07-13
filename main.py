import logging
from telegram.ext import Updater

from objects import emails, webscraper, db
from objects.bot import Responder
from utilities import config, handlers

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s')
logger = logging.getLogger(__name__)


def main():
    """This function is the starting point of the bot script."""
    responder = Responder(webscraper.Scraper(config.NACC_TENDERS_URL),
                          emails.Email(),
                          db.DBHelper(config.DB_URI))
    updater = Updater(config.BOT_TOKEN)

    # Add handlers
    # =================================================================
    updater.dispatcher.add_handler(
        handler=handlers.get_start_handler(responder))

    updater.dispatcher.add_handler(
        handler=handlers.get_inline_query_handler(responder))

    updater.dispatcher.add_handler(
        handler=handlers.get_menu_conv_handler(responder))

    updater.dispatcher.add_handler(
        handler=handlers.get_registration_conv_handler(responder)
    )

    # Set up the webhook
    # =================================================================
    updater.start_webhook(listen='0.0.0.0',
                          port=config.PORT,
                          url_path=config.BOT_TOKEN)
    updater.bot.set_webhook(config.BASE_WEBHOOK_URL + config.BOT_TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
