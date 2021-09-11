from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.hashers import check_password, make_password
from mystore.models import Customer, Order, Product, Category
from django.views import View

# Create your views here.


class Cart(View):
    def get(self,request): #session bu sessiyalar qachonki foydalanuvchi qandaydir amalni bajarsa saytga kirsa yoqiladi, va foydalanuvchi saytdan chiqishi bilan sessiya vaqti tugaydi 
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        print(products)
        return render(request, 'cart.html', {'products':products})
    
class CheckOut(View):
    def post(self,request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_products_by_id(cart.keys())
        print(address, phone, customer, cart, products)
        for product in products:
            print(cart.get(str(product.id)))
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart']={}
        return redirect('cart')
    
class Index(View):
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1: #1
                        cart.pop(product) #0
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1        
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('homepage')
    
    def get(self, request):
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')
    
def store(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart']={}
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_all_products_by_categoryid(categoryID)
    else:
        products = Product.get_all_products()
    data = {}
    data['products'] = products
    data['categories'] = categories
    print('you are:', request.session.get('email'))
    return render(request, 'index.html', data)

class Login(View):
    return_url = None
    
    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')
    
    def post(self,request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'Email or Password invalid'
        else:
            error_message = 'Email or Password invalid'
        print(email, password)
        return render(request, 'login.html',{'error':error_message})

def logout(request):
    request.session.clear()
    return redirect('login')

class OrderView(View):
    def get(self,request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(orders)
        return render(request, 'orders.html',{'orders':orders})
    
class Signup(View):
    def get(self,request):
        return render(request, 'signup.html')
    
    def post(self,request):
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        
        #validatsiya
        
        value = {
            'first_name':first_name,
            'last_name':last_name,
            'phone':phone,
            'email':email,
            'password':password
        }
        error_message = None
        customer = Customer(first_name = first_name,
                            last_name = last_name,
                            phone = phone,
                            email = email,
                            password = password)
        
        error_message = self.validateCustomer(customer)
        if not error_message:
            print(first_name, last_name, phone, email, password)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')
        else:
            data = {
                'error':error_message,
                'values':value,
            }
            return render(request, 'signup.html', data)
    
    def validateCustomer(self, customer):
        error_message = None
        if (not customer.first_name):
            error_message = 'First Name Required!'
        elif len(customer.first_name) < 5:
            error_message = "First Name must be 5 char long or more"
        elif not customer.last_name:
            error_message = "Last Name Required!"
        elif len(customer.last_name) < 5:
            error_message = "Last Name must be 5 char long or more"
        elif not customer.phone:
            error_message = "Phone Required!"
        elif len(customer.phone) < 10:
            error_message = "Phone must be 10 char long or more"
        elif not customer.password:
            error_message = "Password Required!"
        elif len(customer.password) < 6:
            error_message = "Password must be 6 char long or more"
        elif len(customer.email) < 10:
            error_message = "Email Address must be 10 char lon or more"
        elif customer.isExists():
            error_message = "Email Address Already Registered!"
        return error_message 