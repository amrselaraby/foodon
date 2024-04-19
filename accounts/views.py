from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from accounts.forms import UserForm
from accounts.models import User, UserProfile
from accounts.utils import (
    detect_user,
    send_verification_email,
)
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
            # Send verification email
            mail_subject = "Welcome onboard! Please activate your account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)

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

            # Send verification email
            mail_subject = "Welcome onboard! Please activate your account"
            mail_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, mail_template)
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


def activate(request, uidb64, token):
    # Activate user by setting is_active status to true.
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations Your account has been activated")
        return redirect("my-account")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("my-account")


@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customer_dashboard(request):
    return render(request, "accounts/customer-dashboard.html")


@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendor_dashboard(request):
    return render(request, "accounts/vendor-dashboard.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send reset password email
            mail_subject = "Reset your Password"
            mail_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, mail_template)
            messages.success(request, "Password reset link has been sent to your email")
            return redirect("login")
        else:
            messages.error("Account does not exist")
            return redirect("forgot-password")
    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password")
        return redirect("reset-password")
    else:
        messages.error(request, "This link has been expired")
        return redirect("my-account")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect("login")

        else:
            messages.error(request, "Passwords don't match")
            return redirect("reset-password")
    return render(request, "accounts/reset_password.html")


# def send_ver_email(request):
#     send_verification_email(request, request.user)
#     return redirect("login")
