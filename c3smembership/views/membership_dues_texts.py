# -*- coding: utf-8 -*-
"""
Email creation for invoices notifications.
"""
from c3smembership.mail_utils import (
    get_template_text,
    get_email_footer,
    get_salutation,
)


def make_dues_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues15_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_05_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_05_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_06_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_06_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_07_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_07_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_08_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_08_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_09_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_09_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_10_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_10_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))


def make_dues18_11_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_11_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues18_12_invoice_email(member, invoice, invoice_url, invoice_quarter):
    """
    Create email subject and body for an invoice notification for full
    members.
    """
    return (
        get_template_text('dues_invoice_subject', member.locale),
        get_template_text('dues_invoice_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_12_amount),
            invoice_url=invoice_url,
            invoice_quarter=invoice_quarter,
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))

def make_dues_invoice_investing_email(member):
    """
    Create email subject and body for an invoice notification for investing
    members.
    """
    return (
        get_template_text('dues_invoice_investing_subject', member.locale),
        get_template_text(
            'dues_invoice_investing_body',
            member.locale
        ).format(
            salutation=get_salutation(member),
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))


def make_dues_invoice_legalentity_email(member):
    """
    Create email subject and body for an invoice notification for legal entity
    members.
    """
    return (
        get_template_text('dues_invoice_legalentity_subject', member.locale),
        get_template_text(
            'dues_invoice_legalentity_body',
            member.locale
        ).format(
            salutation=get_salutation(member),
            legal_entity_name=member.lastname,
            membership_number=member.membership_number,
            footer=get_email_footer(member.locale)))


def make_dues_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues15_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))


def make_dues18_05_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_05_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_06_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_06_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_07_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_07_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_08_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_08_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_09_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_09_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_10_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_10_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_11_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_11_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))

def make_dues18_12_reduction_email(member, invoice, invoice_url, reversal_url):
    """
    Create email subject and body for an invoice reduction.
    """
    return (
        get_template_text('dues_reduction_subject', member.locale),
        get_template_text('dues_reduction_body', member.locale).format(
            salutation=get_salutation(member),
            dues_amount=str(member.dues18_12_amount_reduced),
            invoice_number=invoice.invoice_no_string,
            membership_number=member.membership_number,
            invoice_url=invoice_url,
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))


def make_dues_exemption_email(member, reversal_url):
    """
    Create email subject and body for an invoice exemption.
    """
    return (
        get_template_text('dues_exemption_subject', member.locale),
        get_template_text('dues_exemption_body', member.locale).format(
            salutation=get_salutation(member),
            reversal_invoice_url=reversal_url,
            footer=get_email_footer(member.locale)))
