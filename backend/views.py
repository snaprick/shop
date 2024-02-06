from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, DetailView

from backend.forms import ProductForm, RegistrationForm
from backend.models import Product, Category


class AllProductsView(View):
    def get(self, request):
        params = request.GET
        products = Product.objects.all()

        if params.get('search'):
            products = products.filter(
                Q(name__icontains=params['search']) | Q(description__icontains=params['search']))  # ilike

        response = [
            {
                'name': product.name,
                'description': product.description[:10],
                'price': product.price
            } for product in products
        ]
        return JsonResponse(data={"response": response})


class ProductView(View):
    def get(self, request, product_id):
        product = Product.objects.filter(id=product_id).first()

        if not product:
            return JsonResponse(data={})

        product_dict = {
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock
        }
        return JsonResponse(data=product_dict)


class CategoryProductView(View):
    def get(self, request, category_id):
        params = request.GET
        products = Product.objects.filter(category_id=category_id).all()

        filter = params.get('filter')
        if filter:
            if filter == 'below_10':
                products = products.filter(price__lte=10)
            elif filter == 'above_10':
                products = products.filter(price__gte=10)

        response = [
            {
                'name': product.name,
                'description': product.description[:10],
                'price': product.price
            } for product in products
        ]
        return JsonResponse(data={"response": response})


class HomeTemplateView(TemplateView):
    template_name = 'home.html'


class ProductTemplateView(DetailView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'product'


def product_template(request, pk):
    product = Product.objects.get(id=pk)

    return render(request, "product.html", context={
        "product": product
    })


class CategoryTemplateView(DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = 'category'


class ContactTemplateView(TemplateView):
    template_name = 'contact.html'


class AboutTemplateView(TemplateView):
    template_name = 'about.html'


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products')
        else:
            raise Exception("Form is not valid")
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
@permission_required('backend.change_product')
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


class ChangePasswordView(PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('profile')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})
