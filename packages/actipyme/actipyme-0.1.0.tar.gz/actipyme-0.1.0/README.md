# ActiPyme

![actiTime Logo][actitime]
![Python Logo][py]

Python interface to *actiTIME* API.

## Basic usage

```python
from actipyme import ApiClient

url = "<actitime_api_url>"
username = "<your_username>"
passwors = "<your_password>"

client = ApiClient(url, (username, password))

me = client.get_me()
print("Me:", me)
```

----

[py]: https://www.python.org/static/img/python-logo.png
[actitime]: https://www.actitime.com/_nuxt/assets/img/actitime-logo-color-bec498a.svg