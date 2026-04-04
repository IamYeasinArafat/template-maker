# 🚀 Template Maker (Automated Admitted Posts)

**Template Maker** is a backend automation service designed to instantly generate personalized "Admitted" social media cards. By connecting a Google Form to a FastAPI backend via webhooks, this tool eliminates manual graphic design work, providing high-quality, 1:1 ratio images ready for posting.

## 🛠 The Workflow
The automation pipeline follows a seamless three-step process:
1.  **Google Form:** A student or admin submits data (Name, Major, ID, etc.).
2.  **Webhook Trigger:** The form submission triggers an Apps Script or third-party webhook.
3.  **FastAPI Backend:** The API receives the JSON payload, injects it into an HTML/CSS template, and renders a high-definition image (PNG/JPG).

---

## 🏗 Tech Stack
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Templating:** HTML/CSS (for pixel-perfect design control)
* **Image Rendering:** Playwright or Selenium (for headless browser screenshots)
* **Integration:** Google Apps Script / Webhooks

---

## 🎨 Current Design Progress
> [!NOTE]
> The project is currently in the **Initial Designing** phase. The current output is a functional MVP (Minimum Viable Product) focusing on the 1:1 aspect ratio suitable for Instagram and LinkedIn.

| Feature | Status |
| :--- | :--- |
| Google Form Integration | ✅ Done |
| FastAPI Endpoint | ✅ Done |
| Dynamic Data Injection | ✅ Done |
| Advanced UI/UX Styling | 🏗 In Progress |
| Custom Profile Photo Uploads | 📅 Planned |

---

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* Pip (Python package manager)

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/IamYeasinArafat/template-maker.git
   cd template-maker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

---

## 📈 Future Roadmap
* [ ] Support for multiple themes (Dark Mode, University Colors).
* [ ] Direct auto-posting to social media APIs.
* [ ] PDF generation for official certificates.
* [ ] Web dashboard for manual overrides and previews.

---

## 🤝 Contributing
Since this is an evolving project, feedback and contributions are welcome! Feel free to open an issue or submit a pull request if you have ideas for better template designs or more efficient rendering logic.

**Maintainer:** [IamYeasinArafat](https://github.com/IamYeasinArafat)