# data_extractor/scrapers/profile_scraper.py

from bs4 import BeautifulSoup, Tag
import re

class ProfileScraper:
    """
    Final, robust version built from forensic HTML analysis.
    This version uses a list of selectors for each field to handle multiple page layouts.
    It is designed to fail gracefully on a per-field basis.
    """
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')

    def _get_text_or_none(self, element: Tag | None) -> str | None:
        return element.get_text(strip=True) if element else None

    def _find_first(self, selectors: list[tuple[str, dict]]) -> Tag | None:
        """Tries a list of selectors and returns the first element found."""
        for tag, attrs in selectors:
            element = self.soup.find(tag, **attrs)
            if element:
                return element
        return None

    def extract_data(self) -> dict:
        return {
            "doctor_name": self.extract_doctor_name(),
            "specialty": self.extract_specialty(),
            "years_of_experience": self.extract_experience(),
            "recommendation_percent": self.extract_recommendation(),
            "clinic_name": self.extract_clinic_name(),
            "address": self.extract_address(),
            "ratings_and_reviews": self.extract_reviews_and_ratings(),
            "contact_number": None,
            "contact_email": None,
        }

    def extract_doctor_name(self) -> str | None:
        selectors = [
            ('h1', {'class_': 'u-title', 'data-qa-id': 'doctor-name'}),
            ('h1', {'class_': 'c-profile__title'})
        ]
        return self._get_text_or_none(self._find_first(selectors))

    def extract_specialty(self) -> str | None:
        container = self.soup.find('div', class_='c-profile--qualification')
        if container:
            specialty_tag = container.find('h2', class_='c-profile__details')
            return self._get_text_or_none(specialty_tag)
        
        # Fallback for the other layout
        container = self.soup.find('div', class_='u-d-flex')
        if container:
            specialty_tag = container.find('p', class_='u-large-font')
            return self._get_text_or_none(specialty_tag)
        return None

    def extract_experience(self) -> int | None:
        # Tries multiple methods to find experience
        try:
            # Method 1: Look for the specific data-qa-id
            exp_tag = self.soup.find('span', {'data-qa-id': 'years_of_experience'})
            if exp_tag and (text := self._get_text_or_none(exp_tag)):
                if match := re.search(r'(\d+)', text):
                    return int(match.group(1))

            # Method 2: Look for it combined with specialty text
            h2_tags = self.soup.find_all('h2', class_='c-profile__details')
            for tag in h2_tags:
                text = tag.get_text()
                if "Years Experience Overall" in text:
                    if match := re.search(r'(\d+)', text):
                        return int(match.group(1))
        except Exception:
            return None
        return None

    def extract_recommendation(self) -> int | None:
        try:
            rec_container = self.soup.find('div', attrs={'data-qa-id': 'doctor-recommendation'})
            if rec_container:
                text = self._get_text_or_none(rec_container.find('span'))
                if text and (match := re.search(r'(\d+)%', text)):
                    return int(match.group(1))
        except (ValueError, TypeError):
            pass
        return None

    def extract_clinic_name(self) -> str | None:
        selectors = [
            ('a', {'class_': 'c-profile--clinic__name'}),
            ('p', {'class_': 'u-bold u-d-inline-block u-valign--middle'}),
            ('p', {'data-qa-id': 'doctor_clinic_name'})
        ]
        return self._get_text_or_none(self._find_first(selectors))

    def extract_address(self) -> str | None:
        selectors = [
            ('p', {'data-qa-id': 'clinic-address'}),
            ('p', {'data-qa-id': 'practice-address'})
        ]
        return self._get_text_or_none(self._find_first(selectors))

    def extract_reviews_and_ratings(self) -> dict:
        summary = {'total_reviews': 0, 'overall_rating': None, 'reviews_summary': []}
        try:
            # Get total reviews
            stories_tab = self.soup.find('li', {'data-qa-id': 'feedback-tab'})
            if stories_tab:
                text = self._get_text_or_none(stories_tab)
                if text and (match := re.search(r'\((\d+)\)', text)):
                    summary['total_reviews'] = int(match.group(1))
            
            # Get overall star rating
            rating_container = self.soup.find('div', class_='common__star-rating')
            if rating_container:
                 rating_value = rating_container.find('span', class_='common__star-rating__value')
                 summary['overall_rating'] = self._get_text_or_none(rating_value)

            # Get review text
            review_elements = self.soup.find_all('p', class_='feedback__content')
            summary['reviews_summary'] = [self._get_text_or_none(r) for r in review_elements if r]
        except Exception:
            pass
        return summary