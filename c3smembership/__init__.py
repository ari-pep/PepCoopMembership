# -*- coding: utf-8 -*-
"""
This module holds the main method: config and route declarations
"""

import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

from c3smembership.data.model.base import Base
from c3smembership.security.request import RequestWithUserAttribute
from c3smembership.security import (
    Root,
    groupfinder
)
from c3smembership.presentation.views.dashboard import (
    dashboard_content_size_provider
)
from c3smembership.presentation.views.membership_listing import (
    membership_content_size_provider
)
from c3smembership.i18n import enforcing_locale_negotiator


__version__ = open(os.path.join(os.path.abspath(
    os.path.dirname(__file__)), '../VERSION')).read()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy(
        's0secret!!',
        callback=groupfinder,)
    authz_policy = ACLAuthorizationPolicy()

    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory,
                          root_factory=Root)

    # using a custom request with user information
    config.set_request_factory(RequestWithUserAttribute)
    config.set_locale_negotiator(enforcing_locale_negotiator)

    config.include('pyramid_mailer')
    config.include('pyramid_chameleon')
    config.include('cornice')
    config.include('c3smembership.presentation.pagination')

    config.add_translation_dirs(
        'colander:locale/',
        'deform:locale/',
        'c3smembership:../customization/locale/')

    config.add_static_view('static_deform', 'deform:static')
    config.add_static_view(
        'static',
        'c3smembership:static', cache_max_age=3600)
    config.add_static_view(
        'docs',
        '../docs/_build/html/', cache_max_age=3600)

    config.add_subscriber('c3smembership.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.add_subscriber(
        'c3smembership.subscribers.add_base_bootstrap_template',
        'pyramid.events.BeforeRender')
    config.add_subscriber('c3smembership.subscribers.add_backend_template',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('c3smembership.subscribers.add_locale_to_cookie',
                          'pyramid.events.NewRequest')
    config.add_renderer(name='csv',
                        factory='c3smembership.renderers.CSVRenderer')

    from c3smembership.data.repository.share_repository import ShareRepository
    from c3smembership.business.share_acquisition import ShareAcquisition
    share_acquisition = ShareAcquisition(ShareRepository)
    config.registry.share_acquisition = share_acquisition

    # Membership application process
    # Step 1 (join.pt): home is /, the membership application form
    config.add_route('join', '/')
    # Step 2 (success.pt): check and edit data
    config.add_route('success', '/success')
    # Step 3 email was sent (check-mail.pt): send verification email address
    config.add_route('success_check_email', '/check_email')
    # Still step 3 (verify_password.pt): enter password
    # and step 4 (verify_password.pt): download form
    config.add_route('verify_email_password', '/verify/{email}/{code}')  # PDF
    # PDF download of Step 4.
    config.add_route('success_pdf', '/pEp_coop_SCE_AFM_{namepart}.pdf')  # download
    # confirm email address later (30c3 cases)
    config.add_route(
        'verify_afm_email',
        '/vae/{refcode}/{token}/{email}')  # verify afm email

    # applications for membership
    config.add_route('dashboard', '/dashboard')
    config.make_pagination_route(
        'dashboard',
        dashboard_content_size_provider,
        sort_property_default='id',
        page_size_default=int(
            settings.get('c3smembership.dashboard_number', 30)))

    config.add_route('dash', '/dash/{number}/{orderby}/{order}')
    config.add_route('toolbox', '/toolbox')
    config.add_route('stats', '/stats')
    config.add_route('staff', '/staff')
    # this is verboten for the time being
    # config.add_route('new_member', '/new_member')
    config.add_route('detail', '/detail/{memberid}')
    config.add_route('edit', '/edit/{_id}')

    # TODO: move application layer setup to separate module
    from c3smembership.data.repository.member_repository import (
        MemberRepository
    )
    from c3smembership.business.membership_application import (
        MembershipApplication
    )
    membership_application = MembershipApplication(MemberRepository)
    config.registry.membership_application = membership_application
    config.add_route('switch_sig', '/switch_sig/{memberid}')
    config.add_route('switch_pay', '/switch_pay/{memberid}')

    config.add_route('mail_sig_confirmation', '/mail_sig_conf/{memberid}')
    config.add_route('regenerate_pdf', '/re_C3S_SCE_AFM_{code}.pdf')
    config.add_route('mail_pay_confirmation', '/mail_pay_conf/{member_id}')
    config.add_route('mail_mail_confirmation', '/mail_mail_conf/{memberid}')
    config.add_route('mail_sig_reminder', '/mail_sig_reminder/{memberid}')
    config.add_route('mail_pay_reminder', '/mail_pay_reminder/{memberid}')
    config.add_route('delete_entry', '/delete/{memberid}')
    config.add_route('delete_afms', '/delete_afms')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    # gather missing information
    config.add_route('mail_mtype_form', '/mtype/{afmid}')  # mail link to form
    config.add_route('mtype_form', '/mtype/{refcode}/{token}/{email}')  # form
    config.add_route('mtype_thanks', '/mtype_thanks')  # thanks

    # applications for membership
    config.add_route('afms_awaiting_approval', '/afms_awaiting_approval')

    # memberships
    config.add_route('make_member', '/make_member/{afm_id}')
    config.add_route('merge_member', '/merge_member/{afm_id}/{mid}')

    config.add_route('membership_listing_backend',
                     '/memberships')
    config.make_pagination_route(
        'membership_listing_backend',
        membership_content_size_provider,
        sort_property_default='id',
        page_size_default=int(
            settings.get('c3smembership.membership_number', 30)))

    config.add_route('membership_listing_alphabetical',
                     '/aml')

    # membership list
    from c3smembership.data.repository.member_repository import (
        MemberRepository
    )
    from c3smembership.business.member_information import MemberInformation
    config.registry.member_information = MemberInformation(MemberRepository)

    config.add_route('membership_listing_date_pdf',
                     '/aml-{date}.pdf')

    config.add_route('membership_listing_aufstockers',
                     '/aml_aufstockers')

    # membership dues 2018_05
    config.add_route('send_dues18_05_invoice_email',
                     '/dues18_05_invoice/{member_id}')
    config.add_route('send_dues18_05_invoice_batch', '/dues18_05_invoice_batch')
    config.add_route('make_dues18_05_invoice_no_pdf',
                     '/dues18_05_invoice_no/{code}/C3S-dues18_05-{i}.pdf')
    config.add_route('dues18_05_reduction',
                     '/dues18_05_reduction/{member_id}')
    config.add_route('make_dues18_05_reversal_invoice_pdf',
                     '/dues18_05_reversal/{code}/C3S-dues18_05-{no}-S.pdf')
    config.add_route('dues18_05_notice', '/dues18_05_notice/{member_id}')
    config.add_route('dues18_05_listing', '/dues18_05_listing')

    # membership dues 2018_06
    config.add_route('send_dues18_06_invoice_email',
                     '/dues18_06_invoice/{member_id}')
    config.add_route('send_dues18_06_invoice_batch', '/dues18_06_invoice_batch')
    config.add_route('make_dues18_06_invoice_no_pdf',
                     '/dues18_06_invoice_no/{code}/C3S-dues18_06-{i}.pdf')
    config.add_route('dues18_06_reduction',
                     '/dues18_06_reduction/{member_id}')
    config.add_route('make_dues18_06_reversal_invoice_pdf',
                     '/dues18_06_reversal/{code}/C3S-dues18_06-{no}-S.pdf')
    config.add_route('dues18_06_notice', '/dues18_06_notice/{member_id}')
    config.add_route('dues18_06_listing', '/dues18_06_listing')

    # membership dues 2018_07
    config.add_route('send_dues18_07_invoice_email',
                     '/dues18_07_invoice/{member_id}')
    config.add_route('send_dues18_07_invoice_batch', '/dues18_07_invoice_batch')
    config.add_route('make_dues18_07_invoice_no_pdf',
                     '/dues18_07_invoice_no/{code}/C3S-dues18_07-{i}.pdf')
    config.add_route('dues18_07_reduction',
                     '/dues18_07_reduction/{member_id}')
    config.add_route('make_dues18_07_reversal_invoice_pdf',
                     '/dues18_07_reversal/{code}/C3S-dues18_07-{no}-S.pdf')
    config.add_route('dues18_07_notice', '/dues18_07_notice/{member_id}')
    config.add_route('dues18_07_listing', '/dues18_07_listing')

    # membership dues 2018_08
    config.add_route('send_dues18_08_invoice_email',
                     '/dues18_08_invoice/{member_id}')
    config.add_route('send_dues18_08_invoice_batch', '/dues18_08_invoice_batch')
    config.add_route('make_dues18_08_invoice_no_pdf',
                     '/dues18_08_invoice_no/{code}/C3S-dues18_08-{i}.pdf')
    config.add_route('dues18_08_reduction',
                     '/dues18_08_reduction/{member_id}')
    config.add_route('make_dues18_08_reversal_invoice_pdf',
                     '/dues18_08_reversal/{code}/C3S-dues18_08-{no}-S.pdf')
    config.add_route('dues18_08_notice', '/dues18_08_notice/{member_id}')
    config.add_route('dues18_08_listing', '/dues18_08_listing')

    # membership dues 2018_09
    config.add_route('send_dues18_09_invoice_email',
                     '/dues18_09_invoice/{member_id}')
    config.add_route('send_dues18_09_invoice_batch', '/dues18_09_invoice_batch')
    config.add_route('make_dues18_09_invoice_no_pdf',
                     '/dues18_09_invoice_no/{code}/C3S-dues18_09-{i}.pdf')
    config.add_route('dues18_09_reduction',
                     '/dues18_09_reduction/{member_id}')
    config.add_route('make_dues18_09_reversal_invoice_pdf',
                     '/dues18_09_reversal/{code}/C3S-dues18_09-{no}-S.pdf')
    config.add_route('dues18_09_notice', '/dues18_09_notice/{member_id}')
    config.add_route('dues18_09_listing', '/dues18_09_listing')

    # membership dues 2018_10
    config.add_route('send_dues18_10_invoice_email',
                     '/dues18_10_invoice/{member_id}')
    config.add_route('send_dues18_10_invoice_batch', '/dues18_10_invoice_batch')
    config.add_route('make_dues18_10_invoice_no_pdf',
                     '/dues18_10_invoice_no/{code}/C3S-dues18_10-{i}.pdf')
    config.add_route('dues18_10_reduction',
                     '/dues18_10_reduction/{member_id}')
    config.add_route('make_dues18_10_reversal_invoice_pdf',
                     '/dues18_10_reversal/{code}/C3S-dues18_10-{no}-S.pdf')
    config.add_route('dues18_10_notice', '/dues18_10_notice/{member_id}')
    config.add_route('dues18_10_listing', '/dues18_10_listing')

    # membership dues 2018_11
    config.add_route('send_dues18_11_invoice_email',
                     '/dues18_11_invoice/{member_id}')
    config.add_route('send_dues18_11_invoice_batch', '/dues18_11_invoice_batch')
    config.add_route('make_dues18_11_invoice_no_pdf',
                     '/dues18_11_invoice_no/{code}/C3S-dues18_11-{i}.pdf')
    config.add_route('dues18_11_reduction',
                     '/dues18_11_reduction/{member_id}')
    config.add_route('make_dues18_11_reversal_invoice_pdf',
                     '/dues18_11_reversal/{code}/C3S-dues18_11-{no}-S.pdf')
    config.add_route('dues18_11_notice', '/dues18_11_notice/{member_id}')
    config.add_route('dues18_11_listing', '/dues18_11_listing')

    # membership dues 2018_12
    config.add_route('send_dues18_12_invoice_email',
                     '/dues18_12_invoice/{member_id}')
    config.add_route('send_dues18_12_invoice_batch', '/dues18_12_invoice_batch')
    config.add_route('make_dues18_12_invoice_no_pdf',
                     '/dues18_12_invoice_no/{code}/C3S-dues18_12-{i}.pdf')
    config.add_route('dues18_12_reduction',
                     '/dues18_12_reduction/{member_id}')
    config.add_route('make_dues18_12_reversal_invoice_pdf',
                     '/dues18_12_reversal/{code}/C3S-dues18_12-{no}-S.pdf')
    config.add_route('dues18_12_notice', '/dues18_12_notice/{member_id}')
    config.add_route('dues18_12_listing', '/dues18_12_listing')

    # TODO: move application layer setup to separate module
    from c3smembership.models import C3sMember
    from c3smembership.models import Dues18_05Invoice
    from c3smembership.data.model.base import DBSession
    from c3smembership.business.dues_invoice_archiving import (
        DuesInvoiceArchiving
    )
    from c3smembership.views.membership_dues_2018_05 import (
        make_invoice_pdf_pdflatex,
        make_reversal_pdf_pdflatex,
    )
    invoices_archive_path = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../invoices/'))
    config.registry.dues_invoice_archiving = DuesInvoiceArchiving(
        DBSession,
        C3sMember,
        Dues18_05Invoice,
        make_invoice_pdf_pdflatex,
        make_reversal_pdf_pdflatex,
        invoices_archive_path)
    config.add_route(
        'batch_archive_pdf_invoices',
        '/batch_archive_pdf_invoices')

    # utilities & wizardry
    config.add_route('plz_dist', '/plz_dist')
    config.add_route('get_member', '/members/{member_id}')
    config.add_route('error_page', '/error')  # generic error view

    # shares
    config.add_route('shares_detail', '/shares_detail/{id}')
    config.add_route('shares_edit', '/shares_edit/{id}')
    config.add_route('shares_delete', '/shares_delete/{id}')

    # membership_certificate
    config.add_route('certificate_mail', '/cert_mail/{id}')
    config.add_route('certificate_pdf', '/cert/{id}/C3S_{name}_{token}.pdf')
    config.add_route('certificate_pdf_staff', '/cert/{id}/C3S_{name}.pdf')

    # annual reports
    from c3smembership.data.repository.share_repository import ShareRepository
    from c3smembership.business.share_information import ShareInformation
    config.registry.share_information = ShareInformation(ShareRepository)
    config.add_route('annual_reporting', '/annual_reporting')

    # invite people
    config.add_route('invite_member', '/invite_member/{m_id}')
    config.add_route('invite_batch', '/invite_batch/{number}')

    # search for people
    config.add_route('search_people', '/search_people')
    config.add_route('autocomplete_people_search', '/aps/')

    # search for codes
    config.add_route('search_codes', '/search_codes')
    config.add_route('autocomplete_input_values', '/aiv/')

    config.scan()
    return config.make_wsgi_app()
