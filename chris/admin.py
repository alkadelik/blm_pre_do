# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from chris.models import *

admin.site.register(UserProfile)
admin.site.register(Budget)
admin.site.register(Bank)
admin.site.register(Token)
