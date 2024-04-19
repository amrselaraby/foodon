from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from accounts.forms import UserForm
from accounts.models import User, UserProfile
from accounts.utils import detect_user
from vendor.forms import VendorForm


# Create your views here.


# Restrict the vendor from accessing customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def register_user(request):
    if request.user.is_authenticated:
        messages.warning(request, "you are already logged in.")
        return redirect("dashboard")
    elif request.method == "POST":

        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form
            # password = form.cleaned_data["password"]
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method from User model
            user_attributes = {**form.cleaned_data}
            del user_attributes["phone_number"]
            del user_attributes["confirm_password"]
            user = User.objects.create_user(**user_attributes)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "Your account has been registered successfully")
            return redirect("register-user")
        else:
            print("invalid form")
            print(form.errors)

    else:
        form = UserForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register_user.html", context)


def register_vendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "you are already logged in.")
        return redirect("dashboard")
    elif request.method == "POST":
        # STORE THE DATA AND CREATE USER
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            # Create the user using create_user method from User model
            user_attributes = {**form.cleaned_data}
            del user_attributes["phone_number"]
            del user_attributes["confirm_password"]
            user = User.objects.create_user(**user_attributes)
            user.role = User.Vendor
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(
                request,
                "Your account has been registered successfully! Please wait for the approval",
            )
            return redirect("register-vendor")
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        "form": form,
        "v_form": v_form,
    }
    return render(request, "accounts/register_vendor.html", context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "you are already logged in.")
        return redirect("my-account")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "you are now logged in")
            return redirect("my-account")
        else:
            messages.error(request, "Invalid login credentials")

    return render(request, "accounts/login.html")


def logout(request):
    auth.logout(request)
    messages.info(request, "you are logged out")
    return redirect("login")


@login_required(login_url="login")
def my_account(request):
    redirect_url = detect_user(request.user)
    return redirect(redirect_url)


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, "accounts/customer-dashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, "accounts/vendor-dashboard.html")
