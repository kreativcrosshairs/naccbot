class Tender(object):
    def __init__(self, title=None, number=None, closing_date=None,
                 pdf_url=None):
        self.title = title
        self.number = number
        self.closing_date = closing_date
        self.pdf_url = pdf_url
