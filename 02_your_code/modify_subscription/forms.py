from django import forms


# Create a form class for the configuration features to change
class ConfigureFeaturesForm(forms.Form):
    # Define form fields as integer fields with required attribute set to True
    CERTIFICATES_INSTRUCTOR_GENERATION = forms.IntegerField(required=True)
    INSTRUCTOR_BACKGROUND_TASKS = forms.IntegerField(required=True)
    ENABLE_COURSEWARE_SEARCH = forms.IntegerField(required=True)
    ENABLE_COURSE_DISCOVERY = forms.IntegerField(required=True)
    ENABLE_DASHBOARD_SEARCH = forms.IntegerField(required=True)
    ENABLE_EDXNOTES = forms.IntegerField(required=True)

    # Define a clean method to validate if a key is missing or if a value is empty
    def clean(self):
        cleaned_data = super().clean()

        # List of fields to check
        field_names = [
            'CERTIFICATES_INSTRUCTOR_GENERATION',
            'INSTRUCTOR_BACKGROUND_TASKS',
            'ENABLE_COURSEWARE_SEARCH',
            'ENABLE_COURSE_DISCOVERY',
            'ENABLE_DASHBOARD_SEARCH',
            'ENABLE_EDXNOTES',
        ]

        # Check for missing fields and empty values
        for field_name in field_names:
            value = cleaned_data.get(field_name, None)
            if value is None or value == "":
                self.add_error(field_name, "This field cannot be empty.")
