# -*- coding: utf-8 -*-
"""
This module has functionality to let staff do administrative tasks.
"""

from c3smembership.data.model.base import DBSession
from c3smembership.models import (
    C3sMember,
    C3sStaff,
    Group,
)
from c3smembership.gnupg_encrypt import encrypt_with_gnupg
from c3smembership.presentation.views.dashboard import get_dashboard_redirect
import colander
from datetime import (
    datetime,
    date
)
import deform
from deform import ValidationFailure
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    authenticated_userid,
)
from types import NoneType
from c3smembership.presentation.i18n import (
    _,
    ZPT_RENDERER,
)


DEBUG = False
LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/staff.pt',
             permission='manage',
             route_name='staff')
def staff_view(request):
    """
    This view lets admins edit staff personnel.

    - edit/change password
    - delete
    """
    _staffers = C3sStaff.get_all()

    class Staffer(colander.MappingSchema):
        login = colander.SchemaNode(
            colander.String(),
            title='login',
        )
        password = colander.SchemaNode(
            colander.String(),
            title='passwort',
        )

    schema = Staffer()

    stafferform = deform.Form(
        schema,
        buttons=[
            deform.Button('new_staffer', 'save')
        ]
    )

    if 'action' in request.POST:
        # print(request.POST['id'])
        try:
            _staffer = C3sStaff.get_by_id(int(request.POST['id']))
        except:
            return HTTPFound(location=request.route_url('staff'))
        if request.POST['action'] == u'delete':
            C3sStaff.delete_by_id(_staffer.id)
            encrypted = encrypt_with_gnupg('''hi,
%s was deleted from the backend by %s.

best,
your membership tool''' % (_staffer.login,
                           authenticated_userid(request)))
            message = Message(
                subject='[p≡p coop Yes] staff was deleted.',
                sender='members-admin@pep.coop',
                recipients=[
                    request.registry.settings['c3smembership.mailaddr']],
                body=encrypted
            )
            mailer = get_mailer(request)
            mailer.send(message)
            return HTTPFound(location=request.route_url('staff'))
        elif request.POST['action'] == 'edit':
            appstruct = {
                'login': _staffer.login,
                'password': '_UNCHANGED_',
            }
            stafferform.set_appstruct(appstruct)

    if 'new_staffer' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = stafferform.validate(controls)
        except ValidationFailure, e:
            return {
                'stafferform': e.render()
            }
        # XXX login must be unique!
        existing = C3sStaff.get_by_login(appstruct['login'])
        if existing is not None:
            if u'_UNCHANGED_' in appstruct['password']:
                pass
            else:
                existing.password = appstruct['password']
                existing.last_password_change = datetime.now()
            encrypted = encrypt_with_gnupg('''hi,
the password of %s was changed by %s.

best,
your membership tool''' % (existing.login,
                           authenticated_userid(request)))
            message = Message(
                subject='[p≡p coop Yes] staff password changed.',
                sender='members-admin@pep.coop',
                recipients=[
                    request.registry.settings['c3smembership.mailaddr']],
                body=encrypted
            )

        else:  # create new entry
            staffer = C3sStaff(
                login=appstruct['login'],
                password=appstruct['password'],
                email=u'',
            )
            staffer.groups = [Group.get_staffers_group()]
            DBSession.add(staffer)
            DBSession.flush()
            print "added staffer"
            encrypted = encrypt_with_gnupg('''hi,
%s was added to the backend by %s.

best,
your membership tool''' % (staffer.login,
                           authenticated_userid(request)))
            message = Message(
                subject='[p≡p coop Yes] staff was added.',
                sender='members-admin@pep.coop',
                recipients=[
                    request.registry.settings['c3smembership.mailaddr']],
                body=encrypted
            )
            mailer = get_mailer(request)
            mailer.send(message)

        return HTTPFound(
            request.route_url('staff')
        )

    return {
        'staffers': _staffers,
        'stafferform': stafferform.render(),
    }


@view_config(renderer='templates/delete_afms.pt',
             permission='manage',
             route_name='delete_afms')
def delete_afms(request):
    '''
    Delete a bunch of AfMs in one go.

    I wrote this while implementing mass import to ease development 8-)
    '''
    class DeleteAfMRange(colander.MappingSchema):
        first = colander.SchemaNode(
            colander.Integer(),
            title='first ID to delete'
        )
        last = colander.SchemaNode(
            colander.Integer(),
            title='last ID to delete'
        )
    schema = DeleteAfMRange()
    delete_range_form = deform.Form(
        schema,
        buttons=[deform.Button('delete_them', 'DELETE')]
    )
    if 'first' in request.POST:
        # print "form was submitted!"
        # print "first ID to delete: %s" % request.POST['first']
        controls = request.POST.items()
        try:
            appstruct = delete_range_form.validate(controls)
            _first = appstruct['first']
            _last = appstruct['last']
            assert(_first < _last)  # XXX TODO: how about just one id? test!
        except ValidationFailure, e:
            return {
                'resetform': e.render()
            }
        for i in range(_first, _last+1):
            try:
                C3sMember.delete_by_id(i)
            except:
                print 'id %s didnt exist'
        return HTTPFound(request.route_url('dashboard'))
    return {
        'delete_form': delete_range_form.render()
    }


#@view_config(permission='manage',
#             route_name='mail_mail_confirmation')
def mail_mail_conf(request):
    '''
    Send email to member to confirm her email address by clicking a link.

    Needed for applications that came in solely on paper
    and were digitalized/entered into DB by staff.
    '''
    afmid = request.matchdict['memberid']
    afm = C3sMember.get_by_id(afmid)
    if isinstance(afm, NoneType):
        request.session.flash(
            'id not found. no mail sent.',
            'messages')
        return get_dashboard_redirect(request)

    import random
    import string
    _looong_token = u''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in range(13))
    _url = (request.registry.settings['c3smembership.url'] +
            '/vae/' + afm.email_confirm_code +
            '/' + _looong_token + '/' + afm.email)

    _body = u'''[english version below]

Hallo {1} {2},

möchten wir Dich bitten uns kurz zu bestätigen, dass diese E-Mail-Adresse korrekt ist und Du auf diesem
Wege erreichbar bist. Dafür brauchst Du nur den folgenden Link aufzurufen:

  {0}

Solltest Du nicht {1} {2} sein und diese Adresse nicht bei uns angegeben haben,
antworte bitte kurz auf diese E-Mail. Dann werden wir die Adresse aus unser
Datenbank streichen.

Antworte bitte ebenfalls, falls Du die E-Mail-Adresse ändern möchtest.


Viele Grüße :: Das p≡p coop Team

++++++++++++++++++++++++++++++++++++++++++++++++++

Hello {1} {2},

please confirm your email address.

Just click the following link to confirm your address:

    {0}

If you are not {1} {2} and you didn't give this email address to us, please
reply to this email with a short explanation. Then we will remove your address
from our database.

Should you want to change your email address please reply to this mail, too.

Best wishes :: The p≡p coop Team
    '''.format(
        _url,  # {0}
        afm.firstname,  # {1}
        afm.lastname,  # {2}
    )

    log.info("mailing mail confirmation to AFM # {0}".format(afm.id))

    message = Message(
        subject=(u'[p≡p coop] Please confirm your email address! '
                 u'/ Bitte E-Mail-Adresse bestätigen!'),
        sender='members-admin@pep.coop',
        recipients=[afm.email],
        body=_body
    )
    mailer = get_mailer(request)
    mailer.send(message)
    afm.email_confirm_token = _looong_token
    afm.email_confirm_mail_date = datetime.now()
    return get_dashboard_redirect(request, afm.id)


@view_config(renderer='templates/verify-mail.pt',
             route_name='verify_afm_email')
def verify_mailaddress_conf(request):
    '''
    Let a prospective member confirm her email address by clicking a link.

    Needed for applications that came in solely on paper
    and were digitalized/entered into DB by staff.
    '''
    user_email = request.matchdict['email']
    refcode = request.matchdict['refcode']
    token = request.matchdict['token']
    # try to get entry from DB
    afm = C3sMember.get_by_code(refcode)
    if isinstance(afm, NoneType):  # no entry?
        return {
            'confirmed': False,
            'firstname': 'foo',
            'lastname': 'bar',
            'result_msg': 'bad URL / bad codes. please contact members-admin@pep.coop!',
        }
    # check token
    if ('_used' in afm.email_confirm_token):  # token was invalidated already
        return {
            'confirmed': False,
            'firstname': afm.firstname,
            'lastname': afm.lastname,
            'result_msg': ('your token is invalid. '
                           'please contact members-admin@pep.coop!'),
        }

    try:
        assert(afm.email_confirm_token in token)
        assert(token in afm.email_confirm_token)
        assert(afm.email in user_email)
        assert(user_email in afm.email)
    except:
        return {
            'confirmed': False,
            'firstname': 'foo',
            'lastname': 'bar',
            'result_msg': 'bad token/email. please contact members-admin@pep.coop!',
        }

    afm.email_is_confirmed = True
    afm.email_confirm_token += u'_used'
    DBSession.flush()
    # notify staff
    message = Message(
        subject='[p≡p coop Yes!] afm email confirmed',
        sender='members-admin@pep.coop',
        recipients=[request.registry.settings['c3smembership.mailaddr'], ],
        body=u'see {}/detail/{}'.format(
            request.registry.settings['c3smembership.url'],
            afm.id)
    )
    mailer = get_mailer(request)
    mailer.send(message)
    return {
        'confirmed': True,
        'firstname': afm.firstname,
        'lastname': afm.lastname,
        'result_msg': u'',
    }


@view_config(permission='manage',
             route_name='mail_mtype_form')
def mail_mtype_fixer_link(request):
    '''
    Send email to prospective member
    to let her set her membership type details by visiting a form.

    Was needed for crowdfunders from startnext: data was missing.
    '''
    afmid = request.matchdict['afmid']
    afm = C3sMember.get_by_id(afmid)
    if isinstance(afm, NoneType):
        request.session.flash(
            'id not found. no mail sent.',
            'messages')
        return get_dashboard_redirect(request)

    import random
    import string
    _looong_token = u''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in range(13))
    _url = (request.registry.settings['c3smembership.url'] +
            '/mtype/' + afm.email_confirm_code +
            '/' + _looong_token + '/' + afm.email)

    from .mail_mtype_util import make_mtype_email_body
    _body = make_mtype_email_body(afm, _url)

    log.info("mailing membership status form link to AFM # %s" % afm.id)

    if afm.locale == 'de':
        _subject = u'[p≡p coop] Hilfe benötigt: Dein Mitgliedschaftsstatus'
    else:
        _subject = u'[p≡p coop] Help needed: Your Membership Status'

    message = Message(
        subject=_subject,
        sender='members-admin@pep.coop',
        recipients=[
            afm.email,
            request.registry.settings['c3smembership.mailaddr']],
        body=_body
    )
    mailer = get_mailer(request)
    mailer.send(message)
    afm.mtype_confirm_token = _looong_token
    afm.mtype_email_date = datetime.now()
    afm.membership_type = u'pending'
    return get_dashboard_redirect(request, afm.id)


@view_config(renderer='templates/mtype-form.pt',
             route_name='mtype_form')
def membership_status_fixer(request):
    '''
    Let a prospective member confirm her email address by filling a form.

    Was needed for crowdfunders from startnext: data was missing.
    '''
    user_email = request.matchdict['email']
    refcode = request.matchdict['refcode']
    token = request.matchdict['token']
    # try to get entry from DB
    afm = C3sMember.get_by_code(refcode)
    if isinstance(afm, NoneType):  # no entry?
        request.session.flash(
            'bad URL / bad codes. please contact members-admin@pep.coop!',
            'message_above_form'
        )
        return {
            'form': '',
            'confirmed': False,
            'firstname': 'foo',
            'lastname': 'bar',
            'result_msg': 'bad URL / bad codes. please contact members-admin@pep.coop!',
        }
    if (len(afm.mtype_confirm_token) == 0) or (
            afm.mtype_confirm_token.endswith('_used')):
        request.session.flash(
            'your token is invalid. please contact members-admin@pep.coop!',
            'message_above_form'
        )
        return {
            'form': '',
            'confirmed': False,
            'result_msg': ('your token is invalid. please contact '
                           'members-admin@pep.coop!'),
        }

    try:
        print "token: {}".format(token)
        assert(afm.mtype_confirm_token in token)
        assert(token in afm.mtype_confirm_token)
        assert(afm.email in user_email)
        assert(user_email in afm.email)
    except:
        request.session.flash(
            'bad token/email. please contact members-admin@pep.coop!',
            'message_above_form')
        return {
            'form': '',
            'confirmed': False,
            'result_msg': 'bad token/email. please contact members-admin@pep.coop!',
        }

    # construct a form
    class MembershipInfo(colander.Schema):
        yes_no = ((u'yes', _(u'Yes')),
                  (u'no', _(u'No')))
        membership_type = colander.SchemaNode(
            colander.String(),
            title=_(u'I want to become a ... (choose '
                    u'membership type, see p≡p coop SCE statute sec. 4)'),
            description=_(u'choose the type of membership.'),
            widget=deform.widget.RadioChoiceWidget(
                values=(
                    (u'normal',
                     _(u'FULL member. Full members have to be natural persons '
                       u'who register at least three works with p≡p coop they '
                       u'created themselves. This applies to composers, '
                       u'lyricists and remixers. They get a vote.')),
                    (u'investing',
                     _(u'INVESTING member. Investing members can be natural '
                       u'or legal entities or private companies that do not '
                       u'register works with p≡p coop. They do not get a vote, '
                       u'but may counsel.'))
                ),
            ),
            oid="mtype",
        )
        member_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=_(
                u'Currently, I am a member of (at least) one other '
                u'collecting society.'),
            validator=colander.OneOf([x[0] for x in yes_no]),
            widget=deform.widget.RadioChoiceWidget(values=yes_no),
            oid="other_colsoc",
        )
        name_of_colsoc = colander.SchemaNode(
            colander.String(),
            title=_(u'If so, which one(s)? (comma separated)'),
            description=_(
                u'Please tell us which collecting societies '
                u'you are a member of. '
                u'If more than one, please separate them by comma(s).'),
            missing=unicode(''),
            oid="colsoc_name",
        )

    class MembershipForm(colander.Schema):
        """
        The Form consists of
        - Membership Information
        """
        membership_info = MembershipInfo(
            title=_(u"Membership Requirements")
        )

    schema = MembershipForm()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', _(u'Submit')),
            deform.Button('reset', _(u'Reset'))
        ],
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
            if 'no' in appstruct['membership_info']['member_of_colsoc']:
                appstruct['membership_info']['name_of_colsoc'] = ''
                print appstruct['membership_info']['name_of_colsoc']
                # print '-'*80

        except ValidationFailure, e:
            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{
                'confirmed': True,
                'form': e.render()}
        # all good, store the information
        afm.membership_type = appstruct['membership_info']['membership_type']
        afm.member_of_colsoc = (
            appstruct['membership_info']['member_of_colsoc'] == u'yes')
        afm.name_of_colsoc = appstruct['membership_info']['name_of_colsoc']

        # remove old messages from the session
        request.session.pop_flash()

        # invalidate token
        afm.mtype_confirm_token += u'_used'
        # # notify staff
        message = Message(
            subject='[p≡p coop Yes!] membership status confirmed',
            sender='members-admin@pep.coop',
            recipients=[
                request.registry.settings['c3smembership.mailaddr'],
            ],
            body=u'see {}/detail/{}'.format(
                request.registry.settings['c3smembership.url'],
                afm.id)
        )
        mailer = get_mailer(request)
        mailer.send(message)

        return HTTPFound(request.route_url('mtype_thanks'))

    # render the form in a template
    html = form.render()

    return {
        'form': html,
        'confirmed': True,
    }


@view_config(renderer='templates/mtype-thanks.pt',
             route_name='mtype_thanks')
def membership_status_thanks(request):
    '''
    say thanks afterwards.
    '''
    return {'foo': 'bar'}
