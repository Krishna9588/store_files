import httpx

# r = httpx.get('https://www.birlasoft.com/services/enterprise-products/aws')
r = httpx.post('https://www.birlasoft.com/services/enterprise-products/aws', data={'key': 'value'})

r
r.status_code
r.headers['content-type']
r.text