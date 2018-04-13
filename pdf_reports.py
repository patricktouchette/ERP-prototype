from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.units import inch, mm
import os

class Order_Confirmation():

    def __init__(self, pdf_file):
        self.canvas = canvas.Canvas(pdf_file, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.width, self.height = letter
        self.pdf_file = pdf_file

        self.create_header()
        self.save()

    def coord(self, x, y, unit=inch):
        x = x * unit
        y = self.height - y * unit
        return x, y

    def create_header(self):
        logo_path = 'img\\logo.png'
        logo = Image(logo_path, 2.222*inch, 1*inch)
        logo.wrapOn(self.canvas, self.width, self.height)
        logo.drawOn(self.canvas, *self.coord(.5, 1.5, inch))

        ptext = '<font size=22><b>Confirmation de commande</b></font>'
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(3.5, 1))

        ptext= '''  <font size=10>
                    <b>Client:</b> MachinMachine <br/>
                    <b>Date:</b> {}<br/>
                    <b>Adresse:</b> 5 Rue des axes,<br/>
                    Granby, QC J2J<br/>
                    <b>Tel:</b> (450) 123-1111<br/>
                    </font>
                    '''.format('01/01/2018')
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(1, 3, inch))

        ptext= '''  <font size=10>
                    <b>Fournisseur:</b> SuperShop <br/>
                    <b>Date:</b> {}<br/>
                    <b>Adresse:</b> 123 Rue des colonnes,<br/>
                    Granby, QC J2J<br/>
                    <b>Tel:</b> (450) 123-1234<br/>
                    </font>
                    '''.format('01/01/2018')
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(6, 3, inch))

        ptext= '''  <font size=10>
                    Monsieur Machin,<br/><br/>
                    Voici notre confirmation pour votre commande 123431 pour des beignes en titane<br/>
                    selon le dessin beignes_001293_revA. <br/>
                    <br/>
                    Cordialement, <br/>
                    <br/>
                    Patrick Touchette
                    </font>
                    '''.format('01/01/2018')
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(1, 5, inch))


    def save(self):
        self.canvas.save()
        os.startfile(self.pdf_file)

class Price_Quotation():

    def __init__(self, pdf_file):
        self.canvas = canvas.Canvas(pdf_file, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.width, self.height = letter
        self.pdf_file = pdf_file

        self.create_header()
        self.save()

    def coord(self, x, y, unit=inch):
        x = x * unit
        y = self.height - y * unit
        return x, y

    def create_header(self):
        logo_path = 'img\\logo.png'
        logo = Image(logo_path, 2.222*inch, 1*inch)
        logo.wrapOn(self.canvas, self.width, self.height)
        logo.drawOn(self.canvas, *self.coord(.5, 1.5, inch))

        ptext = '<font size=22><b>Soumission</b></font>'
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(3.5, 1))

        ptext= '''  <font size=10>
                    <b>Client:</b> MachinMachine <br/>
                    <b>Date:</b> {}<br/>
                    <b>Adresse:</b> 5 Rue des axes,<br/>
                    Granby, QC , J2J<br/>
                    <b>Tel:</b> (450) 123-1111<br/>
                    </font>
                    '''.format('01/01/2018')
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(1, 3, inch))

        ptext= '''  <font size=10>
                    <b>Fournisseur:</b> SuperShop <br/>
                    <b>Date:</b> {}<br/>
                    <b>Adresse:</b> 123 Rue des colonnes,<br/>
                    Granby, QC J2J<br/>
                    <b>Tel:</b> (450) 123-1234<br/>
                    </font>
                    '''.format('01/01/2018')
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(6, 3, inch))

        ptext= '''  <font size=10>
                    Monsieur Machin,<br/><br/>
                    Voici notre soumission pour l'usinage de vos beignes en titane<br/>
                    selon le dessin beignes_001293_revA.<br/><br/>
                    Prix: $1000.00 / chaque <br/>
                    Quantite: 1000 <br/>
                    Total: $1,000,000.00 <br/>
                    <br/>
                    Cordialement, <br/>
                    <br/>
                    Patrick Touchette
                    </font>
                    '''.format('01/01/2018')
        p = Paragraph(ptext, self.styles['Normal'])
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(1, 6, inch))


    def save(self):
        self.canvas.save()
        os.startfile(self.pdf_file)


if __name__ == '__main__':
    confirmation_file = 'Confirmation de commande.pdf'
    order_confirmation = Order_Confirmation(confirmation_file)
    quote_file = 'Soumission.pdf'
    quote = Price_Quotation(quote_file)
