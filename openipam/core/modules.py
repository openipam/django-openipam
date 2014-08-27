from django.utils.safestring import mark_safe

from admin_tools.dashboard.modules import DashboardModule


class HTMLContentModule(DashboardModule):
    title = 'HTML Content'
    template = 'admin_tools/dashboard/modules/html_content.html'
    layout = 'stacked'
    html = 'This is some HTML!'

    def init_with_context(self, context):
        if self._initialized:
            return
        self.title = mark_safe(self.title)
        self.html = mark_safe(self.html)
        self._initialized = True

    def is_empty(self):
        return True if not self.html else False
