# .rel attribute is now deprecated, using remote_field instead if not .rel
def get_rel(field):
    if hasattr(field, "rel") and field.rel:
        return field.rel
    elif hasattr(field, "remote_field") and field.remote_field:
        return field.remote_field
    return None


class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        # post_save.connect(reset_state, sender=self.__class__,
        #    dispatch_uid='%s-DirtyFieldsMixin-sweeper' % self.__class__.__name__)
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self):
        return dict(
            [
                (lambda fname: (fname, f.to_python(getattr(self, fname))))(
                    f.name + "_id" if get_rel(f) else f.name
                )
                for f in self._meta.local_fields
            ]
        )

    def get_dirty_fields(self):
        new_state = self._as_dict()

        return dict(
            [
                (key, value)
                for key, value in list(self._original_state.items())
                if value != new_state[key]
            ]
        )

    def is_dirty(self):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk:
            return True
        return {} != self.get_dirty_fields()


def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()
