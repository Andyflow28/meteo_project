from django import forms
from .models import UserStation, StationData

class UserStationForm(forms.ModelForm):
    class Meta:
        model = UserStation
        fields = ['station_id', 'location', 'description']
        widgets = {
            'station_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID único de la estación'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación física de la estación'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción opcional de la estación',
                'rows': 3
            }),
        }

class StationDataForm(forms.ModelForm):
    class Meta:
        model = StationData
        fields = [
            'temperatura', 'humedad', 'presion', 
            'gas_detectado', 'voltaje_mq135', 
            'indice_uv', 'nivel_uv'
        ]
        widgets = {
            'temperatura': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1',
                'placeholder': 'Temperatura en °C'
            }),
            'humedad': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1',
                'placeholder': 'Humedad relativa en %'
            }),
            'presion': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1',
                'placeholder': 'Presión atmosférica en hPa'
            }),
            'gas_detectado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'voltaje_mq135': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Voltaje del sensor MQ135'
            }),
            'indice_uv': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1',
                'placeholder': 'Índice UV'
            }),
            'nivel_uv': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nivel UV (Muy bajo, Bajo, Moderado, etc.)'
            }),
        }