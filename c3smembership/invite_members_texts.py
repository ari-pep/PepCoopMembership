# -*- coding: utf-8 -*-
"""
Email creation for invitation to barcamp and general assembly.
"""
from c3smembership.mail_utils import (
    get_template_text,
    get_email_footer,
    get_salutation,
)

DEBUG = False


def make_bcga18_invitation_email(member, url):
    """
    Create email subject and body for an invitation email for members.

    Returns:
        Tuple: message subject and body in users language.
    """
    if DEBUG:  # pragma: no cover
        print(u"the member: {}".format(member))
        print(u"the member.locale: {}".format(member.locale))
        print(u"the url: {}".format(url))
        print(u"the subject: {}".format(
            get_template_text('bcga2018_invite_subject', member.locale)))
        print(u"the salutation: {}".format(get_salutation(member)))
        print(u"the footer: {}".format(get_email_footer(member.locale)))
        print(u"the body: {}".format(
            get_template_text('bcga2018_invite_body', member.locale).format(
                salutation=get_salutation(member),
                invitation_url=url,
                footer=get_email_footer(member.locale))))
    return (
        get_template_text('bcga2018_invite_subject', member.locale).rstrip(
            '\n'),  # remove newline (\n) from mail subject
        get_template_text('bcga2018_invite_body', member.locale).format(
            salutation=get_salutation(member),
            invitation_url=url,
            footer=get_email_footer(member.locale)
        )
    )
