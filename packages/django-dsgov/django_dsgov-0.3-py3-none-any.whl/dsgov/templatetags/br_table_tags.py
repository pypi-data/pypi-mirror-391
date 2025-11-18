import uuid
import re
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

def _uniq_id(prefix='id'):
    """Gera um ID único de 8 caracteres com um prefixo."""
    return f'{prefix}-{uuid.uuid4().hex[:8]}'

@register.tag(name='br_table')
def do_br_table(parser, token):
    """
    Tag de bloco para renderizar o componente br-table.
    Uso: {% br_table title="Título" data-search="true" %}...{% end_br_table %}
    """
    bits = token.split_contents()
    kwargs = {}
    # Processa argumentos da tag
    for bit in bits[1:]:
        if '=' in bit:
            k, v = bit.split('=', 1)
            kwargs[k] = v.strip('"\'')
    
    nodelist = parser.parse(('end_br_table',))
    parser.delete_first_token()
    return BRTableNode(nodelist, **kwargs)

class BRTableNode(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.nodelist = nodelist
        self.kwargs = {k: str(v) for k, v in kwargs.items()}

    def render(self, context):
        # Acessa os valores de kwargs de forma segura, tratando-os como strings.
        meta = {
            'title': self.kwargs.get('title', ''),
            'data_search': self.kwargs.get('data-search', ''),
            'data_selection': self.kwargs.get('data-selection', ''),
            'data_collapse': self.kwargs.get('data-collapse', ''),
            'data_random': self.kwargs.get('data-random', ''),
            # Converte para int de forma segura
            'data_total': int(self.kwargs.get('data-total', 0) or 0),
            'data_current': int(self.kwargs.get('data-current', 1) or 1),
            'data_per_page': int(self.kwargs.get('data-per-page', 10) or 10),
            'search_input_id': _uniq_id('table-searchbox'),
            'search_button_id': _uniq_id('button-input-search'),
            'per_page_select_id': _uniq_id('per-page-selection'),
            'go_to_select_id': _uniq_id('go-to-selection'),
        }

        context.push()
        context['br_table_meta'] = meta
        content = self.nodelist.render(context)
        context.pop()

        return format_html(
            '<div class="br-table" data-search="{data_search}" data-selection="{data_selection}" data-collapse="{data_collapse}" data-random="{data_random}"> {content} </div>',
            data_search=meta['data_search'],
            data_selection=meta['data_selection'],
            data_collapse=meta['data_collapse'],
            data_random=meta['data_random'],
            content=mark_safe(content)
        )


@register.tag(name='br_table_header')
def do_br_table_header(parser, token):
    """Tag de bloco para renderizar o cabeçalho da tabela."""
    nodelist = parser.parse(('end_br_table_header',))
    parser.delete_first_token()
    return BRTableHeaderNode(nodelist)

class BRTableHeaderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é HTML de template, portanto, é marcado como seguro.
        content = self.nodelist.render(context)

        match = re.search(r'<!--\s*BR_TABLE_SEARCH_START\s*-->(.*?)<!--\s*BR_TABLE_SEARCH_END\s*-->', content, re.DOTALL)
        
        if match:
            search_bar_html = match.group(1)
            top_bar_html = content.replace(match.group(0), "")
        else:
            search_bar_html = ""
            top_bar_html = content

        if '<div class="top-bar"' in top_bar_html:
            top_bar_final = top_bar_html
        else:
            top_bar_final = format_html('<div class="top-bar">{}</div>', mark_safe(top_bar_html))

        # mark_safe é usado para top_bar e search_bar pois contêm HTML de template.
        return format_html(
            '<div class="table-header">{top_bar}{search_bar}</div>',
            top_bar=mark_safe(top_bar_final),
            search_bar=mark_safe(search_bar_html)
        )

@register.tag(name='br_table_title')
def do_br_table_title(parser, token):
    """
    Tag de bloco para renderizar o título da tabela.
    Uso: {% br_table_title %}Título da Tabela{% end_br_table_title %}
    """
    nodelist = parser.parse(('end_br_table_title',))
    parser.delete_first_token()
    return BRTableTitleNode(nodelist)


class BRTableTitleNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context).strip()
        return format_html('<div class="table-title">{}</div>', content)

@register.simple_tag(name='br_table_actions_trigger')
def br_table_actions_trigger():
    """
    Renderiza o bloco de ações (trigger de densidade) da tabela.
    Uso: {% br_table_actions_trigger %}
    """
    # O HTML é estático e seguro, format_html é usado para clareza e segurança.
    return format_html('''
        <div class="actions-trigger text-nowrap">
            <button class="br-button circle" type="button" id="button-dropdown-density"
                title="Ver mais opções" data-toggle="dropdown" data-target="target01-12653"
                aria-label="Definir densidade da tabela" aria-haspopup="true" aria-live="polite">
                <i class="fas fa-ellipsis-v" aria-hidden="true"></i>
            </button>
            <div class="br-list" id="target01-12653" role="menu"
                aria-labelledby="button-dropdown-density" hidden="hidden">
                <button class="br-item" type="button" data-density="small" role="menuitem">
                    Densidade alta
                </button><span class="br-divider"></span>
                <button class="br-item" type="button" data-density="medium" role="menuitem">
                    Densidade média
                </button><span class="br-divider"></span>
                <button class="br-item" type="button" data-density="large" role="menuitem">
                    Densidade baixa
                </button>
            </div>
        </div>
    ''')

@register.tag(name='br_table_search')
def do_br_table_search(parser, token):
    """
    Tag de bloco para renderizar o componente de busca da tabela.
    Uso: {% br_table_search placeholder="Buscar" %}
    """
    bits = token.split_contents()
    kwargs = {}
    for bit in bits[1:]:
        if '=' in bit:
            k, v = bit.split('=', 1)
            kwargs[k] = v.strip('"\'')
    return BRTableSearchNodeUnified(**{k: str(v) for k, v in kwargs.items()})

class BRTableSearchNodeUnified(template.Node):
    def __init__(self, **kwargs):
        self.placeholder = format_html('{}', kwargs.get('placeholder', 'Buscar na tabela'))

    def render(self, context):
        meta = context.get('br_table_meta', {})
        button_id = meta.get('search_button_id', _uniq_id('button-input-search'))
        input_id = meta.get('search_input_id', _uniq_id('table-searchbox'))
        search_bar_id = _uniq_id('search-bar')

        start_marker = '<!-- BR_TABLE_SEARCH_START -->'
        end_marker = '<!-- BR_TABLE_SEARCH_END -->'

        # format_html garante o escape de todos os argumentos, exceto aqueles
        # marcados como seguros (mark_safe).
        return format_html(
            '''
            <div class="search-trigger">
                <button class="br-button circle" type="button"
                        id="{button_id}" data-toggle="search"
                        aria-label="Abrir busca" aria-controls="{input_id}">
                    <i class="fas fa-search" aria-hidden="true"></i>
                </button>
            </div>
            {start_marker}
            <div class="search-bar" id="{search_bar_id}" hidden aria-hidden="true">
                <div class="br-input">
                    <label for="{input_id}">Buscar na tabela</label>
                    <input id="{input_id}" type="search" placeholder="{placeholder}"
                           aria-labelledby="{button_id}" aria-label="Buscar na tabela"/>
                    <button class="br-button" type="button" aria-label="Buscar">
                        <i class="fas fa-search" aria-hidden="true"></i>
                    </button>
                </div>
                <button class="br-button circle" type="button"
                        data-dismiss="search" aria-label="Fechar busca">
                    <i class="fas fa-times" aria-hidden="true"></i>
                </button>
            </div>
            {end_marker}
            ''',
            button_id=button_id,
            input_id=input_id,
            search_bar_id=search_bar_id,
            placeholder=self.placeholder,
            start_marker=mark_safe(start_marker),
            end_marker=mark_safe(end_marker),
        )

@register.tag(name='table')
def do_table(parser, token):
    """Tag de bloco para renderizar a tag <table>."""
    nodelist = parser.parse(('end_table',))
    parser.delete_first_token()
    return BRTableTableNode(nodelist)

class BRTableTableNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é HTML de template, marcado como seguro.
        content = self.nodelist.render(context)
        return format_html('<table>{}</table>', mark_safe(content))

@register.tag(name='table_head')
def do_table_head(parser, token):
    """Tag de bloco para renderizar a tag <thead>."""
    nodelist = parser.parse(('end_table_head',))
    parser.delete_first_token()
    return TableHeadNode(nodelist)

class TableHeadNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é HTML de template, marcado como seguro.
        return format_html('<thead><tr>{}</tr></thead>', mark_safe(self.nodelist.render(context)))

@register.tag(name='head_collums')
def do_head_collums(parser, token):
    """
    Tag de bloco para renderizar a tag <th>.
    Uso: {% head_collums data-sort="true" %}Coluna{% end_head_collums %}
    """
    bits = token.split_contents()
    kwargs = {}
    for bit in bits[1:]:
        if '=' in bit:
            k, v = bit.split('=', 1)
            kwargs[k] = v.strip('"\'')
    nodelist = parser.parse(('end_head_collums',))
    parser.delete_first_token()

    return HeadCollumsNode(nodelist, **{k: str(v) for k, v in kwargs.items()})

class HeadCollumsNode(template.Node):
    def __init__(self, nodelist, **attrs):
        self.nodelist = nodelist
        # Converte todos os valores para strings seguras, pois são atributos de tag.
        self.attrs = {k: str(v) for k, v in attrs.items()}

    def render(self, context):
        # O conteúdo interno é renderizado e escapado automaticamente.
        content = self.nodelist.render(context)
        attrs_str = ' '.join(format_html('{}="{}"', k, v) for k, v in self.attrs.items() if v)
        
        if attrs_str:
            # mark_safe é usado para attrs_str pois format_html já escapou os valores.
            # mark_safe é usado para content pois é HTML de template.
            return format_html('<th {}>{}</th>', mark_safe(attrs_str), mark_safe(content))
        
        # mark_safe é usado para content pois é HTML de template.
        return format_html('<th>{}</th>', mark_safe(content))

@register.tag(name='table_body')
def do_table_body(parser, token):
    """Tag de bloco para renderizar a tag <tbody>."""
    nodelist = parser.parse(('end_table_body',))
    parser.delete_first_token()
    return TableBodyNode(nodelist)


class TableBodyNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é HTML de template, marcado como seguro.
        return format_html('<tbody>{}</tbody>', mark_safe(self.nodelist.render(context)))


@register.tag(name='body_row')
def do_body_row(parser, token):
    """Tag de bloco para renderizar a tag <tr>."""
    nodelist = parser.parse(('end_body_row',))
    parser.delete_first_token()
    return BodyRowNode(nodelist)


class BodyRowNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é HTML de template, marcado como seguro.
        return format_html('<tr>{}</tr>', mark_safe(self.nodelist.render(context)))


@register.tag(name='body_rows_collums')
def do_body_rows_collums(parser, token):
    """Tag de bloco para renderizar a tag <td>."""
    nodelist = parser.parse(('end_body_rows_collums',))
    parser.delete_first_token()
    return BodyRowsCollumsNode(nodelist)


class BodyRowsCollumsNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é renderizado e escapado automaticamente.
        content = self.nodelist.render(context)
        return format_html('<td>{}</td>', content)

@register.tag(name='br_table_footer')
def do_br_table_footer(parser, token):
    """Tag de bloco para renderizar o rodapé da tabela."""
    nodelist = parser.parse(('end_br_table_footer',))
    parser.delete_first_token()
    return BRTableFooterNode(nodelist)


class BRTableFooterNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # O conteúdo interno é HTML de template, marcado como seguro.
        return format_html('<div class="table-footer">{}</div>', mark_safe(self.nodelist.render(context)))

# -----------------------------------------------------------------------------
# Funções utilitárias necessárias para a paginação DSGov (versão tabela)
# -----------------------------------------------------------------------------

def build_page_url(request, page, extra_params=""):
    """Monta a URL com o número da página e preserva outros parâmetros GET."""
    params = request.GET.copy()

    # Atualiza ou adiciona o parâmetro 'page'
    params["page"] = page

    querystring = params.urlencode()

    # 🔹 Remove 'page' e 'per_page' duplicados de extra_params
    if extra_params:
        cleaned_extra = "&".join(
            [
                p
                for p in extra_params.split("&")
                if not (p.startswith("page=") or p.startswith("per_page="))
            ]
        )
        if cleaned_extra:
            querystring += f"&{cleaned_extra}"

    return f"?{querystring}"


def build_per_page_url(request, per_page, extra_params=""):
    """Monta a URL com o número de itens por página e reseta para a primeira página."""
    params = request.GET.copy()

    # Remove o per_page anterior para não duplicar
    if "per_page" in params:
        del params["per_page"]

    params["per_page"] = per_page

    querystring = params.urlencode()

    # Remove 'page' e 'per_page' duplicados de extra_params
    if extra_params:
        cleaned_extra = "&".join(
            [
                p
                for p in extra_params.split("&")
                if not (p.startswith("page=") or p.startswith("per_page="))
            ]
        )
        if cleaned_extra:
            querystring += f"&{cleaned_extra}"

    return f"?{querystring}"


@register.simple_tag(takes_context=True)
def br_table_pagination(context, page_obj=None, extra_params="", per_page_options=None):
    """
    Renderiza paginação DSGov (versão tabela).

    Exemplo de uso no template:
        {% br_table_pagination page_obj=page_obj extra_params=extra_params %}

    - page_obj: objeto do Django Paginator (ex: `page_obj` vindo da view)
    - extra_params: string adicional de parâmetros (opcional)
    - per_page_options: lista de opções de "itens por página" (ex: 10,20,30,50,100 etc)
    """
    request = context["request"]

    if not page_obj:
        # Renderiza a versão genérica/placeholder
        return format_html(
            """
            <nav class="br-pagination" aria-label="paginação" data-total="50" data-current="1" data-per-page="20">
              <div class="pagination-per-page">
                <div class="br-select">
                  <div class="br-input">
                    <label for="per-page-selection">Exibir</label>
                    <input id="per-page-selection" type="text" placeholder=" " value="20"/>
                    <button class="br-button" type="button" aria-label="Exibir lista" tabindex="-1" data-trigger="data-trigger"><i class="fas fa-angle-down" aria-hidden="true"></i>
                    </button>
                  </div>
                  <div class="br-list" tabindex="0">
                    <div class="br-item" tabindex="-1">
                      <div class="br-radio">
                        <input id="per-page-10" type="radio" name="per-page" value="10"/>
                        <label for="per-page-10">10</label>
                      </div>
                    </div>
                    <div class="br-item" tabindex="-1">
                      <div class="br-radio">
                        <input id="per-page-20" type="radio" name="per-page" value="20" checked="checked"/>
                        <label for="per-page-20">20</label>
                      </div>
                    </div>
                    <div class="br-item" tabindex="-1">
                      <div class="br-radio">
                        <input id="per-page-30" type="radio" name="per-page" value="30"/>
                        <label for="per-page-30">30</label>
                      </div>
                    </div>
                  </div>
                </div>
              </div><span class="br-divider d-none d-sm-block mx-3"></span>
              <div class="pagination-information d-none d-sm-flex"><span class="current">1</span>&ndash;<span class="per-page">20</span>&nbsp;de&nbsp;<span class="total">50</span>&nbsp;itens</div>
              <div class="pagination-go-to-page d-none d-sm-flex ml-auto">
                <div class="br-select">
                  <div class="br-input">
                    <label for="go-to-selection">Página</label>
                    <input id="go-to-selection" type="text" placeholder=" " value="1"/>
                    <button class="br-button" type="button" aria-label="Exibir lista" tabindex="-1" data-trigger="data-trigger"><i class="fas fa-angle-down" aria-hidden="true"></i>
                    </button>
                  </div>
                  <div class="br-list" tabindex="0">
                    <div class="br-item" tabindex="-1">
                      <div class="br-radio">
                        <input id="go-to-1" type="radio" name="go-to" value="1" checked="checked"/>
                        <label for="go-to-1">1</label>
                      </div>
                    </div>
                    <div class="br-item" tabindex="-1">
                      <div class="br-radio">
                        <input id="go-to-2" type="radio" name="go-to" value="2"/>
                        <label for="go-to-2">2</label>
                      </div>
                    </div>
                    <div class="br-item" tabindex="-1">
                      <div class="br-radio">
                        <input id="go-to-3" type="radio" name="go-to" value="3"/>
                        <label for="go-to-3">3</label>
                      </div>
                    </div>
                  </div>
                </div>
              </div><span class="br-divider d-none d-sm-block mx-3"></span>
              <div class="pagination-arrows ml-auto ml-sm-0">
                <button class="br-button circle disabled" type="button" aria-label="Voltar página"><i class="fas fa-angle-left" aria-hidden="true"></i>
                </button>
                <button class="br-button circle" type="button" aria-label="Página seguinte"><i class="fas fa-angle-right" aria-hidden="true"></i>
                </button>
              </div>
            </nav>
            """
        )

    # Dados base
    current_page = page_obj.number
    total_items = page_obj.paginator.count
    per_page = page_obj.paginator.per_page
    total_pages = page_obj.paginator.num_pages

    per_page_options = per_page_options or [10, 20, 30]

    # Cálculo da exibição “X–Y de Z itens”
    start_item = (current_page - 1) * per_page + 1
    end_item = min(start_item + per_page - 1, total_items)

    # Botões prev/next
    prev_disabled = "disabled" if not page_obj.has_previous() else ""
    next_disabled = "disabled" if not page_obj.has_next() else ""

    prev_link = (
        build_page_url(request, page_obj.previous_page_number(), extra_params)
        if page_obj.has_previous()
        else "javascript:void(0)"
    )
    next_link = (
        build_page_url(request, page_obj.next_page_number(), extra_params)
        if page_obj.has_next()
        else "javascript:void(0)"
    )

    # Select de “itens por página”
    per_page_html = []
    for opt in per_page_options:
        checked = "checked" if opt == per_page else ""
        # Adicionar a URL de navegação ao clicar no rádio
        url = build_per_page_url(request, opt, extra_params)
        per_page_html.append(
            format_html(
                """
                <div class="br-item" tabindex="-1">
                    <div class="br-radio">
                        <input id="per-page-{0}" type="radio" name="per-page" value="{0}" {1} 
                               onclick="window.location.href='{2}'"/>
                        <label for="per-page-{0}">{0}</label>
                    </div>
                </div>
                """,
                opt,
                mark_safe(checked),
                mark_safe(url),
            )
        )

    # Select de “ir para página”
    go_to_html = []
    for p in range(1, total_pages + 1):
        checked = "checked" if p == current_page else ""
        # Adicionar a URL de navegação ao clicar no rádio
        url = build_page_url(request, p, extra_params)
        go_to_html.append(
            format_html(
                """
                <div class="br-item" tabindex="-1">
                    <div class="br-radio">
                        <input id="go-to-{0}" type="radio" name="go-to" value="{0}" {1} 
                               onclick="window.location.href='{2}'"/>
                        <label for="go-to-{0}">{0}</label>
                    </div>
                </div>
                """,
                p,
                mark_safe(checked),
                mark_safe(url),
            )
        )

    # HTML final
    return format_html(
        """
        <nav class="br-pagination" aria-label="paginação" 
            data-total="{total}" data-current="{current}" data-per-page="{per_page}">
            <div class="pagination-per-page">
                <div class="br-select">
                    <div class="br-input">
                        <label for="per-page-selection">Exibir</label>
                        <input id="per-page-selection" type="text" placeholder=" " value="{per_page}">
                        <button class="br-button" type="button" aria-label="Exibir lista" tabindex="-1" data-trigger="data-trigger">
                            <i class="fas fa-angle-down" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div class="br-list" tabindex="0">
                        {per_page_html}
                    </div>
                </div>
            </div>
            <span class="br-divider d-none d-sm-block mx-3"></span>
            <div class="pagination-information d-none d-sm-flex">
                <span class="current">{start}</span>&ndash;
                <span class="per-page">{end}</span>&nbsp;de&nbsp;
                <span class="total">{total}</span>&nbsp;itens
            </div>
            <div class="pagination-go-to-page d-none d-sm-flex ml-auto">
                <div class="br-select">
                    <div class="br-input">
                        <label for="go-to-selection">Página</label>
                        <input id="go-to-selection" type="text" placeholder=" " value="{current}">
                        <button class="br-button" type="button" aria-label="Exibir lista" tabindex="-1" data-trigger="data-trigger">
                            <i class="fas fa-angle-down" aria-hidden="true"></i>
                        </button>
                    </div>
                    <div class="br-list" tabindex="0">
                        {go_to_html}
                    </div>
                </div>
            </div>
            <span class="br-divider d-none d-sm-block mx-3"></span>
            <div class="pagination-arrows ml-auto ml-sm-0">
                <a href="{prev_link}" class="br-button circle {prev_disabled}" type="button" aria-label="Voltar página">
                    <i class="fas fa-angle-left" aria-hidden="true"></i>
                </a>
                <a href="{next_link}" class="br-button circle {next_disabled}" type="button" aria-label="Página seguinte">
                    <i class="fas fa-angle-right" aria-hidden="true"></i>
                </a>
            </div>
        </nav>
        """,
        total=total_items,
        current=current_page,
        per_page=per_page,
        start=start_item,
        end=end_item,
        per_page_html=mark_safe("".join(per_page_html)),
        go_to_html=mark_safe("".join(go_to_html)),
        prev_link=prev_link,
        next_link=next_link,
        prev_disabled=prev_disabled,
        next_disabled=next_disabled,
    )
