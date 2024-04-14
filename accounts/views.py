from django.shortcuts import redirect, render
from django.contrib import messages

from accounts.forms import UserForm
from accounts.models import User


# Create your views here.
def register_user(request):
    if request.method == "POST":

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
