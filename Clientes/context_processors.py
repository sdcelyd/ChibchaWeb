def cliente_context(request):
    if request.user.is_authenticated:
        try:
            return {'cliente': request.user.cliente}
        except:
            return {}
    return {}
