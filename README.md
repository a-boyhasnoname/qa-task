# Authorized Partner - Signup Automation

Automation script for the complete signup flow on https://authorized-partner.vercel.app/

Built with **Python + Playwright** for the Vrit Technologies QA Intern Task Round.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (tested on 3.13)
- **Node.js 18+** (for Playwright browser install)
- **Mailosaur account** (for email OTP verification)

### Installation

```bash
# Clone and enter the project
git clone <your-repo-url>
cd authorized-partner-qa

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install playwright mailosaur python-dotenv

# Install Chromium browser
playwright install chromium
```

### Configuration

Create a `.env` file in the project root:
Look at the .env.example file in this repo.
---

## ▶️ How to Run

### Normal run (browser visible - good for watching)
```bash
python signup_automation_script.py
```

### Headless mode (for CI/CD)
```bash
# Windows PowerShell
$env:HEADLESS="true"; python signup_automation_script.py

# Or edit .env and set HEADLESS=true
```

### What happens when you run it:
1. Opens https://authorized-partner.vercel.app/register
2. Accepts Terms & Conditions
3. Fills personal info (name, email, Nepal phone, password)
4. **Automatically fetches OTP from Mailosaur** and verifies email
5. Fills agency details (name, role, address, region)
6. Completes professional experience (experience, metrics, services)
7. Sets business preferences (registration number, countries, institution types)
8. Uploads test document (`test_data/test.webp`)
9. Submits final application
10. Verifies success redirect to `/admin/profile`

---

## 🛠️ Environment & Setup Details

| Component | Version/Details |
|-----------|-----------------|
| **Language** | Python 3.13 |
| **Automation Framework** | Playwright 1.65.2 (sync API) |
| **Browser** | Chromium (headless/headed) |
| **Email/OTP** | Mailosaur Python SDK 8.1.1 |
| **Config Management** | python-dotenv 1.2.4 |
| **Test Runner** | Standalone script (can wrap with pytest) |
| **OS Tested** | Windows 11 (PowerShell) |

### Browser/Driver Versions
- Playwright manages its own Chromium binary (~130MB)
- No separate ChromeDriver needed
- Run `playwright install chromium` to get the exact version Playwright expects

---

## 📊 Test Data & Accounts Used

### Phone Numbers (Nepal +977)
The script rotates through **18 pre-authorized test numbers** to avoid duplicates:
```
9753163134, 9752890888, 9847891323, 9762744086,
9639032687, 9008425867, 9616635338, 9725869657,
9708302877, 9829959805, 9605959137, 9759522274,
9762489076, 9005000039, 9880332970, 9760234319,
9603901662, 9007899245
```
- Stored in `signup_automation_script.py` as `NEPAL_TEST_NUMBERS`
- Used numbers tracked in `phone_number_history.json`
- Reset with: `echo "[]" > phone_number_history.json`

### Email Addresses
- **Generated dynamically** per run: `qa-{uuid}@{MAILOSAUR_DOMAIN}`
- Example: `qa-a1b2c3d4e5@2ivkry6u.mailosaur.net`
- No real mailbox needed - Mailosaur catches them

### Password
- Default: `QaTesting@123` (set via `TEST_PASSWORD` in .env)

### Test Document
- File: `test_data/test.webp` (3.3 KB sample image)
- Used for the document upload step in Verification & Preferences

### Country/Region Selections
- **Phone country**: Nepal (+977) - default, not changed
- **Region of Operation**: "Test" (searchable dropdown)
- **Preferred Countries**: "Test" (multi-select)
- **Institution Types**: Universities + Colleges checkboxes

---

## 📁 Project Structure

```
authorized-partner-qa/
├── signup_automation_script.py      # Main automation script
├── README_execution_steps.md        # This file
├── requirements.txt                 # Python dependencies
├── .env.example                     # Template for .env
├── .gitignore                       # Excludes .env, reports, __pycache__
├── phone_number_history.json        # Tracks used phone numbers
├── test_data/
│   └── test.webp                    # Upload test file
├── utils/
│   ├── __init__.py
│   └── email_verification.py        # Mailosaur OTP helper
└── reports/                         # Generated after each run
    ├── screenshots/
    │   ├── 00_personal_information.png
    │   ├── 01_agency_details.png
    │   ├── 02_professional_experience.png
    │   ├── 03_verification_preferences.png
    │   └── 04_signup_success.png
    └── videos/
        └── page@<timestamp>.webm    # Full execution recording
```

---

## 📸 Reports & Evidence

After every run you get:

| Artifact | Location | Purpose |
|----------|----------|---------|
| **5 Screenshots** | `reports/screenshots/` | One per major step |
| **Video Recording** | `reports/videos/` | Full run in WebM format |
| **Console Logs** | Terminal output | Step-by-step progress |

---

## ⚠️ Known Limitations & Notes

- **Mailosaur required** - free tier works but needs valid API key
- **Phone pool is finite** - 18 numbers, then you must reset history
- **UI changes break locators** - uses role-based selectors where possible
- **No parallel runs** - `phone_number_history.json` isn't thread-safe
- **Test accounts persist** - each run creates a real account on the platform
- **Headed mode default** - set `HEADLESS=true` for CI

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `playwright: command not found` | `pip install playwright && playwright install chromium` |
| `MAILOSAUR_API_KEY not set` | Check `.env` file exists and has correct keys |
| OTP timeout / not found | Verify Mailosaur server ID and domain match |
| "All Nepal test numbers used" | `echo "[]" > phone_number_history.json` |
| Element not found / timeout | Run headed (`HEADLESS=false`) to watch and debug |
| File upload fails | Ensure `test_data/test.webp` exists |

---

## 👨‍💻 About This Project

Built as part of the **Vrit Technologies QA Intern Task Round**.

The goal was to automate the complete agency registration flow on the Authorized Partner platform - from landing on the register page through email verification, multi-step forms, document upload, and final submission confirmation.

**Key challenges solved:**
- Dynamic React components with Playwright's auto-waiting
- Mailosaur integration for real email OTP retrieval
- Searchable dropdown handling (Region, Countries)
- Test data rotation to avoid duplicate phone numbers
- File upload in headless/headed modes
- Robust success verification (URL + content checks)

---
