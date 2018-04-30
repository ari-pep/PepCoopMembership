# -*- coding: utf-8 -*-
from c3smembership.mail_utils import (
    get_template_text,
    format_date,
    get_email_footer,
    get_salutation,
)
import customization as c


def make_signature_reminder_email(member):
    '''
    a mail body to remind membership applicants
    to send the form with their signature
    '''
    return (
        get_template_text('signature_reminder_subject', member.locale),
        get_template_text('signature_reminder_body', member.locale).format(
            salutation=get_salutation(member),
            submission_date=format_date(
                member.date_of_submission,
                member.locale),
            footer=get_email_footer(member.locale)))


def make_payment_reminder_email(member):
    '''
    a mail body to remind membership applicants
    to send the payment for their shares
    '''
    reminder_params=dict(
        salutation=get_salutation(member),
        submission_date=format_date(
            member.date_of_submission,
            member.locale),
        shares_value=int(member.num_shares) * c.share_price + member.entry_fee,
        shares_count=member.num_shares,
        transfer_purpose=u'C3Shares ' + member.email_confirm_code,
        # ToDo: this is a hack for de/en only. Have proper l10n
        # leave the ' '(space) at end of string
        entry_fee_snippet=u'entry fee and the ' if member.locale == 'en' else u'das Eintrittsgeld und deine ',
        footer=get_email_footer(member.locale)
    )

    return (
        get_template_text('payment_reminder_subject', member.locale),
        get_template_text('payment_reminder_body', member.locale).format(**reminder_params)
    )
