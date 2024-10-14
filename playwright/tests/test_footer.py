import re

from utils import validate_date_format

from playwright.sync_api import Page, expect


def test_site_navigation(home_page: Page):
    """Test links in the Site Navigation section redirect to the correct page."""
    links = {
        "Home": "Home",
        "Contribute": "Contribute",
        "About the Portal": "About",
        "Information på svenska": "Information på svenska",
        "Glossary": "Glossary",
        "Contact": "Contact",
        "Privacy policy": "Privacy Policy",
    }

    site_navigation = home_page.get_by_role("heading", name="Site navigation").locator("..")

    for name, title in links.items():
        site_navigation.get_by_role("link", name=name).click()
        expect(home_page).to_have_title(re.compile(title))


def test_funding_logos(home_page: Page):
    """Test that the funding logos are visible and have right hrefs"""
    logos = {
        "Knut and Alice Wallenberg": "https://kaw.wallenberg.org/en",
        "Swedish Foundation for Strategic Research": "https://strategiska.se/en/",
        "SciLifeLab": "https://www.scilifelab.se/",
    }
    for name, url in logos.items():
        logo_link = home_page.get_by_role("link", name=re.compile(name))
        expect(logo_link).to_be_visible()
        expect(logo_link).to_have_attribute("href", url)


def test_social_media_links(home_page: Page):
    """Test that the social media links are visible and have right hrefs"""
    links = {
        "LinkedIn": "https://www.linkedin.com/company/scilifelab/",
        "Twitter": "https://x.com/scilifelab",
        "YouTube": "https://www.youtube.com/channel/UCfWQHAK8UW0mPghV8R-Jqzg",
    }

    socials_section = home_page.get_by_role("heading", name="Stay Updated").locator("..")

    for name, url in links.items():
        link = socials_section.get_by_role("link", name=name)
        expect(link).to_be_visible()
        expect(link).to_have_attribute("href", url)


def test_site_last_updated(home_page: Page):
    """
    Test footer has a last updated section with a correctly formatted date.
    """
    last_updated_text = home_page.get_by_text(re.compile("Website last updated:"))
    expect(last_updated_text).to_be_visible()

    date = last_updated_text.inner_text().split(":")[1].strip()
    # Check that the date is in the correct format
    validate_date_format(date=date, date_format="%d %B %Y")
