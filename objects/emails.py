import smtplib
from email.headerregistry import Address
from email.message import EmailMessage


class Email(object):
    def __init__(self):
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.ehlo()
        self.server.starttls()
        self.email_address = "naccbot@gmail.com"
        self.email_password = "naccbotmail"
        self.server.login(self.email_address, self.email_password)

    def send_tender_email(self, tender, address_to):
        body = "Tender Title: {}\n\n" \
               "Tender Number: {}\n\n" \
               "Closing Date: {}\n\n" \
               "Tender Document: {}".format(tender.title,
                                            tender.number,
                                            tender.closing_date,
                                            tender.pdf_url)
        message = EmailMessage()
        message.set_content(body)
        message["Subject"] = tender.title
        message["From"] = Address("NACC Telegram Bot", "naccbot",
                                  "gmail.com")
        message["To"] = address_to

        self.server.send_message(message)
