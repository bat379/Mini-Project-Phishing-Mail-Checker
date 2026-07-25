# Mini-Project-Phishing-Mail-Checker
This repository is a beginnerlevel programming and cybersecurity project created during my learning journey.It combines my programming knowledge with AIassisted development to explore keyboard input handling and event processing.The project is still under development,helping me improve coding skills and understand operating system input mechanisms.


# 🛡️ PhishGuard

PhishGuard is a Python-based desktop application designed to help users identify and understand phishing emails through safe, read-only analysis. It examines email headers, sender information, embedded links, and common social engineering techniques to explain why a message may be suspicious.

Rather than detecting phishing through simple keyword matching alone, PhishGuard combines multiple security checks to evaluate an email's overall risk and presents the findings in an easy-to-understand format. The project is intended for cybersecurity education, awareness training, and defensive security research.

---

## 🚀 Features

- Analyze raw email content or imported `.eml` files
- Inspect email headers for suspicious indicators
- Detect sender and Reply-To mismatches
- Review SPF, DKIM, and DMARC authentication results
- Identify common social engineering techniques
- Analyze embedded URLs for suspicious characteristics
- Assign heuristic-based phishing risk scores
- Generate detailed PDF analysis reports
- Modern desktop interface built with CustomTkinter
- Educational module with phishing examples and awareness content
- Logging and scan history support

---

## 📂 Project Structure

```text
PhishGuard/
│
├── gui/
│   ├── Dashboard
│   ├── Email Analyzer
│   ├── Reports
│   ├── Awareness Hub
│   └── Settings
│
├── analyzer/
│   ├── Email Parser
│   ├── Header Analyzer
│   ├── Content Analyzer
│   └── Link Analyzer
│
├── education/
│   ├── Awareness Content
│   └── Phishing Examples
│
├── reports/
│   └── PDF Report Generator
│
├── database/
│   └── Database Manager
│
├── utils/
│   ├── Validators
│   └── Logger
│
├── assets/
├── main.py
└── requirements.txt
```

---

## ⚙️ Technologies

- Python 3.11+
- CustomTkinter
- Email Parser Libraries
- Regular Expressions (Regex)
- ReportLab
- SQLite
- Logging Module

---

## 🎯 How It Works

PhishGuard analyzes emails using several defensive security techniques.

The analysis process includes:

1. Loading raw email content or an `.eml` file.
2. Parsing email headers and sender metadata.
3. Checking SPF, DKIM, and DMARC authentication information.
4. Inspecting links for suspicious characteristics.
5. Detecting common phishing and social engineering patterns.
6. Calculating a heuristic risk score based on the collected indicators.
7. Generating a detailed PDF report explaining the results.

---

## 📊 Detection Indicators

The application evaluates several phishing indicators, including:

- Suspicious sender addresses
- Reply-To mismatches
- Missing or failed SPF, DKIM, and DMARC authentication
- Urgent or manipulative language
- Requests for sensitive information
- Suspicious or misleading URLs
- Multiple indicators combined into an overall phishing risk score

> **Note:** A high risk score does **not** guarantee that an email is malicious. It serves as an indicator that the message should be reviewed more carefully.

---

## 🖥️ Requirements

- Windows 10 / Windows 11
- Python 3.11 or later
- Dependencies listed in `requirements.txt`

---

## ▶️ Installation

```bash
git clone https://github.com/yourusername/PhishGuard.git

cd PhishGuard

pip install -r requirements.txt

python main.py
```

---

## 📚 Educational Purpose

PhishGuard was developed as a learning platform for students, security analysts, and cybersecurity enthusiasts who want to better understand how phishing attacks are identified. The project demonstrates how email headers, authentication records, link analysis, and social engineering indicators can be combined to assess suspicious emails without interacting with real-world attackers or modifying email systems.

---

## ⚠️ Disclaimer

PhishGuard is intended **solely for educational and defensive cybersecurity purposes**. The application performs read-only analysis of emails provided by the user and does not send emails, create phishing campaigns, spoof identities, harvest credentials, or perform any offensive activities. Always ensure you have permission before analyzing emails that are not your own.

---

## 📌 GitHub Description

**A Python-based phishing email analysis tool that examines email headers, authentication records, links, and social engineering indicators to help users identify suspicious messages and improve phishing awareness.**
```
