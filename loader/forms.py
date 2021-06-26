from django import forms

class LoaderForm(forms.Form):
    #used to upload simple files to our app.
    formdata = forms.FileField()
