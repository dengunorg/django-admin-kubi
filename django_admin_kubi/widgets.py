from django import forms
from django.forms.widgets import Textarea


class TinyMceEditorWidget(Textarea):
    """
    Widget providing TinyMce for Rich Text Editing.
    """
    @property
    def media(self):
        return forms.Media(
            js=(
                'tinymce/tinymce.min.js',
                'tinymce/tinymce.init.js',
            ),
        )

    def __init__(self, attrs=None):
        default_attrs = {'data-editor': 'tinymce'}
        if attrs:
            default_attrs.update(attrs)
        super(TinyMceEditorWidget, self).__init__(default_attrs)


class RichTextEditorWidget(TinyMceEditorWidget):
    pass
