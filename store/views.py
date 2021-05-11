from django.shortcuts import render
from django.http import JsonResponse
from .models import *
import json
import datetime
import os
# Create your views here.
from .models import *
from .utils import cookieCart, cartData, guestOrder
#Update image
from django.core.files.storage import FileSystemStorage
from django.conf import settings

#login
from django.contrib.auth import login,authenticate,logout
from django.shortcuts import redirect
from django.contrib.auth.models import User

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()


    context = {'products' :products, 'cartItems':cartItems}
    return render(request,'store/user/store.html',context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,'store/user/cart.html',context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    

    context = {'items': items, 'order': order, 'cartItems':cartItems}
    return render(request,'store/user/checkout.html',context)

def shopproduct(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    products = Product.objects.all()

    context = {'items':items, 'order':order, 'cartItems':cartItems, 'products':products}
    return render(request,'store/user/product.html',context)


def product_single(request,id):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    get_prodcut = Product.objects.get(id=id)

    get_productImages = ProductImages.objects.filter(product = get_prodcut)

    context = {'items': items, 'order': order, 'cartItems':cartItems,"product":get_prodcut,"productimages":get_productImages}
    return render(request,'store/user/product-single.html',context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added',safe=False)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)


    else:
        customer,order=guestOrder(request,data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete!', safe=False)

# Hàm login
def Mylogin(request):
    if request.user.is_authenticated:
        # return redirect('store:store')
        return render(request,'store/user/store.html')

    if request.method == 'POST':
        #Lấy uername và password
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Kiểm tra xem username và password có trong dữ liệu
        user = authenticate(username=username, password=password)

        #Kiểm tra nếu là admin 
        if user.is_superuser:
            products = Product.objects.all()
            return render(request, 'store/admin/list.html',{'products':products})
        
        if user is not None: # Nếu tìm thấy user có username và password đã nhập
            if user.is_active: #Tài khoản có bị vô hiệu hóa - đã/còn hiệu lực
                login(request,user)
                #Trả về trang index
                return redirect('store')
            else:
                return render(request,"store/user/login.html",{'message':'Tài khoản đã bị vô hiệu hóa'})
        else:
            return render(request,"store/user/login.html",{'message':'Tài khoản không tồn tại'})

    return render(request,'store/user/login.html')

def MyRegistration(request):
    # Nếu đã đăng nhập trả -->index
    if request.user.is_authenticated:
        # Data
        return redirect('store')
    else:
        if request.method == 'POST':
            # Lấy username, pass1 và pass2
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            # Kiểm tra username, password1 và password2 có rỗng hoặc password 1 khác password2
            if (username == '' or password1 == '' or password2 == '' or password1 != password2 or email==''):
                render(request, 'store/user/registration.html')
            else:
                new_user = User()
                new_user.username = username
                new_user.set_password(password1)
                new_user.email=email
                new_user.save()
                user = authenticate(username=username, password=password1,email=email)

                new_customer= Customer()
                new_customer.user = user
                new_customer.name = username
                new_customer.email = email
                new_customer.save()

                login(request, user)

                # Data
                return redirect('store')

    return render(request,'store/user/registration.html')

def MyLogout(request):
    #Nếu không có tài khoản thì không thực hiện hàm đăng xuất
    try:
        logout(request)
    except:
        pass
    #Nếu đăng xuất thành công => trả về trang đăng nhập -login
    # return render(request,'store/user/login.html')
    return redirect('login')

# Trang admin
def AddProduct(request):
    if request.method == 'POST':
        #Lấy dữ liệu
        title = request.POST.get('Title')
        name = request.POST.get('Name')
        detail = request.POST.get('Detail')
        price = request.POST.get('Price')
        image = request.POST.get('Image')

       
            
        if(title=='' or name == '' or detail == '' or price== '' or image == ''):
            return render(request, 'store/admin/add-product.html')
        else:
            new_product = Product()
            new_product.title = title
            new_product.name = name
            new_product.detail = detail
            new_product.price = price
            #Update anh
            myfile = request.FILES['Image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)

            uploaded_file_url = myfile.name
            new_product.image = uploaded_file_url
            new_product.save()

            # Nhiều ảnh sản phẩm
            ProductImages1 = request.FILES.getlist('ProductImages')

            for productimage in ProductImages1:
                productimages = ProductImages()
                productimages.product = new_product

                myfileproduct = productimage
                fs = FileSystemStorage()
                filename = fs.save(myfileproduct.name, myfileproduct)

                uploaded_file_url = myfileproduct.name
                productimages.productimages = uploaded_file_url
                productimages.save()

            
    return render(request,'store/admin/add-product.html')


def ListProduct(request):
    products = Product.objects.all()
    return render(request, 'store/admin/list.html',{'products':products})

# Hàm sửa sản phẩm
def EditProdut(request,id):
    get_product=Product.objects.get(id=id)
    if request.method == 'POST':
        #Lấy dữ liệu
        title = request.POST.get('Title')
        name = request.POST.get('Name')
        detail = request.POST.get('Detail')
        price = request.POST.get('Price')
        image = request.POST.get('Image')


        get_product.title = title
        get_product.name = name
        get_product.detail = detail
        get_product.price = price
        # Update anh
        myfile = request.FILES['Image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)

        uploaded_file_url = myfile.name
        get_product.image = uploaded_file_url
        get_product.save()
        products = Product.objects.all()
        return render(request, 'store/admin/list.html', {'products': products})

    context = {
        'product':get_product,
    }

    return render(request,'store/admin/editproduct.html',context)

def DeleteProduct(request,id):
    get_product=Product.objects.get(id=id)
    os.remove('D:/Bai_Tap/Dai_Hoc/Hoc_Ky_6/Thuc_Tap_Ky_Thuat_Phan_Mem/Thuc_Tap_Ky_Thuat_Phan_Mem/ecommerce/static/images/' + get_product.imageURL)
    
    #Dùng filter để lấy nhiều
    get_productImages = ProductImages.objects.filter(product = get_product)

    for productimage in get_productImages:
        os.remove('D:/Bai_Tap/Dai_Hoc/Hoc_Ky_6/Thuc_Tap_Ky_Thuat_Phan_Mem/Thuc_Tap_Ky_Thuat_Phan_Mem/ecommerce/static/images/' + productimage.productImageURL)

    get_product.delete()
    return redirect('ListProduct')


#User
def AddUser(request):
    if request.method == 'POST':
        #Lấy dữ liệu:
        username = request.POST.get('username')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')

        if(username == '' or firstname == '' or lastname == '' or email =='' or password == ''):
            return render(request,'store/admin/add-user.html')
        else:
            new_user = User()
            new_user.username = username
            new_user.set_password(password)
            new_user.first_name = firstname
            new_user.last_name = lastname
            new_user.email = email
            new_user.save()

            new_customer = Customer()
            new_customer.user = new_user
            new_customer.name = username
            new_customer.email = email
            new_customer.save()
            
    return render(request,'store/admin/add-user.html')

def ListUser(request):
    users = User.objects.all()
    orders = Order.objects.all()
    customers = Customer.objects.all()
    context = {'users':users,'orders':orders,'customers':customers}
    return render(request, 'store/admin/listuser.html', context)

def DeleteUser(request,id):
    get_user = User.objects.get(id=id)
    get_user.delete()

    orders = Order.objects.all()
    orderitems = OrderItem.objects.all()

    customers = Customer.objects.all()
    users = User.objects.all()
    context = {'users': users, 'orders': orders, 'customers': customers}
    return render(request, 'store/admin/listuser.html', context)

def EditUser(request, id):
    get_user = User.objects.get(id=id)
    if request.method == 'POST':
        # Lấy dữ liệu:
        username = request.POST.get('username')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')

        if (username == '' or firstname == '' or lastname == '' or email == '' or password == ''):
            return render(request, 'store/admin/edituser.html')
        else:
            get_user.username = username
            get_user.set_password(password)
            get_user.first_name = firstname
            get_user.last_name = lastname
            get_user.email = email
            get_user.save()

            users = User.objects.all()
            orders = Order.objects.all()
            customers = Customer.objects.all()
            context = {'users': users, 'orders': orders, 'customers': customers}
            return render(request, 'store/admin/listuser.html', context)
    return render(request, 'store/admin/edituser.html',{'user':get_user})
