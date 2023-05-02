#!/usr/bin/env python3

import requests
import json

from django.http import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .forms import ConfigureFeaturesForm
from django.http import JsonResponse


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
def upgrade_subscription(request, subscription_id, subscription_level):
    # Only PUT method is supported
    if request.method == 'PUT':
        user = get_userdata(subscription_id)

        if isinstance(user, HttpResponse):
            # If the response is an HttpResponse, return it directly
            return user

        level_asked = subscription_level.lower()
        # Validates that only enters one of the 3 subscriptions
        if level_asked != "free" and level_asked != "basic" and level_asked != "premium":
            return HttpResponse("Only allowed:\nfree\nbasic\npremium")

        subscription = user["data"]["SUBSCRIPTION"]

        # Premium users can't upgrade more
        if subscription == "premium":
            return HttpResponse("You are already premium!", status=400)
        elif subscription == "basic" and level_asked == "free":
            return HttpResponse("Case not allowed here, please try the downgrade service", status=400)

        # Assign the level of the subscription asked
        user["data"]["SUBSCRIPTION"] = level_asked

        # Insert the label UPGRADE_DATE with the current date and time
        user["data"]["UPGRADE_DATE"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Update the user information in the customerdata microservice
        result = set_customerdata(user, subscription_id)
        return result
    else:
        return HttpResponse("Method not supported", status=405)


@csrf_exempt
# Downgrades the subscription level of a user, depending on its current subscription
def downgrade_subscription(request, subscription_id, subscription_level):
    # Only PUT method is supported
    if request.method == 'PUT':
        user = get_userdata(subscription_id)

        if isinstance(user, HttpResponse):
            # If the response is an HttpResponse, return it directly
            return user

        level_asked = subscription_level.lower()
        # Validates that only enters one of the 3 subscriptions
        if level_asked != "free" and level_asked != "basic" and level_asked != "premium":
            return HttpResponse("Only allowed:\nfree\nbasic\npremium")

        subscription = user["data"]["SUBSCRIPTION"]

        # Only free subscriptors are not allowed to downgrade more
        if subscription == "free":
            return HttpResponse("You're have already a free subscription")
        elif level_asked == "free":
            # Downgrade to free will turn off all the features

            user["data"]["ENABLED_FEATURES"]["CERTIFICATES_INSTRUCTOR_GENERATION"] = False
            user["data"]["ENABLED_FEATURES"]["INSTRUCTOR_BACKGROUND_TASKS"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_COURSEWARE_SEARCH"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_COURSE_DISCOVERY"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_DASHBOARD_SEARCH"] = False
            user["data"]["ENABLED_FEATURES"]["ENABLE_EDXNOTES"] = False
        elif level_asked == "premium":
            return HttpResponse("Case not allowed here, please try the upgrade service", status=400)

        # Assign the level of the subscription asked
        user["data"]["SUBSCRIPTION"] = level_asked

        # Insert the label DOWNGRADE_DATE with the current date and time
        user["data"]["DOWNGRADE_DATE"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Update the user information in the customerdata microservice
        result = set_customerdata(user, subscription_id)
        return result
    else:
        return HttpResponse("Method not supported", status=405)


@csrf_exempt
# Customize the features for basic/premium subscriptions only
def customize_features(request, subscription_id):
    # Only PUT method is supported
    if request.method == 'PUT':
        # Load request data as JSON
        data = json.loads(request.body)
        # Validate the request data using ConfigureFeaturesForm
        form = ConfigureFeaturesForm(data)

        # If the form is valid, proceed with processing the request.
        if form.is_valid():
            user = get_userdata(subscription_id)

            if isinstance(user, HttpResponse):
                # If the response is an HttpResponse, return it directly
                return user

            # Deny customization for users with a free subscription
            if user["data"]["SUBSCRIPTION"] == "free":
                return HttpResponse("Your subscription doesn't allow you to customize your features", status=400)

            # Retrieve the user's enabled features
            features = user["data"]["ENABLED_FEATURES"]

            # Update the user's enabled features based on the request data
            for key in data:
                if data[key] == 0:
                    data[key] = False
                    features[key] = data[key]
                elif data[key] != 1:
                    return HttpResponse("Values can only be 0 for False, or 1 for True", status=400)
                else:
                    data[key] = True
                    features[key] = data[key]

            # Save the updated user data
            set_customerdata(user, subscription_id)

            return HttpResponse("Features updated", status=200)
        else:
            # If the form is not valid, log the errors and return them as JSON
            return JsonResponse({'errors': form.errors}, status=400)

    else:
        return HttpResponse("Method not supported", status=405)