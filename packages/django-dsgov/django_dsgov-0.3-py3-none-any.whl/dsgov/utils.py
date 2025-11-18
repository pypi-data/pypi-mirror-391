from urllib.parse import urlencode, parse_qs

def build_page_url(request, page_num, extra_params=None):
    """
    Monta uma URL de paginação baseada na request atual, sobrescrevendo `page`.

    - Mantém os parâmetros existentes da URL.
    - Remove qualquer `page` anterior.
    - Aceita `extra_params` como string no formato querystring (ex: "busca=lapis&categoria=arte").
    """
    # começa com os params atuais
    params = request.GET.copy()

    # remove page atual
    params.pop("page", None)

    # adiciona extra_params se houver
    if extra_params:
        parsed_extra = parse_qs(extra_params, keep_blank_values=True)
        parsed_extra.pop("page", None)
        for key, values in parsed_extra.items():
            params.setlist(key, values)

    # sobrescreve page
    params["page"] = page_num

    return f"{request.path}?{urlencode(params, doseq=True)}"
