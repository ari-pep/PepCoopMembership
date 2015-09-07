# -*- coding: utf-8 -*-
"""
This module holds code for membership dues functionality.

- Send email to a member:
  - request transferral of membership dues.
  - also send link to invoice PDF.
- Produce an invoice PDF when member clicks her invoice link.
- Batch-send email to n members.
- When dues transfer arrives, book it to member.
- When member asks for reduction of dues fee, let staff handle it:
  - set a new reduced amount
  - send email with update: reversal invoice and new invoice
"""
from datetime import datetime
import os
# import envoy
import subprocess
import tempfile
from pyramid.httpexceptions import HTTPFound
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.response import Response
from pyramid.view import view_config

from c3smembership.models import (
    C3sMember,
    DBSession,
    Dues15Invoice,
)

from .membership_dues_texts import (
    dues_invoice_mailbody_normal_de,
    dues_invoice_mailbody_normal_en,
    dues_invoice_mailbody_investing_de,
    dues_invoice_mailbody_investing_en,
    dues_legalentities_de,
    dues_legalentities_en,
    # dues_receipt_mail_de,
    # dues_receipt_mail_en,
    dues_update_reduction_de,
    dues_update_reduction_en,
    dues_exemption_de,
    dues_exemption_en,
)

DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


def make_random_string():
    """
    a random string used as dues token
    """
    import random
    import string
    return u''.join(
        random.choice(
            string.ascii_uppercase
        ) for x in range(10))


def calculate_partial_dues(member):
    """
    helper function:
    calculate dues depending on quarter of entry date
    """
    loc = member.locale
    if member.membership_date < datetime(2015, 4, 1):
        # first quarter of 2015 or earlier
        _start = u"ganzes Jahr" if 'de' in loc else u"whole year"
        _amount = "50"
    elif member.membership_date < datetime(2015, 7, 1):
        # second quarter of 2015 or earlier
        _start = u"ab Quartal 2" if 'de' in loc else u"from 2nd quarter"
        _amount = "37,50"
    elif member.membership_date < datetime(2015, 10, 1):
        # third quarter of 2015 or earlier
        _start = u"ab Quartal 3" if 'de' in loc else u"from 3rd quarter"
        _amount = "25"
    elif member.membership_date >= datetime(2015, 10, 1):
        # third quarter of 2015 or earlier
        _start = u"ab Quartal 4" if 'de' in loc else u"from 4th quarter"
        _amount = "12,50"
    return (_start, _amount)


@view_config(
    permission='manage',
    route_name='send_dues_invoice_email')
def send_dues_invoice_email(request, m_id=None):
    """
    Send email to a member to prompt her to pay the membership dues.
    - For normal members, also send link to invoice.
    - For investing members that are legal entities,
      ask for additional support depending on yearly turnover.

    This view function works both if called via URL, e.g. /dues_invoice/123
    and if called as a function with a member id as parameter.
    The latter is useful for batch processing.

    When this function is used for the first time for one member,
    some database fields are filled:
    - Invoice number
    - Invoice amount (calculated from date of membership approval by the board)
    - Invoice token
    Also, the database table of invoices (and cancellations) is appended.

    If this function gets called the second time for a member,
    no new invoice is produced, but the same mail sent again.
    """
    # either we are given a member id via url or function parameter
    try:  # view was called via http/s
        _m_id = request.matchdict['member_id']
        _batch = False
    except:  # ...or was called as function with parameter (see batch)
        _m_id = m_id
        _batch = True

    try:  # get member from DB
        _m = C3sMember.get_by_id(_m_id)
        assert(_m is not None)
    except:
        if not _batch:
            # print("member with id {} not found in DB!".format(_m_id))
            request.session.flash(
                "member with id {} not found in DB!".format(_m_id),
                'message_to_staff')
            return HTTPFound(request.route_url('toolbox'))

    # sanity check:is this a member?
    try:
        assert(_m.membership_accepted)  # must be accepted member!
    except:
        request.session.flash(
            "member {} not accepted by the board!".format(_m_id),
            'message_to_staff')
        # print("member {} not accepted by the board!".format(_m_id))
        return HTTPFound(request.route_url('toolbox'))

    # check if invoice no already exists.
    #     if yes: just send that email again!
    #     also: offer staffers to cancel this invoice

    if _m.dues15_invoice is True:
        # print("found existing invoice! NOT creating a new one, ",
        #      "just re-sending email")
        _i = Dues15Invoice.get_by_invoice_no(_m.dues15_invoice_no)
        _m.dues15_invoice_date = datetime.now()

    else:  # if no invoice already exists:
        # make dues token and ...
        randomstring = make_random_string()
        # check if dues token is already used
        while (C3sMember.check_for_existing_dues15_token(randomstring)):
            # create a new one, if the new one already exists in the database
            randomstring = make_random_string()  # pragma: no cover

        # prepare invoice number
        try:
            # either we already have an invoice number for that client...
            _invoice_no = _m.dues15_invoice_no
            assert _invoice_no is not None
        except:
            # ... or we create a new one and save it
            # get max invoice no from db
            _max_invoice_no = C3sMember.get_max_dues15_invoice_no()
            # print("got max invoice no {}".format(_max_invoice_no))
            # use the next free number, save it to db
            _new_invoice_no = int(_max_invoice_no) + 1
            # print("using invoice no {}".format(_m.invoice_no))
            DBSession.flush()  # save dataset to DB

        # calculate dues amount (maybe partial, depending on quarter)
        dues_start, dues_amount = calculate_partial_dues(_m)

        '''
        now we have enough info to update the member info
        and persist invoice info for bookkeeping
        '''
        # store some info in DB/member table
        _m.dues15_invoice = True
        _m.dues15_invoice_no = _new_invoice_no
        _m.dues15_invoice_date = datetime.now()
        # _m.dues15_invoice_no ???
        _m.dues15_token = randomstring
        _m.dues15_start = dues_start
        _m.dues15_amount = dues_amount

        if 'normal' in _m.membership_type:  # only for normal members
            # store some more info about invoice in invoice table
            _i = Dues15Invoice(
                invoice_no=_m.dues15_invoice_no,
                invoice_no_string=(
                    u'C3S-dues2015-' + str(_m.dues15_invoice_no).zfill(4)),
                invoice_date=_m.dues15_invoice_date,
                invoice_amount=u'' + _m.dues15_amount,
                member_id=_m.id,
                membership_no=_m.membership_number,
                email=_m.email,
                token=_m.dues15_token,
            )
            DBSession.add(_i)
        DBSession.flush()

    # now: prepare that email
    """
    only normal (not investing) members *have to* pay the dues.
    only the normal members get an invoice link and PDF produced for them.
    only investing legalentities are asked for more support.
    """
    if 'investing' not in _m.membership_type:
        # choose subject and body template depending on language
        if 'de' in _m.locale:
            _mail_subject = u"Mitgliedsbeiträge C3S SCE - Rechnung"
            _mail_template = dues_invoice_mailbody_normal_de
        else:
            _mail_subject = u"Membership contributions C3S SCE - invoice"
            _mail_template = dues_invoice_mailbody_normal_en
        # prepare invoice URL
        _invoice_url = (
            request.route_url(
                'make_dues_invoice_no_pdf',
                email=_m.email,
                code=_m.dues15_token,
                i=str(_m.dues15_invoice_no).zfill(4)
            )
        )
        # construct a message to send
        message = Message(
            subject=_mail_subject,
            sender='yes@office.c3s.cc',
            recipients=[_m.email],
            body=_mail_template.format(
                _m.firstname,  # {0}
                _m.lastname,  # {1}
                _i.invoice_no_string,  # {2}
                _m.dues15_amount,  # {3}
                _invoice_url,  # {4}
                _m.dues15_start,  # {5}
            ),
            extra_headers={
                'Reply-To': 'yes@c3s.cc',
            }
        )
    elif 'investing' in _m.membership_type:
        # choose subject, body template and snippet depending on language
        if 'de' in _m.locale:
            _mail_subject = (u"Mitgliedsbeiträge C3S SCE – "
                             u"Bitte um Unterstützung")
            _mail_template = dues_invoice_mailbody_investing_de
            _dues_legalentities = dues_legalentities_de
        else:
            _mail_subject = u"Membership C3S SCE – a call for support"
            _mail_template = dues_invoice_mailbody_investing_en
            _dues_legalentities = dues_legalentities_en

        # construct a message to send
        message = Message(
            subject=_mail_subject,
            sender='yes@office.c3s.cc',
            recipients=[_m.email],
            body=_mail_template.format(
                _m.firstname,  # {0}
                _m.lastname,  # {1}
                'C3S-dues2015-' + str(_m.dues15_invoice_no).zfill(4),  # {2}
                _dues_legalentities if _m.is_legalentity else '',  # {3}
            ),
            extra_headers={
                'Reply-To': 'yes@c3s.cc',
            }
        )

    # print to console or send mail
    if 'true' in request.registry.settings['testing.mail_to_console']:
        print(message.body.encode('utf-8'))  # pragma: no cover
    else:
        mailer = get_mailer(request)
        mailer.send(message)

    # now choose where to redirect
    if 'detail' in request.referrer:
        return HTTPFound(
            request.route_url(
                'detail',
                memberid=_m.id) +
            '#dues15')
    else:
        return HTTPFound(request.route_url(  # pragma: no cover
            'membership_listing_backend',
            number=request.cookies['on_page'],
            order=request.cookies['order'],
            orderby=request.cookies['orderby']) +
                         '#member_' + str(_m.id))


@view_config(
    permission='manage',
    route_name='send_dues_invoice_batch'
)
def send_dues_invoice_batch(request):
    """
    Send dues invoice to n members at the same time (batch processing).

    The number (n) is configurable, defaults to 5.
    """
    try:  # how many to process?
        n = int(request.matchdict['number'])
    except:
        n = 5
    if 'submit' in request.POST:
        # print("request.POST: {}".format(request.POST))
        try:
            n = int(request.POST['number'])
        except:  # pragma: no cover
            n = 5

    _invoicees = C3sMember.get_dues_invoicees(n)
    # print("got {} invitees".format(len(_invoicees)))

    if len(_invoicees) == 0:
        request.session.flash('no invoicees left. all done!',
                              'message_to_staff')
        return HTTPFound(request.route_url('toolbox'))

    _num_sent = 0
    _ids_sent = []

    for _m in _invoicees:

        # print(u"invoicee {} {}".format(_m.firstname, _m.lastname))

        send_dues_invoice_email(request=request, m_id=_m.id)

        _num_sent += 1
        _ids_sent.append(_m.id)

    request.session.flash(
        "sent out {} mails (to members with ids {})".format(
            _num_sent, _ids_sent),
        'message_to_staff')

    return HTTPFound(request.route_url('toolbox'))


# @view_config(
#     permission='manage',
#     route_name='send_dues_receipt_mail'
# )
# def send_dues_receipt_mail(request):
#     """
#     When membership dues for a member were received,
#     reception is checked in the backend
#     and a receipt email is send to that member.
#     """
#     _m_id = request.matchdict['member_id']
#     try:
#         _m = C3sMember.get_by_id(_m_id)
#     except:
#         print("member with id {} not found in DB!".format(_m_id))
#         return HTTPFound(request.route_url('toolbox'))

#     message = Message(
#         subject=(u'[C3S] membership dues received '
#                  u'/ Mitgliedsbeitrag eingegangen'),
#         sender='yes@office.c3s.cc',
#         recipients=[_m.email],
#         body=dues_receipt_mail.format(
#             _m.firstname,
#             _m.lastname,
#         ),
#         extra_headers={
#             'Reply-To': 'yes@c3s.cc',
#         }
#     )
#     if 'true' in request.registry.settings['testing.mail_to_console']:
#         # ^^ yes, a little ugly, but works; it's a string
#         # print "printing mail"
#         # print(message.subject)
#         # print(message.body)
#         print(message.body.encode('utf-8'))
#     else:
#         # print "sending mail"
#         mailer = get_mailer(request)
#         mailer.send(message)
#     return HTTPFound(request.route_url('toolbox'))


# @view_config(route_name='make_dues_invoice_pdf')  # retired!
# def make_dues_invoice_pdf(request):  # retired! use make_dues_invoice_no_pdf
#     """
#     Superseeded by make_dues_invoice_no_pdf
#
#     Create an invoice PDF on the fly.
#
#     This view checks supplied information (in URL) against info in database
#     and conditionally returns
#     - an error message or
#     - a PDF as receipt
#     """
#     _email = request.matchdict['email']
#     _code = request.matchdict['code']
#     # if DEBUG:
#     # print("email: {}, code: {}".format(_email, _code))
#
#     try:
#         _m = C3sMember.get_by_dues15_token(_code)
#         # print _m
#         assert _m.dues15_token == _code
#         assert _m.email == _email
#
#     except:
#         request.session.flash(
#             u"This member and token did not match!",
#             'message_to_user'  # message queue for user
#         )
#         return HTTPFound(request.route_url('error_page'))
#
#     # return a pdf file
#     pdf_file = make_dues_pdf_pdflatex(_m)
#     response = Response(content_type='application/pdf')
#     pdf_file.seek(0)  # rewind to beginning
#     response.app_iter = open(pdf_file.name, "r")
#     return response


@view_config(route_name='make_dues_invoice_no_pdf')
def make_dues_invoice_no_pdf(request):
    """
    Create invoice PDFs on-the-fly.

    This view checks supplied information (in URL) against info in database
    and OBreturns
    - an error message OR
    - a PDF as receipt
    """
    _email = request.matchdict['email']
    _code = request.matchdict['code']
    _i = request.matchdict['i']
    # if DEBUG:
    # print("email: {}, code: {}, invoice: {}".format(_email, _code, _i))

    try:
        _m = C3sMember.get_by_dues15_token(_code)
        # print _m
        assert _m.dues15_token == _code
        assert _m.email == _email
    except:
        request.session.flash(
            u"This member and token did not match!",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))

    try:
        _inv = Dues15Invoice.get_by_invoice_no(
            _i.lstrip('0'))
        assert _inv is not None
    except:
        request.session.flash(
            u"No invoice found!",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))

    # sanity check: invoice token must match with token
    try:
        assert(_inv.token == _code)
    except:
        request.session.flash(
            u"Token did not match!",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))
    # return a pdf file
    pdf_file = make_dues_pdf_pdflatex(_m, _inv)
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")
    return response


def make_dues_pdf_pdflatex(_member, _inv=None):
    """
    This function uses pdflatex to create a PDF
    as receipt for the members membership dues.

    default output is the current invoice.
    if _i_no is suplied, the relevant invoice number is produced
    """

    DEBUG = True

    # directory of pdf and tex files
    # pdflatex_dir = tempfile.mkdtemp()
    pdflatex_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../../certificate/'
        ))
    # print("the dir: {}".format(pdflatex_dir))

    # pdf backgrounds
    pdf_backgrounds = {
        'blank': pdflatex_dir + '/' + 'Urkunde_Hintergrund_blank.pdf',
    }

    # latex templates
    latex_templates = {
        # 'generic': pdflatex_dir + '/' + 'membership_dues_receipt.tex',
        'generic': pdflatex_dir + '/' + 'dues15_invoice_de_v0.2.tex',
        'generic_en': pdflatex_dir + '/' + 'dues15_invoice_en_v0.2.tex',
    }

    # choose background and template
    _bg = 'blank'
    _tpl = 'generic' if 'de' in _member.locale else 'generic_en'

    # pick background and template
    bg_pdf = pdf_backgrounds[_bg]
    tpl_tex = latex_templates[_tpl]

    # pick temporary file for pdf
    receipt_pdf = tempfile.NamedTemporaryFile(prefix='invoice_', suffix='.pdf')
    # print("the receipt_pdf.name: {}".format(receipt_pdf.name))

    (_path, _filename) = os.path.split(receipt_pdf.name)
    _filename = os.path.splitext(_filename)[0]

    # print("the _filename: {}".format(_filename))
    # print('#*'*60)
    # print("_inv: {}".format(_inv))
    # print("_inv.invoice_no: {}".format(_inv.invoice_no))

    if _inv is None:  # maybe exclude from tests?
        # this branch is deprecated, because we always supply an invoice number
        # use invoice no from member record
        _invoice_no = str(_member.dues15_invoice_no).zfill(4)
        _invoice_date = _member.dues15_invoice_date
        # print("got invoice no from db: {}".format(_invoice_no))
    else:
        # use invoice no from URL
        _invoice_no = str(_inv.invoice_no).zfill(4)
        # print("got invoice no from URL: {}".format(_invoice_no))
        _invoice_date = _inv.invoice_date.strftime('%d. %m. %Y')

    # print("member.dues15_reduced is {}".format(_member.dues15_reduced))
    # print("member.dues15_amount_reduced is {}".format(
    #    _member.dues15_amount_reduced))

    # set variables for tex command
    _tex_vars = {
        'personalFirstname': _member.firstname,
        'personalLastname': _member.lastname,
        'personalAddressOne': _member.address1,
        'personalAddressTwo': _member.address2,
        'personalPostCode': _member.postcode,
        'personalCity': _member.city,
        'personalMShipNo': _member.membership_number,
        'invoiceNo': str(_invoice_no).zfill(4),  # leading zeroes!
        'invoiceDate': _invoice_date,
        'duesStart': _member.dues15_start,
        'duesAmount': _inv.invoice_amount,
        # _member.dues15_amount_reduced if (
        #     _member.dues15_reduced) else _member.dues15_amount,
        'lang': 'de',
        'pdfBackground': bg_pdf,
    }

    # generate tex command for pdflatex
    tex_cmd = u''
    for key, val in _tex_vars.iteritems():
        # print(u"key: {}".format(key))
        # print(u"val: {}".format(val))
        # tex_cmd += '\\newcommand{\\%s}{%s}' % (key, val)
        tex_cmd += '\\newcommand{\\%s}{%s}' % (key, val)
    tex_cmd += '\\input{%s}' % tpl_tex
    tex_cmd = u'"'+tex_cmd+'"'

    # print(u"the tex_cmd: {}".format(tex_cmd))

    # generate pdf
    # _command = 'pdflatex -jobname {} -output-directory {} '.format(
    #     _filename,
    #     _path
    # )
    # _command += tex_cmd.encode('latin_1')
    # _command += tex_cmd.encode('utf-8')
    # print("------------------- the command:")
    # print _command
    # print("------------------- end of command.")

    # XXX: try to find out, why utf-8 doesn't work on debian
    FNULL = open(os.devnull, 'w')  # hide output here ;-)
    # r = envoy.run(_command)
    pdflatex_output = subprocess.call(
        [
            'pdflatex',
            '-jobname', _filename,
            '-output-directory', _path,
            '-interaction', 'nonstopmode',
            '-halt-on-error',
            tex_cmd.encode('latin_1')
        ],
        stdout=FNULL, stderr=subprocess.STDOUT,
        cwd=pdflatex_dir
    )

    if DEBUG:
        # print("status code: ".format(r.status_code))
        # print("std out: {}".format(r.std_out))
        # print("std err: {}".format(r.std_err))
        # print("the output: {}".format(pdflatex_output))
        pdflatex_output
        pass

    # cleanup
    _aux = os.path.join(_path, _filename+'.aux')
    if os.path.isfile(_aux):
        os.unlink(_aux)
    # _log = os.path.join(_path, _filename+'.log')
    # if os.path.isfile(_log):
    #    os.unlink(_log)

    return receipt_pdf


@view_config(
    route_name='dues15_listing',
    permission='manage',
    renderer='c3smembership:templates/dues15_list.pt'
)
def dues15_listing(request):
    """
    a listing of all invoices for the 2015 dues run.
    shall show both active/valid and cancelled/invalid invoices.
    """
    # get them all from the DB
    _dues15_invoices = Dues15Invoice.get_all()
    from datetime import date
    _today = date.today()

    return {
        'count': len(_dues15_invoices),
        '_today': _today,
        'invoices': _dues15_invoices,
    }


@view_config(
    route_name='dues15_reduction',
    permission='manage',
    renderer='c3smembership:templates/dues15_list.pt'
)
def dues15_reduce(request):
    """
    reduce a members dues upon valid request to do so.

    * change payable amount for member
    * cancel old invoice by issuing a cancellation
    * issue a new invoice with the new amount

    this will only work for *normal* members.
    """
    _m_id = request.matchdict['member_id']
    _reduced_amount = request.POST['amount']

    try:
        _m = C3sMember.get_by_id(_m_id)
        assert _m.membership_accepted
        assert 'investing' not in _m.membership_type
    except:
        request.session.flash(
            u"No member OR not accepted OR not normal member",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))

    # sanity checks
    if _reduced_amount == _m.dues15_amount_reduced:
        request.session.flash(
            u"Auf diesen Beitrag wurde schon reduziert!",
            'dues15_message_to_staff'  # message queue for user
        )
        return HTTPFound(
            request.route_url('detail', memberid=_m.id)
            + '#dues15')

    # prepare: get highest invoice no from db
    _max_invoice_no = C3sMember.get_max_dues15_invoice_no()

    # things to be done:
    # * change dues amount for that member
    # * cancel old invoice by issuing a reversal invoice
    # * issue a new invoice with the new amount

    _current_amount = _m.dues15_amount_reduced if (
        _m.dues15_amount_reduced is not None) else _m.dues15_amount

    _m.dues15_reduced = True
    _m.dues15_amount_reduced = _reduced_amount
    request.session.flash('reduction to {}'.format(_reduced_amount),
                          'dues15_message_to_staff')

    _old_invoice = Dues15Invoice.get_by_invoice_no(_m.dues15_invoice_no)
    _old_invoice.is_cancelled = True

    # prepare reversal invoice number
    _new_invoice_no = _max_invoice_no + 1
    # create reversal invoice
    _reversal_invoice = Dues15Invoice(
        invoice_no=_new_invoice_no,
        invoice_no_string=(
            u'C3S-dues2015-' + str(_new_invoice_no).zfill(4)) + '-S',
        invoice_date=datetime.today(),
        invoice_amount=u'-' + str(_current_amount),
        member_id=_m.id,
        membership_no=_m.membership_number,
        email=_m.email,
        token=_m.dues15_token,
    )
    _reversal_invoice.preceding_invoice_no = _old_invoice.invoice_no
    _reversal_invoice.is_reversal = True
    # print("the old invoice id: {}".format(_old_invoice.invoice_no))
    # print("reversal invoice id: {}".format(_reversal_invoice.id))
    DBSession.add(_reversal_invoice)
    DBSession.flush()
    _old_invoice.succeeding_invoice_no = _new_invoice_no

    _new_invoice = Dues15Invoice(
        invoice_no=_new_invoice_no + 1,
        invoice_no_string=(
            'C3S-dues2015-' + str(_new_invoice_no + 1).zfill(4)),
        invoice_date=datetime.today(),
        invoice_amount=u'' + str(_reduced_amount),
        member_id=_m.id,
        membership_no=_m.membership_number,
        email=_m.email,
        token=_m.dues15_token,
    )
    _new_invoice.preceding_invoice_no = _reversal_invoice.invoice_no
    _reversal_invoice.succeeding_invoice_no = _new_invoice_no + 1
    DBSession.add(_new_invoice)

    # in the members record, store the current invoice no
    _m.dues15_invoice_no = _new_invoice_no + 1

    DBSession.flush()  # persist newer invoices
    # print("reversal invoice id: {}".format(_reversal_invoice.id))
    # print("the new invoice id: {}".format(_new_invoice.id))

    # print("created reversal invoice with no {} and id {}".format(
    #     _reversal_invoice.invoice_no, _reversal_invoice.id,))
    # print("created new invoice with no {} and id {}".format(
    #    _new_invoice.invoice_no, _new_invoice.id,))

    # choose subject and body template depending on language
    if 'de' in _m.locale:
        _mail_subject = u"Mitgliedsbeiträge C3S SCE - Rechnungsupdate"
        _mail_template = dues_update_reduction_de
    else:
        _mail_subject = u"Membership contributions C3S SCE - invoice update"
        _mail_template = dues_update_reduction_en
    # prepare invoice URLs
    _reversal_url = (
        request.route_url(
            'make_dues_invoice_no_pdf',
            email=_m.email,
            code=_m.dues15_token,
            i=_reversal_invoice.invoice_no
        )
    )
    _invoice_url = (
        request.route_url(
            'make_dues_invoice_no_pdf',
            email=_m.email,
            code=_m.dues15_token,
            i=_new_invoice_no + 1
        )
    )

    # now send member a mail!
    update = Message(
            subject=_mail_subject,
            sender='yes@office.c3s.cc',
            recipients=[_m.email],
            body=_mail_template.format(
                _m.firstname,  # {0}
                _m.lastname,  # {1}
                'C3S-dues2015-' + str(_m.dues15_invoice_no).zfill(4),  # {2}
                # 'C3S-dues2015-' + str(_m.dues15_invoice_no),  # {2}
                _m.dues15_amount,  # {3}
                _reversal_url,  # {4}
                _invoice_url,  # {5}
            ),
            extra_headers={
                'Reply-To': 'yes@c3s.cc',
            }

    )
    request.session.flash('update email was sent to user!',
                          'dues15_message_to_staff')

    # print to console or send mail
    if 'true' in request.registry.settings['testing.mail_to_console']:
        print(update.body.encode('utf-8'))  # pragma: no cover
    else:
        mailer = get_mailer(request)
        mailer.send(update)

    return HTTPFound(
        request.route_url(
            'detail',
            memberid=_m_id) +
        '#dues15')


@view_config(
    route_name='make_reversal_invoice_pdf',
    permission='manage')
def make_reversal_invoice_pdf(request):
    """
    This view checks supplied information (in URL) against info in database
    -- especially the invoice number --
    and conditionally returns
    - an error message or
    - a PDF
    """
    # print('#'*60)
    # print('# this is make_reversal_invoice_pdf')

    _email = request.matchdict['email']
    _code = request.matchdict['code']
    _no = request.matchdict['no']
    # if DEBUG:
    # print("email: {}, code: {}, number: {}".format(
    #     _email, _code, _no))

    try:
        _m = C3sMember.get_by_email(_email)[0]
        # print _m
        # print('_m.dues15_token: {}'.format(
        #     _m.dues15_token))
        assert _m.dues15_token == _code

    except:
        request.session.flash(
            u"This member and token did not match!",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))

    try:
        _inv = Dues15Invoice.get_by_invoice_no(_no)
        # import pdb
        # pdb.set_trace()
        assert _inv is not None
    except:
        request.session.flash(
            u"Token did not match!",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))

    # sanity check: invoice token must match with token
    try:
        assert(_inv.token == _code)
    except:
        request.session.flash(
            u"No invoice found!",
            'message_to_user'  # message queue for user
        )
        return HTTPFound(request.route_url('error_page'))

    # print("# now handing it over to make_dues_pdf_pdflatex...")
    # print('#'*60)

    # return a pdf file
    pdf_file = make_storno_pdf_pdflatex(_m, _inv)
    response = Response(content_type='application/pdf')
    pdf_file.seek(0)  # rewind to beginning
    response.app_iter = open(pdf_file.name, "r")
    return response


def make_storno_pdf_pdflatex(_member, _inv=None):
    """
    This function uses pdflatex to create a PDF
    as reversal invoice: cancel and balance out a formar invoice.
    """

    DEBUG = True

    pdflatex_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../../certificate/'
        ))
    # pdf backgrounds
    pdf_backgrounds = {
        'blank': pdflatex_dir + '/' + 'Urkunde_Hintergrund_blank.pdf',
    }

    # latex templates
    latex_templates = {
        # 'generic': pdflatex_dir + '/' + 'membership_dues_receipt.tex',
        'generic': pdflatex_dir + '/' + 'dues15_storno_de_v0.1.tex',
        'generic_en': pdflatex_dir + '/' + 'dues15_storno_en_v0.1.tex',
    }

    # choose background and template
    _bg = 'blank'
    _tpl = 'generic' if 'de' in _member.locale else 'generic_en'

    # pick background and template
    bg_pdf = pdf_backgrounds[_bg]
    tpl_tex = latex_templates[_tpl]

    # pick temporary file for pdf
    receipt_pdf = tempfile.NamedTemporaryFile(prefix='storno_', suffix='.pdf')

    (_path, _filename) = os.path.split(receipt_pdf.name)
    _filename = os.path.splitext(_filename)[0]

    _invoice_no = str(_inv.invoice_no).zfill(4)
    # print("got invoice no from db: {}".format(_invoice_no))
    # print("got locale from db: {}".format(_member.locale))
    # set variables for tex command
    _tex_vars = {
        'personalFirstname': _member.firstname,
        'personalLastname': _member.lastname,
        'personalAddressOne': _member.address1,
        'personalAddressTwo': _member.address2,
        'personalPostCode': _member.postcode,
        'personalCity': _member.city,
        'personalMShipNo': _member.membership_number,
        'invoiceNo': _invoice_no,
        # 'duesStart': dues_start,
        'duesAmount': _inv.invoice_amount,
        'origInvoiceRef': ('C3S-dues2015-' +
                           str(_inv.preceding_invoice_no).zfill(4) + '-S'),
        'lang': 'de',
        'pdfBackground': bg_pdf,
    }

    # generate tex command for pdflatex
    tex_cmd = u''
    for key, val in _tex_vars.iteritems():
        # print(u"key: {}, val: {}".format(key,val))
        # tex_cmd += '\\newcommand{\\%s}{%s}' % (key, val)
        tex_cmd += '\\newcommand{\\%s}{%s}' % (key, val)
    tex_cmd += '\\input{%s}' % tpl_tex
    tex_cmd = u'"'+tex_cmd+'"'

    # print(u"the tex_cmd: {}".format(tex_cmd))

    # generate pdf
    # _command = 'pdflatex -jobname {} -output-directory {} '.format(
    #     _filename,
    #     _path
    # )
    # _command += tex_cmd.encode('latin_1')
    # _command += tex_cmd.encode('utf-8')
    # print("------------------- the command:")
    # print _command
    # print("------------------- end of command.")

    # XXX: try to find out, why utf-8 doesn't work on debian
    FNULL = open(os.devnull, 'w')  # hide output here ;-)
    # r = envoy.run(_command)
    pdflatex_output = subprocess.call(
        [
            'pdflatex',
            '-jobname', _filename,
            '-output-directory', _path,
            '-interaction', 'nonstopmode',
            '-halt-on-error',
            tex_cmd.encode('latin_1')
        ],
        stdout=FNULL, stderr=subprocess.STDOUT,
        cwd=pdflatex_dir
    )

    if DEBUG:
        # print("status code: ".format(r.status_code))
        # print("std out: {}".format(r.std_out))
        # print("std err: {}".format(r.std_err))
        # print("the output: {}".format(pdflatex_output))
        pdflatex_output
        pass

    # cleanup
    _aux = os.path.join(_path, _filename+'.aux')
    if os.path.isfile(_aux):
        os.unlink(_aux)
    # _log = os.path.join(_path, _filename+'.log')
    # if os.path.isfile(_log):
    #    os.unlink(_log)

    return receipt_pdf