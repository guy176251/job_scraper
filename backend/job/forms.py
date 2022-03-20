from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Row, Submit
from django import forms

from .models import Application, Job


class RedirectForm(forms.Form):
    redirect = forms.CharField(widget=forms.HiddenInput)


class AppForm(RedirectForm):
    is_applying = forms.CharField(
        label="Applying?",
        max_length=5,
        widget=forms.RadioSelect(choices=Application.APPLY_CHOICES),
        required=False,
    )
    notes = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("is_applying"),
            Div("notes"),
            Div("redirect"),
            Div(
                Submit(name="submit_button", value="Submit"),
            ),
        )

    @classmethod
    def from_job(cls, job: Job, redirect: str):
        return cls(
            {
                "notes": job.application.notes,
                "is_applying": job.application.is_applying,
                "redirect": redirect,
            }
        )


class CompanyForm(RedirectForm):
    BOOL_CHOICES = [
        (1, "Yes"),
        (0, "No"),
    ]
    blocked = forms.CharField(
        label="Block company?",
        widget=forms.RadioSelect(choices=BOOL_CHOICES),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("blocked"),
            Div("redirect"),
            Div(
                Submit(name="submit_button", value="Submit"),
            ),
        )


class SearchForm(forms.Form):
    BOOL_CHOICES = [
        (1, "Yes"),
        (0, "No"),
    ]
    search = forms.CharField(
        label="",
        strip=True,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search"}),
    )
    regex = forms.CharField(
        label="Regex?",
        widget=forms.RadioSelect(choices=BOOL_CHOICES),
        required=False,
    )
    location = forms.CharField(
        label="Location",
        widget=forms.RadioSelect(choices=Job.LOCATION_CHOICES),
        required=False,
    )
    apply = forms.CharField(
        label="Apply Status",
        widget=forms.RadioSelect(choices=Application.APPLY_CHOICES),
        required=False,
    )
    indeed = forms.CharField(
        label="Apply through Indeed?",
        widget=forms.RadioSelect(choices=BOOL_CHOICES),
        required=False,
    )
    min_years = forms.ChoiceField(
        label="Minimum Years",
        choices=[(num, num) for num in range(11)],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gutter = "g-2"
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column("search", css_class="col-9"),
                        Column(
                            Submit(name="submit_button", value="Search"),
                            css_class="col-3",
                        ),
                        css_class=gutter,
                    ),
                    css_class="col-12",
                ),
                Column(
                    Row(
                        Column("regex"),
                        Column("location"),
                        Column("apply"),
                        Column("min_years"),
                        css_class=gutter,
                    ),
                    css_class="col-12",
                ),
                css_class=gutter,
            )
        )

    @classmethod
    def from_search(cls, search: str, apply: str):
        values = {
            "apply": apply,
        }

        if search:
            values.update(
                {
                    "search": search,
                    # "location": get_location(request),
                    # "regex": get_regex(request),
                }
            )

        return cls(values)


class KeywordsForm(RedirectForm):
    keywords = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 30}), required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div("keywords"),
            Div("redirect"),
            Div(
                Submit(name="submit_button", value="Submit"),
            ),
        )

    @classmethod
    def from_job(cls, job: Job, redirect: str):
        return cls({"keywords": job.keyword_string, "redirect": redirect})
