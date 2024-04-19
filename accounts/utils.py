def detect_user(user):
    if user.role == 1:
        redirect_url = "vendor-dashboard"
        return redirect_url
    elif user.role == 2:
        redirect_url = "customer-dashboard"
        return redirect_url
    elif user.role == None and user.is_superadmin:
        redirect_url = "/admin"
        return redirect_url
