
# 🩺 Doctor Data Scraper & Analyzer
*From Chaos to Clarity: Transform Healthcare Data with Intelligence*

<div align="center">

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Async](https://img.shields.io/badge/async-enabled-green.svg)
![AI-Powered](https://img.shields.io/badge/AI-powered-purple.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

**🚀 Scrape → 🧹 Clean → 🎯 Analyze → 📊 Export**

*Turn messy healthcare websites into crystal-clear data goldmines*

</div>

---

### 🎯 What Does This Do?

Ever tried manually collecting doctor information from healthcare websites? **It's painful.** 

This project is your **AI-powered assistant** that:
- 🕷️ **Sneaks into** healthcare platforms and extracts doctor profiles (legally!)
- 🧠 **Thinks smart** about the data — validates addresses, cleans phone numbers
- 💬 **Reads between the lines** of patient reviews using sentiment analysis
- 📈 **Serves you** polished Excel reports that your boss will actually love
  

### 🎪 The Magic Happens in 3 Acts:

🎭 ACT I: The Hunter 🎭 ACT II: The Alchemist 🎭 ACT III: The Storyteller

Playwright crawls webs → Python cleans & validates → Excel gets the royal treatment
Extracts hidden data, Geo-codes addresses and generates Beautiful summaries with AI

---

### 🎮 Input vs Output (The Transformation)

### 🔴 **BEFORE:** Messy URLs

https://www.practo.com/pune/doctor/some-messy-url-with-weird-params?id=12345

### 🟢 **AFTER:** Pure Gold
| 👨‍⚕️ Doctor | 🩺 Specialty | 📅 Experience | 📍 Address | 🏥 Hospital | ⭐ Rating | 💬 What Patients Say |
|------------|-------------|---------------|------------|-------------|-----------|---------------------|
| Dr. Rajesh Sharma | Cardiologist | 15 years | Apollo Clinic, Pune | Apollo Healthcare | 4.8⭐ | PROS: Amazing bedside manner, quick diagnosis; CONS: none; 92% Highly Recommended ✨ |

---

### 🛠️ Setup (2 Minutes to Glory!)

### 🎯 Quick Start
1. Clone this bad boy : </br>
git clone https://github.com/yourusername/doctor-data-scraper.git

2. Jump in :</br>
cd doctor-data-scraper

3. Create your fortress :</br>
python -m venv venv</br>
source venv/bin/activate # Linux/Mac</br>

   OR </br>
venv\Scripts\activate # Windows 

4. Arm yourself :</br>
pip install -r requirements.txt

5. Download AI brain :</br>
python -c "import nltk; nltk.download('vader_lexicon')"

6. FIRE! 🚀 </br>
python -m data_extractor.main

---

### 🏗️ Architecture (The Brain Behind The Beauty)
🎬 Start  
   ↓  
📥 **Input**  
   • URL List (`.csv`)  
   ↓  
🤖 **Scraper Bot** (Playwright)  
   • Navigates to each profile  
   • Clicks “Call Now” for contacts  
   ↓  
💾 **Raw Data** (`.json`)  
   ↓  
🧹 **Data Cleaner**  
   • Validates & geocodes addresses  
   • Classifies specialty  
   • Standardizes fields  
   ↓  
🔍 **Structured Data** (`.json`)  
   ↓  
📊 **Excel Master**  
   • Formats 10 columns  
   • Cleans phone, ratings, reviews  
   • Sentiment-based pros & cons  
   • Recommendation scoring  
   ↓  
🎨 **Final Report** (`.xlsx`)  
   • “Doctor Data” sheet with polished data  
   ↓  
🏁 End  

---

### 🎪 Features That'll Blow Your Mind

### 🕵️‍♀️ **Stealth Mode Scraping**
- Headless browser automation (they'll never see us coming!)
- Auto-clicks "Call Now" buttons to reveal hidden contact info
- Handles dynamic content like a ninja

### 🧠 **AI-Powered Intelligence**
- Sentiment analysis reads patient emotions
- Auto-generates pros/cons summaries
- Smart recommendation scoring

### 🎨 **Excel Wizardry**
- Phone numbers that don't turn into scientific notation
- Color-coded ratings and recommendations
- Clean, professional formatting your clients will love

---

### 🎯 What You Get

### 📋 **10 Perfect Columns:**
1. 🏠 **Complete Address** - Full location details
2. 👨‍⚕️ **Doctor Name** - Crystal clear names
3. 🩺 **Specialty** - What they're good at
4. 🏥 **Clinic/Hospital** - Where they practice
5. 📅 **Years of Experience** - Their expertise level
6. 📞 **Contact Number** - Direct phone lines
7. 📧 **Contact Email** - Digital reach
8. ⭐ **Ratings** - Star power (or "not available")
9. 💬 **Reviews** - What patients actually say
10. 🎯 **AI Summary** - Smart pros/cons analysis

---

### 🏆 Pro Tips

Test with small batches first
TEST_LIMIT = 10 # in config.py

Then go full beast mode
TEST_LIMIT = None

---

### 🤝 Join the Revolution

Found a bug? Have an idea? Want to add superpowers?

**We welcome all data warriors!** 🛡️

---

<div align="center">

### 🌟 **Ready to Transform Healthcare Data?**

**Star this repo if it saved your sanity!** ⭐

*Built with ❤️ and lots of ☕ by data enthusiasts*

</div>
