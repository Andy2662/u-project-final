from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Csv

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','password1','password2']

class medidasForm(forms.ModelForm):
    class Meta:
        model = medidas
        fields = ('test_name','observacion',)
        labels = {
            "observacion": "Observación",
            "test_name": "Nombre de la prueba"
        }

class csvForm(forms.ModelForm):
    class Meta:
        model = user_csvs
        fields = ('titulo','comentario','archivocsv')

class towerForm(forms.ModelForm):
    class Meta:
        model = torre
        fields = ('cell_id','lac','observacion','operador','torre','altura',)
        labels = {
            "observacion": "Observación",
            "cell_id": "Cell ID",
            "lac": "LAC",
            "operador": "Operador",
            "torre": "Torre",
            "Altura": "Altura",
        }

class tdataForm(forms.ModelForm):
    class Meta:
        model = torre_measure
        fields = ('test_name','observacion',)
        labels = {
            "test_name": "Nombre de la prueba",
            "observacion": "Observación",
        
        }

class tdata_from_csv(forms.ModelForm):
    class Meta:
        model = torre
        fields = ('cell_id','lac','observacion','operador','torre','altura',
                'latitud','longitud',)


class CsvModelForm(forms.ModelForm):
    class Meta:
        model = Csv
        fields = ('file_name',)
        labels = {'file_name':'Nombre del archivo para actualizar los datos de Señales'}

class CsvModelFormT(forms.ModelForm):
    class Meta:
        model = CsvT
        fields = ('file_name',)       
        labels = {'file_name':'Nombre del archivo para actualizar los datos de Torres'}            