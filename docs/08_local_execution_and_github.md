# Local Execution (Section 31) & GitHub Strategy (Section 40)

## Run it locally
```bash
# STEP 1 - get the project (unzip, or clone) and enter the folder
cd Social-Media-Privacy-Risk-Assessment

# STEP 2 - virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1

# STEP 3 - dependencies
pip install -r requirements.txt

# STEP 4 - synthetic dataset (1,000 fictional rows)
python data/generate_dataset.py

# STEP 5 + 6 - start backend; it also serves the frontend
python backend/app.py

# STEP 7 - open http://127.0.0.1:5000  -> "Start Privacy Assessment"
# STEP 8 - answer all 44 questions
# STEP 9 - click "Generate my privacy score"
# STEP 10 - view category radar/bars, findings and recommendations
# STEP 11 - tick findings in the Improvement Simulator -> "Simulate"
# STEP 12 - "Open report" -> Print / Save as PDF  (or Download report)
```
Extras: `python scripts/run_demo.py` (fictional demo profile), `python -m pytest tests -v`, `python tools/metadata_tool.py photo.jpg --strip`.

Optional: copy `.env.example` to `.env` to change port, rate limit, retention or weights.

## GitHub
Repository name: `Social-Media-Privacy-Risk-Assessment`

Description: *Privacy-focused cybersecurity framework for assessing social-media exposure, account-security practices, social-engineering risk, digital-footprint risk, and personalized privacy improvements using synthetic/self-reported data.*

Topics: `cybersecurity privacy social-media-privacy privacy-risk security-awareness python flask fastapi digital-footprint risk-assessment grc privacy-by-design defensive-security`

```bash
git init
git add .
git commit -m "Initialize social media privacy risk assessment"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

Recommended commit history (make these as separate commits to show progress; `git add <files>` then commit):
1. Create privacy assessment architecture
2. Add privacy questionnaire
3. Generate synthetic assessment dataset
4. Implement privacy feature extraction
5. Add category risk scoring
6. Implement overall privacy risk engine
7. Add privacy findings engine
8. Implement recommendation engine
9. Build privacy improvement simulator
10. Create privacy analytics dashboard
11. Add privacy assessment report
12. Implement privacy-by-design controls
13. Add automated privacy tests
14. Complete README and documentation

Before pushing: confirm `.env`, `instance/` and `*.db` are NOT staged (`git status`), and add screenshots to `screenshots/`.
