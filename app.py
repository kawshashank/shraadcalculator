import streamlit as st
import streamlit.components.v1 as components
import base64
try:
    import swisseph as swe
except ImportError:
    swe = None
import math
from datetime import datetime, timedelta, time
import pytz
import urllib.parse
import os

# --- PAGE CONFIGURATION (Must be first) ---
st.set_page_config(page_title="Kashmiri Shraad Calculator", page_icon="🕉️", layout="centered")

# --- CONSTANTS & CONFIGURATION ---
TZ_IST = pytz.timezone("Asia/Kolkata")

KASHMIRI_TITHIS = [
    "Okdoh", "Doy", "Trey", "Choram", "Pancham", 
    "Shish", "Saptam", "Aetham", "Navam", "Daham", 
    "Kah", "Bah", "Truvah", "Tshodah", "Purnima",
    "Okdoh", "Doy", "Trey", "Choram", "Pancham", 
    "Shish", "Saptam", "Aetham", "Navam", "Daham", 
    "Kah", "Bah", "Truvah", "Tshodah", "Mawas"
]

MONTH_NAMES = [
    "Chaitra", "Vaisakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"
]

# --- CALENDAR GENERATION FUNCTIONS ---
def generate_google_calendar_url(date_obj, name_str):
    event_title = f"Shraad{' for ' + name_str if name_str else ''}"
    start_time = datetime.combine(date_obj, time(8, 0)).astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
    end_time = datetime.combine(date_obj, time(13, 0)).astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
    details = "Calculated via Kashmiri Hindu Shraad Calculator based on Vijayshwar Jantri rules."
    
    params = {
        'action': 'TEMPLATE',
        'text': event_title,
        'dates': f"{start_time}/{end_time}",
        'details': details
    }
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"

def generate_ics(date_obj, name_str):
    event_title = f"Shraad{' for ' + name_str if name_str else ''}"
    start_time = datetime.combine(date_obj, time(8, 0)).astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
    end_time = datetime.combine(date_obj, time(13, 0)).astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
    timestamp = datetime.now(pytz.utc).strftime('%Y%m%dT%H%M%SZ')
    
    ics_content = f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Kashmiri Shraad Calculator//EN\nBEGIN:VEVENT\nUID:{timestamp}@kashmirishraad.com\nDTSTAMP:{timestamp}\nDTSTART:{start_time}\nDTEND:{end_time}\nSUMMARY:{event_title}\nDESCRIPTION:Calculated via Kashmiri Hindu Shraad Calculator based on Vijayshwar Jantri rules.\nEND:VEVENT\nEND:VCALENDAR""".replace('\n', '\r\n')
    return ics_content

# --- SESSION STATE INITIALIZATION ---
if "transfer_date" not in st.session_state: st.session_state.transfer_date = None
if "transfer_name" not in st.session_state: st.session_state.transfer_name = ""
if "trigger_tab_switch" not in st.session_state: st.session_state.trigger_tab_switch = False
if "name1" not in st.session_state: st.session_state.name1 = ""
if "name2" not in st.session_state: st.session_state.name2 = ""
if "calc_state" not in st.session_state: st.session_state.calc_state = None
if "rev_calc_state" not in st.session_state: st.session_state.rev_calc_state = None
if "welcome_guide_dismissed" not in st.session_state: st.session_state.welcome_guide_dismissed = False

# --- UI: MAHADEV BACKGROUND & PREMIUM THEME CSS ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f: data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    try:
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = f'''
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,600&display=swap');
        
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(15, 15, 15, 0.85), rgba(15, 15, 15, 0.85)), url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: top center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{ background: rgba(0,0,0,0); }}
        .stApp * {{ color: #f8f9fa !important; }}
        
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div, 
        div[data-baseweb="base-input"] {{
            background-color: rgba(30, 30, 30, 0.6) !important;
            border-color: #555 !important;
            color: white !important;
        }}
        
        /* Typography: Sacred Serif Header */
        .custom-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(1.8rem, 6vw, 2.8rem);
            font-weight: 700;
            white-space: normal; 
            padding-bottom: 0.2rem;
            line-height: 1.1;
            color: #F4D06F !important;
            text-align: center;
        }}
        .ornamental-divider {{
            text-align: center; color: #C8922A; margin-top: 5px; margin-bottom: 25px; font-size: 1.1rem; opacity: 0.8;
        }}
        
        /* Premium Tabs */
        .stTabs [data-baseweb="tab-list"] {{ gap: 8px; background-color: transparent; }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(40, 40, 40, 0.7) !important;
            border-radius: 12px 12px 0px 0px !important;
            padding: 10px 20px !important;
            color: #aaa !important;
            border: 1px solid #444 !important;
            border-bottom: none !important;
            transition: all 0.2s ease-in-out;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(200, 146, 42, 0.85) !important; /* Sacred Amber */
            color: white !important;
            border-color: rgba(200, 146, 42, 0.8) !important;
            font-weight: 600 !important;
            box-shadow: inset 0 -2px 10px rgba(255,200,100,0.3) !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{ background-color: transparent !important; }}
        
        /* Sacred Result Card */
        .sacred-card {{
            background-color: rgba(30, 25, 15, 0.85);
            border: 1px solid #C8922A;
            border-radius: 10px;
            padding: 25px 20px;
            text-align: center;
            margin: 25px 0 15px 0;
            box-shadow: 0 8px 20px rgba(0,0,0,0.5);
            position: relative;
        }}
        .sacred-card-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(1.5rem, 4vw, 2.2rem);
            color: #F4D06F;
            margin: 10px 0 5px 0;
            font-weight: 700;
        }}
        
        /* Metadata Strip */
        .meta-strip {{
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(0,0,0,0.4); padding: 12px 16px; border-radius: 6px;
            margin-bottom: 8px; border-left: 3px solid #C8922A;
        }}
        .meta-label {{ color: #aaa; font-size: 0.9rem; letter-spacing: 0.5px; text-transform: uppercase; font-weight: 600; }}
        .meta-val {{ color: #fff; font-weight: 600; font-size: 1rem; }}
        
        /* 5-Year Timeline */
        .timeline-row {{
            display: flex; justify-content: space-between; padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .timeline-year {{ color: #C8922A; font-weight: 700; font-size: 1.1rem; }}
        .timeline-date {{ color: #eee; font-size: 1rem; }}
        
        /* Feature Cards (Welcome) */
        .feat-card {{
            display: flex; gap: 16px; background: rgba(255,255,255,0.06);
            padding: 16px; border-radius: 10px; margin-bottom: 12px;
            border: 1px solid rgba(255,255,255,0.08); align-items: center;
        }}
        .feat-icon {{ font-size: 1.8rem; background: rgba(200,146,42,0.2); border-radius: 50%; padding: 10px; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; }}
        .feat-title {{ color: #F4D06F; font-weight: 700; font-size: 1.1rem; margin-bottom: 4px; display: block; }}
        .feat-desc {{ color: #ccc; font-size: 0.9rem; line-height: 1.4; margin: 0; }}
        
        /* Privacy Badge */
        .privacy-badge {{
            display: inline-block; background: rgba(40,40,40,0.8); border: 1px solid #555;
            color: #aaa; padding: 5px 16px; border-radius: 20px; font-size: 0.8rem; margin: 10px auto 25px auto;
        }}
        
        div[data-testid="stButton"] button {{ width: 100%; }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Background image 'mahadev.jpg' not found.")

# --- DIALOGS ---
@st.dialog("🙏 Welcome to the Kashmiri Shraad Calculator")
def welcome_guide():
    st.markdown("This tool accurately calculates traditional Kashmiri Hindu Shraad dates for your departed loved ones, mathematically aligned with the authentic **Vijayshwar Jantri**.")
    st.markdown("""
    <div class="feat-card">
        <div class="feat-icon">📅</div>
        <div><span class="feat-title">Search Shraad Date</span><p class="feat-desc">Know the English date of passing? Enter it here to find the exact Shraad date for any upcoming year.</p></div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">⏪</div>
        <div><span class="feat-title">Reverse Date Lookup</span><p class="feat-desc">Only remember the traditional Tithi (e.g., Zoon Pachh Truvah)? Use this tab to find the historical English date of passing.</p></div>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🗓️</div>
        <div><span class="feat-title">Calendar Integration</span><p class="feat-desc">Easily add calculated dates directly to your Google, Apple, or Outlook calendars so you never miss them.</p></div>
    </div>
    """, unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)
    if st.button("Proceed to Calculator ✨", use_container_width=True):
        st.session_state["welcome_guide_dismissed"] = True
        st.rerun()

@st.dialog("💬 Support & Feedback")
def feedback_form():
    st.iframe("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 5px; background-color: transparent; }
    .fb-container { display: flex; flex-direction: column; gap: 14px; }
    .fb-label { font-weight: 600; font-size: 14px; color: #1C1C1E; margin-bottom: 4px; display: block; }
    .fb-radio-label { display: flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer; padding: 4px 0; color: #121212; }
    .fb-input, .fb-textarea { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #D1D1D6; background-color: #FFFFFF; color: #121212; font-size: 14px; box-sizing: border-box; font-family: inherit; }
    .fb-textarea { resize: none; }
    .fb-btn { background-color: #1C1C1E; color: white; padding: 12px; border: none; border-radius: 8px; font-weight: 600; font-size: 15px; cursor: pointer; width: 100%; margin-top: 5px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-family: inherit; transition: background-color 0.2s; }
    .fb-btn:hover { background-color: #3A3A3C; }
    @media (prefers-color-scheme: dark) {
        body { color: #F8F8FA; } .fb-label { color: #F8F8FA; } .fb-radio-label { color: #F8F8FA; }
        .fb-input, .fb-textarea { background-color: #2C2C2E; border-color: #48484A; color: #F8F8FA; }
        .fb-btn { background-color: #3A3A3C; border: 1px solid #48484A; } .fb-btn:hover { background-color: #48484A; }
    }
    </style>
    </head>
    <body>
    <div class="fb-container">
        <div>
            <label class="fb-label">What would you like to share?</label>
            <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 6px;">
                <label class="fb-radio-label"><input type="radio" name="fb_type_group" id="type_general" value="general" checked onchange="stToggleFields()"> General Feedback / Suggestion</label>
                <label class="fb-radio-label"><input type="radio" name="fb_type_group" id="type_bug" value="bug" onchange="stToggleFields()"> Report an Incorrect Date</label>
            </div>
        </div>
        <div><label class="fb-label">Your Email Address (So we can reply!)</label><input type="email" id="fb_email" class="fb-input" placeholder="name@example.com"></div>
        <div id="bug_fields" style="display: none; flex-direction: column; gap: 14px;">
            <div><label class="fb-label">What is the actual Date of Passing?</label><input type="text" id="fb_dob" class="fb-input" placeholder="e.g., 22 Jan 1960"></div>
            <div><label class="fb-label">What is the Expected Result? (As per Jantri)</label><input type="text" id="fb_expected" class="fb-input" placeholder="e.g., 10 Feb 2026"></div>
            <div><label class="fb-label">What Result did the App give you?</label><input type="text" id="fb_actual" class="fb-input" placeholder="e.g., 30 Jan 2027"></div>
            <div><label class="fb-label">Any other details? (Time of passing, Year being checked, etc.)</label><textarea id="fb_notes" class="fb-textarea" rows="2" placeholder="Provide extra context here..."></textarea></div>
        </div>
        <div id="general_fields" style="display: flex; flex-direction: column; gap: 14px;">
            <div><label class="fb-label">Your Feedback / Suggestion</label><textarea id="fb_text" class="fb-textarea" rows="4" placeholder="Type your suggestion here..."></textarea></div>
        </div>
        <button type="button" class="fb-btn" onclick="stSendFeedback()">✉️ Send Feedback via Email</button>
    </div>
    <script>
    function stToggleFields() {
        var type = document.querySelector('input[name="fb_type_group"]:checked').value;
        if(type === "bug") { document.getElementById("bug_fields").style.display = "flex"; document.getElementById("general_fields").style.display = "none"; }
        else { document.getElementById("bug_fields").style.display = "none"; document.getElementById("general_fields").style.display = "flex"; }
    }
    function stSendFeedback() {
        var type = document.querySelector('input[name="fb_type_group"]:checked').value;
        var email = document.getElementById("fb_email").value.trim();
        if(!email) { alert("⚠️ Please provide your email address before sending."); return; }
        var subject = ""; var body = "";
        if(type === "bug") {
            subject = "Bug Report: Shraad Calculator";
            var dob = document.getElementById("fb_dob").value; var expected = document.getElementById("fb_expected").value;
            var actual = document.getElementById("fb_actual").value; var notes = document.getElementById("fb_notes").value;
            body = "User Email: " + email + "\\n\\n--- BUG REPORT ---\\nActual Date: " + dob + "\\nExpected Result: " + expected + "\\nApp Result: " + actual + "\\n\\nAdditional Notes:\\n" + notes;
        } else {
            subject = "Feedback: Shraad Calculator"; var text = document.getElementById("fb_text").value;
            if(!text.trim()) { alert("⚠️ Please type your feedback message before sending."); return; }
            body = "User Email: " + email + "\\n\\n--- FEEDBACK ---\\n" + text;
        }
        window.location.href = "mailto:kawshashank@gmail.com?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
    }
    </script>
    </body>
    </html>
    """, height=560)


# --- ASTRONOMICAL CORE FUNCTIONS (UNTOUCHED LOGIC) ---
def get_julian_day(dt: datetime) -> float:
    if dt.tzinfo is None: dt = TZ_IST.localize(dt)
    utc_dt = dt.astimezone(pytz.utc)
    decimal_hour = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)

def get_sun_moon_longitude(jd: float):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_info, _ = swe.calc_ut(jd, swe.SUN, flags)
    moon_info, _ = swe.calc_ut(jd, swe.MOON, flags)
    return sun_info[0], moon_info[0]

def calculate_tithi_from_jd(jd: float) -> int:
    sun_long, moon_long = get_sun_moon_longitude(jd)
    angle_diff = (moon_long - sun_long) % 360
    tithi_index = math.floor(angle_diff / 12.0) + 1
    return min(max(tithi_index, 1), 30)

def get_lunar_month_index(jd: float, tithi_idx: int) -> int:
    sun_long, moon_long = get_sun_moon_longitude(jd)
    diff = (moon_long - sun_long) % 360
    test_jd = jd - (diff / 12.190749)
    for _ in range(5):
        s, m = get_sun_moon_longitude(test_jd)
        current_diff = (m - s) % 360
        if current_diff > 180: current_diff -= 360 
        test_jd -= (current_diff / 12.190749)
        if abs(current_diff) < 0.001: break
            
    sun_long_at_new_moon, _ = get_sun_moon_longitude(test_jd)
    adjusted_sun_long = sun_long_at_new_moon - 1.5
    if adjusted_sun_long < 0: adjusted_sun_long += 360
    
    rashi_index = math.floor(adjusted_sun_long / 30.0)
    month_index = (rashi_index + 1) % 12
    if tithi_idx > 15: month_index = (month_index + 1) % 12
    return month_index

def format_tithi_name(tithi_idx: int) -> str:
    if tithi_idx == 15: return "Purnima"
    elif tithi_idx == 30: return "Mawas (Amavasya)"
    paksha = "Zoon Pachh" if tithi_idx < 15 else "Gat Pachh"
    name = KASHMIRI_TITHIS[tithi_idx - 1]
    return f"{paksha} {name}"

# --- UNIFIED ENGINE LOGIC (UNTOUCHED LOGIC) ---
def resolve_death_tithi(death_date, death_time):
    if death_time < time(6, 30):
        effective_date = death_date - timedelta(days=1)
        is_predawn = True
    else:
        effective_date = death_date
        is_predawn = False
        
    jd_sunrise = get_julian_day(datetime.combine(effective_date, time(7, 0)))
    tithi_idx = calculate_tithi_from_jd(jd_sunrise)
    jd_yesterday = get_julian_day(datetime.combine(effective_date - timedelta(days=1), time(7, 0)))
    tithi_yesterday = calculate_tithi_from_jd(jd_yesterday)
    
    if tithi_idx == tithi_yesterday:
        tithi_idx += 1
        if tithi_idx > 30: tithi_idx = 1
            
    return tithi_idx, effective_date, is_predawn

def calculate_target_shraad_date(target_year: int, target_month_idx: int, target_tithi_idx: int) -> datetime.date:
    start_date = datetime(target_year, 1, 1)
    udaya_days = []
    aparahna_days = []
    
    for day_offset in range(400):
        scan_date = start_date + timedelta(days=day_offset)
        jd_udaya = get_julian_day(datetime.combine(scan_date, time(7, 0)))
        t_udaya = calculate_tithi_from_jd(jd_udaya)
        m_udaya = get_lunar_month_index(jd_udaya, t_udaya)
        if m_udaya == target_month_idx and t_udaya == target_tithi_idx: udaya_days.append(scan_date.date())
            
        jd_ap_start = get_julian_day(datetime.combine(scan_date, time(13, 30)))
        t_ap_start = calculate_tithi_from_jd(jd_ap_start)
        m_ap_start = get_lunar_month_index(jd_ap_start, t_ap_start)
        jd_ap_end = get_julian_day(datetime.combine(scan_date, time(15, 45)))
        t_ap_end = calculate_tithi_from_jd(jd_ap_end)
        m_ap_end = get_lunar_month_index(jd_ap_end, t_ap_end)
        
        if (m_ap_start == target_month_idx and t_ap_start == target_tithi_idx) or \
           (m_ap_end == target_month_idx and t_ap_end == target_tithi_idx):
            aparahna_days.append(scan_date.date())

    if len(udaya_days) > 0: return udaya_days[0]
    if len(aparahna_days) > 0: return aparahna_days[0]
    return None

def find_original_dates(target_year: int, target_month_idx: int, target_tithi_idx: int):
    start_date = datetime(target_year, 1, 1)
    matching_dates = []
    for day_offset in range(400):
        scan_date = start_date + timedelta(days=day_offset)
        jd_udaya = get_julian_day(datetime.combine(scan_date, time(7, 0)))
        t_udaya = calculate_tithi_from_jd(jd_udaya)
        m_udaya = get_lunar_month_index(jd_udaya, t_udaya)
        if m_udaya == target_month_idx and t_udaya == target_tithi_idx:
            if scan_date.year == target_year: matching_dates.append(scan_date.date())
    return matching_dates

# --- INIT UI & JAVASCRIPT INJECTIONS ---
set_background('mahadev.jpg')

# Mobile Keyboard Suppression Fix
st.markdown("""
<script>
(function () {
    function patchSelectInputs() {
        var inputs = window.parent.document.querySelectorAll('[data-baseweb="select"] input');
        inputs.forEach(function (inp) {
            if (!inp.hasAttribute('data-kb-patched')) { inp.setAttribute('inputmode', 'none'); inp.setAttribute('data-kb-patched', '1'); }
        });
    }
    patchSelectInputs();
    var observer = new MutationObserver(patchSelectInputs);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

if st.session_state.trigger_tab_switch:
    st.markdown("""
        <script>
            var elements = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
            if (elements.length > 0) { elements[0].click(); }
        </script>
    """, unsafe_allow_html=True)
    st.session_state.trigger_tab_switch = False 

# Trigger Welcome Dialog
if not st.session_state.welcome_guide_dismissed:
    st.session_state.welcome_guide_dismissed = True
    welcome_guide()

# --- MAIN APP LAYOUT ---
st.markdown("<div class='custom-title'>Kashmiri Hindu<br>Shraad Calculator</div>", unsafe_allow_html=True)
st.markdown("<div class='ornamental-divider'>◈ ─── ॐ ─── ◈</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Search Shraad Date", "Search Original Date of Passing"])

# --- TAB 1: STANDARD CALCULATOR ---
with tab1:
    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    default_name_1 = st.session_state.transfer_name
    soul_name_1 = st.text_input("Name of the Departed Soul (Optional)", value=default_name_1, placeholder="Enter name...", key="name1")

    col1, col2 = st.columns(2)
    with col1:
        default_date = st.session_state.transfer_date if st.session_state.transfer_date else datetime(2020, 10, 2).date()
        death_date = st.date_input("Date of Passing", min_value=datetime(1930, 1, 1).date(), max_value=datetime.today().date(), value=default_date, format="DD/MM/YYYY")
        
        if st.session_state.transfer_date:
            st.success("✨ Date auto-filled from Reverse Lookup!")
            st.session_state.transfer_date = None 
            
        current_yr = datetime.today().year
        target_year = st.number_input("Find Shraad Date for Year", min_value=2024, max_value=2100, value=current_yr, step=1)
        
    with col2:
        knows_time = st.checkbox("I know the exact time of passing", value=False) 
        if knows_time:
            st.markdown("<p style='font-size: 0.85rem; margin-bottom: -15px;'>Time of Passing (IST)</p>", unsafe_allow_html=True)
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1: hr_str = st.selectbox("Hour", [f"{i:02d}" for i in range(1, 13)], index=1)
            with t_col2: mn_str = st.selectbox("Min", [f"{i:02d}" for i in range(60)], index=0)
            with t_col3: ampm_str = st.selectbox("AM/PM", ["AM", "PM"], index=1)
                
            hr_int = int(hr_str)
            if ampm_str == "PM" and hr_int != 12: hr_int += 12
            if ampm_str == "AM" and hr_int == 12: hr_int = 0
            death_time = time(hr_int, int(mn_str))
        else:
            death_time = None
            st.info("If exact time is unknown, calculation evaluates standard Sunrise boundary options.")

    st.write("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    b_col1, b_col2 = st.columns([4, 1])
    with b_col1: calc_btn = st.button("Calculate Shraad Date", type="primary", use_container_width=True)
    with b_col2: 
        if st.button("💬 Feedback", use_container_width=True, key="fb_btn_1"): feedback_form()

    input_key = f"{soul_name_1}-{death_date}-{death_time}-{target_year}-{knows_time}"
    if calc_btn: st.session_state.calc_state = input_key
        
    if st.session_state.calc_state == input_key:
        st.write("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        with st.spinner("Analyzing exact astronomical position..."):
            
            display_name = f" for {soul_name_1.strip()}" if soul_name_1.strip() else ""
            clean_name = soul_name_1.strip() if soul_name_1.strip() else "Shraad"
            
            if knows_time:
                tithi_idx, effective_date, is_predawn = resolve_death_tithi(death_date, death_time)
                jd_effective = get_julian_day(datetime.combine(effective_date, time(7, 0)))
                month_idx = get_lunar_month_index(jd_effective, tithi_idx) 
                shraad_date = calculate_target_shraad_date(target_year, month_idx, tithi_idx)
                
                if is_predawn: st.caption(f"🌙 *Time is before dawn. Calculation anchored to previous Hindu day ({effective_date.strftime('%d %B %Y')}).*")
                else: st.caption(f"☀️ *Calculation anchored to today's Hindu day ({effective_date.strftime('%d %B %Y')}).*")
                    
                st.markdown(f"""
                <div class='meta-strip'><span class='meta-label'>Lunar Masa</span><span class='meta-val'>{MONTH_NAMES[month_idx]}</span></div>
                <div class='meta-strip'><span class='meta-label'>Official Tithi</span><span class='meta-val'>{format_tithi_name(tithi_idx)}</span></div>
                """, unsafe_allow_html=True)
                
                if shraad_date:
                    st.markdown(f"""
                    <div class='sacred-card'>
                        <div class='sacred-divider'>ॐ</div>
                        <div style='color:#aaa; font-size:0.95rem; text-transform:uppercase; letter-spacing:1px;'>Calculated shraad date{display_name}</div>
                        <div class='sacred-card-title'>{shraad_date.strftime('%A, %d %B %Y')}</div>
                    </div>
                    <div style="text-align:center;"><span class="privacy-badge">🔒 Privacy First: Computed locally. No data saved.</span></div>
                    """, unsafe_allow_html=True)
                    
                    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    cal_col1, cal_col2 = st.columns(2)
                    with cal_col1: st.link_button("🗓️ Add to Google Calendar", generate_google_calendar_url(shraad_date, clean_name), use_container_width=True)
                    with cal_col2: st.download_button("📥 Download .ics (Apple/Outlook)", generate_ics(shraad_date, clean_name), file_name=f"shraad_{target_year}.ics", mime="text/calendar", use_container_width=True)
                    
                    st.write("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                    with st.expander("📅 View Upcoming Shraad Dates (Next 5 Years)", expanded=False):
                        html_timeline = "<div style='padding: 10px 5px;'>"
                        for next_y in range(target_year + 1, target_year + 6):
                            ny_date = calculate_target_shraad_date(next_y, month_idx, tithi_idx)
                            if ny_date: html_timeline += f"<div class='timeline-row'><span class='timeline-year'>{next_y}</span><span class='timeline-date'>{ny_date.strftime('%A, %d %B %Y')}</span></div>"
                        html_timeline += "</div>"
                        st.markdown(html_timeline, unsafe_allow_html=True)
                else:
                    st.error("Could not accurately resolve a structural date match.")
                    
            else:
                st.warning("Because Hindu calendar days begin at Sunrise, the Shraad date depends on whether passing occurred before or after dawn:")
                st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # --- PRE-DAWN SCENARIO ---
                t_idx_pre, date_pre, _ = resolve_death_tithi(death_date, time(3, 0))
                jd_pre = get_julian_day(datetime.combine(date_pre, time(7, 0)))
                m_idx_pre = get_lunar_month_index(jd_pre, t_idx_pre)
                shraad_pre = calculate_target_shraad_date(target_year, m_idx_pre, t_idx_pre)
                
                st.markdown(f"<div style='color:#ddd; padding-left:5px;'>🌙 <b>If passing occurred BEFORE dawn (~6:30 AM)</b><br><span style='font-size:0.85rem; color:#C8922A;'>({format_tithi_name(t_idx_pre)} in {MONTH_NAMES[m_idx_pre]})</span></div>", unsafe_allow_html=True)
                
                if shraad_pre:
                    st.markdown(f"""
                    <div class='sacred-card'>
                        <div class='sacred-divider'>ॐ</div>
                        <div style='color:#aaa; font-size:0.95rem; text-transform:uppercase; letter-spacing:1px;'>Calculated shraad date{display_name}</div>
                        <div class='sacred-card-title'>{shraad_pre.strftime('%A, %d %B %Y')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    cal_col1, cal_col2 = st.columns(2)
                    with cal_col1: st.link_button("🗓️ Add to Google Calendar", generate_google_calendar_url(shraad_pre, clean_name), use_container_width=True, key="gcal_pre")
                    with cal_col2: st.download_button("📥 Download .ics (Apple/Outlook)", generate_ics(shraad_pre, clean_name), file_name=f"shraad_pre_{target_year}.ics", mime="text/calendar", use_container_width=True, key="ics_pre")
                    
                    with st.expander("📅 View Upcoming Shraad Dates (Next 5 Years)", expanded=False):
                        html_timeline = "<div style='padding: 10px 5px;'>"
                        for next_y in range(target_year + 1, target_year + 6):
                            ny_date = calculate_target_shraad_date(next_y, m_idx_pre, t_idx_pre)
                            if ny_date: html_timeline += f"<div class='timeline-row'><span class='timeline-year'>{next_y}</span><span class='timeline-date'>{ny_date.strftime('%A, %d %B %Y')}</span></div>"
                        html_timeline += "</div>"
                        st.markdown(html_timeline, unsafe_allow_html=True)
                    
                st.write("<div style='height: 30px;'></div>", unsafe_allow_html=True)
                
                # --- POST-DAWN SCENARIO ---
                t_idx_post, date_post, _ = resolve_death_tithi(death_date, time(8, 0))
                jd_post = get_julian_day(datetime.combine(date_post, time(7, 0)))
                m_idx_post = get_lunar_month_index(jd_post, t_idx_post)
                shraad_post = calculate_target_shraad_date(target_year, m_idx_post, t_idx_post)
                
                st.markdown(f"<div style='color:#ddd; padding-left:5px;'>☀️ <b>If passing occurred AFTER dawn (~6:30 AM)</b><br><span style='font-size:0.85rem; color:#C8922A;'>({format_tithi_name(t_idx_post)} in {MONTH_NAMES[m_idx_post]})</span></div>", unsafe_allow_html=True)
                
                if shraad_post:
                    st.markdown(f"""
                    <div class='sacred-card'>
                        <div class='sacred-divider'>ॐ</div>
                        <div style='color:#aaa; font-size:0.95rem; text-transform:uppercase; letter-spacing:1px;'>Calculated shraad date{display_name}</div>
                        <div class='sacred-card-title'>{shraad_post.strftime('%A, %d %B %Y')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    cal_col1, cal_col2 = st.columns(2)
                    with cal_col1: st.link_button("🗓️ Add to Google Calendar", generate_google_calendar_url(shraad_post, clean_name), use_container_width=True, key="gcal_post")
                    with cal_col2: st.download_button("📥 Download .ics (Apple/Outlook)", generate_ics(shraad_post, clean_name), file_name=f"shraad_post_{target_year}.ics", mime="text/calendar", use_container_width=True, key="ics_post")
                    
                    with st.expander("📅 View Upcoming Shraad Dates (Next 5 Years)", expanded=False):
                        html_timeline = "<div style='padding: 10px 5px;'>"
                        for next_y in range(target_year + 1, target_year + 6):
                            ny_date = calculate_target_shraad_date(next_y, m_idx_post, t_idx_post)
                            if ny_date: html_timeline += f"<div class='timeline-row'><span class='timeline-year'>{next_y}</span><span class='timeline-date'>{ny_date.strftime('%A, %d %B %Y')}</span></div>"
                        html_timeline += "</div>"
                        st.markdown(html_timeline, unsafe_allow_html=True)

                st.markdown('<div style="text-align:center; margin-top:20px;"><span class="privacy-badge">🔒 Privacy First: Computed locally. No data saved.</span></div>', unsafe_allow_html=True)


# --- TAB 2: REVERSE LOOKUP CALCULATOR ---
with tab2:
    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0; padding-top:0; color:#F4D06F;'>Reverse Date Lookup</h3>", unsafe_allow_html=True)
    st.caption("If you know the traditional Kashmiri Tithi and the year of passing, you can find the exact calendar date.")
    
    soul_name_2 = st.text_input("Name of the Departed Soul (Optional)", placeholder="Enter name...", key="name2")
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        rev_year = st.number_input("Year of Passing", min_value=1930, max_value=2100, value=1989, step=1, key="rev_year")
        rev_month_name = st.selectbox("Lunar Month (Masa)", MONTH_NAMES, index=7, key="rev_month")
        
    with r_col2:
        rev_paksha = st.selectbox("Lunar Phase (Paksha)", ["Zoon Pachh (Shukla)", "Gat Pachh (Krishna)"], index=1, key="rev_paksha")
        tithi_ui_list = []
        for i in range(1, 16):
            if i == 15: tithi_ui_list.append("Purnima" if "Zoon" in rev_paksha else "Mawas (Amavasya)")
            else: tithi_ui_list.append(KASHMIRI_TITHIS[i - 1])
        rev_tithi_name = st.selectbox("Tithi", tithi_ui_list, index=12, key="rev_tithi")
        
    st.write("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    b_col3, b_col4 = st.columns([4, 1])
    with b_col3: rev_btn = st.button("Find Exact Date of Passing", type="primary", use_container_width=True, key="rev_btn")
    with b_col4: 
        if st.button("💬 Feedback", use_container_width=True, key="fb_btn_2"): feedback_form()
            
    rev_key = f"{soul_name_2}-{rev_year}-{rev_month_name}-{rev_paksha}-{rev_tithi_name}"
    if rev_btn: st.session_state.rev_calc_state = rev_key
    
    if st.session_state.rev_calc_state == rev_key:
        st.write("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        with st.spinner("Scanning historical ephemeris records..."):
            
            display_name_rev = f" for {st.session_state.name2.strip()}" if st.session_state.name2.strip() else ""
            rev_month_idx = MONTH_NAMES.index(rev_month_name)
            t_base_idx = tithi_ui_list.index(rev_tithi_name) + 1
            if "Gat Pachh" in rev_paksha: t_base_idx += 15
                
            matched_dates = find_original_dates(rev_year, rev_month_idx, t_base_idx)
            
            if not matched_dates:
                st.error(f"Could not find any day in {rev_year} where {format_tithi_name(t_base_idx)} was active at sunrise during {rev_month_name}. It may have been a Kshaya (skipped) Tithi.")
            else:
                transfer_dt = matched_dates[0]
                
                if len(matched_dates) == 1:
                    st.markdown(f"""
                    <div class='sacred-card'>
                        <div class='sacred-divider'>ॐ</div>
                        <div style='color:#aaa; font-size:0.95rem; text-transform:uppercase; letter-spacing:1px;'>Original Date of Passing{display_name_rev}</div>
                        <div class='sacred-card-title'>{matched_dates[0].strftime('%A, %d %B %Y')}</div>
                        <div style='color:#C8922A; font-size:0.9rem; margin-top:5px;'>({format_tithi_name(t_base_idx)} in {rev_month_name} {rev_year})</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"This was a **Devadev** (Double Tithi) in {rev_year}. It was active at sunrise on two consecutive days:")
                    for idx, d in enumerate(matched_dates):
                        st.markdown(f"""
                        <div class='sacred-card' style='margin-top:10px;'>
                            <div class='sacred-divider'>ॐ</div>
                            <div style='color:#aaa; font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;'>{'Primary' if idx==0 else 'Secondary'} Date Match</div>
                            <div class='sacred-card-title' style='font-size:1.8rem;'>{d.strftime('%A, %d %B %Y')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.write("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:#ddd; font-weight:600;'>Want to find the upcoming Shraad for this date?</p>", unsafe_allow_html=True)
                
                def trigger_transfer():
                    st.session_state.transfer_date = transfer_dt
                    st.session_state.name1 = st.session_state.name2 
                    st.session_state.trigger_tab_switch = True
                
                c1, c2, c3 = st.columns([1, 2, 1])
                c2.button("Calculate Upcoming Shraad ➡️", on_click=trigger_transfer, use_container_width=True, key="transfer_btn")


# --- SHARE APP SECTION (FOOTER) ---
st.write("<div style='height: 40px;'></div>", unsafe_allow_html=True)
st.divider()
st.markdown("<h4 style='text-align: center; color: #F4D06F; font-family: \"Cormorant Garamond\", serif; font-size: 1.8rem; margin-bottom: 5px;'>Share this App</h4>", unsafe_allow_html=True)

APP_URL = "https://shraad-alert.streamlit.app" 
whatsapp_msg = urllib.parse.quote(f"Check out the Kashmiri Shraad Calculator! Save this link to easily find traditional Shraad dates: {APP_URL}")
fb_url = urllib.parse.quote(APP_URL)

WA_SVG = '<svg viewBox="0 0 448 512" style="width:16px;height:16px;fill:white;margin-right:8px;vertical-align:middle;"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3 18.7-68.1-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-5.5-2.8-23.2-8.5-44.2-27.1-16.4-14.6-27.4-32.6-30.6-37.9-3.2-5.5-.3-8.5 2.5-11.2 2.5-2.5 5.5-6.6 8.3-9.9 2.8-3.3 3.7-5.6 5.6-9.2 1.9-3.7.9-6.6-.5-9.2-1.4-2.8-12.5-30.1-17.1-41.1-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 13.2 5.7 23.5 9.2 31.6 11.8 13.3 4.2 25.4 3.6 35 2.2 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/></svg>'
FB_SVG = '<svg viewBox="0 0 512 512" style="width:16px;height:16px;fill:white;margin-right:8px;vertical-align:middle;"><path d="M504 256C504 119 393 8 256 8S8 119 8 256c0 123.78 90.69 226.38 209.25 245.26V312.6h-66.38V256h66.38V212.87c0-65.51 38.89-101.62 98.45-101.62 28.53 0 58.31 5.1 58.31 5.1v64h-32.81c-32.36 0-42.48 20.06-42.48 40.63V256h72.06l-11.51 56.6h-60.55v188.66C413.31 482.38 504 379.78 504 256z"/></svg>'
IG_SVG = '<svg viewBox="0 0 448 512" style="width:16px;height:16px;fill:white;margin-right:8px;vertical-align:middle;"><path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/></svg>'

# Footer: Muted Share Buttons
st.markdown(f"""
<div style="display:flex;gap:12px;justify-content:center;margin-top:10px;margin-bottom:15px;flex-wrap:wrap;">
    <a href="https://wa.me/?text={whatsapp_msg}" target="_blank" style="text-decoration:none;background-color:rgba(40,40,40,0.8);border:1px solid #555;color:#eee;padding:8px 16px;border-radius:20px;font-size:0.9rem;transition:all 0.2s;white-space:nowrap;">{WA_SVG}WhatsApp</a>
    <a href="https://www.facebook.com/sharer/sharer.php?u={fb_url}" target="_blank" style="text-decoration:none;background-color:rgba(40,40,40,0.8);border:1px solid #555;color:#eee;padding:8px 16px;border-radius:20px;font-size:0.9rem;transition:all 0.2s;white-space:nowrap;">{FB_SVG}Facebook</a>
    <a href="https://instagram.com" target="_blank" style="text-decoration:none;background-color:rgba(40,40,40,0.8);border:1px solid #555;color:#eee;padding:8px 16px;border-radius:20px;font-size:0.9rem;transition:all 0.2s;white-space:nowrap;">{IG_SVG}Instagram</a>
</div>
""", unsafe_allow_html=True)

st.code(APP_URL, language=None)
st.markdown("<p style='text-align: center; color: #666; font-size: 0.8rem; margin-top:-5px;'>Click the copy icon to copy link</p>", unsafe_allow_html=True)

st.write("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777; font-size: 0.85rem; margin-top: 0px; margin-bottom: 4px;'>With traditional insights from Saroj Kaw</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777; font-size: 0.85rem; margin-top: 0px;'>Built for our community by Shashank Kaw</p>", unsafe_allow_html=True)