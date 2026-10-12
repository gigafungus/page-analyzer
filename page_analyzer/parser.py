import requests
from bs4 import BeautifulSoup


def parse_page(response: requests.Response) -> dict[str, str]:
    html = response.content
    soup = BeautifulSoup(html, features='html.parser')
    data = {}

    h1 = soup.h1
    print(h1)
    if h1:
        data['h1'] = h1.get_text(separator=' ', strip=True)

    title = soup.title
    if title:
        data['title'] = title.get_text(separator=' ', strip=True)

    meta = soup.find('meta', attrs={"name": "description"})
    if meta and meta.has_attr('content'):
        data['description'] = meta.get('content', default='').strip() # type: ignore

    return data