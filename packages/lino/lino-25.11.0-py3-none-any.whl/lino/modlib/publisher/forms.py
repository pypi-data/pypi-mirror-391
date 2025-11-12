# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django import forms
from django.forms.models import fields_for_model
from lino.api import dd


class FormCorpus(forms.Form):

    def __init__(self, *args, **kwargs):
        actor = kwargs.pop("actor")
        super().__init__(*args, **kwargs)
        for name, field in actor.parameters.items():
            if isinstance(field, dd.DummyField):
                continue
            fld = field.formfield()
            fld.help_text = None
            fld.widget.attrs.update({"class": "form-control", "title": field.help_text})
            self.fields[name] = fld
