# bodega/forms.py
from django import forms
from .models import Producto, Cliente, Distribuidor, Marca

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'epc': forms.TextInput(attrs={'class': 'form-control', 'id': 'epc-field'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'marca': forms.Select(attrs={'class': 'form-control'}),
            'distribuidor': forms.Select(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DistribuidorForm(forms.ModelForm):
    class Meta:
        model = Distribuidor
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# bodega/forms.py
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Sony, Samsung, Nike...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional de la marca...'
            }),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Marca.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe una marca con este nombre.')
        return nombre
    

# bodega/forms.py
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Sony, Samsung, Nike...'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional de la marca...'
            }),
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Marca.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe una marca con este nombre.')
        return nombre