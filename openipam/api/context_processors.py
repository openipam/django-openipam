from openipam.api import VERSION


def api_version(request):
    return {"ipam_api_version": VERSION}
