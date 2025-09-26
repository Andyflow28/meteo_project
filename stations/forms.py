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
            'temperature_aht20', 'humidity_aht20',
            'temperature_bmp280', 'pressure_bmp280',
            'voltage_mq2', 'digital_mq2',
            'voltage_mq135', 'digital_mq135'
        ]
        widgets = {
            'temperature_aht20': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'humidity_aht20': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'temperature_bmp280': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'pressure_bmp280': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'voltage_mq2': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'digital_mq2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'voltage_mq135': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'digital_mq135': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }