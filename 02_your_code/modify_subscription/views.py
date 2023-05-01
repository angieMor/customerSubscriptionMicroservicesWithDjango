import requests
import json

from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


# Fetch the user data from the API microservice
def get_userdata(subscription_id):

    # Construct the API URL using the provided subscription_id
    url = "http://127.0.0.1:8010/api/v1/customerdata/" + str(subscription_id) + "/"

    # Send an HTTP GET request to the API and store the response
    response = requests.get(url)

    # Check the status code of the response, continuing with the flow of the request or returning an error
    if response.status_code == 200:
        # Deserialize JSON data from the response text and return it
        return json.loads(response.text)

    elif response.status_code == 404:
        # Return an HttpResponse indicating the requested ID was not found, with a 404 status code
        return HttpResponse("id requested wasn't found", status=404)

    # For other cases, return an HttpResponse indicating the microservice is not running, with a 500 status code
    return HttpResponse("01_our_microservice is not running", status=500)


# Insert the data fields that were modified for the user
def set_customerdata(user, subscription_id):
    # Construct the API URL using the provided subscription_id
    url_of_customer = "http://127.0.0.1:8010/api/v1/customerdata/" + str(subscription_id) + "/"

    # Send an HTTP PUT request to the API to store the new data
    response = requests.put(url_of_customer, json=user)

    if response.status_code == 200:
        return HttpResponse("Success", status=200)

    return HttpResponse("Subscription/features couldn't be changed", status=404)


@csrf_exempt
# Upgrades the subscription level of a user, depending on its current subscription
def upgrade_subscription(request, subscription_id):
    # Only PUT method is supported
    if request.method == 'PUT':
        user = get_userdata(subscription_id)

        if isinstance(user, HttpResponse):
            # If the response is an HttpResponse, return it directly
            return user

        subscription = user["data"]["SUBSCRIPTION"]

        # Validate the actual subscription of the user, to upgrade it if possible
        if subscription == "free":
            user["data"]["SUBSCRIPTION"] = "basic"

        elif subscription == "basic":
            user["data"]["SUBSCRIPTION"] = "premium"

        else:
            return HttpResponse("You are already premium!", status=400)

        # Insert the label UPGRADE_DATE with the current date and time
        user["data"]["UPGRADE_DATE"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Update the user information in the customerdata microservice
        result = set_customerdata(user, subscription_id)
        return result
    else:
        return HttpResponse("Method not supported", status=405)


@csrf_exempt
# Downgrades the subscription level of a user, depending on its current subscription
def downgrade_subscription(request, subscription_id):
    # Only PUT method is supported
    if request.method == 'PUT':
        user = get_userdata(subscription_id)

        subscription = user["data"]["SUBSCRIPTION"]

        # Validates subscription value of the user, to downgrated if possible
        if subscription == "premium":
            user["data"]["SUBSCRIPTION"] = "basic"

        elif subscription == "basic":
            # Downgrade to free will turn off all the features
            user["data"]["SUBSCRIPTION"] = "free"

            user["data"]["ENABLED_FEATURES"]["CERTIFICATES_INSTRUCTOR_GENERATION"] = False
            user["data"]["ENABLED_FEATURES"]["INSTRUCTOR_BACKGROUND_TASKS"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_COURSEWARE_SEARCH"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_COURSE_DISCOVERY"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_DASHBOARD_SEARCH"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_EDXNOTES"] = False

        else:
            return HttpResponse("Subscription can't be more downgraded")

        # Insert the label DOWNGRADE_DATE with the current date and time
        user["data"]["DOWNGRADE_DATE"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Update the user information in the customerdata microservice
        result = set_customerdata(user, subscription_id)
        return result
    else:
        return HttpResponse("Method not supported", status=405)
