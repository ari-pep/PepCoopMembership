# -*- coding: utf-8 -*-
"""
Handles share acquisitions.
"""

import customization as c
class ShareAcquisition(object):
    """
    Handles share acquisitions.
    """

    def __init__(self, share_repository):
        """
        Initialises the share acquisition.

        Args:
            share_repository: The share repository providing data access
                functionality for shares.
        """
        self.share_repository = share_repository

    def create(self, membership_number, shares_quantity,
               board_confirmation=None):
        """
        Creates a share acquisition.

        Args:
            membership_number: The membership number of the member for which
                the share acquisition is created.
            shares_quantity: The number of shares which are acquired.
            board_confirmation: Optional. The date on which the board of
                directors confirmed the acquisition of the shares.
        """

        if not isinstance(shares_quantity, int):
            raise ValueError(
                'The parameter "shares_quantity" must be of type "int".')
        if shares_quantity < 1 or shares_quantity > c.max_shares:
            raise ValueError(
                'The parameter "shares_quantity" must be at least 1 and at most {}'.format(c.max_shares))

        return self.share_repository.create(
            membership_number, shares_quantity, board_confirmation)

    def set_signature_reception(self, shares_id, reception_date=None):
        """
        Sets the signature reception date.

        Args:
            shares_id: The technical ID of the shares package for which the
                signature reception date is set.
            reception_date: Optional. The signature reception date to be set to
                the share process. If not specified the signature reception
                date is unset.
        """
        self.share_repository.set_signature_reception(
            shares_id,
            reception_date)

    def set_signature_confirmation(self, shares_id, confirmation_date=None):
        """
        Sets the signature reception date.

        Args:
            shares_id: The technical ID of the shares package for which the
                signature reception date is set.
            confirmation_date: Optional. The signature confirmation date to be
                set to the share process. If not specified the signature
                confirmation date is unset.
        """
        self.share_repository.set_signature_confirmation(
            shares_id, confirmation_date)

    def set_payment_reception(self, shares_id, reception_date=None):
        """
        Sets the payment confirmation of the shares package.

        Args:
            shares_id: The technical ID of the shares package for which the
                payment confirmation is set.
            reception_date: Optional. The payment reception date which is set.
                If not specified the payment reception date is unset.

        """
        self.share_repository.set_payment_reception(shares_id, reception_date)

    def set_payment_confirmation(self, shares_id, confirmation_date=None):
        """
        Sets the payment confirmation of the shares package.

        Args:
            shares_id: The technical ID of the shares package for which the
                payment confirmation is set.
            confirmation_date: Optional. The payment confirmation date which is
                set. If not specified the payment confirmation date is unset.

        """
        self.share_repository.set_payment_confirmation(
            shares_id, confirmation_date)

    def set_reference_code(self, shares_id, reference_code):
        """
        Sets the reference code of the shares package.

        Args:
            shares_id: The technical ID of the shares package for which the
                payment confirmation is set.
            reference_code: The reference code which is set.
        """
        self.share_repository.set_reference_code(shares_id, reference_code)
