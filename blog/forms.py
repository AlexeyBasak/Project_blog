from django import forms
from blog.models import Comment, Post

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'author', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        

class SearchForm(forms.Form):
    query = forms.CharField()

