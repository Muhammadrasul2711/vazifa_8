from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Goods import models


def myCart(request):
    cart,_ = models.Cart.objects.get_or_create(author=request.user, is_active=True)
    cartProduct = models.CartProduct.objects.filter(cart=cart)
    context = {}
    context['cart']=cart
    context['cartpro']=cartProduct
    return render(request, 'user/detail.html', context)


def addProductToCart(request, id):
    product_id = id
    if request.method == 'POST' and 'quantity' in request.POST:
        quantity = int(request.POST['quantity'])
    else:
        quantity = 1
    product = models.Product.objects.get(id=product_id)
    cart, _ = models.Cart.objects.get_or_create(author=request.user, is_active=True)

    cart_product, created = models.CartProduct.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        defaults={'quantity': quantity, 'total_price': quantity * float(product.price) if product.price else 0}
    )

    if not created:
        cart_product.quantity += quantity
        cart_product.total_price = cart_product.quantity * float(product.price) if product.price else 0
        cart_product.save()

    return redirect('mycart')


def substruct(request, id):
    code = id
    quantity = int(request.POST['quantity'])
    product_cart = models.CartProduct.objects.get(id=code)
    product_cart.quantity = quantity
    product_cart.save()
    if not product_cart.quantity:
        product_cart.delete()
    if quantity and product_cart.product.price:
        product_cart.total_price = quantity * float(product_cart.product.price)
        product_cart.save()
    return redirect('mycart')



def deleteProductCart(request, id):
    product_cart = models.CartProduct.objects.get(id=id)
    product_cart.delete()
    return redirect('mycart')


def CreateOrder(request, id):
    cart = models.Cart.objects.get(id=id)
    
    cart_products = models.CartProduct.objects.filter(cart=cart)

    done_products = []

    for cart_product in cart_products:
        if cart_product.quantity <= cart_product.product.quantity:
            cart_product.product.quantity -= cart_product.quantity
            cart_product.product.save()
            done_products.append(cart_product)
        else:
            for product in done_products:
                product.product.quantity += product.quantity
                product.product.save()
            raise ValueError('Qoldiqda kamchilik')
    if request.method == 'POST':
        models.Order.objects.create(
            cart_id=cart.id,
            full_name = request.POST['full_name'],
            email = request.POST['email'],
            phone = request.POST['phone'],
            address = request.POST['address'],
            status = 1
            )
        cart.is_active = False
        cart.save()
        return render(request, 'user/order.html')
    return redirect('mycart')


def wishList(request):
    wish_list = models.WishList.objects.filter(user=request.user).select_related('product')
    product_ids = [wish.product.id for wish in wish_list]
    product_images = models.ProductImg.objects.filter(product_id__in=product_ids).select_related('product')
    product_images_dict = {img.product.id: img for img in product_images}
    combined = [(wish, product_images_dict.get(wish.product.id)) for wish in wish_list]

    context = {
        'combined': combined
    }

    return render(request, 'user/wishList.html', context)




def addOrDeleteWishList(request, id):
    product = get_object_or_404(models.Product, id=id)

    data, created = models.WishList.objects.get_or_create(
        product=product,
        user=request.user,
    )
    if not created:
        data.delete()
    
    next_url = request.META.get('HTTP_REFERER', 'shop')  
    return redirect(next_url)


def userSearch(request):
    q = request.GET.get('q')
    if q:
        result = models.Product.objects.filter(name=q)
        return render(request, 'user/query.html', {'result':result})
    return redirect('/')









"""
return redirect(request.path)



Product.objects.filter(
    created_at:date = date,
    created_at:date__gt = date,
    created_at:date__gte = date,
    created_at:date__lt = date,
    created_at:date__lte = date,
)

Product.objects.filter(
    created_at:time = time
)

Product.objects.filter(
    created_at:date_time = date_time
)

Product.objects.filter(
    created_at:date_time__year = 2024,
    region_name__icontains = 'a'
)

# 12, 15, 15, 10
# Yan, Fev, Mar, Apr, May, Iy, ... Dec
[10,11,12,13,15,16,17,123,432,123]
[Yan, Fev, Mar, Apr, May, Iy, iyul, avg, sen, okt, Dec]

product = Product.objects.all()
paginator = Paginator(product, per_page=3)
product = [1,2,3,4,5,6,7,8,9,10]
paginator = [[1,2,3]]
paginator.object_list -> 4

"""