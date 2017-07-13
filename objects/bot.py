"""This module contains the main bot responder object"""
from uuid import uuid4

import requests
from telegram import ParseMode, ChatAction, InlineQueryResultArticle, \
    InputTextMessageContent
from telegram.ext import ConversationHandler

from utilities import keyboard, config
from utilities.config import AUTH_HEADER
from utilities.decorators import sync_db


class Responder(object):
    """This class contains all the callbacks passed to the handlers."""

    def __init__(self, scraper, email, db_helper):
        self.scraper = scraper
        self.email = email
        self.db = db_helper

    @sync_db
    def start(self, bot, update):
        """This method responds to the /start command."""
        chat_id = update.message.chat.id
        text = 'Hello *{}*,\n' \
               'I am The NACC Bot. I can help you get information ' \
               'from the [National AIDS Control Council](' \
               'nacc.or.ke).\n\n' \
               '*I will respond to the following commands:*\n\n' \
               '/menu - launch main menu' \
            .format(update.message.from_user.first_name)

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

    def menu(self, bot, update):
        """This method responds to the /menu command."""
        chat_id = update.message.chat.id
        text = 'Choose an option from the Menu below:'
        reply_markup = keyboard.build_main_menu()

        bot.send_message(chat_id=chat_id,
                         text=text,
                         reply_markup=reply_markup)

        return 0

    def tenders_list(self, bot, update):
        """This method responds to clicks on the main menu."""
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        text = 'Here is a list of available tenders. Which one would ' \
               'you like me to show you?'

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text)

        tenders = self.scraper.get_tenders()
        reply_markup = keyboard.build_tenders_menu(tenders)

        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=reply_markup)
        return 1

    def register(self, bot, update, user_data):
        user_id = update.callback_query.from_user.id
        user = self.db.read_user(user_id)
        firm_name = user.get('firm_name', None)
        if firm_name:
            callback_query_id = update.callback_query.id
            text = 'Your firm {} is already registered.'.format(
                firm_name)

            bot.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text)

            return 0

        else:
            user_data['User_Id'] = user_id

            chat_id = update.callback_query.message.chat.id
            message_id = update.callback_query.message.message_id
            text = 'Welcome to the Registration Form.\n' \
                   'You will fill out the form by sending relevant ' \
                   'input to me via messages. Mandatory fields will ' \
                   'be in *bold* and you will be required to send a ' \
                   'valid input before you can move on.' \
                   'Fields not in bold are optional and you can send ' \
                   '/skip to move on to the next field if you cannot ' \
                   'provide an input for that field.\n\n' \
                   '*1. E-Mail Address:*'

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text,
                                  parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

    def tender_detail(self, bot, update, chat_data):
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id

        tender_number = update.callback_query.data
        chat_data['tender_number'] = tender_number
        tender = self.scraper.find_tender_by_number(tender_number)
        if tender:
            text = '*Tender Title:* {}\n\n' \
                   '*Tender Number:* {}\n\n' \
                   '*Closing Date:* {}\n'.format(tender.title,
                                                 tender.number,
                                                 tender.closing_date)

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text,
                                  parse_mode=ParseMode.MARKDOWN)

            reply_markup = keyboard.build_tender_actions()
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=reply_markup)
        return 2

    def back_to_main_menu(self, bot, update):
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        text = 'Choose an option from the Menu below:'

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text)

        reply_markup = keyboard.build_main_menu()

        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=reply_markup)

        return 0

    def send_document(self, bot, update, chat_data):
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id

        tender_number = chat_data['tender_number']
        tender = self.scraper.find_tender_by_number(tender_number)
        if tender:
            callback_query_id = update.callback_query.id
            if update.callback_query.data == 'download_document':
                document = tender.pdf_url
                caption = tender.title

                bot.send_chat_action(chat_id=chat_id,
                                     action=ChatAction.UPLOAD_DOCUMENT)

                bot.send_document(chat_id=chat_id,
                                  document=document,
                                  caption=caption)

                text = 'Document sent'

                bot.answer_callback_query(
                    callback_query_id=callback_query_id,
                    text=text)
            elif update.callback_query.data == 'email_document':
                user_id = update.callback_query.from_user.id
                user = self.db.read_user(user_id)
                email_address = user.get('email', None)
                if email_address:
                    bot.send_chat_action(chat_id=chat_id,
                                         action=ChatAction.TYPING)

                    self.email.send_tender_email(tender, email_address)

                    text = 'Email sent successfully'

                    bot.answer_callback_query(
                        callback_query_id=callback_query_id,
                        text=text)
                else:
                    text = 'You have not registered your email.'

                    bot.answer_callback_query(
                        callback_query_id=callback_query_id,
                        text=text)

                    return 2

        text = '*Talk to me using the following commands:*\n\n' \
               '/menu - launch main menu'

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text,
                              parse_mode=ParseMode.MARKDOWN)

        return ConversationHandler.END

    def back_to_tenders_list(self, bot, update):
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        text = 'Here is a list of available tenders. Which one ' \
               'would you like me to show you?'

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text)

        tenders = self.scraper.get_tenders()
        reply_markup = keyboard.build_tenders_menu(tenders)

        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=reply_markup)

        return 1

    def exit_menu(self, bot, update):
        """Responds to the 'Exit Menu' callback query."""
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        callback_query_id = update.callback_query.id
        text = 'Exit Menu'

        bot.answer_callback_query(callback_query_id=callback_query_id,
                                  text=text)

        text = '*Talk to me using the following commands:*\n\n' \
               '/menu - launch main menu'

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text,
                              parse_mode=ParseMode.MARKDOWN)

        return ConversationHandler.END

    def email_address(self, bot, update, user_data):
        _email_address = update.message.text
        user_data['email'] = _email_address

        chat_id = update.message.chat.id
        text = '*2. Name Of Authorized Person Filling The Form:* _(' \
               'Must adhere to proper ' \
               'capitalization)_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 1

    def full_name(self, bot, update, user_data):
        _full_name = update.message.text
        user_data['fname'] = _full_name

        chat_id = update.message.chat.id
        text = '*3. Mobile Phone Number:* _(07XXXXXXXX)_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 2

    def full_name_invalid(self, bot, update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*2. Name Of Authorized Person Filling The Form:* _(' \
               'must adhere to proper capitalization)_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 1

    def mobile_number(self, bot, update, user_data):
        _mobile_number = update.message.text
        user_data['mobile_no'] = _mobile_number

        chat_id = update.message.chat.id
        text = '*4. Name Of Firm:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 3

    def mobile_number_invalid(self, bot, update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*3. Mobile Phone Number:* _(07XXXXXXXX)_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 2

    def name_of_firm(self, bot, update, user_data):
        _name_of_firm = update.message.text
        user_data['firm_name'] = _name_of_firm

        chat_id = update.message.chat.id
        text = '*5. Registration Certificate Number:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 4

    def registration_certificate_number(self, bot, update,
                                        user_data):
        _reg_cert_no = update.message.text
        user_data['reg_cert_no'] = _reg_cert_no

        chat_id = update.message.chat.id
        text = '*6. Date Of Registration:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 5

    def date_of_registration(self, bot, update, user_data):
        _date_of_registration = update.message.text
        user_data['reg_date'] = _date_of_registration

        chat_id = update.message.chat.id
        text = '*7. Name Of Director:* _(Must adhere to proper ' \
               'capitalization)_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 6

    def date_of_registration_invalid(self, bot, update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*6. Date Of Registration:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 5

    def name_of_director(self, bot, update, user_data):
        _name_of_director = update.message.text
        user_data['director_name'] = _name_of_director

        chat_id = update.message.chat.id
        text = '*8. Postal Address & Code*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 7

    def name_of_director_invalid(self, bot, update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*7. Name Of Director:* _(Must adhere to proper ' \
               'capitalization)_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 6

    def postal_address(self, bot, update, user_data):
        _postal_address = update.message.text
        user_data['postal_address'] = _postal_address

        chat_id = update.message.chat.id
        text = '*9. Town:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 8

    def town(self, bot, update, user_data):
        _town = update.message.text
        user_data['town'] = _town

        chat_id = update.message.chat.id
        text = '*10. Building:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 9

    def building(self, bot, update, user_data):
        _building = update.message.text
        user_data['building'] = _building

        chat_id = update.message.chat.id
        text = '*11. Floor:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 10

    def floor(self, bot, update, user_data):
        _floor = update.message.text
        user_data['floor'] = _floor

        chat_id = update.message.chat.id
        text = '*12. Street or Avenue:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 11

    def street(self, bot, update, user_data):
        _street = update.message.text
        user_data['street'] = _street

        chat_id = update.message.chat.id
        text = '*13. KRA Pin Number:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 12

    def kra_pin(self, bot, update, user_data):
        _kra_pin = update.message.text
        user_data['kra_pin'] = _kra_pin

        chat_id = update.message.chat.id
        text = '*14. Tax Compliance Certificate Expiry Date:* ' \
               '_dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 13

    def tax_compliance_certificate_expiry_date(self, bot, update,
                                               user_data):
        _tax_compliance_exp_date = update.message.text
        user_data['tax_compliance_exp_date'] = _tax_compliance_exp_date

        chat_id = update.message.chat.id
        text = '15. AGPO Certificate Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 14

    def tax_compliance_certificate_expiry_date_invalid(self, bot,
                                                       update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*14. Tax Compliance Certificate Expiry Date:* ' \
               '_dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 13

    def agpo_certificate_number(self, bot, update, user_data):
        _agpo_cert_number = update.message.text
        user_data['agpo_cert_no'] = _agpo_cert_number

        chat_id = update.message.chat.id
        text = '*16. AGPO Certificate Expiry Date:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 15

    def agpo_certificate_number_skip(self, bot, update, user_data):
        user_data['agpo_cert_no'] = None
        user_data['agpo_cert_exp_date'] = None

        chat_id = update.message.chat.id
        text = '*17. Number Of Employees:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 16

    def agpo_certificate_expiry_date(self, bot, update, user_data):
        _agpo_certificate_expiry_date = update.message.text
        user_data[
            'agpo_cert_exp_date'] = _agpo_certificate_expiry_date

        chat_id = update.message.chat.id
        text = '*17. Number Of Employees:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 16

    def agpo_certificate_expiry_date_invalid(self, bot, update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*16. AGPO Certificate Expiry Date:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 15

    def number_of_employees(self, bot, update, user_data):
        _employees_no = update.message.text
        user_data['employees_no'] = _employees_no

        chat_id = update.message.chat.id
        text = '18. NSSF Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 17

    def nssf_number(self, bot, update, user_data):
        _nssf_no = update.message.text
        user_data['nssf_no'] = _nssf_no

        chat_id = update.message.chat.id
        text = '*19. NSSF Compliance Certificate Expiry Date:* ' \
               '_dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 18

    def nssf_number_skip(self, bot, update, user_data):
        user_data['nssf_no'] = None
        user_data['nssf_cert_exp_date'] = None

        chat_id = update.message.chat.id
        text = '20. NHIF Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 19

    def nssf_compliance_certificate_expiry_date(self, bot, update,
                                                user_data):
        nssf_compliance_cert_exp_date = update.message.text
        user_data['nssf_cert_exp_date'] = nssf_compliance_cert_exp_date

        chat_id = update.message.chat.id
        text = '20. NHIF Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 19

    def nssf_compliance_certificate_expiry_date_invalid(self, bot,
                                                        update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*19. NSSF Compliance Certificate Expiry ' \
               'Date:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 18

    def nhif_number(self, bot, update, user_data):
        _nhif_no = update.message.text
        user_data[
            'nhif_no'] = _nhif_no

        chat_id = update.message.chat.id
        text = '*21. NHIF Compliance Certificate Expiry Date:* ' \
               '_dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 20

    def nhif_number_skip(self, bot, update, user_data):
        user_data['nhif_no'] = None
        user_data['nhif_cert_exp_date'] = None

        chat_id = update.message.chat.id
        text = '22. IATA Certificate Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 21

    def nhif_compliance_certificate_expiry_date(self, bot, update,
                                                user_data):
        _nhif_compliance_cert_exp_date = update.message.text
        user_data[
            'nhif_cert_exp_date'] = \
            _nhif_compliance_cert_exp_date

        chat_id = update.message.chat.id
        text = '22. IATA Certificate Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 21

    def nhif_compliance_certificate_expiry_date_invalid(self, bot,
                                                        update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*21. NHIF Compliance Certificate Expiry ' \
               'Date:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 20

    def iata_certificate_number(self, bot, update, user_data):
        _iata_cert_no = update.message.text
        user_data[
            'iata_cert_no'] = _iata_cert_no

        chat_id = update.message.chat.id
        text = '*23. NCA Number:* or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 22

    def iata_certificate_number_skip(self, bot, update, user_data):
        user_data['iata_cert_no'] = None

        chat_id = update.message.chat.id
        text = '23. NCA Number: or /skip'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 22

    def nca_number(self, bot, update, user_data):
        _nca_no = update.message.text
        user_data['nca_no'] = _nca_no

        chat_id = update.message.chat.id
        text = '*24. NCA Compliance Certificate Expiry Date:* ' \
               '_dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 23

    def nca_number_skip(self, bot, update, user_data):
        user_data['nca_no'] = None
        user_data['nca_cert_exp_date'] = None

        chat_id = update.message.chat.id
        text = '*25. Category Of Special Group:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 24

    def nca_certificate_expiry_date(self, bot, update,
                                    user_data):
        _nca_cert_exp_date = update.message.text
        user_data['nca_cert_exp_date'] = _nca_cert_exp_date

        chat_id = update.message.chat.id
        text = '*25. Category Of Special Group:*'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 24

    def nca_certificate_expiry_date_invalid(self, bot, update):
        chat_id = update.message.chat.id
        text = 'Invalid!\n' \
               '*24. NCA Compliance Certificate Certificate Expiry ' \
               'Date:* _dd/mm/yyyy_'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)

        return 23

    def category_of_special_group(self, bot, update, user_data):
        _category = update.message.text
        user_data[
            'category'] = _category

        chat_id = update.message.chat.id
        text = 'Registration Form completely filled.\n\n' \
               'Please /submit'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return 25

    def submit(self, bot, update, user_data):
        requests.post(config.NACC_BACKEND_SERVER, data=user_data, headers=config.AUTH_HEADER)

        chat_id = update.message.chat.id
        text = '*The following data has been saved*\n\n'
        for key in user_data.keys():
            text += '*{}:* {}\n'.format(key, user_data[key])



        text += '\n\n' \
                '*Talk to me using the following commands.*\n\n' \
                '/menu - launch main menu'

        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

    def inline_query(self, bot, update):
        query = update.inline_query.query

        results = list()

        matched_tenders = self.scraper.search_tenders(query)
        for tender in matched_tenders:
            message_text = '*Tender Title:* {}\n\n' \
                           '*Tender Number:* {}\n\n' \
                           '*Closing Date:* {}\n'.format(tender.title,
                                                         tender.number,
                                                         tender.closing_date)
            results.append(
                InlineQueryResultArticle(id=uuid4(),
                                         title=tender.title,
                                         input_message_content=InputTextMessageContent(
                                             message_text=message_text,
                                             parse_mode=ParseMode.MARKDOWN
                                         ))
            )

        update.inline_query.answer(results)
