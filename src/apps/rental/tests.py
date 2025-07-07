import requests

# Endpoint URL
url = "https://alameedapi.ariflawfirm.com/api/rentals/rentals/"

# Your payload (form data)
payload = {
    'customer_data.first_name': 'test',
    'customer_data.middle_name': 'hello',
    'customer_data.last_name': 'user',
    'customer_data.phone_number': '123456789',
    'customer_data.id_number': '142525',
    'customer_data.nationality': 'egyption',
    'vehicle': '65',
    'start_date': '2025-05-21',
    'end_date': '2025-05-21'
}

# Download a sample image from the internet
image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTc9APxkj0xClmrU3PpMZglHQkx446nQPG6lA&s'
image_response = requests.get(image_url)
image_bytes = image_response.content

# Prepare files as tuples: (filename, bytes, mimetype)
files = [
    ('customer_data.license_front_photo', ('license_front.jpg', image_bytes, 'image/jpeg')),
    ('customer_data.license_back_photo', ('license_back.jpg', image_bytes, 'image/jpeg')),
    ('customer_data.id_front_photo', ('id_front.jpg', image_bytes, 'image/jpeg')),
    ('customer_data.id_back_photo', ('id_back.jpg', image_bytes, 'image/jpeg')),
    ('inspection_form', ('inspection.jpg', image_bytes, 'image/jpeg')),
]

# Your JWT token
headers = {
    'Authorization': 'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUyMzQyMzk5LCJpYXQiOjE3NTE3Mzc1OTksImp0aSI6ImY4ZjNmNDQwZDRhYzQwZTg5ZTE1MWYwNGY5NjdiZDE0IiwidXNlcl9pZCI6Mn0.Pb16ZN2_mZ3c8E-3QBEXzgSQ875XZ0hFFyQ36dvt06w'
}

# Send the POST request
response = requests.post(url, headers=headers, data=payload, files=files)

# Print response
print(response.status_code)
print(response.text)
