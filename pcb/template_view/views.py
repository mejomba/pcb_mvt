import json
import requests
from django.shortcuts import render
from django.conf import settings


def pcb_order(request):
    return render(request, 'components/order/pcb_order.html', {})