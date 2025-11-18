from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def send_confirmation_professional(self, user, request):
        from allauth.account.models import EmailAddress, EmailConfirmationHMAC

        email_address = EmailAddress.objects.get(user=user)
        confirmation = EmailConfirmationHMAC(email_address)
        confirmation.send(request=request, signup=False)
