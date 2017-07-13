"""This module contains methods to retrieve all the Handler objects."""
from telegram.ext import CommandHandler, ConversationHandler, \
    CallbackQueryHandler, RegexHandler, InlineQueryHandler, \
    MessageHandler, Filters

from utilities import patterns


def get_start_handler(responder):
    return CommandHandler('start', responder.start)


def get_inline_query_handler(responder):
    return InlineQueryHandler(responder.inline_query)


def get_menu_conv_handler(responder):
    return ConversationHandler(
        entry_points=[
            CommandHandler('menu', responder.menu)
        ],
        states={
            0: [
                CallbackQueryHandler(responder.exit_menu,
                                     pattern=r'^exit_menu$'),
                CallbackQueryHandler(responder.tenders_list,
                                     pattern=r'^tenders$'),
                CallbackQueryHandler(responder.register,
                                     pattern='^register',
                                     pass_user_data=True)
            ],
            1: [
                CallbackQueryHandler(responder.exit_menu,
                                     pattern=r'^exit_menu$'),
                CallbackQueryHandler(responder.back_to_main_menu,
                                     pattern=r'^back_to_main_menu'),
                CallbackQueryHandler(responder.tender_detail,
                                     # pattern=r'^NACC',
                                     pass_chat_data=True)
            ],
            2: [
                CallbackQueryHandler(responder.send_document,
                                     pattern=r'^\w+_document$',
                                     pass_chat_data=True),
                CallbackQueryHandler(responder.back_to_tenders_list,
                                     pattern=r'^tenders_list$'),
                CallbackQueryHandler(responder.exit_menu,
                                     pattern=r'^exit_menu$')
            ]
        },
        fallbacks=[

        ],
        allow_reentry=True
    )


def get_registration_conv_handler(responder):
    return ConversationHandler(
        entry_points=[
            RegexHandler(patterns.EMAIL_ADDRESS,
                         responder.email_address,
                         pass_user_data=True)
        ],
        states={
            1: [
                RegexHandler(patterns.FULL_NAME, responder.full_name,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.full_name_invalid)
            ],
            2: [
                RegexHandler(patterns.PHONE_NUMBER,
                             responder.mobile_number,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.mobile_number_invalid)
            ],
            3: [
                MessageHandler(Filters.text, responder.name_of_firm,
                               pass_user_data=True)
            ],
            4: [
                MessageHandler(Filters.text,
                               responder.registration_certificate_number,
                               pass_user_data=True)
            ],
            5: [
                RegexHandler(patterns.DATE,
                             responder.date_of_registration,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.date_of_registration_invalid)
            ],
            6: [
                RegexHandler(patterns.FULL_NAME,
                             responder.name_of_director,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.name_of_director_invalid)
            ],
            7: [
                MessageHandler(Filters.text,
                               responder.postal_address,
                               pass_user_data=True)
            ],
            8: [
                MessageHandler(Filters.text, responder.town,
                               pass_user_data=True)
            ],
            9: [
                MessageHandler(Filters.text, responder.building,
                               pass_user_data=True)
            ],
            10: [
                MessageHandler(Filters.text, responder.floor,
                               pass_user_data=True)
            ],
            11: [
                MessageHandler(Filters.text, responder.street,
                               pass_user_data=True)
            ],
            12: [
                MessageHandler(Filters.text, responder.kra_pin,
                               pass_user_data=True)
            ],
            13: [
                RegexHandler(patterns.DATE,
                             responder.tax_compliance_certificate_expiry_date,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.tax_compliance_certificate_expiry_date_invalid)
            ],
            14: [
                MessageHandler(Filters.text,
                               responder.agpo_certificate_number,
                               pass_user_data=True),
                CommandHandler('skip',
                               responder.agpo_certificate_number_skip,
                               pass_user_data=True)
            ],
            15: [
                RegexHandler(patterns.DATE,
                             responder.agpo_certificate_expiry_date,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.agpo_certificate_expiry_date_invalid)
            ],
            16: [
                MessageHandler(Filters.text,
                               responder.number_of_employees,
                               pass_user_data=True)
            ],
            17: [
                MessageHandler(Filters.text, responder.nssf_number,
                               pass_user_data=True),
                CommandHandler('skip', responder.nssf_number_skip,
                               pass_user_data=True)
            ],
            18: [
                RegexHandler(patterns.DATE,
                             responder.nssf_compliance_certificate_expiry_date,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.nssf_compliance_certificate_expiry_date_invalid)
            ],
            19: [
                MessageHandler(Filters.text, responder.nhif_number,
                               pass_user_data=True),
                CommandHandler('skip', responder.nhif_number_skip,
                               pass_user_data=True)
            ],
            20: [
                RegexHandler(patterns.DATE,
                             responder.nhif_compliance_certificate_expiry_date,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.nhif_compliance_certificate_expiry_date_invalid)
            ],
            21: [
                MessageHandler(Filters.text,
                               responder.iata_certificate_number,
                               pass_user_data=True),
                CommandHandler('skip',
                               responder.iata_certificate_number_skip,
                               pass_user_data=True)
            ],
            22: [
                MessageHandler(Filters.text,
                               responder.nca_number,
                               pass_user_data=True),
                CommandHandler('skip', responder.nca_number_skip,
                               pass_user_data=True)
            ],
            23: [
                RegexHandler(patterns.DATE,
                             responder.nca_certificate_expiry_date,
                             pass_user_data=True),
                MessageHandler(Filters.text,
                               responder.nca_certificate_expiry_date_invalid)
            ],
            24: [
                MessageHandler(Filters.text,
                               responder.category_of_special_group,
                               pass_user_data=True)
            ],
            25: [
                CommandHandler('submit', responder.submit,
                               pass_user_data=True)
            ]
        },
        fallbacks=[

        ],
        allow_reentry=True
    )
