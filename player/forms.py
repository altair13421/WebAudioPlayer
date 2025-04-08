from django import forms


class FolderSelectWidget(forms.Widget):
    template_name = "widgets/folder_select.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["type"] = "input"
        context["widget"]["input_type"] = "file"
        context["widget"]["accept"] = "/folder"
        return context


class FolderSelectField(forms.Field):
    widget = FolderSelectWidget

    def validate(self, value):
        if not value:
            raise forms.ValidationError("Please select a folder.")

        # You can add additional validation here
        super().validate(value)


class FolderSelectForm(forms.Form):
    folder_select = FolderSelectField(required=True)
