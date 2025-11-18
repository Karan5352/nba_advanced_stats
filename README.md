# VIBE - Valued Impact Basketball Estimate

A comprehensive basketball analytics website featuring the **VIBE** metric - a sophisticated player evaluation system that combines offensive skill, defensive impact, and team performance.

## 🏀 Official VIBE Formula v2.0

VIBE is a standardized metric that evaluates players across multiple dimensions:

### Formula Components

**VIBE = 100 + 15 × (0.75×Skill + 0.25×Impact - LeagueMean) / LeagueStd**

Where:
- **Skill = 0.6×OVIBE + 0.4×DVIBE** (z-scores)
- **Impact = Plus-minus per 100 possessions** (z-score)
- **Minutes shrinkage** applied for statistical stability

### 1. Inputs Required (Season Totals)

- **Basic:** GP, MIN, PTS, FGA, FGM, FG3A, FG3M, FTA, FTM
- **Rebounds:** ORB, DRB  
- **Playmaking:** AST, TOV
- **Defense:** STL, BLK, PF
- **Impact:** PLUS_MINUS

### 2. Player Possessions
```
PlayerPoss = MIN × 100 / 240
(240 = 48 minutes × 5 players)
```

### 3. Per-100 Statistics
For any stat X:
```
X_100 = 100 × X / PlayerPoss
```

### 4. True Shooting Efficiency
```
TSA = FGA + 0.44×FTA
TS% = PTS / (2×TSA)
```

### 5. Offensive VIBE (OVIBE)
**Components weighted by impact:**
```
OVIBE_z = 1.8×z_TS + 1.2×z_PTS100 + 1.3×z_AST100 + 0.8×z_ORB100 - 1.4×z_TOV100
```
- **True Shooting (1.8):** Efficiency is paramount
- **Assists (1.3):** Playmaking heavily valued  
- **Scoring Volume (1.2):** Raw production matters
- **Offensive Rebounds (0.8):** Extra possessions
- **Turnovers (-1.4):** Strongly penalized

### 6. Defensive VIBE (DVIBE) - Position-Based
**Measurable defensive contributions normalized within position groups:**
```
DVIBE_z = 1.3×z_STL100 + 1.1×z_BLK100 + 0.5×z_DRB100 - 1.0×z_PF100
```

**🎯 Key Innovation:** All defensive stats compared within position groups:
- **GUARDS** vs other guards (steals/assists focus)
- **WINGS** vs other wings (balanced role)
- **BIGS** vs other bigs (rim protection focus)

**Updated Weights:**
- **Steals (1.3):** Increased - most valuable defensive stat
- **Blocks (1.1):** Strong rim protection value  
- **Defensive Rebounds (0.5):** Reduced to prevent big man bias
- **Fouls (-1.0):** Increased penalty for poor discipline

### 7. Plus-Minus Impact
**Team performance component:**
```
PM_100 = PLUS_MINUS / PlayerPoss × 100
Impact_z = z_PM100
```

### 8. NEW: Position-Based Methodology
**Fair defensive evaluation across positions:**

1. **Position Assignment:**
   - **GUARDS:** 4+ assists per game (playmaker role)
   - **BIGS:** 7+ rebounds per game (interior role) 
   - **WINGS:** Balanced players (perimeter role)

2. **Position-Specific Z-Scores:**
   - Guards compared only to other guards
   - Wings compared only to other wings  
   - Bigs compared only to other bigs
   - Prevents positional bias in DVIBE

3. **Updated Blend Ratios:**
   - **Skill = 60% OVIBE + 40% DVIBE**
   - **VIBE = 65% Skill + 35% Impact** (increased from 25%)

### 9. Minutes-Based Shrinkage
**Statistical stability adjustment:**
```
ShrinkFactor = MIN / (MIN + 600)
VIBE_shrunk = VIBE_raw × ShrinkFactor
```
- Low-minute players shrunk toward average
- High-minute players trusted more

### 10. Final Scaling
**100-point scale with interpretable ranges:**
```
VIBE_Final = 100 + 15 × (VIBE_shrunk - LeagueMean) / LeagueStd
```

## 🎯 VIBE Interpretation

| Range | Level | Description |
|-------|-------|-------------|
| **140+** | 🏆 **MVP** | Generational impact |
| **125-140** | 🌟 **All-NBA** | Elite production |
| **115-125** | ⭐ **Strong Starter** | High-level contributor |
| **100** | 📊 **League Average** | Baseline NBA player |
| **85-100** | 📉 **Below Average** | Limited impact |
| **<85** | ❌ **Poor** | Negative contributor |

## 🔧 Technical Implementation

### Key Features
- **Z-score standardization** across all components
- **Weighted combinations** based on basketball importance
- **Minutes-based reliability** adjustments
- **League normalization** for consistent scaling

### Data Requirements
- NBA API integration for live statistics
- Season-long data for accurate z-scores
- Minimum minutes thresholds for stability

## 📊 Website Features

- **Player Leaderboards** with VIBE rankings
- **Component Breakdown** (OVIBE/DVIBE/Impact)
- **Season Comparisons** across multiple years
- **Dark neon theme** for modern aesthetics
- **Responsive design** for all devices

## 🚀 Quick Start & Deployment

### Option 1: Local Development
```bash
# Clone the repository
git clone <repository-url>
cd nba_advanced_stats

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### Option 2: Production Deployment

#### Heroku (Recommended)
```bash
# Install Heroku CLI and login
heroku login
heroku create your-nba-app-name

# Deploy
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Your app will be live at: https://your-nba-app-name.herokuapp.com
```

#### Railway
1. Connect your GitHub repository to Railway
2. No configuration needed - auto-deploys with `Procfile`

#### Render
1. Connect repository, set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`

#### Manual Server
```bash
# Production setup
export FLASK_ENV=production
export PORT=8000
python run.py
```

### Environment Variables
```bash
FLASK_ENV=production     # For production deployment
PORT=8000               # Port number (auto-set by most platforms)
```

### File Structure
```
nba_advanced_stats/
├── 📄 Core Application Files
│   ├── app.py                 # Main Flask application
│   ├── run.py                 # Production deployment script
│   ├── vibe_calculator.py     # Position-based VIBE formula
│   └── nba_simple_fetcher.py  # NBA API data fetching
│
├── 🌐 Web Templates
│   ├── templates/base.html    # Dark theme layout
│   ├── templates/index.html   # Player leaderboard
│   ├── templates/players.html # Player details
│   ├── templates/teams.html   # Team statistics  
│   └── templates/about.html   # VIBE formula docs
│
├── 🚀 Deployment Files
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # Heroku deployment config
│   ├── runtime.txt           # Python version
│   └── .gitignore            # Git ignore rules
│
└── 📖 Documentation
    └── README.md             # This file
```

### 🎯 Repository Status: ✅ DEPLOYMENT READY

**✅ Clean & Optimized**
- No unnecessary files or dependencies
- No sensitive data or API keys
- Optimized for GitHub public repository

**✅ Production Ready**  
- Multiple deployment options (Heroku, Railway, Render)
- Environment variable support
- Production-grade Flask configuration

**✅ Professional Quality**
- Comprehensive documentation
- Modern dark theme UI
- Sophisticated VIBE formula with position-based normalization

**🏀 Live Demo**: Deploy to see 279 NBA players ranked by the position-balanced VIBE metric!

# Run the website
python3 app.py
```

Visit http://localhost:8000 to explore NBA analytics with the official VIBE metric.

---

**VIBE** provides a comprehensive, defensible metric that combines the best of traditional box score analysis with modern impact measurement, perfect for basketball analytics portfolios and professional evaluation systems.