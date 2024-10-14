"""
Some checks for the contact page, focussed on the contact form.

Currently do not test a successful form submission, as this would require a valid recaptcha token.
"""

import re

import pytest

from playwright.sync_api import Locator, Page, expect


@pytest.fixture
def recaptcha_alert(contact_page: Page) -> Locator:
    """
    Recaptcha alert message.
    Becomes visible if form attempts to be submitted without recaptcha.
    """
    return contact_page.get_by_label("reCAPTCHA verification alert")


@pytest.fixture
def form_alert(contact_page: Page) -> Locator:
    """
    Form alert message for missing or badly formatted field.
    Becomes visible if form attempts to be submitted without all required fields filled in.
    """
    return contact_page.get_by_text("Please fill out all the")


def test_has_title(contact_page: Page):
    """Test that the contact page has the correct title."""
    expect(contact_page).to_have_title(re.compile("Contact"))


def test_error_messages_hidden(contact_page: Page, form_alert: Locator, recaptcha_alert: Locator):
    """
    Test that the error messages are hidden by default.
    """
    expect(form_alert).to_be_hidden()
    expect(recaptcha_alert).to_be_hidden()


def test_no_recapatcha(contact_page: Page, form_alert: Locator, recaptcha_alert: Locator):
    """
    Validate that filling in whole form but not doing recaptcha raises the recaptcha alert message.
    """
    # fill out form except the description and recaptcha.
    contact_page.get_by_placeholder("first name last name").fill("a name")
    contact_page.locator("#emailInput").fill("anemail@gmail.com")
    contact_page.get_by_text("Expression of interest to").click()
    contact_page.get_by_label("text input").fill("some descriptive text")
    contact_page.get_by_label("Submit the form").click()

    # check that the alert messages are displayed.
    expect(recaptcha_alert).to_be_visible()
    expect(form_alert).to_be_hidden()


def test_not_fill_in_description(contact_page: Page, form_alert: Locator, recaptcha_alert: Locator):
    """
    Validate that not filling in the description and recaptcha raises both alert messages.
    """
    # fill out form except the description and recaptcha.
    contact_page.get_by_placeholder("first name last name").fill("a name")
    contact_page.locator("#emailInput").fill("anemail@gmail.com")
    contact_page.get_by_text("Expression of interest to").click()
    contact_page.get_by_label("Submit the form").click()

    # check that both alert messages are correctly displayed.
    expect(recaptcha_alert).to_be_visible()
    expect(form_alert).to_be_visible()


def test_bad_format_email_raises_warning(contact_page: Page, form_alert: Locator, recaptcha_alert: Locator):
    """
    Validate that filling in a bad email format raises an alert message.
    """
    # fill out form except the description and recaptcha.
    contact_page.get_by_placeholder("first name last name").fill("a name")
    contact_page.locator("#emailInput").fill("a bad formatted email")
    contact_page.get_by_text("Expression of interest to").click()
    contact_page.get_by_label("text input").fill("some descriptive text")
    contact_page.get_by_label("Submit the form").click()

    # check that both alert messages are correctly displayed.
    expect(recaptcha_alert).to_be_visible()
    expect(form_alert).to_be_visible()

    # correct email, and check that alert message goes away
    contact_page.locator("#emailInput").fill("realemail@gmail.com")
    contact_page.get_by_label("Submit the form").click()
    expect(form_alert).to_be_hidden()
