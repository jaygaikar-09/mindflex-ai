import streamlit as st
import requests
from dotenv import load_dotenv
import textwrap

load_dotenv()

import json

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        default_users = {"student": "mindflex", "admin": "admin"}
        try:
            with open(USERS_FILE, "w") as f:
                json.dump(default_users, f)
        except Exception:
            pass
        return default_users

def save_user(username, password):
    users = load_users()
    users[username.lower()] = password
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        return True
    except Exception:
        return False


STUDY_PLANNER_FILE = "study_planner.json"

def load_study_planner(username):
    import os
    if not os.path.exists(STUDY_PLANNER_FILE):
        return {"topics": [], "weak_areas": []}
    try:
        with open(STUDY_PLANNER_FILE, "r") as f:
            data = json.load(f)
            return data.get(username, {"topics": [], "weak_areas": []})
    except Exception:
        return {"topics": [], "weak_areas": []}

def save_study_planner(username, user_data):
    import os
    try:
        all_data = {}
        if os.path.exists(STUDY_PLANNER_FILE):
            try:
                with open(STUDY_PLANNER_FILE, "r") as f:
                    all_data = json.load(f)
            except Exception:
                pass
        all_data[username] = user_data
        with open(STUDY_PLANNER_FILE, "w") as f:
            json.dump(all_data, f, indent=4)
        return True
    except Exception:
        return False


st.set_page_config(
    page_title="MindFlex AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000/chat"

LESSONS = {
    "📐 Calculus - Integration by Substitution": {
        "notes": """Topic: Calculus - Integration by Substitution
Goal: Simplify integrals of composite functions.
Step 1: Choose a substitution u = g(x)
Step 2: Find du = g'(x)dx
Step 3: Substitute into the integral
Step 4: Integrate with respect to u
Step 5: Replace u with g(x)

Example:
∫ 2x cos(x²) dx
Let: u = x², du = 2x dx
Integral becomes: ∫ cos(u) du""",
        "steps": [
            {"title": "Step 1: Choose substitution u = g(x)", "content": "Look for a function inside another function. For $\\int 2x \\cos(x^2) dx$, let $u = x^2$."},
            {"title": "Step 2: Find du = g'(x)dx", "content": "Differentiate $u$. Since $u = x^2$, the derivative is $2x$, so $du = 2x dx$."},
            {"title": "Step 3: Substitute into the integral", "content": "Replace $x^2$ with $u$ and $2x dx$ with $du$. The integral becomes $\\int \\cos(u) du$."},
            {"title": "Step 4: Integrate with respect to u", "content": "Integrate $\\cos(u)$ to get $\\sin(u) + C$."},
            {"title": "Step 5: Replace u with original g(x)", "content": "Substitute back $u = x^2$. The final answer is $\\sin(x^2) + C$."}
        ]
    },
    "📊 Algebra - Quadratic Formula": {
        "notes": """Topic: Algebra - Quadratic Formula
Goal: Solve quadratic equations of the form ax² + bx + c = 0.
Step 1: Identify coefficients a, b, c
Step 2: Calculate the discriminant D = b² - 4ac
Step 3: Apply the quadratic formula x = (-b ± √D) / 2a

Example:
x² - 5x + 6 = 0
Let: a=1, b=-5, c=6
D = (-5)² - 4(1)(6) = 1""",
        "steps": [
            {"title": "Step 1: Identify coefficients", "content": "For $x^2 - 5x + 6 = 0$, coefficients are $a=1$, $b=-5$, $c=6$."},
            {"title": "Step 2: Calculate Discriminant D = b² - 4ac", "content": "Compute $D = (-5)^2 - 4(1)(6) = 25 - 24 = 1$. Since $D > 0$, there are two real roots."},
            {"title": "Step 3: Apply Quadratic Formula", "content": "Solve $x = \\frac{-(-5) \\pm \\sqrt{1}}{2(1)} = \\frac{5 \\pm 1}{2}$. Roots are $x=3$ and $x=2$."}
        ]
    },
    "🍎 Physics - Work-Energy Theorem": {
        "notes": """Topic: Physics - Work-Energy Theorem
Goal: Relate the work done on an object to its change in kinetic energy.
Formula: W_net = ΔK = 1/2 m v_f² - 1/2 m v_i²
Step 1: Identify mass (m) and velocities (v_i, v_f)
Step 2: Calculate Net Work done

Example:
An object of mass 2kg accelerates from 2m/s to 4m/s.
ΔK = 1/2 * 2 * (16 - 4) = 12 Joules.
Net Work = 12 Joules.""",
        "steps": [
            {"title": "Step 1: Identify parameters", "content": "Find the mass of the object $m$, initial velocity $v_i$, and final velocity $v_f$."},
            {"title": "Step 2: Relate Net Work to Kinetic Energy", "content": "Net Work $W_{net}$ equals the change in kinetic energy $\\Delta K = K_f - K_i = \\frac{1}{2}mv_f^2 - \\frac{1}{2}mv_i^2$."}
        ]
    }
}


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

/* Main font styling */
html, body, p, li, a, strong, em, button, select, input, textarea, h1, h2, h3, h4, h5, h6, .stMarkdown {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Base page background styling */
[data-testid="stAppViewContainer"] {
    background-color: #030712;
    background-image: radial-gradient(at 0% 0%, rgba(17, 24, 39, 0.8) 0, transparent 50%), radial-gradient(at 50% 0%, rgba(31, 41, 55, 0.3) 0, transparent 50%);
    color: #f3f4f6;
}

[data-testid="stSidebar"] {
    background-color: #0b0f19;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Glassmorphism panels */
div[data-testid="stColumn"] {
    background: rgba(17, 24, 39, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.3s ease;
}

/* Accent borders on columns */
div[data-testid="stColumn"]:hover {
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}

/* Reset nested columns inside chat messages and other column groupings */
div[data-testid="stChatMessage"] div[data-testid="stColumn"],
div[data-testid="stColumn"] div[data-testid="stColumn"] {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    transform: none !important;
}

/* Chat container glassmorphism */
div[data-testid="stElementContainer"] > div[style*="height"] {
    background: rgba(15, 23, 42, 0.4) !important;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px;
}

/* Avatar Card */
.avatar-card {
    text-align: center;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.avatar-emoji {
    font-size: 64px;
    margin-bottom: 12px;
    animation: pulse 2s infinite ease-in-out;
}

.avatar-status {
    font-size: 13px;
    color: #9ca3af;
    line-height: 1.4;
    margin-top: 8px;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}

.badge {
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 12px;
    display: inline-block;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Custom styled scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* Custom offline CSS chevrons for Streamlit expander headers to prevent text overlap */
summary span > span > span {
    font-size: 0px !important;
    color: transparent !important;
    display: none !important;
}

summary span > span {
    width: 8px !important;
    height: 8px !important;
    border-right: 2px solid rgba(255, 255, 255, 0.7) !important;
    border-bottom: 2px solid rgba(255, 255, 255, 0.7) !important;
    transform: rotate(-45deg) !important; /* Pointing right */
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: inline-block !important;
    margin-right: 12px !important;
    margin-left: 4px !important;
    margin-top: -2px !important;
    vertical-align: middle !important;
}

details[open] summary span > span {
    transform: rotate(45deg) !important; /* Pointing down */
}
</style>
""", unsafe_allow_html=True)



if "emotion" not in st.session_state:
    st.session_state.emotion = "focused"

if "current_topic" not in st.session_state:
    st.session_state.current_topic = list(LESSONS.keys())[0]

if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = "⚡ Groq Cloud"

if "groq_api_key" not in st.session_state:
    import os
    # Try fetching from Streamlit secrets, then environment variables
    api_key = ""
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")
    st.session_state.groq_api_key = api_key

# --- USER AUTHENTICATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat_interactions" not in st.session_state:
    st.session_state.chat_interactions = 0

if "labs_explored" not in st.session_state:
    st.session_state.labs_explored = set()

if "tts_reads" not in st.session_state:
    st.session_state.tts_reads = 0

if "moods_experienced" not in st.session_state:
    st.session_state.moods_experienced = {"focused": 1, "confused": 0, "engaged": 0}

if not st.session_state.logged_in:
    st.markdown(textwrap.dedent("""
    <div style="text-align: center; margin-top: 40px; margin-bottom: 30px;">
        <h1 style="font-size: 44px; font-weight: 700; color: #f3f4f6; margin-bottom: 5px; letter-spacing: -0.5px;">🧠 MindFlex AI</h1>
        <p style="color: #9ca3af; font-size: 16px; font-weight: 400; margin-top: 0;">Emotion-Aware Virtual Learning Assistant</p>
    </div>
    """), unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(textwrap.dedent("""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.37);">
            <h2 style="color: #34d399; margin-top: 0; font-size: 24px; font-weight: 600; margin-bottom: 10px;">Core AI Capabilities</h2>
            <p style="color: #9ca3af; font-size: 13px; margin-bottom: 30px;">An adaptive tutoring space designed to meet your cognitive and emotional needs.</p>
            <div style="margin-bottom: 25px; display: flex; align-items: flex-start;">
                <div style="font-size: 24px; margin-right: 15px; margin-top: 2px;">🎭</div>
                <div>
                    <b style="color: #f3f4f6; font-size: 15px; display: block;">Emotion-Adaptive Explanations</b>
                    <span style="color: #9ca3af; font-size: 13px; display: block; margin-top: 2px;">Dynamically adapts tutoring style to patient recipes for confusion, precise layouts for focus, and challenges for interest.</span>
                </div>
            </div>
            <div style="margin-bottom: 25px; display: flex; align-items: flex-start;">
                <div style="font-size: 24px; margin-right: 15px; margin-top: 2px;">🤖</div>
                <div>
                    <b style="color: #f3f4f6; font-size: 15px; display: block;">Heuristic Sentiment Detection</b>
                    <span style="color: #9ca3af; font-size: 13px; display: block; margin-top: 2px;">Automatically identifies confusion or interest flags directly in student prompt inputs to swap states instantly.</span>
                </div>
            </div>
            <div style="margin-bottom: 25px; display: flex; align-items: flex-start;">
                <div style="font-size: 24px; margin-right: 15px; margin-top: 2px;">🔊</div>
                <div>
                    <b style="color: #f3f4f6; font-size: 15px; display: block;">Instant Speech Synthesis (TTS)</b>
                    <span style="color: #9ca3af; font-size: 13px; display: block; margin-top: 2px;">Converts text answers into audible speech right inside your browser window with zero API latency.</span>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start;">
                <div style="font-size: 24px; margin-right: 15px; margin-top: 2px;">🛠️</div>
                <div>
                    <b style="color: #f3f4f6; font-size: 15px; display: block;">Concept Play Laboratories</b>
                    <span style="color: #9ca3af; font-size: 13px; display: block; margin-top: 2px;">Hands-on calculators and graphers to visualize variables swap steps and solve quadratic algebra metrics.</span>
                </div>
            </div>
        </div>
        """), unsafe_allow_html=True)

    with col2:
        st.markdown(textwrap.dedent("""
        <div style="background: rgba(17, 24, 39, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 25px 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); text-align: center; display: flex; flex-direction: column;">
            <div style="font-size: 36px; margin-bottom: 10px;">🧑‍🎓</div>
            <h3 style="margin-top: 0; margin-bottom: 5px; color: #f3f4f6; font-size: 20px; font-weight: 600;">Student Access Portal</h3>
            <p style="color: #6b7280; font-size: 12px; margin-bottom: 20px;">Access your personalized learning profile and AI tutor.</p>
        """), unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Sign Up"])
        
        users = load_users()
        
        with tab_login:
            login_user = st.text_input("Username", placeholder="e.g. student", key="login_username")
            login_pass = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
            
            login_btn = st.button("Access Dashboard 🚀", use_container_width=True, key="login_btn_submit")
            
            if login_btn:
                login_user_clean = login_user.strip().lower()
                if not login_user_clean or not login_pass:
                    st.error("Fields cannot be empty!")
                elif login_user_clean in users and users[login_user_clean] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user_clean
                    st.toast(f"Welcome back, {login_user_clean.capitalize()}!", icon="🎉")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
                    
        with tab_signup:
            signup_user = st.text_input("Choose Username", placeholder="e.g. alex", key="signup_username")
            signup_pass = st.text_input("Choose Password", type="password", placeholder="••••••••", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="signup_confirm")
            
            signup_btn = st.button("Create Account ✨", use_container_width=True, key="signup_btn_submit")
            
            if signup_btn:
                signup_user_clean = signup_user.strip().lower()
                if not signup_user_clean or not signup_pass:
                    st.error("Fields cannot be empty!")
                elif signup_pass != signup_confirm:
                    st.error("Passwords do not match!")
                elif signup_user_clean in users:
                    st.error("Username already exists!")
                else:
                    if save_user(signup_user_clean, signup_pass):
                        st.session_state.logged_in = True
                        st.session_state.username = signup_user_clean
                        st.toast(f"Account created! Welcome, {signup_user_clean.capitalize()}!", icon="✨")
                        st.rerun()
                    else:
                        st.error("Database save failed. Try again.")
                        
        st.markdown(textwrap.dedent("""
        <div style="margin-top: 30px; text-align: center; font-size: 11px; color: #4b5563; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 10px;">
            🔑 <b>Default Access:</b> Username: <code style="color: #10b981;">student</code> | Password: <code style="color: #10b981;">mindflex</code>
        </div>
        </div>
        """), unsafe_allow_html=True)

    st.stop()


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "text": "Hello! I am MindFlex AI. Ask me anything about today's lesson.",
            "badge": None
        }
    ]


THEMES = {
    "focused": {
        "name": "Focused 🟢",
        "color": "#34d399",
        "avatar": "🧐",
        "status": "Providing direct, structured, and precise step-by-step notes.",
        "glow": "rgba(52, 211, 153, 0.4)"
    },
    "confused": {
        "name": "Confused 🟠",
        "color": "#fbbf24",
        "avatar": "💡",
        "status": "Simplifying concepts, using real-world analogies, and breaking steps down.",
        "glow": "rgba(251, 191, 36, 0.4)"
    },
    "engaged": {
        "name": "Engaged 🟣",
        "color": "#a78bfa",
        "avatar": "🚀",
        "status": "Injecting active practice problems and tutoring challenges.",
        "glow": "rgba(167, 139, 250, 0.4)"
    }
}


def ask_ai(question, emotion, notes):
    provider = st.session_state.get("llm_provider", "⚡ Groq Cloud")
    
    # 1. Build prompt based on student state (exactly matches main.py logic)
    emotion = emotion.lower()
    if emotion == "confused":
        system_instruction = (
            "You are an AI Tutor, a highly supportive, patient and encouraging teacher. "
            "The student is currently CONFUSED. Your absolute priority is to simplify. "
            "1. Start with supportive words (e.g., 'No worries, let's break this down together!').\n"
            "2. Use real-world analogies (e.g., comparing substitution to swapping labels or unpacking nested boxes).\n"
            "3. Avoid using overly dense mathematical terminology where simple words work.\n"
            "4. Keep explanations short, simple, and step-by-step. Avoid huge walls of text.\n"
            "5. End with a simple, encouraging question to check if they understand the first step.\n\n"
            f"Lesson Notes:\n{notes}"
        )
        user_prompt = (
            f"Student Question: {question}\n\n"
            "Explain step by step in extremely simple language with supportive analogies."
        )
    elif emotion == "engaged":
        system_instruction = (
            "You are an AI Tutor, an energetic, interactive and enthusiastic teacher. "
            "The student is highly ENGAGED and motivated. Your goal is to keep them challenged and active. "
            "1. Acknowledge their positive attitude briefly (e.g., 'Awesome! Let's put this into practice!').\n"
            "2. Provide a brief explanation of the requested concept, focusing on how to solve it.\n"
            "3. Present them with a concrete practice problem/exercise (similar to the example in the lesson notes) and ask them to try solving it.\n"
            "4. Keep the pacing dynamic and interactive.\n\n"
            f"Lesson Notes:\n{notes}"
        )
        user_prompt = (
            f"Student Question: {question}\n\n"
            "Explain briefly and present a practice problem for them to solve."
        )
    else:  # focused
        system_instruction = (
            "You are an AI Tutor, a precise and structured teacher. "
            "The student is FOCUSED and ready to learn. Your goal is to provide concise, structured explanations. "
            "1. Provide a direct, step-by-step explanation using clean formatting.\n"
            "2. Include the mathematical details and structured steps.\n"
            "3. Point out potential edge cases or tricky steps (e.g. constant of integration, finding du correctly).\n"
            "4. Keep explanations highly professional, concise, and structured.\n\n"
            f"Lesson Notes:\n{notes}"
        )
        user_prompt = (
            f"Student Question: {question}\n\n"
            "Explain step by step with clear math formatting and point out common edge cases."
        )

    # 2. Call the chosen LLM provider
    if provider == "⚡ Groq Cloud":
        api_key = st.session_state.get("groq_api_key", "").strip()
        if not api_key:
            try:
                if "GROQ_API_KEY" in st.secrets:
                    api_key = st.secrets["GROQ_API_KEY"]
            except Exception:
                pass
        if not api_key:
            import os
            api_key = os.environ.get("GROQ_API_KEY", "")
            
        if not api_key:
            return "⚠️ Please enter your Groq API Key in the sidebar to use Groq Cloud!"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                res_data = response.json()
                return res_data["choices"][0]["message"]["content"]
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", {}).get("message", response.text)
                except Exception:
                    pass
                return f"❌ Groq API Error ({response.status_code}): {error_msg}"
        except Exception as e:
            return f"❌ Connection Error (Groq): {str(e)}"
            
    else:  # Local Ollama
        import ollama
        try:
            response = ollama.Client(host="http://127.0.0.1:11434").chat(
                model="qwen2.5:3b",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response["message"]["content"]
        except Exception as e:
            return (
                "❌ Connection Error (Ollama): Could not connect to local Ollama on http://localhost:11434.\n\n"
                "**To fix this:**\n"
                "1. Make sure the Ollama desktop application is running.\n"
                "2. Verify the model `qwen2.5:3b` is pulled by running: `ollama run qwen2.5:3b` in your terminal.\n"
                "3. Alternatively, switch to **⚡ Groq Cloud** in the sidebar!"
            )


def trigger_emotion(emotion):

    st.session_state.emotion = emotion

    if "moods_experienced" in st.session_state:
        st.session_state.moods_experienced[emotion] = st.session_state.moods_experienced.get(emotion, 0) + 1

    st.toast(
        f"Emotion changed to {emotion}",
        icon="✨"
    )


def detect_emotion_from_text(text: str, current_emotion: str) -> str:
    text_lower = text.lower()
    
    # Words indicating confusion
    confusion_keywords = [
        "confused", "stuck", "don't understand", "do not understand", "lost", "hard", 
        "difficult", "explain again", "what is", "how do", "clueless", "cannot get", 
        "can't get", "makes no sense", "unclear", "doubt", "explain step", 
        "puzzled", "confusing", "too fast", "slow down"
    ]
    
    # Words indicating engagement/practice request
    engagement_keywords = [
        "practice", "exercise", "question", "problem", "test me", "challenge", 
        "try", "engaged", "more examples", "solve", "quiz", "give me a"
    ]
    
    # Words indicating focus/understanding
    focus_keywords = [
        "understand", "got it", "makes sense", "clear", "focused", "easy", 
        "i see", "ah", "okay", "ok", "fine", "yes", "cool", "got clear"
    ]
    
    for word in confusion_keywords:
        if word in text_lower:
            return "confused"
            
    for word in engagement_keywords:
        if word in text_lower:
            return "engaged"
            
    for word in focus_keywords:
        if word in text_lower:
            return "focused"
            
    return current_emotion


def send_message(text):
    # Stop any active speaking playback
    st.session_state.currently_playing = None
    st.session_state.stop_speak = True

    # Increment chat interactions
    st.session_state.chat_interactions = st.session_state.get("chat_interactions", 0) + 1

    # Auto-detect emotion from text
    detected_emotion = detect_emotion_from_text(text, st.session_state.emotion)
    
    # Track mood history
    if "moods_experienced" in st.session_state:
        st.session_state.moods_experienced[detected_emotion] = st.session_state.moods_experienced.get(detected_emotion, 0) + 1

    if detected_emotion != st.session_state.emotion:
        st.session_state.emotion = detected_emotion
        st.toast(
            f"Auto-detected state: {detected_emotion.capitalize()}",
            icon="🤖"
        )

    st.session_state.chat_history.append(
        {
            "role": "user",
            "text": text,
            "badge": None
        }
    )

    with st.spinner("MindFlex AI is thinking..."):

        answer = ask_ai(
            question=text,
            emotion=st.session_state.emotion,
            notes=LESSONS[st.session_state.current_topic]["notes"]
        )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "text": answer,
            "badge": (
                THEMES[st.session_state.emotion]["color"],
                f"Emotion: {st.session_state.emotion}"
            )
        }
    )


with st.sidebar:

    st.title("🧠 MindFlex AI")

    # Welcome card and learning analytics profile dashboard
    st.markdown(
        f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 12px; margin-bottom: 15px; text-align: center;">
            <span style="font-size: 11px; color: #9ca3af;">Student Profile:</span><br>
            <span style="font-size: 16px; font-weight: 700; color: #34d399;">{st.session_state.get('username', 'student').capitalize()} 🧑‍🎓</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📊 Learning Analytics")
    
    # Calculate custom progress score
    total_interactions = st.session_state.get("chat_interactions", 0)
    labs_count = len(st.session_state.get("labs_explored", set()))
    tts_count = st.session_state.get("tts_reads", 0)
    
    # Integrate study planner topics coverage
    username = st.session_state.get('username', 'student')
    planner_data = load_study_planner(username)
    planner_count = len(planner_data.get("topics", []))
    
    progress_score = min(100, (total_interactions * 10) + (labs_count * 20) + (tts_count * 10) + (planner_count * 25))
    
    st.progress(progress_score / 100.0)
    st.caption(f"Engagement Score: **{progress_score}%**")
    
    # Mood Analytics
    moods = st.session_state.get("moods_experienced", {"focused": 1, "confused": 0, "engaged": 0})
    st.markdown(
        f"""
        <div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px;">Tutor State Analytics:</div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <span style="background: rgba(52, 211, 153, 0.08); color: #34d399; padding: 2px 6px; border-radius: 6px; font-size: 10px; font-weight: 600;">Focus: {moods.get('focused', 0)}</span>
            <span style="background: rgba(251, 191, 36, 0.08); color: #fbbf24; padding: 2px 6px; border-radius: 6px; font-size: 10px; font-weight: 600;">Confused: {moods.get('confused', 0)}</span>
            <span style="background: rgba(167, 139, 250, 0.08); color: #a78bfa; padding: 2px 6px; border-radius: 6px; font-size: 10px; font-weight: 600;">Engaged: {moods.get('engaged', 0)}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Log Out 🔒", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()

    # Render dynamic AI Tutor Avatar card
    current = THEMES[st.session_state.emotion]
    st.markdown(
        f"""
        <div class="avatar-card" style="box-shadow: 0 0 20px {current['glow']}; border-color: {current['color']}40;">
            <div class="avatar-emoji">{current['avatar']}</div>
            <div style="font-weight: 700; font-size: 16px; color: {current['color']};">Tutor Status: {current['name']}</div>
            <div class="avatar-status">{current['status']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Manual Override")

    st.button(
        "Focused 🟢",
        use_container_width=True,
        on_click=trigger_emotion,
        args=("focused",)
    )

    st.button(
        "Confused 🟠",
        use_container_width=True,
        on_click=trigger_emotion,
        args=("confused",)
    )

    st.button(
        "Engaged 🟣",
        use_container_width=True,
        on_click=trigger_emotion,
        args=("engaged",)
    )

    st.markdown("### LLM Configuration")

    st.selectbox(
        "LLM Provider:",
        ["⚡ Groq Cloud", "🤖 Local Ollama"],
        key="llm_provider"
    )

    if st.session_state.llm_provider == "⚡ Groq Cloud":
        st.text_input(
            "Groq API Key:",
            type="password",
            placeholder="gsk_...",
            key="groq_api_key",
            help="Get your free API key from https://console.groq.com/"
        )

    st.divider()

    if st.button("Reset Chat", use_container_width=True):

        st.session_state.chat_history = [
            {
                "role": "assistant",
                "text": "Hello! I am MindFlex AI. Ask me anything about today's lesson.",
                "badge": None
            }
        ]
        st.session_state.currently_playing = None
        st.session_state.stop_speak = True

        st.rerun()


current = THEMES[st.session_state.emotion]

st.markdown(
    f"""
    # 🧠 MindFlex AI
    **Current Emotion:** <span style='color:{current["color"]}'>{current["name"]}</span>
    """,
    unsafe_allow_html=True
)


main_tab1, main_tab2 = st.tabs(["📚 Learning Dashboard", "📅 Study Planner"])

with main_tab1:
    left, right = st.columns([1, 2])


    with left:

        st.subheader("📚 Lesson Modules")

        # Dynamic topic selector dropdown
        selected_topic = st.selectbox(
            "Choose Subject / Topic:",
            list(LESSONS.keys()),
            key="current_topic",
            on_change=lambda: st.toast("Switched to new learning module!", icon="📚")
        )

        lesson_data = LESSONS[selected_topic]

        st.write("Click on the steps below to expand the interactive walkthrough:")
        # Interactive collapsible accordion steps
        for step in lesson_data["steps"]:
            with st.expander(step["title"]):
                st.write(step["content"])

        # Topic-specific interactive play laboratory
        st.divider()
        st.subheader("🛠️ Concept Playground")

        if "Calculus" in selected_topic:
            show_sub = st.checkbox("Toggle Variable Substitution Swap")
            if show_sub:
                if "labs_explored" in st.session_state:
                    st.session_state.labs_explored.add("calculus_swap")
                st.latex(r"\int 2x \cos(x^2) dx \quad \xrightarrow{u = x^2, \, du = 2x\,dx} \quad \int \cos(u) du")
                st.info("Substitution simplified the composite integral into a basic trigonometric form!")
            else:
                st.latex(r"\int 2x \cos(x^2) dx")
                st.caption("Check the box above to simulate the substitution swap step!")

        elif "Algebra" in selected_topic:
            st.write("Enter quadratic coefficients to test the discriminant solver:")
            c_a = st.number_input("a (quadratic coefficient)", value=1, step=1)
            c_b = st.number_input("b (linear coefficient)", value=-5, step=1)
            c_c = st.number_input("c (constant)", value=6, step=1)
            if c_a != 1 or c_b != -5 or c_c != 6:
                if "labs_explored" in st.session_state:
                    st.session_state.labs_explored.add("algebra_solver")

            disc = c_b**2 - 4*c_a*c_c
            st.write(f"Discriminant $D = b^2 - 4ac$ = **{disc}**")
            if disc > 0:
                st.success("Two distinct real roots exist.")
            elif disc == 0:
                st.warning("Exactly one real root exists.")
            else:
                st.error("No real roots exist (roots are complex numbers).")

        elif "Physics" in selected_topic:
            st.write("Adjust mass and velocities to calculate kinetic energy net work:")
            p_mass = st.slider("Object Mass (kg)", 1, 10, 2)
            p_vi = st.slider("Initial Velocity (m/s)", 0, 10, 2)
            p_vf = st.slider("Final Velocity (m/s)", 0, 20, 6)
            if p_mass != 2 or p_vi != 2 or p_vf != 6:
                if "labs_explored" in st.session_state:
                    st.session_state.labs_explored.add("physics_calculator")

            k_i = 0.5 * p_mass * (p_vi**2)
            k_f = 0.5 * p_mass * (p_vf**2)
            work_done = k_f - k_i

            st.metric(label="Initial Kinetic Energy", value=f"{k_i} J")
            st.metric(label="Final Kinetic Energy", value=f"{k_f} J")
            st.metric(label="Net Work Done (W_net)", value=f"{work_done} Joules")


    with right:

        st.subheader("💬 Adaptive Tutor")

        chat_container = st.container(height=450)

        with chat_container:

            for i, msg in enumerate(st.session_state.chat_history):

                # Use cute emoji avatars to avoid offline Material Icon loading issues (e.g., 'art_')
                avatar_emoji = "🤖" if msg["role"] == "assistant" else "🧑‍🎓"

                with st.chat_message(msg["role"], avatar=avatar_emoji):

                    st.markdown(msg["text"])

                    badge_col, speak_col = st.columns([9, 1])

                    with badge_col:
                        if msg["badge"]:
                            color, badge_text = msg["badge"]
                            st.markdown(
                                f"""
                                <div class="badge"
                                     style="border:1px solid {color};
                                     color:{color};">
                                     {badge_text}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    with speak_col:
                        if msg["role"] == "assistant":
                            is_playing = st.session_state.get("currently_playing") == i
                            button_label = "🔇" if is_playing else "🔊"
                            button_help = "Stop reading aloud" if is_playing else "Read aloud"
                            
                            if st.button(button_label, key=f"speak_{i}", help=button_help):
                                if is_playing:
                                    st.session_state.currently_playing = None
                                    st.session_state.stop_speak = True
                                else:
                                    import re
                                    st.session_state.tts_reads = st.session_state.get("tts_reads", 0) + 1
                                    # Clean up markdown markers for speech synthesis
                                    clean_text = re.sub(r'[*#_`\-]', ' ', msg["text"])
                                    # Strip double spaces and LaTeX syntax
                                    clean_text = re.sub(r'\\\(|\\\)|\\\[|\\\]', ' ', clean_text)
                                    st.session_state.speak_text = clean_text
                                    st.session_state.currently_playing = i
                                    if "stop_speak" in st.session_state:
                                        del st.session_state.stop_speak
                                st.rerun()

        st.markdown("### Quick Questions")

        c1, c2, c3 = st.columns(3)

        with c1:
            if st.button(
                "Explain Step 3",
                use_container_width=True
            ):
                send_message("Explain Step 3")
                st.rerun()

        with c2:
            if st.button(
                "I am confused",
                use_container_width=True
            ):
                send_message("I am confused about substitution")
                st.rerun()

        with c3:
            if st.button(
                "Practice Problem",
                use_container_width=True
            ):
                send_message("Give me a practice problem")
                st.rerun()

        prompt = st.chat_input(
            "Ask MindFlex AI..."
        )

        if prompt:

            send_message(prompt)

            st.rerun()

with main_tab2:
    st.subheader("📅 Study Planner")
    st.caption("Adaptive • Intelligent • Personal")

    # Load data for active user
    username = st.session_state.get("username", "student")
    planner_data = load_study_planner(username)
    topics = planner_data.get("topics", [])
    weak_areas = planner_data.get("weak_areas", [])

    # ALL TOPICS definitions matching LESSONS
    STUDY_TOPICS_MAPPING = {
        "📐 Calculus": ["Integration by Substitution"],
        "📊 Algebra": ["Quadratic Formula"],
        "🍎 Physics": ["Work-Energy Theorem"]
    }
    ALL_PLANNER_TOPICS = [t for group in STUDY_TOPICS_MAPPING.values() for t in group]

    # Calculate overall progress and average score stats
    mastered_count = sum(1 for t in topics if t["score"] >= 70)
    weak_count = len(weak_areas)
    topics_logged = len(topics)
    avg_score = round(sum(t["score"] for t in topics) / topics_logged) if topics_logged > 0 else 0
    progress_pct = round((topics_logged / len(ALL_PLANNER_TOPICS)) * 100) if len(ALL_PLANNER_TOPICS) > 0 else 0

    # Display Stat Cards using columns
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 5px;">📚</div>
            <div style="font-size: 18px; font-weight: 700; color: #f3f4f6;">{topics_logged}</div>
            <div style="font-size: 11px; color: #9ca3af;">Topics Logged</div>
            <div style="font-size: 10px; color: #6b7280;">of {len(ALL_PLANNER_TOPICS)}</div>
        </div>
        """, unsafe_allow_html=True)
    with s_col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 5px;">🎯</div>
            <div style="font-size: 18px; font-weight: 700; color: #f3f4f6;">{avg_score}%</div>
            <div style="font-size: 11px; color: #9ca3af;">Avg Score</div>
            <div style="font-size: 10px; color: #6b7280;">{"Great!" if avg_score >= 70 else "Keep going" if avg_score > 0 else "No quizzes yet"}</div>
        </div>
        """, unsafe_allow_html=True)
    with s_col3:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 5px;">🏆</div>
            <div style="font-size: 18px; font-weight: 700; color: #f3f4f6;">{mastered_count}</div>
            <div style="font-size: 11px; color: #9ca3af;">Mastered</div>
            <div style="font-size: 10px; color: #6b7280;">score &ge; 70%</div>
        </div>
        """, unsafe_allow_html=True)
    with s_col4:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 5px;">⚠️</div>
            <div style="font-size: 18px; font-weight: 700; color: #f3f4f6;">{weak_count}</div>
            <div style="font-size: 11px; color: #9ca3af;">Weak Areas</div>
            <div style="font-size: 10px; color: #6b7280;">need revision</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sub-tabs for the Study Planner sections
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📅 Schedule", "📚 My Topics", "➕ Log Topic"])

    with sub_tab1:
        # Schedule tab
        st.subheader("Your Study Schedule")
        
        # Display weak areas as badges if any
        if weak_areas:
            weak_badges = "".join([f"<span style='background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 2px 8px; font-size: 11px; margin-right: 5px; display: inline-block;'>{w}</span>" for w in weak_areas])
            st.markdown(f"**Needs Revision:** {weak_badges}", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Plan generation algorithm
        import datetime
        today = datetime.date.today()
        covered = [t["name"] for t in topics]
        new_topics = [t for t in ALL_PLANNER_TOPICS if t not in covered]
        
        plan = {}
        for i in range(3):
            day_date = today + datetime.timedelta(days=i)
            if i == 0:
                label = "Today"
            elif i == 1:
                label = "Tomorrow"
            else:
                label = day_date.strftime("%A")
            
            sessions = []
            # Revision for weak areas
            for w_topic in weak_areas[:2]:
                sessions.append({"topic": w_topic, "duration": 30, "type": "Revision", "icon": "🔁", "color": "rgba(244, 63, 94, 0.1)", "border": "rgba(244, 63, 94, 0.2)", "text_color": "#fda4af"})
            # New Topic if available
            if i < len(new_topics):
                sessions.append({"topic": new_topics[i], "duration": 25, "type": "New Topic", "icon": "📘", "color": "rgba(59, 130, 246, 0.1)", "border": "rgba(59, 130, 246, 0.2)", "text_color": "#93c5fd"})
            # Quiz on day 3
            if i == 2:
                sessions.append({"topic": "Mixed Quiz", "duration": 20, "type": "Quiz", "icon": "🧪", "color": "rgba(245, 158, 11, 0.1)", "border": "rgba(245, 158, 11, 0.2)", "text_color": "#fde047"})
            
            plan[label] = sessions
            
        # Select active day
        active_day = st.radio("Choose Day:", list(plan.keys()), horizontal=True, key="planner_active_day")
        
        if active_day:
            day_sessions = plan[active_day]
            total_time = sum(s["duration"] for s in day_sessions)
            st.caption(f"⏱ Total study time: {total_time} mins")
            
            if not day_sessions:
                st.info("No study sessions scheduled for this day! Log some topics to generate revision tasks.")
            else:
                for session in day_sessions:
                    st.markdown(f"""
                    <div style="background: {session['color']}; border: 1px solid {session['border']}; border-radius: 12px; padding: 12px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 24px; margin-right: 15px;">{session['icon']}</span>
                            <div>
                                <div style="font-weight: 600; color: {session['text_color']}; font-size: 14px;">{session['topic']}</div>
                                <div style="font-size: 11px; color: #9ca3af; margin-top: 1px;">{session['type']}</div>
                            </div>
                        </div>
                        <div style="font-weight: 700; color: #f3f4f6; font-size: 14px;">{session['duration']} min</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        if topics_logged == 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("💡 Log some completed topics under **Log Topic** to dynamically populate your adaptive revision schedule!")

    with sub_tab2:
        # My Topics list
        st.subheader("Your Logged Topics")
        search_query = st.text_input("🔍 Search topics...", placeholder="Type topic name...", key="topics_search")
        
        filtered_topics = [t for t in topics if search_query.lower() in t["name"].lower()]
        
        if not filtered_topics:
            st.info("No topics found matching your search. Go to **Log Topic** to add one!")
        else:
            for t in filtered_topics:
                score = t["score"]
                bar_color = "#34d399" if score >= 70 else "#fbbf24" if score >= 50 else "#f87171"
                
                # HTML template for topic row
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 12px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <span style="font-weight: 600; color: #f3f4f6; font-size: 14px;">{t['name']}</span>
                        <span style="font-weight: 700; color: {bar_color}; font-size: 14px;">{score}%</span>
                    </div>
                    <div style="width: 100%; border-radius: 10px; height: 6px; background: rgba(255, 255, 255, 0.05);">
                        <div style="background: {bar_color}; height: 6px; border-radius: 10px; width: {score}%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #6b7280; margin-top: 5px;">
                        <span>Completed on: {t['date']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render delete button for each topic
                del_col1, del_col2 = st.columns([9, 1])
                with del_col2:
                    if st.button("🗑️", key=f"del_{t['id']}", help=f"Remove {t['name']}"):
                        topics = [x for x in topics if x["id"] != t["id"]]
                        weak_areas = [w for w in weak_areas if w != t["name"]]
                        planner_data["topics"] = topics
                        planner_data["weak_areas"] = weak_areas
                        save_study_planner(username, planner_data)
                        st.toast(f"Removed topic: {t['name']}", icon="🗑️")
                        st.rerun()

    with sub_tab3:
        # Log Topic tab
        st.subheader("Log a Completed Topic")
        
        # Select topic dropdown
        available_choices = []
        for category, items in STUDY_TOPICS_MAPPING.items():
            for item in items:
                is_logged = any(t["name"] == item for t in topics)
                available_choices.append((item, category, is_logged))
                
        # Format option labels
        option_labels = []
        option_values = []
        for item, category, is_logged in available_choices:
            option_values.append(item)
            label = f"{category} - {item}"
            if is_logged:
                label += " (✓ Completed)"
            option_labels.append(label)
            
        selected_log_topic = st.selectbox(
            "Select Completed Topic:",
            options=option_values,
            format_func=lambda x: option_labels[option_values.index(x)],
            key="log_topic_select"
        )
        
        score_val = st.number_input("Quiz Score (0-100):", min_value=0, max_value=100, value=75, key="log_topic_score")
        
        # Feedback indicator message
        if score_val >= 70:
            st.success("🏆 Excellent! Topic mastered.")
        elif score_val >= 50:
            st.warning("📖 Good effort! A bit more practice needed.")
        else:
            st.error("⚠️ Will be added to weak areas for revision.")
            
        if st.button("Save Topic →", use_container_width=True, key="log_topic_save_btn"):
            if not selected_log_topic:
                st.error("Please select a topic!")
            else:
                existing = next((t for t in topics if t["name"] == selected_log_topic), None)
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                
                if existing:
                    existing["score"] = score_val
                    existing["date"] = today_str
                else:
                    topics.append({
                        "id": int(datetime.datetime.now().timestamp()),
                        "name": selected_log_topic,
                        "score": score_val,
                        "date": today_str
                    })
                
                # Update weak areas
                if score_val < 60:
                    if selected_log_topic not in weak_areas:
                        weak_areas.append(selected_log_topic)
                else:
                    weak_areas = [w for w in weak_areas if w != selected_log_topic]
                    
                planner_data["topics"] = topics
                planner_data["weak_areas"] = weak_areas
                
                if save_study_planner(username, planner_data):
                    st.toast(f"Successfully logged {selected_log_topic}!", icon="✨")
                    st.rerun()
                else:
                    st.error("Failed to save. Try again.")


# --- Speech Synthesis Player ---
if "speak_text" in st.session_state and st.session_state.speak_text:
    escaped_text = st.session_state.speak_text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    st.components.v1.html(
        f"""
        <script>
            if ('speechSynthesis' in window.parent) {{
                window.parent.speechSynthesis.cancel();
                let utterance = new SpeechSynthesisUtterance("{escaped_text}");
                utterance.rate = 1.05;
                window.parent.speechSynthesis.speak(utterance);
            }}
        </script>
        """,
        height=0,
        width=0
    )
    st.session_state.speak_text = ""

if st.session_state.get("stop_speak"):
    st.components.v1.html(
        """
        <script>
            if ('speechSynthesis' in window.parent) {
                window.parent.speechSynthesis.cancel();
            }
        </script>
        """,
        height=0,
        width=0
    )
    st.session_state.stop_speak = False