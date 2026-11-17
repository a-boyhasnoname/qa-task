import json
import os
import re
import uuid
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from utils.email_verification import get_email_otp

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / '.env')
BASE_URL = 'https://authorized-partner.vercel.app/'
REPORT_DIR = PROJECT_DIR / 'reports'
SCREENSHOT_DIR = REPORT_DIR / 'screenshots'
VIDEO_DIR = REPORT_DIR / 'videos'
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)
PHONE_HISTORY_FILE = PROJECT_DIR / 'phone_number_history.json'
PASSWORD = os.getenv('TEST_PASSWORD', 'QaTesting@123')
HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
TEST_COUNTRY = os.getenv('TEST_COUNTRY', 'Test')

# Authorized QA fixture numbers supplied by the user.
NEPAL_TEST_NUMBERS = [
    '9753163134', '9752890888', '9847891323', '9762744086',
    '9639032687', '9008425867', '9616635338', '9725869657',
    '9708302877', '9829959805', '9605959137', '9759522274',
    '9762489076', '9005000039', '9880332970', '9760234319',
    '9603901662', '9007899245',
]


def load_phone_history():
    if not PHONE_HISTORY_FILE.exists():
        return []
    with PHONE_HISTORY_FILE.open('r', encoding='utf-8') as file:
        history = json.load(file)
    if not isinstance(history, list) or not all(isinstance(x, str) for x in history):
        raise ValueError('phone_number_history.json must contain a list of strings')
    return history


def mark_phone_used(number):
    history = load_phone_history()
    if number not in history:
        history.append(number)
        temporary = PHONE_HISTORY_FILE.with_suffix('.tmp')
        with temporary.open('w', encoding='utf-8') as file:
            json.dump(history, file, indent=2)
        temporary.replace(PHONE_HISTORY_FILE)


def get_next_phone_number():
    used = set(load_phone_history())
    for number in NEPAL_TEST_NUMBERS:
        if number not in used:
            return number
    raise RuntimeError('All 18 Nepal test numbers have been used. Review test accounts before reusing numbers.')


def fill_nepal_phone(page):
    phone = page.get_by_role('textbox', name='Phone Number')
    expect(phone).to_be_visible()
    # Nepal (+977) is the form default. Do not open the country selector.
    country = page.get_by_role('combobox').first
    expect(country).to_contain_text('🇳🇵')
    number = get_next_phone_number()
    phone.fill(number)
    expect(phone).to_have_value(number)
    # Reserve immediately, even if a later stage fails, to avoid duplicate attempts.
    mark_phone_used(number)
    print(f'Nepal test phone selected: +977 {number}')
    return number


def take_screenshot(page, filename):
    page.screenshot(path=str(SCREENSHOT_DIR / f'{filename}.png'), full_page=True)


def generate_test_email():
    domain = os.environ['MAILOSAUR_DOMAIN'].strip()
    if '@' in domain:
        domain = domain.rsplit('@', 1)[1]
    return f'qa-{uuid.uuid4().hex[:10]}@{domain}'


def click_next(page):
    button = page.get_by_role('button', name='Next', exact=True)
    expect(button).to_be_visible()
    expect(button).to_be_enabled()
    button.click()


def close_dialog(page, outside_locator=None):
    dialog = page.get_by_role('dialog')
    if dialog.count() == 0 or not dialog.is_visible():
        return
    page.keyboard.press('Escape')
    if dialog.is_visible() and outside_locator is not None:
        outside_locator.click()
    expect(dialog).not_to_be_visible()


def select_dialog_value(page, dropdown, value):
    dropdown.click()
    dialog = page.get_by_role('dialog')
    expect(dialog).to_be_visible()
    dialog.get_by_role('textbox', name='Search...').fill(value)
    selection = dialog.get_by_text(value, exact=True)
    expect(selection).to_be_visible()
    selection.click()
    expect(dropdown).to_contain_text(value)
    close_dialog(page, page.get_by_role('textbox', name='Address', exact=True))


def select_experience(page, value='1 year'):
    dropdown = page.get_by_role('combobox').first
    expect(dropdown).to_be_visible()
    dropdown.click()
    dialog = page.get_by_role('dialog')
    if dialog.count() > 0 and dialog.is_visible():
        search = dialog.get_by_role('textbox', name='Search...')
        if search.count() > 0:
            search.fill(value)
        choice = dialog.get_by_text(value, exact=True)
    else:
        option = page.get_by_role('option', name=value, exact=True)
        choice = option if option.count() > 0 else page.get_by_text(value, exact=True)
    try:
        expect(choice).to_be_visible(timeout=5000)
        choice.click()
    except (AssertionError, PlaywrightTimeoutError):
        print('Experience dropdown snapshot:')
        print(page.locator('body').aria_snapshot())
        raise
    close_dialog(page)
    print(f'Experience selected: {value}')


def select_preferred_country(page, country='Test'):
    dropdown = page.get_by_role('combobox', name='Preferred Countries')
    expect(dropdown).to_be_visible()
    dropdown.click()
    dialog = page.get_by_role('dialog')
    if dialog.count() > 0 and dialog.is_visible():
        search = dialog.get_by_role('textbox', name='Search...')
        if search.count() > 0:
            search.fill(country)
        choice = dialog.get_by_text(country, exact=True)
        expect(choice).to_be_visible()
        choice.click()
        expect(dropdown).to_contain_text(country)
        close_dialog(page)
    else:
        choice = page.get_by_role('option', name=country, exact=True)
        expect(choice).to_be_visible()
        choice.click()
    print(f'Preferred country selected: {country}')


def signup(page):
    print('\nStarting signup automation...')
    test_email = generate_test_email()

    page.goto(BASE_URL, wait_until='domcontentloaded')
    page.locator('button').filter(has_text=re.compile(r'^Join Us Now$')).click()
    print('Registration page opened.')

    page.get_by_role('checkbox', name='I agree to the Terms of').check()
    page.get_by_role('button', name='Continue').click()
    expect(page.get_by_role('textbox', name='First Name')).to_be_visible()
    print('Terms accepted.')

    page.get_by_role('textbox', name='First Name').fill('John')
    page.get_by_role('textbox', name='Last Name').fill('Doe')
    page.get_by_role('textbox', name='Email Address').fill(test_email)
    fill_nepal_phone(page)
    page.locator('input[name="password"]').fill(PASSWORD)
    page.locator('input[name="confirmPassword"]').fill(PASSWORD)
    expect(page.get_by_role('textbox', name='Email Address')).to_have_value(test_email)
    take_screenshot(page, '00_personal_information')
    click_next(page)
    print('Personal information submitted.')

    print('Retrieving OTP from test inbox...')
    verification_code = get_email_otp(test_email)
    otp_input = page.get_by_role('textbox').first
    expect(otp_input).to_be_visible()
    otp_input.fill(verification_code)
    page.get_by_role('button', name='Verify Code').click()
    expect(page.get_by_role('textbox', name='Role in Agency')).to_be_visible(timeout=15000)
    print('Email verification completed.')

    page.get_by_role('textbox', name='Name', exact=True).fill('John Doe')
    page.get_by_role('textbox', name='Role in Agency').fill('Manager')
    page.get_by_role('textbox', name='Email Address').fill(test_email)
    page.get_by_role('textbox', name='Website').fill('www.example.com')
    page.get_by_role('textbox', name='Address', exact=True).fill('Kathmandu, Nepal')
    select_dialog_value(page, page.get_by_role('combobox').first, 'Test')
    print('Region of Operation: Test selected')
    take_screenshot(page, '01_agency_details')
    click_next(page)
    expect(page.get_by_role('spinbutton', name='Number of Students Recruited')).to_be_visible(timeout=15000)
    print('Professional Experience page opened.')

    select_experience(page, '1 year')
    page.get_by_role('spinbutton', name='Number of Students Recruited').fill('1000')
    page.get_by_role('textbox', name='Focus Area').fill('Student recruitment to Australia')
    page.get_by_role('spinbutton', name='Success Metrics').fill('85')
    for service in ['Career Counseling', 'Visa Processing', 'Test Prepration']:
        page.get_by_role('checkbox', name=service).check()
    admission = page.get_by_role('checkbox', name='Admission Applications')
    if admission.count() > 0:
        admission.check()
    take_screenshot(page, '02_professional_experience')
    click_next(page)
    expect(page.get_by_role('textbox', name='Business Registration Number')).to_be_visible(timeout=15000)
    print('Professional Experience submitted.')

    page.get_by_role('textbox', name='Business Registration Number').fill('12121231234')
    select_preferred_country(page, TEST_COUNTRY)
    page.get_by_role('checkbox', name='Universities').check()
    page.get_by_role('checkbox', name='Colleges').check()
    print('Business preferences completed.')

    test_file = PROJECT_DIR / 'test_data' / 'test.webp'
    if not test_file.is_file():
        raise FileNotFoundError(f'Test document not found: {test_file}')
    file_input = page.locator('input[type="file"]').first
    expect(file_input).to_be_attached()
    file_input.set_input_files(str(test_file))
    print('Test document uploaded.')
    take_screenshot(page, '03_verification_preferences')

    submit_button = page.get_by_role('button', name='Submit', exact=True)
    expect(submit_button).to_be_visible()
    expect(submit_button).to_be_enabled()
    submit_button.click()
    print('Final submission clicked.')

    success_url = re.compile(r'/admin/profile/?(?:\?.*)?$')
    success_message = page.get_by_text(re.compile(
        r'registration successful|application submitted successfully|registration completed|thank you for registering',
        re.IGNORECASE
    )).first
    try:
        page.wait_for_url(success_url, timeout=15000)
    except PlaywrightTimeoutError:
        try:
            expect(success_message).to_be_visible(timeout=5000)
        except (AssertionError, PlaywrightTimeoutError):
            take_screenshot(page, 'signup_unconfirmed')
            print('Current URL:', page.url)
            print(page.locator('body').aria_snapshot())
            raise AssertionError('Signup submission could not be confirmed through the UI.')

    take_screenshot(page, '04_signup_success')
    print('\n==============================')
    print('SIGNUP AUTOMATION PASSED')
    print('==============================')
    print(f'Test email: {test_email}')
    print(f'Final URL: {page.url}')


def test_complete_signup():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=HEADLESS,
            slow_mo=200 if not HEADLESS else 0
        )
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            record_video_dir=str(VIDEO_DIR)
        )
        page = context.new_page()
        page.set_default_timeout(15000)
        try:
            signup(page)
        except Exception:
            take_screenshot(page, 'error')
            raise
        finally:
            context.close()
            browser.close()


if __name__ == '__main__':
    test_complete_signup()
