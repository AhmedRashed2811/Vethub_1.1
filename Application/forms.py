
# ? -------------------------------------------------------------------------------------------------------IMPORTING LIBRARIES
from django.forms import ModelForm
from .models import *


class SupportTeamMessageForm(ModelForm):
    class Meta:
        model = SupportTeamMessage
        fields = ['message']
        exclude = ['customer', 'date']

