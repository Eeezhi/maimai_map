from requests_html import HTMLSession

for a in range(0, 46):
    session = HTMLSession()
    response = session.get(
        url="https://location.am-all.net/alm/location?gm=96&ct=1000&at={a}&lang=en".format(a=a)
    )
    
    