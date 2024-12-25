import os

# User Service
base_url = os.getenv("USER_MICROSERVICE_URL", "")
route_bp = "/users"
get_profile_url = base_url + route_bp + "/profile"
update_profile_url = base_url + route_bp + "/profile"