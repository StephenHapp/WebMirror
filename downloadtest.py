import requests

response = requests.get("https://" + "upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Graeco-Roman_surgical_instruments._Wellcome_L0012385.jpg/220px-Graeco-Roman_surgical_instruments._Wellcome_L0012385.jpg")
print(response.ok)
print(response.status_code)