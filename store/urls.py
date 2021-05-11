from django.urls import  path
from . import views


urlpatterns = [
    path('',views.store, name = "store"),
    path('cart/',views.cart, name = "cart"),
    path('checkout/',views.checkout, name = "checkout"),
    path('product/',views.shopproduct, name = "shopproduct"),
    path('product/product-single/<int:id>',views.product_single, name = "product_single"),

    path('update_item/',views.updateItem, name = "update_item"),
    path('process_order/',views.processOrder, name = "process_order"),

    # Admin
    path('login/',views.Mylogin, name = "login"),
    path('registration/',views.MyRegistration, name = "registration"),
    path('logout/',views.MyLogout, name = "logout"),

    #Trang Admin
    #Sản phẩm
    path('Quanly/list-product/add-product/',views.AddProduct, name="AddProduct"),
    path('Quanly/listproduct/',views.ListProduct, name="ListProduct"),
    path('Quanly/list-product/editproduct/<int:id>',views.EditProdut, name = "EditProdut"),
    path('Quanly/list-product/delete/<int:id>',views.DeleteProduct, name = "DeleteProduct"),
    #User
    path('Quanly/list-user/add-user',views.AddUser,name="AddUser"),
    path('Quanly/list-user/',views.ListUser,name="ListUser"),
    path('Quanly/list-user/delete/<int:id>',views.DeleteUser, name = "DeleteUser"),
    path('Quanly/list-user/edit/<int:id>',views.EditUser, name = "EditUser"),
]