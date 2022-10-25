from openipam.user.models import User

from dal import autocomplete


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.all()
        if self.q:
            qs = qs.filter(username__istartswith=self.q)

        return qs
