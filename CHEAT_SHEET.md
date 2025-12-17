# Google Sheets Integration - Cheat Sheet

## 🚀 30-Second Setup

```powershell
# Step 1: Get credentials
python -c "from src.google_sheets_uploader import setup_google_sheets_integration; setup_google_sheets_integration()"

# Step 2: Save JSON as google_credentials.json

# Step 3: Edit config.py
GOOGLE_SHEETS_ENABLED = True

# Step 4: Run
python run_phase2.py

# Done! Watch your Google Sheet update automatically!
```

---

## 📋 Configuration (config.py)

```python
# MAIN SETTINGS
GOOGLE_SHEETS_ENABLED = True                        # On/off
GOOGLE_CREDENTIALS_PATH = "google_credentials.json" # Creds file
GOOGLE_SHEET_NAME = "HuggingFace Organizations"    # Sheet name
UPLOAD_INTERVAL = 25                                # Update frequency

# TIMING
REQUEST_TIMEOUT = 60                                # Wait 60s for response
REQUEST_DELAY = 1                                   # Wait 1s between requests

# PATHS
INPUT_CSV_PATH = "output/huggingface_organizations.csv"
OUTPUT_CSV_PATH = "output/huggingface_organizations_detailed.csv"
```

---

## ✅ Verify Setup

```powershell
# Comprehensive check
python test_google_sheets.py

# Should see:
# [1/4] Checking config.py... [OK]
# [2/4] Checking credentials file... [OK]
# [3/4] Checking required packages... [OK]
# [4/4] Testing Google Sheets authentication... [OK]
```

---

## 🏃 Quick Commands

```powershell
# RUN SCRAPER WITH GOOGLE SHEETS
python run_phase2.py

# VERIFY SETUP
python test_google_sheets.py

# VIEW LOGS
Get-Content output/phase2_scraper_*.log -Tail 50

# SEARCH UPLOADS IN LOGS
Select-String "\[SHEETS\]" output/phase2_scraper_*.log

# CHECK CSV LOCALLY
Import-Csv output/huggingface_organizations_detailed.csv | Select-Object -First 5

# COUNT ROWS
(Import-Csv output/huggingface_organizations_detailed.csv).Count

# DISABLE GOOGLE SHEETS (LOCAL ONLY)
# Edit config.py: GOOGLE_SHEETS_ENABLED = False
```

---

## 🛠️ Common Tasks

### Adjust Upload Frequency
```python
# In config.py:
UPLOAD_INTERVAL = 10   # Upload every 10 orgs (more frequent)
UPLOAD_INTERVAL = 100  # Upload every 100 orgs (faster scraping)
```

### Change Google Sheet Name
```python
# In config.py:
GOOGLE_SHEET_NAME = "My Custom Sheet Name"
```

### Increase Timeouts
```python
# In config.py:
REQUEST_TIMEOUT = 120  # 2 minutes instead of 60s
```

### Resume Scraping
```powershell
# Just run again - automatically resumes
python run_phase2.py
```

---

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| Credentials not found | Run setup command again, download JSON |
| Permission denied | Share Google Sheet with service account email |
| Upload timing out | Increase `REQUEST_TIMEOUT` in config.py |
| Module not found | Run `pip install -r requirements.txt` |
| No Google Sheets updates | Check `GOOGLE_SHEETS_ENABLED = True` in config.py |
| Scraper stuck | Ctrl+C to stop, run again to resume |

---

## 📊 Data Fields

What gets uploaded to Google Sheets:

```
organization_name           | Meta Llama
organization_url            | https://huggingface.co/meta-llama
github_links                | https://github.com/meta-llama
website_links               | https://ai.meta.com/llama/
social_media_links          | https://twitter.com/alibaba_qwen
location                    | San Francisco, CA
description                 | Open source AI company...
member_count                | 250
model_count                 | 500
dataset_count               | 150
scrape_status               | success
scrape_timestamp            | 2025-12-16T09:30:00
```

---

## 📈 Performance Tuning

```python
# FAST SCRAPING (less frequent uploads)
UPLOAD_INTERVAL = 100
REQUEST_DELAY = 0.5

# BALANCED (default)
UPLOAD_INTERVAL = 25
REQUEST_DELAY = 1

# HIGH QUALITY (careful, many retries)
UPLOAD_INTERVAL = 10
REQUEST_DELAY = 2
```

---

## 🔐 Security

**Safe:**
- ✓ Share Google Sheet (view-only or edit)
- ✓ Share CSV file (data only)

**Don't share:**
- ✗ google_credentials.json (has private key!)
- ✗ .env file (has API keys!)

---

## 💾 Backup & Recovery

```powershell
# Backup current progress
Copy-Item output/huggingface_organizations_detailed.csv "backup_$(Get-Date -Format yyyyMMdd_HHmmss).csv"

# Restore from backup
Copy-Item "backup_20251216_120000.csv" output/huggingface_organizations_detailed.csv

# Reset to start over
Remove-Item output/phase2_checkpoint.json
Remove-Item output/huggingface_organizations_detailed.csv
python run_phase2.py  # Starts from beginning
```

---

## 📚 Documentation Files

| File | Use |
|------|-----|
| DOCUMENTATION_INDEX.md | Pick your path |
| GOOGLE_SHEETS_QUICK_START.md | 2-minute version |
| GOOGLE_SHEETS_SETUP.md | 5-minute detailed |
| GOOGLE_SHEETS_COMPLETE_GUIDE.md | Full reference |
| config.py | Settings (edit this!) |
| test_google_sheets.py | Verify setup |

---

## 🎯 Success Checklist

- [ ] Run setup command
- [ ] Download and save google_credentials.json
- [ ] Edit config.py: GOOGLE_SHEETS_ENABLED = True
- [ ] Run test_google_sheets.py (all checks pass)
- [ ] Run python run_phase2.py
- [ ] Open Google Sheet and see updates
- [ ] Check logs for [SHEETS] messages

---

## ⚡ Quick Reference

```powershell
# SETUP (one-time)
python -c "from src.google_sheets_uploader import setup_google_sheets_integration; setup_google_sheets_integration()"
# → Download and save google_credentials.json
# → Edit config.py: GOOGLE_SHEETS_ENABLED = True

# VERIFY (before running)
python test_google_sheets.py

# RUN (ongoing)
python run_phase2.py

# MONITOR
# Open Google Sheet while running
# Or check logs: grep [SHEETS] output/phase2_scraper_*.log

# RESUME (if interrupted)
python run_phase2.py  # Picks up where it left off
```

---

## 🆘 Get Help

**Setup issues?** → GOOGLE_SHEETS_SETUP.md (Troubleshooting section)

**Configuration questions?** → config.py (comments) + GOOGLE_SHEETS_COMPLETE_GUIDE.md

**Want full details?** → IMPLEMENTATION_SUMMARY.md

**See architecture?** → ARCHITECTURE_DIAGRAM.py

**Need navigation?** → DOCUMENTATION_INDEX.md

---

## 💡 Pro Tips

1. Start with default UPLOAD_INTERVAL = 25
2. Monitor first run to catch issues
3. Keep CSV as backup (don't rely only on Google Sheets)
4. Adjust UPLOAD_INTERVAL based on your needs
5. Share Google Sheet, never share credentials
6. Check logs regularly for errors
7. Interrupt with Ctrl+C if needed (safe!)

---

## Cost

**Google Sheets Integration = FREE**

- Google Sheets API: Free
- Google Drive API: Free
- Service Account: Free
- Credentials: Free

---

## That's It!

You now have:
✓ Scraper → CSV → Google Sheets (live sync)
✓ Automatic resuming
✓ Detailed logging
✓ Robust error handling

**Run: `python run_phase2.py`**

Happy scraping! 🚀
