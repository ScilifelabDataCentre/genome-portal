"""
Tests for the footer, using the home page (even if footer present on every page).
"""

import re

from playwright.sync_api import Page, expect


def test_site_navigation(home_page: Page) -> None:
    """
    Test links in the Site Navigation section redirect to the correct page.
    """
    SITE_NAVIGATION_LINKS = {
        "Home": "Home",
        "Contribute": "Contribute",
        "About the Portal": "About",
        "Information på svenska": "Information på svenska",
        "Contact us": "Contact",
        "Cite us": "How to cite the Genome Portal and the data",
        "Glossary": "Glossary",
        "User guide": "User guide",
        "Terms of use": "Terms of use",
        "Privacy policy": "Privacy policy",
        "FAQ": "Frequently Asked Questions",
    }
    site_navigation = home_page.get_by_role("heading", name="Site navigation").locator("..")

    for name, title in SITE_NAVIGATION_LINKS.items():
        site_navigation.get_by_role("link", name=name).click()
        expect(home_page).to_have_title(re.compile(title))


def test_funding_logos(home_page: Page) -> None:
    """
    Test that the funding logos are visible and have right hrefs
    """
    LOGOS = {
        "Knut and Alice Wallenberg": "https://kaw.wallenberg.org/en",
        "Swedish Foundation for Strategic Research": "https://strategiska.se/en/",
        "SciLifeLab's Logo": "https://www.scilifelab.se/",
    }
    for name, url in LOGOS.items():
        logo_link = home_page.get_by_role("link", name=re.compile(name))
        expect(logo_link).to_be_visible()
        expect(logo_link).to_have_attribute("href", url)


def test_social_media_links(home_page: Page) -> None:
    """
    Test that the social media links are visible and have right hrefs
    """
    SOCIAL_LINKS = {
        "LinkedIn": "https://www.linkedin.com/company/scilifelab/",
        "Twitter": "https://x.com/scilifelab",
        "YouTube": "https://www.youtube.com/channel/UCfWQHAK8UW0mPghV8R-Jqzg",
    }

    socials_section = home_page.get_by_role("heading", name="Stay Updated").locator("..")

    for name, url in SOCIAL_LINKS.items():
        link = socials_section.get_by_role("link", name=name)
        expect(link).to_be_visible()
        expect(link).to_have_attribute("href", url)
