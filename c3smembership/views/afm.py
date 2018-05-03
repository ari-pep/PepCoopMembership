# -*- coding: utf-8 -*-
"""
This module holds the views for membership acquisition,
aka 'Application for Membership' (afm).

- join_c3s: the membership application form
- show_success: confirm data supplied
- success_check_email: send email with link
- success_verify_email: verify email address, present PDF link
- show_success_pdf: let user download her pdf for printout

Tests for these functions can be found in

- test_views_webdriver.py:JoinFormTests (webdriver: no coverage)
- test_views_webdriver.py:EmailVerificationTests (webdriver: no coverage)
- test_webtest.py (with coverage)

"""

from datetime import (
    date,
    datetime,
)
import logging
from types import NoneType

import colander
from colander import (
    Invalid,
    Range,
)
import deform
from deform import ValidationFailure
from c3smembership.deform_text_input_slider_widget import (
    TextInputSliderWidget
)

from pyramid.i18n import (
    get_locale_name,
)
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_mailer.message import Message
)

from types import NoneType
from c3smembership.data.model.base import DBSession
from c3smembership.models import C3sMember
from c3smembership.presentation.i18n import (
    _,
    ZPT_RENDERER,
)
from c3smembership.utils import (
    generate_pdf,
    accountant_mail,
)
import customization

DEBUG = False
LOGGING = True

if LOGGING:
    LOG = logging.getLogger(__name__)


def statute_validator(node, value):
    """
    Validator for statute confirmation.
    """
    if not value:
        # raise without additional error message as the description
        # already explains the necessity of the checkbox
        raise Invalid(node, u'')


def dues_regulations_validator(node, value):
    """
    Validator for dues regulations confirmation.
    """
    if not value:
        # raise without additional error message as the description
        # already explains the necessity of the checkbox
        raise Invalid(node, u'')


@view_config(renderer='c3smembership:templates/join.pt',
             route_name='join')
def join_c3s(request):
    """
    This is the main membership application form view: Join C3S as member
    """
    # if another language was chosen by clicking on a flag
    # the add_locale_to_cookie subscriber has planted an attr on the request
    if hasattr(request, '_REDIRECT_'):

        _query = request._REDIRECT_
        # set language cookie
        # ToDo: the proper cookie name is _LOCALE_ (pyramid)
        request.response.set_cookie('locale', _query)
        request.locale = _query
        locale_name = _query
        return HTTPFound(location=request.route_url('join'),
                         headers=request.response.headers)
    else:
        locale_name = get_locale_name(request)

    if DEBUG:
        print "-- locale_name: " + str(locale_name)

    # set default of Country select widget according to locale
    try:
        country_default = customization.locale_country_mapping.get(locale_name)
    except AttributeError:
        print(dir(customization))
        country_default = 'GB'

    if DEBUG:
        print("== locale is :" + str(locale_name))
        print("== choosing :" + str(country_default))

    class PersonalData(colander.MappingSchema):
        """
        colander schema for membership application form
        """
        firstname = colander.SchemaNode(
            colander.String(),
            title=_(u"(Real) First Name"),
            oid="firstname",
        )
        lastname = colander.SchemaNode(
            colander.String(),
            title=_(u"(Real) Last Name"),
            oid="lastname",
        )
        email = colander.SchemaNode(
            colander.String(),
            title=_(u'Email Address'),
            validator=colander.Email(),
            oid="email",
        )
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.CheckedPasswordWidget(size=20),
            title=_(u'Password (to protect access to your data)'),
            description=_(u'We need a password to protect your data. After '
                          u'verifying your email you will have to enter it.'),
            oid='password',
        )
        address1 = colander.SchemaNode(
            colander.String(),
            title=_(u'Address Line 1')
        )
        address2 = colander.SchemaNode(
            colander.String(),
            missing=unicode(''),
            title=_(u'Address Line 2')
        )
        postcode = colander.SchemaNode(
            colander.String(),
            title=_(u'Postal Code'),
            oid="postcode"
        )
        city = colander.SchemaNode(
            colander.String(),
            title=_(u'City'),
            oid="city",
        )
        country = colander.SchemaNode(
            colander.String(),
            title=_(u'Country'),
            default=country_default,
            widget=deform.widget.SelectWidget(
                values=country_codes),
            oid="country",
        )
        date_of_birth = colander.SchemaNode(
            colander.Date(),
            title=_(u'Date of Birth'),
            # css_class="hasDatePicker",
            widget=deform.widget.DatePartsWidget(),
            default=date(2013, 1, 1),
            validator=Range(
                min=date(1913, 1, 1),
                # max 18th birthday, no minors through web formular
                max=date(
                    date.today().year-18,
                    date.today().month,
                    date.today().day),
                min_err=_(
                    u'Sorry, but we do not believe that the birthday you '
                    u'entered is correct.'),
                max_err=_(
                    u'Unfortunately, the membership application of an '
                    u'underaged person is currently not possible via our web '
                    u'form. Please send an email to office@c3s.cc.')
            ),
            oid="date_of_birth",
        )
        locale = colander.SchemaNode(colander.String(),
                                       widget=deform.widget.HiddenWidget(),
                                       default=locale_name)

    class MembershipInfo(colander.Schema):
        """
        Basic member information.
        """
        yes_no = ((u'yes', _(u'Yes')),
                  (u'no', _(u'No')))
        if len(customization.membership_types) > 1:
            membership_type = colander.SchemaNode(
                colander.String(),
                title=_(u'I want to become a ... '
                        u'(choose membership type, see C3S SCE statute sec. 4)'),
                description=_(u'choose the type of membership.'),
                widget=deform.widget.RadioChoiceWidget(
                    values=( (i['name'],i['description']) for i in
                        customization.membership_types ),
                ),
                oid='membership_type'
            )
        if customization.enable_colsoc_association:
            member_of_colsoc = colander.SchemaNode(
                colander.String(),
                title=_(
                    u'Currently, I am a member of (at least) one other '
                    u'collecting society.'),
                validator=colander.OneOf([x[0] for x in yes_no]),
                widget=deform.widget.RadioChoiceWidget(values=yes_no),
                oid="other_colsoc",
                # validator=colsoc_validator
            )
            name_of_colsoc = colander.SchemaNode(
                colander.String(),
                title=_(u'If so, which one(s)? Please separate multiple '
                        u'collecting societies by comma.'),
                description=_(
                    u'Please tell us which collecting societies '
                    u'you are a member of. '
                    u'If more than one, please separate them by comma.'),
                missing=unicode(''),
                oid="colsoc_name",
        )


    class Fees(colander.Schema):
        member_type = colander.SchemaNode( colander.String(),
            title=_(u'Please tell us wether you\'re an individual, '
                    u'freelancer or company or want to support us '
                    u'generously as a sustaining member'),
            widget=deform.widget.RadioChoiceWidget(values=[ (member_type, t_description) for fee, member_type, t_description in customization.membership_fees]),
            oid='member_type'
        )

        # not validating here: depends on ^
        # http://deformdemo.repoze.org/require_one_or_another/
        member_custom_fee = colander.SchemaNode(colander.Decimal('1.00'),
            title=_(u'custom membership fee'),
            widget=deform.widget.MoneyInputWidget(symbol=customization.currency,showSymbol=True, defaultZero=True),
            description=_(u'Sustaining members: You can set your fees (minimum 100 €)'),
            oid='membership_custom_fee',
            default=customization.membership_fee_custom_min,
            validator=Range(min=customization.membership_fee_custom_min,max=None,min_err=_(u'please enter at least the minimum fee for sustaining members'))
        )


    class Shares(colander.Schema):
        """
        the number of shares a member wants to hold

        this involves a slider widget: added to deforms widgets.
        see README.Slider.rst
        """
        num_shares = colander.SchemaNode(
            colander.Integer(),
            title=_(u"I want to buy the following number "
                    u"of Shares (50 € each, up to 3000 €, see "
                    u"C3S statute sec. 5)"),
            description=_(
                u'You can choose any amount of shares between 1 and 60.'),
            default="1",
            widget=TextInputSliderWidget(
                size=3, css_class='num_shares_input'),
            validator=colander.Range(
                min=1,
                max=60,
                min_err=_(u'You need at least one share of 50 €.'),
                max_err=_(u'You may choose 60 shares at most (3000 €).'),
            ),
            oid="num_shares")

    class TermsInfo(colander.Schema):
        """
        some legal requirements
        """

        got_statute = colander.SchemaNode(
            colander.Bool(true_val=u'yes'),
            #title=(u''),
            title=_(
                u'I acknowledge that the statutes and membership dues '
                u'regulations determine periodic contributions '
                u'for full members.'),
            label=_(
                u'An electronic copy of the statute of the '
                u'C3S SCE has been made available to me (see link below).'),
            description=_(
                u'You must confirm to have access to the statute.'),
            widget=deform.widget.CheckboxWidget(),
            validator=statute_validator,
            required=True,
            oid='got_statute',
        )

        got_dues_regulations = colander.SchemaNode(
            colander.Bool(true_val=u'yes'),
            title=(u''),
            label=_(
                u'An electronic copy of the temporary membership dues '
                u'regulations of the C3S SCE has been made available to me '
                u'(see link below).'),
            description=_(
                u'You must confirm to have access to the temporary '
                u'membership dues regulations.'),
            widget=deform.widget.CheckboxWidget(),
            validator=dues_regulations_validator,
            required=True,
            oid='got_dues_regulations',
        )

    class MembershipForm(colander.Schema):
        """
        The Form consists of
        - Personal Data
        - Membership Information
        - Shares
        """
        person = PersonalData(title=_(u'Personal Data'))
        if len(customization.membership_types) > 1 or customization.enable_colsoc_association :
            membership_info = MembershipInfo(title=_(u'Membership Data'))

        shares = Shares(title=_(u'Shares'))

        if customization.membership_fees:
            fees = Fees(title=_(u'Membership Fees'))

        acknowledge_terms = TermsInfo(title=_(u'Acknowledgement'))

    schema = MembershipForm()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Next')),
            deform.Button('reset', _(u'Reset'))
        ],
        use_ajax=True,
        renderer=ZPT_RENDERER
    )

    # if the form has NOT been used and submitted, remove error messages if any
    if 'submit' not in request.POST:
        request.session.pop_flash()

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)

            # data sanity: if not in collecting society, don't save
            #  collsoc name even if it was supplied through form
            if customization.membership_types and len(customization.membership_types) > 1 and 'no' in appstruct['membership_info']['member_of_colsoc']:
                appstruct['membership_info']['name_of_colsoc'] = ''

        except ValidationFailure as validation_failure:
            request.session.flash(
                _(u'Please note: There were errors, '
                  u'please check the form below.'),
                'message_above_form',
                allow_duplicate=False)

            # If the validation error was not caused by the password field,
            # manually set an error to the password field because the user
            # needs to re-enter it after a validation error.
            form = validation_failure.field
            if form['person']['password'].error is None:
                form['person']['password'].error = Invalid(
                    None,
                    _(
                        u'Please re-enter your password. For security '
                        u'reasons your password is not cached and therefore '
                        u'needs to be re-entered in case of validation '
                        u'issues.'
                    ))
                validation_failure = ValidationFailure(form, None, form.error)

            return {'form': validation_failure.render()}

        # redirect to success page, then return the PDF
        # first, store appstruct in session
        request.session['appstruct'] = appstruct
        request.session['appstruct']['locale'] = \
            appstruct['person']['locale']
        # empty the messages queue (as validation worked anyways)
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        return HTTPFound(  # redirect to success page
            location=request.route_url('success'),
        )

    # if the form was submitted and gathered info shown on the success page,
    # BUT the user wants to correct their information:
    else:
        # remove annoying message from other session
        deleted_msg = request.session.pop_flash()
        del deleted_msg
        if 'appstruct' in request.session:
            appstruct = request.session['appstruct']
            # pre-fill the form with the values from last time
            form.set_appstruct(appstruct)

    html = form.render()

    return {'form': html}


@view_config(renderer='c3smembership:templates/success.pt',
             route_name='success')
def show_success(request):
    """
    This view shows a success page with the data gathered through the form
    and a link (button) back to the form
    in case some data is wrong/needs correction.
    There is also a button to confirm the dataset
    and have an email set to the user for validation.
    """
    # check if user has used the form or 'guessed' this URL
    if 'appstruct' in request.session:
        # we do have valid info from the form in the session
        appstruct = request.session['appstruct']
        # delete old messages from the session (from invalid form input)
        request.session.pop_flash('message_above_form')
        return {
            'firstname': appstruct['person']['firstname'],
            'lastname': appstruct['person']['lastname'],
        }
    # 'else': send user to the form
    return HTTPFound(location=request.route_url('join'))


@view_config(
    renderer='c3smembership:templates/check-mail.pt',
    route_name='success_check_email')
def success_check_email(request):
    """
    This view is called from the page that shows a user her data for correction
    by clicking a "send email" button.
    This view then sends out the email with a verification link
    and returns a note to go check mail.
    """
    # check if user has used the form (good) or 'guessed' this URL (bad)

    if 'appstruct' in request.session:

        appstruct = request.session['appstruct']

        def make_random_string():
            """
            used as email confirmation code
            """
            import random
            import string
            return u''.join(
                random.choice(
                    string.ascii_uppercase + string.digits
                ) for x in range(10))

        # make confirmation code and
        email_confirm_code = make_random_string()
        # check if confirmation code is already used
        while C3sMember.check_for_existing_confirm_code(email_confirm_code):
            # create a new one, if the new one already exists in the database
            email_confirm_code = make_random_string()  # pragma: no cover

        # to store the data in the DB, an objet is created
        member = C3sMember(
            firstname=appstruct['person']['firstname'],
            lastname=appstruct['person']['lastname'],
            email=appstruct['person']['email'],
            password=appstruct['person']['password'],
            address1=appstruct['person']['address1'],
            address2=appstruct['person']['address2'],
            postcode=appstruct['person']['postcode'],
            city=appstruct['person']['city'],
            country=appstruct['person']['country'],
            locale=appstruct['person']['locale'],
            date_of_birth=appstruct['person']['date_of_birth'],
            email_is_confirmed=False,
            email_confirm_code=email_confirm_code,
            date_of_submission=datetime.now(),
            membership_type=appstruct['membership_info']['membership_type'],
            member_of_colsoc=(
                appstruct['membership_info']['member_of_colsoc'] == u'yes'),
            name_of_colsoc=appstruct['membership_info']['name_of_colsoc'],
            num_shares=appstruct['shares']['num_shares'],
        )
        DBSession().add(member)

        # we do have valid info from the form in the session (good)
        appstruct = request.session['appstruct']
        try:
            mailer = request.registry.get_mailer(request)
        except:
            return HTTPFound(location=request.route_url('join'))

        the_mail_body = customization.address_confirmation_mail.get(appstruct['person']['locale'],'en')
        the_mail = Message(
            subject=request.localizer.translate(_(
                'check-email-paragraph-check-email-subject',
                default=u'C3S: confirm your email address and load your PDF')),
            sender="noreply@c3s.cc",
            recipients=[appstruct['person']['email']],
            body=the_mail_body.format(
                appstruct['person']['firstname'],
                appstruct['person']['lastname'],
                request.registry.settings['c3smembership.url'],
                appstruct['person']['email'],
                email_confirm_code
            )
        )
        if 'true' in request.registry.settings['testing.mail_to_console']:
            LOG.info(the_mail.subject)
            LOG.info(the_mail.recipients)
            LOG.info(the_mail.body)
            # just logging, not printing, b/c test fails otherwise:
            # env/bin/nosetests
            #    c3smembership/tests/test_views_webdriver.py:
            #    JoinFormTests.test_form_submission_de
        else:
            mailer.send(the_mail)

        # make the session go away
        request.session.invalidate()
        return {
            'firstname': appstruct['person']['firstname'],
            'lastname': appstruct['person']['lastname'],
        }
    # 'else': send user to the form
    return HTTPFound(location=request.route_url('join'))


@view_config(
    renderer='c3smembership:templates/verify_password.pt',
    route_name='verify_email_password')
def success_verify_email(request):
    """
    This view is called via links sent in mails to verify mail addresses.
    It extracts both email and verification code from the URL.
    It will ask for a password
    and checks if there is a match in the database.

    If the password matches, and all is correct,
    the view shows a download link and further info.
    """
    # collect data from the URL/matchdict
    user_email = request.matchdict['email']
    confirm_code = request.matchdict['code']
    # if we want to ask the user for her password (through a form)
    # we need to have a url to send the form to
    post_url = '/verify/' + user_email + '/' + confirm_code

    if 'submit' in request.POST:
        request.session.pop_flash('message_above_form')
        request.session.pop_flash('message_above_login')
        # check for password ! ! !
        if 'password' in request.POST:
            _passwd = request.POST['password']

        # get matching dataset from DB
        member = C3sMember.get_by_code(confirm_code)  # returns member or None

        if isinstance(member, NoneType):
            # member not found: FAIL!
            not_found_msg = _(
                u"Not found. Check verification URL. "
                "If all seems right, please use the form again.")
            return {
                'correct': False,
                'namepart': '',
                'result_msg': not_found_msg,
            }

        # check if the password is valid
        try:
            correct = C3sMember.check_password(member.id, _passwd)
        except AttributeError:
            correct = False
            request.session.flash(
                _(u'Wrong Password!'),
                'message_above_login')

        # check if info from DB makes sense
        # -member

        if (member.email == user_email) and correct:
            # set the email_is_confirmed flag in the DB for this signee
            member.email_is_confirmed = True
            # dbsession.flush()
            namepart = member.firstname + member.lastname
            import re
            pdf_file_name_part = re.sub(  # replace characters
                '[^a-zA-Z0-9]',  # other than these
                '_',  # with an underscore
                namepart)

            appstruct = {
                'firstname': member.firstname,
                'lastname': member.lastname,
                'email': member.email,
                'email_confirm_code': member.email_confirm_code,
                'address1': member.address1,
                'address2': member.address2,
                'postcode': member.postcode,
                'city': member.city,
                'country': member.country,
                'locale': member.locale,
                'date_of_birth': member.date_of_birth,
                'date_of_submission': member.date_of_submission,
                # 'activity': set(activities),
                # 'invest_member': u'yes' if member.invest_member else u'no',
                'membership_type': member.membership_type,
                'member_of_colsoc':
                    u'yes' if member.member_of_colsoc else u'no',
                'name_of_colsoc': member.name_of_colsoc,
                # 'opt_band': signee.opt_band,
                # 'opt_URL': signee.opt_URL,
                'num_shares': member.num_shares,
            }
            request.session['appstruct'] = appstruct

            # log this person in, using the session
            LOG.info('verified code and password for id %s', member.id)
            request.session.save()
            return {
                'firstname': member.firstname,
                'lastname': member.lastname,
                'code': member.email_confirm_code,
                'correct': True,
                'namepart': pdf_file_name_part,
                'result_msg': _("Success. Load your PDF!")
            }
    # else: code did not match OR SOMETHING...
    # just display the form
    request.session.flash(
        _(u"Please enter your password."),
        'message_above_login',
        allow_duplicate=False
    )
    return {
        'post_url': post_url,
        'firstname': '',
        'lastname': '',
        'namepart': '',
        'correct': False,
        'result_msg': "something went wrong."
    }


@view_config(route_name='success_pdf')
def show_success_pdf(request):
    """
    Given there is valid information in the session
    this view sends an encrypted mail to C3S staff with the users data set
    and returns a PDF for the user.

    It is called after visiting the verification URL/page/view in
    def success_verify_email below.
    """
    # check if user has used form or 'guessed' this URL
    if 'appstruct' in request.session:
        # we do have valid info from the form in the session
        # send mail to accountants // prepare a mailer
        mailer = request.registry.get_mailer(request)
        # prepare mail
        appstruct = request.session['appstruct']
        message_recipient = request.registry.settings['c3smembership.mailaddr']
        appstruct['message_recipient'] = message_recipient
        the_mail = accountant_mail(appstruct)
        if 'true' in request.registry.settings['testing.mail_to_console']:
            print(the_mail.body)
        else:
            try:
                mailer.send(the_mail)
            except:
                # if mailout fails for some reason (gnupg, whatever), we need
                # 1) a mail to staff, so we take notice and fix it
                # 2) a message to $user, so she does not worry
                staff_mail = Message(
                    subject=_("[yes][ALERT] check the logs!"),
                    sender="noreply@c3s.cc",
                    recipients=['yes@c3s.cc'],
                    body="""
problems! problems!

this is {}

a user could not download her pdf, because....
maybe gnupg failed? something else?

go fix it!
                    """.format(request.registry.settings['c3smembership.url']))
                mailer.send(staff_mail)

                request.session.flash(_(
                    u"Oops. we hit a bug. Staff will be "
                    u"informed. We will come back to you "
                    u"once we fixed it!",
                    'message_to_user')  # msg queue f. user
                )
                return HTTPFound(request.route_url('error_page'))

        return generate_pdf(request.session['appstruct'])
    # 'else': send user to the form
    return HTTPFound(location=request.route_url('join'))
