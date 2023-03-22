import requests

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

params = {
    'db': 'mydb'
}

location = "SERF212"
data = f"climate,location={location} temperature=21,humidity=36"
url = "http://serf212a.desktop.utk.edu:8086/write"

response = requests.post(
    url=url,
    params=params,
    headers=headers,
    data=data
)

print(response)
print(response.status_code)