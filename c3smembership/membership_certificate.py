# -*- coding: utf-8 -*-
"""
This module holds functionality to handle Membership Certificates.

- Send out email with individual links.
- Generate certificate PDFs for users.
- Generate certificate PDFs for staff.

The actual PDFs are generated using *pdflatex*.

The LaTeX templates for this have been factured out into a private repository,
because we do not want others to be able to re-create our membership
certificates and also because there are files contained
that we do not want to be public, e.g. signatures.
"""
from datetime import (
    date,
    datetime
)
import os
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.response import Response
from pyramid_mailer.message import Message
import shutil
import subprocess
import tempfile
from types import NoneType
from c3smembership.mail_utils import (
    make_membership_certificate_email,
    send_message,
)

from c3smembership.models import C3sMember
from c3smembership.tex_tools import TexTools
from c3smembership.presentation.views.membership_listing import (
    get_memberhip_listing_redirect
)

DEBUG = False


def make_random_token():
    """
    Generate a random token used to allow access to certificate.
    """
    import random
    import string
    return u''.join(
        random.choice(
            string.ascii_lowercase + string.digits
        ) for x in range(15))


@view_config(permission='manage',
             route_name='certificate_mail')
def send_certificate_email(request):
    '''
    Send email to a member with a link
    so the member can get her membership certificate.
    '''
    _special_condition = False  # for redirects to referrer

    mid = request.matchdict['id']
    member = C3sMember.get_by_id(mid)
    if isinstance(member, NoneType) or not member.is_member():
        return Response(
            'that id does not exist or is not an accepted member. go back',
            status='404 Not Found',)
    # create a token for the certificate
    member.certificate_token = make_random_token()

    email_subject, email_body = make_membership_certificate_email(
        request,
        member)

    the_message = Message(
        subject=email_subject,
        sender='members-admin@pep.coop',
        recipients=[member.email],
        body=email_body
    )
    send_message(request, the_message)

    member.certificate_email = True
    member.certificate_email_date = datetime.now()

    try:  # pragma: no cover
        if 'detail' in request.referrer:
            _special_condition = True
    except TypeError:  # pragma: no cover
        pass

    if _special_condition:  # pragma: no cover
        return HTTPFound(
            location=request.referrer +
            '#certificate'
        )
    else:
        return get_memberhip_listing_redirect(request, member.id)


@view_config(permission='view',
             route_name='certificate_pdf')
def generate_certificate(request):
    '''
    Generate a membership_certificate for a member.

    Member must posess a link containing an id and a valid token.
    Headquarters sends links to members upon request.
    '''
    mid = request.matchdict['id']
    token = request.matchdict['token']

    try:
        member = C3sMember.get_by_id(mid)

        if DEBUG:  # pragma: no cover
            print member.firstname
            print member.certificate_token
            print type(member.certificate_token)  # NoneType
            print token
            print type(token)  # unicode

        # token may not ne None
        assert(member.certificate_token is not None)
        # token must match entry in database
        assert(str(member.certificate_token) in str(token))
        # and database entry must match token
        assert(str(token) in str(member.certificate_token))

        # check age of token
        from datetime import timedelta
        two_weeks = timedelta(weeks=2)
        assert(member.certificate_email_date is not None)
        delta = datetime.now() - member.certificate_email_date
        assert(delta < two_weeks)
    except AssertionError:
        return Response(
            'Not found. Or invalid credentials.  <br /><br /> '
            'Please contact members-admin@pep.coop. <br /><br /> '
            'Nicht gefunden. Bitte mitgliederverwaltung@pep.coop kontaktieren.',
            status='404 Not Found',
        )

    if isinstance(member, NoneType) or not member.is_member():
        return Response(
            'that id does not exist or is not an accepted member. go back',
            status='404 Not Found',)

    return gen_cert(member)


@view_config(permission='manage',
             route_name='certificate_pdf_staff')
def generate_certificate_staff(request):
    '''
    Generate the membership_certificate of any member for staffers.
    '''
    mid = request.matchdict['id']
    # print("Member id from matchdict: {}".format(mid))

    # chech if member exists
    member = C3sMember.get_by_id(mid)
    if member is None:
        return Response('Not found. Please check URL.')

    if isinstance(member, NoneType) or not member.is_member():
        return Response(
            'Member with this id ({}) is not an accepted member!'.format(mid),
            status='404 Not Found',)

    return gen_cert(member)


def gen_cert(member):
    '''
    Utility function: create a membership certificate PDF file using pdflatex
    '''
    here = os.path.dirname(__file__)

    if 'de' in member.locale:
        latex_background_image = os.path.abspath(
            os.path.join(here, '../customization/certificates/Urkunde_Hintergrund_blank.pdf'))
        # latex header and footer
        latex_header_tex = os.path.abspath(
            os.path.join(here, '../customization/certificates/urkunde_header_de.tex'))
        latex_footer_tex = os.path.abspath(
            os.path.join(here, '../customization/certificates/urkunde_footer_de.tex'))
    else:
        latex_background_image = os.path.abspath(
            os.path.join(here, '../customization/certificates/Urkunde_Hintergrund_blank.pdf'))
        # latex header and footer
        latex_header_tex = os.path.abspath(
            os.path.join(here, '../customization/certificates/urkunde_header_en.tex'))
        latex_footer_tex = os.path.abspath(
            os.path.join(here, '../customization/certificates/urkunde_footer_en.tex'))

    sign_nana = os.path.abspath(
        os.path.join(here, '../customization/certificates/signNana'))

    # a temporary directory for the latex run
    tempdir = tempfile.mkdtemp()

    latex_file = tempfile.NamedTemporaryFile(
        suffix='.tex',
        dir=tempdir,
        delete=False,  # directory will be deleted anyways
    )

    # using tempfile
    pdf_file = tempfile.NamedTemporaryFile(
        dir=tempdir,
        delete=False,  # directory will be deleted anyways
    )
    pdf_file.name = latex_file.name.replace('.tex', '.pdf')

    is_founder = True if 'dungHH_' in member.email_confirm_code else False
    # prepare the certificate text
    if member.locale == 'de':  # german
        hereby_confirmed = u'Hiermit wird bestätigt, dass'
        is_member = u'Mitglied der p$\\equiv$p coop SCE ' \
                    u'mit beschränkter Haftung ist'
        one_more_share = u' und einen weiteren Geschäftsanteil übernommen hat'
        several_shares = u' weitere Geschäftsanteile übernommen hat'
        and_block = u' und '
        if is_founder:
            confirm_date = (
                u'Der Beitritt erfolgte im Rahmen der Gründung am 17.04.2018')
        else:
            confirm_date = u'Der Beitritt wurde am {} zugelassen'.format(
                datetime.strftime(member.membership_date, '%d.%m.%Y'))
        mship_num = u'Die Mitgliedsnummer lautet {}.'.format(
            member.membership_number
        )
        mship_num_text = u'Mitgliedsnummer {}'.format(
            member.membership_number
        )
        exec_dir = u'Geschäftsführender Direktor'

    else:  # default fallback is english
        hereby_confirmed = u'This is to certify that'
        is_member = u'is a member of the >>p$\\equiv$p coop SCE mit beschränkter Haftung<<'
        one_more_share = u' and has subscribed to one additional share'
        several_shares = u'additional shares'
        and_block = u' and has subscribed to'
        if is_founder:
            confirm_date = (
                u'Membership was acquired as a founding member '
                'on the 17th of April 2018')
        else:
            confirm_date = u'Registered on the {}'.format(
                datetime.strftime(member.membership_date, '%Y-%m-%d'))
        mship_num = u'The membership number is {}.'.format(
            member.membership_number
        )
        mship_num_text = u'membership number {}'.format(
            member.membership_number
        )
        exec_dir = 'Executive Director'

    # construct latex_file
    latex_data = '''
\\input{%s}
\\def\\backgroundImage{%s}
\\def\\txtBlkHerebyConfirmed{%s}
\\def\\firstName{%s}
\\def\\lastName{%s}
\\def\\addressOne{%s}
\\def\\postCode{%s}
\\def\\city{%s}
\\def\\numShares{%s}
\\def\\numAddShares{%s}
\\def\\txtBlkIsMember{%s}
\\def\\txtBlkMembershipNumber{%s}
\\def\\txtBlkConfirmDate{%s}
\\def\\signDate{%s}
\\def\\signNana{%s}
\\def\\txtBlkCEO{%s}
\\def\\txtBlkMembershipNum{%s}
    ''' % (
        latex_header_tex,
        latex_background_image,
        hereby_confirmed,
        TexTools.escape(member.firstname),
        TexTools.escape(member.lastname),
        TexTools.escape(member.address1),
        TexTools.escape(member.postcode),
        TexTools.escape(member.city),
        member.num_shares,
        member.num_shares-1,
        is_member,
        TexTools.escape(mship_num),
        confirm_date,
        (
            datetime.strftime(date.today(), "%d.%m.%Y")
            if member.locale == 'de'
            else date.today()),
        sign_nana,
        exec_dir,
        mship_num_text
    )
    if DEBUG:  # pragma: no cover
        print('#'*60)
        print(member.is_legalentity)
        print(member.lastname)
        print('#'*60)
    if member.is_legalentity:
        latex_data += '\n\\def\\company{%s}' % TexTools.escape(member.lastname)
    if member.address2 is not u'':  # add address part 2 iff exists
        latex_data += '\n\\def\\addressTwo{%s}' % TexTools.escape(
            member.address2)
    if member.num_shares > 1:  # how many shares?
        if member.num_shares == 2:  # iff member has exactely two shares...
            latex_data += '\n\\def\\txtBlkAddShares{%s.}' % one_more_share
        if member.num_shares > 2:  # iff more than two
            latex_data += '\n\\def\\txtBlkAddShares{%s %s %s.}' % (
                and_block,
                member.num_shares-1,
                several_shares
            )
    else:  # iff member has exactely one share..
        latex_data += '\n\\def\\txtBlkAddShares{.}'

    # finish the latex document
    latex_data += '\n\\input{%s}' % latex_footer_tex

    if DEBUG:  # pragma: no cover
        print '*' * 70
        print('*' * 30, 'latex data: ', '*' * 30)
        print '*' * 70
        print latex_data
        print '*' * 70
    latex_file.write(latex_data.encode('utf-8'))
    latex_file.seek(0)  # rewind

    # pdflatex latex_file to pdf_file
    # pdflatex_output =
    subprocess.call(
        [
            'pdflatex',
            '-interaction=nonstopmode',
            '-output-directory=%s' % tempdir,
            latex_file.name
        ],
        stdout=open(os.devnull, 'w'),
        stderr=subprocess.STDOUT  # hide output
    )

    # return a pdf file
    response = Response(content_type='application/pdf')
    response.app_iter = open(pdf_file.name, "r")
    shutil.rmtree(tempdir, ignore_errors=True)  # delete temporary directory
    return response
