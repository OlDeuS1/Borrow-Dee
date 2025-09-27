from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.db.models import *
from django.db.models.functions import *
from django.shortcuts import redirect, get_object_or_404
# from .forms import *
from django.db import transaction

class IndexView(View):

    def get(self, request):

        return render(request, "index.html")