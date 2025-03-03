Para acessar api segue o Curl 

Login:

curl --location 'http://recommend-api-lb-1297247750.us-east-1.elb.amazonaws.com/login' \
--header 'Content-Type: application/json' \
--data '{
  "username": "admin",
  "password": "1234"
}'


Recommend API:

curl --location 'http://recommend-api-lb-1297247750.us-east-1.elb.amazonaws.com/recommend?param=4b60db90-152d-4f48-babd-b63125b19274' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE3NDA5NjQ5Nzd9.dE-7N3tmazSrk0nk4hyGWPYiGxZ5XKgQk5jl1LewOLw'

