import random
from django.http.response import HttpResponse
import markdown2
from . import util
from django import forms
from django.urls import reverse
from django.forms import widgets
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage


class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'search',
        'placeholder': 'Search Encyclopedia',
        'autocomplete':'off',
        'autocapitalize':'off',
        'autocorrect':'on'
    }))


class NewPageForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        'placeholder': 'Enter Title',
        'style': 'display:block; margin:10px 0;',
        'autocomplete':'off',
        'autocapitalize':'off',
        'autocorrect':'on'
    }))
    data = forms.CharField(label='', widget=forms.Textarea(attrs={
        'style': 'padding:10px;',
        'class': 'textarea',
    }))
    

class EditPageForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
        'style': 'display:block; margin:10px 0px;',
        'autocomplete':'off',
        'autocapitalize':'off',
        'autocorrect':'on'
    }))
    data = forms.CharField(label='', widget=forms.Textarea(attrs={
        'style': 'padding:10px;',
        'class': 'textarea',
    }))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        'form': SearchForm()
    })


def Entry(request, title):
    entry = util.get_entry(title)
    if entry is None:
        return render(request, 'encyclopedia/Error.html', {            
             'title': title,
             'form': SearchForm(),
        })
    else:
        return render(request, 'encyclopedia/entry.html', {
            'title': title,
            'entry': markdown2.markdown(entry),
            'form': SearchForm(),

        })


def Search(request):
    if request.method == 'POST':
        found_entries = []
        all_entries = util.list_entries()
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            for entry in all_entries:
                if query.upper() == entry.upper():
                    title = entry
                    entry = util.get_entry(title)
                    return HttpResponseRedirect(reverse('Entry', args=[title]))
                if query.upper() in entry.upper():
                    found_entries.append(entry)
            return render(request, 'encyclopedia/search.html', {
                'results': found_entries,
                'query': query,
                'form': SearchForm()
            })
    return render(request, 'encyclopedia/search.html', {
        'results': '',
        'query': '',
        'form': SearchForm(),
    })


def NewPage(request):
    if request.method == 'POST':
        new_entry = NewPageForm(request.POST)
        if new_entry.is_valid():
            title = new_entry.cleaned_data['title']
            data = new_entry.cleaned_data['data']
            all_entries = util.list_entries()
            for entry in all_entries:
                if entry.upper() == title.upper():
                    return render(request, 'encyclopedia/newpage.html', {
                        'NewPageForm': NewPageForm(),
                        'error': 'The entry already exists.',
                        'form': SearchForm()
                    })
                new_entry_title = '#' + title
                new_entry_data = '\n' + data
                content = new_entry_title + new_entry_data
                util.save_entry(title, content)
            entry = util.get_entry(title)
            return render(request, 'encyclopedia/entry.html', {
                'title': title,
                'entry': markdown2.markdown(entry),
                'form': SearchForm(),
            })
    return render(request, 'encyclopedia/newpage.html', {
        'form': SearchForm(),
        'NewPageForm': NewPageForm()
    })


def EditPage(request, title):
    if request.method == 'POST':
        entry = util.get_entry(title)
        form_edit = EditPageForm(initial={'title': title, 'data': entry
                                          })
        return render(request, 'encyclopedia/editpage.html', {
            'form': SearchForm(),
            'EditPageForm': form_edit,
            'entry': entry,
            'title': title,
        })


def SubmitEdit(request, title):
    if request.method == 'POST':
        edit_entry = EditPageForm(request.POST)
        if edit_entry.is_valid():
            content = edit_entry.cleaned_data['data']
            edit_title = edit_entry.cleaned_data['title']
            if edit_title != title:
                filename = f"entries/{title}.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)
            util.save_entry(edit_title, content)
            entry = util.get_entry(edit_title)
        return render(request, 'encyclopedia/entry.html', {
            'title': edit_title,
            'entry': markdown2.markdown(entry),
            'form': SearchForm(),
        })


def Random(request):
    entries = util.list_entries()
    title = random.choice(entries)
    entry = util.get_entry(title)
    return HttpResponseRedirect(reverse(
        'Entry', args=[title]
    ))
