# -*- coding: utf-8  -*-
from c3smembership.gnupg_encrypt import encrypt_with_gnupg
from c3smembership.presentation.i18n import _
import customization
from fdfgen import forge_fdf
from pyramid_mailer.message import (
    Message,
    Attachment,
)
import subprocess
import tempfile
import time
import customization as c

DEBUG = False
# DEBUG = True


country_codes = [
    ('AT', _(u'Austria')),
    ('BE', _(u'Belgium')),
    ('BG', _(u'Bulgaria')),
    ('CH', _(u'Switzerland')),
    ('CZ', _(u'Czech Republic')),
    ('DE', _(u'Germany')),
    ('DK', _(u'Denmark')),
    ('ES', _(u'Spain')),
    ('EE', _(u'Estonia')),
    ('FI', _(u'Finland')),
    ('FR', _(u'France')),
    ('GB', _(u'United Kingdom')),
    ('GR', _(u'Greece')),
    ('HU', _(u'Hungary')),
    ('HR', _(u'Croatia')),
    ('IE', _(u'Ireland')),
    ('IS', _(u'Iceland')),
    ('IT', _(u'Italy')),
    ('LT', _(u'Lithuania')),
    ('LI', _(u'Liechtenstein')),
    ('LV', _(u'Latvia')),
    ('LU', _(u'Luxembourg')),
    ('MT', _(u'Malta')),
    ('NL', _(u'Netherlands')),
    ('NO', _(u'Norway')),
    ('PL', _(u'Poland')),
    ('PT', _(u'Portugal')),
    ('SK', _(u'Slovakia')),
    ('SI', _(u'Slovenia')),
    ('SE', _(u'Sweden')),
    ('XX', _(u'other'))
]

# locale_codes = request.registry.settings[
#    'available_languages'].split()
locale_codes = [
    (u'de', _(u'Deutsch')),
    (u'en', _(u'Englisch')),
    (u'fr', _(u'Français')),
]


def generate_pdf(appstruct):
    """
    this function receives an appstruct
    (a datastructure received via formsubmission)
    and prepares and returns a PDF using pdftk
    """
    DEBUG = False

    fdf_file = tempfile.NamedTemporaryFile()
    pdf_file = tempfile.NamedTemporaryFile()

    # import logging
    # log = logging.getLogger(__name__)
    # log.info("test ...! ")

    import os
    here = os.path.dirname(__file__)
    registration_form_template = os.path.join(here,
                                    "../customization/registrationForm/current-{}.pdf")

    try:
        pdf_to_be_used =registration_form_template.format(appstruct['locale'])
        open(pdf_to_be_used)
    except IOError:
        # deliberatly error out if fallback does not exist
        pdf_to_be_used = registration_form_template.format(customization.default_language)
        open(pdf_to_be_used)


    # convert the date in date_of_birth
    # print(
    #    "generate_pdf: appstruct: date of birth: %s") % (
    #        appstruct['date_of_birth'])
    # print(
    #    "generate_pdf: type of appstruct: date of birth: %s") % type(
    #        appstruct['date_of_birth'])
    # print(
    #    "generate_pdf: str of appstruct: date of birth: %s") % str(
    #        appstruct['date_of_birth'])
    # print("appstruct: date of birth: %s") % appstruct['date_of_birth']
    # print("appstruct: date of submission: %s") % appstruct[
    #    'date_of_submission']
    dob_ = time.strptime(str(appstruct['date_of_birth']), '%Y-%m-%d')
    # print("generate_pdf: date of birth: %s") % dob_
    dob = time.strftime("%d.%m.%Y", dob_)
    # print("generate_pdf: date of birth: %s") % dob
    # dos_ = time.strptime(
    #    str(appstruct['date_of_submission']),
    #    '%Y-%m-%d %H:%M:%S'
    # )
    # print("generate_pdf: date of submission: %s") % dos_
    dos = str(appstruct['date_of_submission'])
    # print("generate_pdf: date of submission: %s") % dos
    # print("generate_pdf: type of date of birth: %s") % type(dob)
    # print("generate_pdf: date of birth: %s") % dob

    # membership_type
    # FieldType: Button
    # FieldName: MembershipType
    # FieldFlags: 49152
    # FieldValue: 2
    # FieldJustification: Left
    # FieldStateOption: 1
    # FieldStateOption: 2
    # FieldStateOption: Off
    # print("the membership type: %s" % appstruct['membership_type'])

    # calculate the amount to be transferred
    # print("the amount: %s" % (appstruct['num_shares'] * 50))
    amount = str(appstruct['num_shares'] * 10)

# here we gather all information from the supplied data to prepare pdf-filling

    from datetime import datetime

    fields = [ (k, appstruct[k]) for k in ('firstname',  'lastname',  'address1',
                'address2',  'postcode',  'city', 'email',  'country',  'num_shares', ) ]

    if len(c.membership_types   ) > 1:
        fields.append(('MembershipType', '1' if appstruct[
            'membership_type'] == u'normal' else '2'))

    if len(c.membership_fees)>1:
        memberTypeIndex=[ i for i,(v,t,d) in enumerate(c.membership_fees) if t==appstruct['member_type']][0]
        if memberTypeIndex == len(c.membership_fees) - 1:
            fields.append(('freeFee',appstruct['fee']))
        else:
            fields.append(('member_type',memberTypeIndex+1))

    fields.extend((
        ('dateofbirth', dob),
        ('submitted', dos),
        ('generated', str(datetime.now())),
        ('code', appstruct['email_confirm_code']),
        ('code2', appstruct['email_confirm_code']),  # for page 2
        ('amount', amount),  # for page 2
    ))

# generate fdf string

    fdf = forge_fdf("", fields, [], [], [])

# write it to a file

    if DEBUG:  # pragma: no cover
        print("== prepare: write fdf")

    fdf_file.write(fdf)
    fdf_file.seek(0)  # rewind to beginning

# process the PDF, fill in prepared data

    if DEBUG:  # pragma: no cover
        print("== PDFTK: fill_form & flatten")

        print("running pdftk...")
    pdftk_output = subprocess.call(
        [
            'pdftk',
            pdf_to_be_used,  # input pdf with form fields
            'fill_form', fdf_file.name,  # fill in values
            'output', pdf_file.name,  # output file
            'flatten',  # make form read-only
            # 'verbose'  # be verbose?
        ]
    )

    if DEBUG:  # pragma: no cover
        print(pdf_file.name)
    pdf_file.seek(0)

    if DEBUG:  # pragma: no cover
        print("===== pdftk output ======")
        print(pdftk_output)

    # return a pdf file
    from pyramid.response import Response
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")

    return response


def generate_csv(appstruct):
    """
    returns a csv with the relevant data
    to ease import of new data sets
    """
    from datetime import date
    import unicodecsv
    # format:
    # date; signature; firstname; lastname; email;
    # city; country; invest_member; opt_URL; opt_band; date_of_birth;
    # composer; lyricist; producer; remixer; dj;
    # member_of_colsoc; name_of_colsoc; noticed_dataProtection

    csv = tempfile.TemporaryFile()
    csvw = unicodecsv.writer(csv, encoding='utf-8')
    fields = (
        date.today().strftime("%Y-%m-%d"),  # e.g. 2012-09-02 date of subm.
        'pending...',  # #                  # has signature ?
        appstruct['firstname'],  # #    # firstname
        appstruct['lastname'],  # #    # surname
        appstruct['email'],  # #   # email
        appstruct['email_confirm_code'],
        appstruct['address1'],
        appstruct['address2'],
        appstruct['postcode'],
        appstruct['city'],
        appstruct['country'],  # # # country
        u'investing' if appstruct[
            'membership_type'] == u'investing' else u'normal',
        appstruct['date_of_birth'],
        'j' if appstruct['member_of_colsoc'] == 'yes' else 'n',
        appstruct['name_of_colsoc'].replace(',', '|'),
        appstruct['num_shares'],
    )

    csvw.writerow(fields)

    DEBUG = False
    if DEBUG:  # pragma: no cover
        # csvr = unicodecsv.reader(csv, encoding='utf-8')
        # print for debugging? seek to beginning!
        csv.seek(0)
        # print("read one line from file: %s") % csv.readline()
        # row = csvr.next()
        # print("DEBUG: the row as list: %s") % row
    csv.seek(0)
    return csv.readline()


def make_mail_body(appstruct):
    """
    construct a multiline string to be used as the emails body
    """
    # # test the types
    # for thing in [
    #     appstruct['firstname'],
    #     appstruct['lastname'],
    #     appstruct['date_of_birth'],  # .strftime("%d.%m.%Y")),  # XXX
    #     appstruct['email'],
    #     appstruct['city'],
    #     appstruct['country'],
    #     appstruct['invest_member'],
    #     appstruct['opt_URL'],
    #     appstruct['opt_band'],
    #     the_activities,
    #     appstruct['member_of_colsoc'],
    #     appstruct['name_of_colsoc'],
    #     appstruct['noticed_dataProtection'],
    # ]:
    #     print("thing: %s, type: %s") % (thing, type(thing))

    unencrypted = u"""
Yay!
we got a membership application through the form: \n
date of submission:             %s
first name:                     %s
last name:                      %s
date of birth:                  %s
email:                          %s
email confirmation code:        %s
street/no                       %s
address cont'd                  %s
postcode:                       %s
city:                           %s
country:                        %s
membership type:                %s
number of shares                %s

member of coll. soc.:           %s
  name of coll. soc.:           %s

that's it.. bye!""" % (
        appstruct['date_of_submission'],
        appstruct['firstname'],
        appstruct['lastname'],
        appstruct['date_of_birth'],  # .strftime("%d.%m.%Y")),  # XXX
        appstruct['email'],
        appstruct['email_confirm_code'],
        appstruct['address1'],
        appstruct['address2'],
        appstruct['postcode'],
        appstruct['city'],
        appstruct['country'],
        appstruct['membership_type'],
        appstruct['num_shares'],
        appstruct['member_of_colsoc'],
        appstruct['name_of_colsoc'],
    )
    if DEBUG:  # pragma: no cover
        print("the mail body: %s") % unencrypted
    return unencrypted


def accountant_mail(appstruct):
    """
    this function returns a message object for the mailer

    it consists of a mail body and an attachment attached to it
    """
    unencrypted = make_mail_body(appstruct)
    # print("accountant_mail: mail body: \n%s") % unencrypted
    # print("accountant_mail: type of mail body: %s") % type(unencrypted)
    encrypted = encrypt_with_gnupg(unencrypted)
    # print("accountant_mail: mail body (enc'd): \n%s") % encrypted
    # print("accountant_mail: type of mail body (enc'd): %s") % type(encrypted)

    message_recipient = appstruct['message_recipient']

    message = Message(
        subject="[p≡p coop] Yes! a new member",
        sender="members-admin@pep.coop",
        recipients=[message_recipient],
        body=encrypted
    )
    # print("accountant_mail: csv_payload: \n%s") % generate_csv(appstruct)
    # print(
    #    "accountant_mail: type of csv_payload: \n%s"
    # ) % type(generate_csv(appstruct))
    csv_payload_encd = encrypt_with_gnupg(generate_csv(appstruct))
    # print("accountant_mail: csv_payload_encd: \n%s") % csv_payload_encd
    # print(
    #    "accountant_mail: type of csv_payload_encd: \n%s"
    # ) % type(csv_payload_encd)

    attachment = Attachment(
        "C3S-SCE-AFM.csv.gpg", "application/gpg-encryption",
        csv_payload_encd)
    message.attach(attachment)

    return message
