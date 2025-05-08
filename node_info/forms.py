from django import forms
from node_info.models import Node

#class NodeCreateForm(forms.Form):
#
#    name = forms.CharField(max_length=32)
#    IPaddress = forms.CharField(max_length=32)
#    port = forms.CharField(max_length=32)
#    #keepalive = forms.IntegerField(choices = NODE_CHOICES)
#    keepalive = forms.IntegerField()


class NodeCreateForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = '__all__'

        # CSS 相关
        widgets = {
            'name': forms.TextInput(attrs={'id': 'name_id', 'class': 'form-control'}),
            'IPaddress': forms.TextInput(attrs={'id': 'ip_id', 'class': 'form-control'}),
            'port': forms.TextInput(attrs={'id': 'port_id', 'class': 'form-control'}),
            'keepalive': forms.NumberInput(attrs={'id': 'keepalive_id', 'class': 'form-control'}),
            'pid': forms.NumberInput(attrs={'id': 'pid', 'class': 'form-control'}),
            'status': forms.NumberInput(attrs={'id': 'status', 'class': 'form-control'}),
        }
        labels ={
            'name': '服务器名称',
        }
# python manage.py shell
# from node_info.forms import NodeCreateForm
# form = NodeCreateForm(data={'name': 'cloud', IPaddress='127.0.0.1', port='18083', keepalive=60})
# form.is_valid()
