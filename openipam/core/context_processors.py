from openipam.core.forms import FeatureRequestForm
from hashlib import md5


def gravatar(request):
    email = getattr(request.user, 'email', '')
    gravatar = None
    gravatar_hash = None

    if email:
        gravatar_hash = md5(email.lower()).hexdigest()
        gravatar = 'https://www.gravatar.com/avatar/%s/' % gravatar_hash

    return {
        'gravatar_hash': gravatar_hash,
        'gravatar': gravatar,
    }


def root_path(request):
    root_path = request.get_full_path().split('/')[1]

    return {
        'root_path': root_path
    }


def feature_form(request):
    return {
        'feature_form': FeatureRequestForm(request.POST or None)
    }
