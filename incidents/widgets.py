from django.forms.widgets import Widget
from django.utils.html import format_html
from django.forms.utils import flatatt

class MultipleFileInput(Widget):
    """
    A custom widget that allows multiple file uploads.
    This widget extends directly from Widget instead of FileInput
    to avoid Django's validation that prevents multiple file uploads.
    """
    template_name = 'django/forms/widgets/file.html'
    needs_multipart_form = True
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = 'multiple'
        attrs['type'] = 'file'
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(self.attrs.copy(), attrs)
        final_attrs['name'] = name
        return format_html('<input{}>', flatatt(final_attrs))
    
    def value_from_datadict(self, data, files, name):
        """
        Get the file objects from the FILES dictionary.
        """
        if files and name in files:
            # Return the list of files
            return files.getlist(name)
        return None
    
    def value_omitted_from_data(self, data, files, name):
        return name not in files
