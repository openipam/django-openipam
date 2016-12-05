from django.db.models import Field, CharField


class BitField(CharField):
    def __init__(self, *args, **kwargs):
        super(BitField, self).__init__(*args, **kwargs)
        #self.validators.append(

    def get_internal_type(self):
        return 'BitField'

    def db_type(self, connection):
        return 'bit({})'.format(self.max_length)
