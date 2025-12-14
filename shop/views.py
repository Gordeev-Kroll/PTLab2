from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import CreateView

from shop.forms import PromoCodeForm

from .models import Product, PromoCode, Purchase


# Create your views here.
def index(request):
    entered_code = request.session.get("promo_code")
    if entered_code and PromoCode.objects.filter(code=entered_code).exists():
        products = Product.objects.filter(
            Q(promo_code__isnull=True) | Q(promo_code__code=entered_code)
        )
    else:
        products = Product.objects.filter(promo_code__isnull=True)

    form = PromoCodeForm()
    context = {"products": products, "form": form}
    return render(request, "shop/index.html", context)


class PurchaseCreate(CreateView):
    model = Purchase
    fields = ["product", "person", "address"]

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(f"Спасибо за покупку, {self.object.person}!")


def apply_promo(request):
    if request.method == "POST":
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            if PromoCode.objects.filter(code=code).exists():
                request.session["promo_code"] = code
    return redirect("index")
