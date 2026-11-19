import streamlit as st
import random
import time
import hashlib
import json
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="돌 강화하기", page_icon="🪨", layout="centered")

DATA_FILE = "save_data.json"

# 2. +0 ~ +20 구간별 밸런스 데이터
LEVELS = [
    {"cost": 10,     "succ": 100.0, "keep": 0.0,  "down": 0.0,  "dest": 0.0,  "shard": 0,     "name": "길가의 조약돌",   "icon": "🪨", "color": "#94a3b8"},
    {"cost": 20,     "succ": 95.0,  "keep": 5.0,  "down": 0.0,  "dest": 0.0,  "shard": 0,     "name": "단단한 화강암",   "icon": "🪨", "color": "#94a3b8"},
    {"cost": 40,     "succ": 90.0,  "keep": 10.0, "down": 0.0,  "dest": 0.0,  "shard": 0,     "name": "매끄러운 차돌",   "icon": "🪨", "color": "#94a3b8"},
    {"cost": 80,     "succ": 85.0,  "keep": 15.0, "down": 0.0,  "dest": 0.0,  "shard": 0,     "name": "철광석 원석",     "icon": "🪨", "color": "#94a3b8"},
    {"cost": 150,    "succ": 80.0,  "keep": 20.0, "down": 0.0,  "dest": 0.0,  "shard": 0,     "name": "빛바랜 수정",     "icon": "🪨", "color": "#94a3b8"},
    {"cost": 300,    "succ": 70.0,  "keep": 30.0, "down": 0.0,  "dest": 0.0,  "shard": 5,     "name": "세공된 비취",     "icon": "💎", "color": "#34d399"},
    {"cost": 500,    "succ": 65.0,  "keep": 25.0, "down": 10.0, "dest": 0.0,  "shard": 12,    "name": "에메랄드 원석",   "icon": "💎", "color": "#34d399"},
    {"cost": 800,    "succ": 60.0,  "keep": 25.0, "down": 15.0, "dest": 0.0,  "shard": 25,    "name": "심연의 흑요석",   "icon": "💎", "color": "#34d399"},
    {"cost": 1200,   "succ": 55.0,  "keep": 25.0, "down": 20.0, "dest": 0.0,  "shard": 50,    "name": "자수정의 결정",   "icon": "💎", "color": "#34d399"},
    {"cost": 2000,   "succ": 50.0,  "keep": 25.0, "down": 25.0, "dest": 0.0,  "shard": 90,    "name": "고대 룬스톤",     "icon": "💎", "color": "#34d399"},
    {"cost": 3500,   "succ": 45.0,  "keep": 25.0, "down": 25.0, "dest": 5.0,  "shard": 160,   "name": "푸른 마력석",     "icon": "🔮", "color": "#60a5fa"},
    {"cost": 5500,   "succ": 40.0,  "keep": 25.0, "down": 25.0, "dest": 10.0, "shard": 300,   "name": "서리 영혼석",     "icon": "🔮", "color": "#60a5fa"},
    {"cost": 8500,   "succ": 35.0,  "keep": 25.0, "down": 25.0, "dest": 15.0, "shard": 550,   "name": "폭풍의 핵",       "icon": "🔮", "color": "#60a5fa"},
    {"cost": 13000,  "succ": 30.0,  "keep": 25.0, "down": 25.0, "dest": 20.0, "shard": 1000,  "name": "별빛의 파편",     "icon": "🔮", "color": "#60a5fa"},
    {"cost": 20000,  "succ": 25.0,  "keep": 25.0, "down": 25.0, "dest": 25.0, "shard": 1800,  "name": "차원의 보주",     "icon": "🔮", "color": "#60a5fa"},
    {"cost": 35000,  "succ": 20.0,  "keep": 20.0, "down": 30.0, "dest": 30.0, "shard": 3200,  "name": "태양의 심장",     "icon": "☀️", "color": "#fb923c"},
    {"cost": 60000,  "succ": 15.0,  "keep": 20.0, "down": 30.0, "dest": 35.0, "shard": 6000,  "name": "불사조의 여의주", "icon": "🔥", "color": "#fb923c"},
    {"cost": 100000, "succ": 10.0,  "keep": 20.0, "down": 30.0, "dest": 40.0, "shard": 11000, "name": "용신의 역린",     "icon": "🐉", "color": "#fb923c"},
    {"cost": 180000, "succ": 5.0,   "keep": 15.0, "down": 35.0, "dest": 45.0, "shard": 20000, "name": "창세의 성물",     "icon": "👑", "color": "#fb923c"},
    {"cost": 300000, "succ": 3.0,   "keep": 12.0, "down": 35.0, "dest": 50.0, "shard": 40000, "name": "초월자의 진리",   "icon": "✨", "color": "#fb923c"},
    {"cost": 0,      "succ": 0.0,   "keep": 0.0,  "down": 0.0,  "dest": 0.0,  "shard": 80000, "name": "태초의 절대석",   "icon": "🌌", "color": "#e879f9"},
]

# 3. 돌 파편 영구 업그레이드 데이터
UPGRADES = [
    {"id": "goldClick",  "name": "1. 채굴의 손길", "desc": "클릭당 골드 획득 +20%",             "max": 50, "base": 5,  "mult": 1.25},
    {"id": "autoGold",   "name": "2. 자동 채굴기", "desc": "행동 시 클릭 골드의 +10% 추가 획득", "max": 30, "base": 10, "mult": 1.35},
    {"id": "addSucc",    "name": "3. 장인의 망치", "desc": "강화 성공 확률 +0.5%",              "max": 20, "base": 15, "mult": 1.50},
    {"id": "discount",   "name": "4. 제련술 숙련", "desc": "강화 골드 비용 -2%",                "max": 25, "base": 10, "mult": 1.30},
    {"id": "lessDown",   "name": "5. 견고한 결속", "desc": "등급 하락 확률 -1%",                "max": 15, "base": 20, "mult": 1.60},
    {"id": "lessDest",   "name": "6. 불굴의 핵",   "desc": "돌 파괴 확률 -1%",                  "max": 10, "base": 30, "mult": 1.80},
    {"id": "feverBoost", "name": "7. 분노의 잔재", "desc": "피버 게이지 충전량 +5%",            "max": 20, "base": 15, "mult": 1.40},
]

# 4. 오늘의 돌 운세 (랜덤 축복 버프)
BLESSINGS = [
    {"id": "gold_rush",  "name": "💰 황금의 축복",   "desc": "모든 채굴 골드 획득량 +50%"},
    {"id": "cheap_enh",  "name": "⚒️ 대장장이의 축복", "desc": "모든 강화 골드 비용 -10%"},
    {"id": "lucky_star", "name": "🍀 행운별의 축복", "desc": "모든 구간 강화 성공 확률 +3.0%"},
    {"id": "rage_fire",  "name": "🔥 격노의 축복",   "desc": "실패 시 피버 게이지 충전량 +25%"},
]

# 5. 보조 아이템 가격 및 목표 상수
SHIELD_COST = 15000
SCROLL_COST = 5000
CHALLENGE_GOAL = 15

# 6. 다크 판타지 대장간 전역 테마 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&display=swap');

.stApp {
    background:
        radial-gradient(circle at 50% 0%, rgba(245, 158, 11, 0.08) 0%, transparent 45%),
        radial-gradient(circle at 85% 20%, rgba(120, 53, 15, 0.14) 0%, transparent 40%),
        linear-gradient(180deg, #0b0d12 0%, #11141c 55%, #090b0f 100%);
    color: #f3f4f6;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #d97706 0%, #ea580c 55%, #b45309 100%) !important;
    border: 1px solid #fbbf24 !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 16px rgba(234, 88, 12, 0.35) !important;
    transition: transform 0.14s ease, box-shadow 0.14s ease, filter 0.14s ease !important;
}

div.stButton > button[kind="primary"]:hover:not(:disabled) {
    transform: translateY(-2px) !important;
    box-shadow: 0 7px 22px rgba(251, 191, 36, 0.45) !important;
    filter: brightness(1.08) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(24, 28, 39, 0.88) !important;
    border: 1px solid #333a4d !important;
    color: #e5e7eb !important;
    font-weight: 700 !important;
    transition: transform 0.14s ease, border-color 0.14s ease !important;
}

div.stButton > button[kind="secondary"]:hover:not(:disabled) {
    transform: translateY(-1px) !important;
    border-color: #f59e0b !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(26, 30, 42, 0.9), rgba(15, 18, 26, 0.95));
    border: 1px solid rgba(251, 191, 36, 0.18);
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 6px 18px rgba(0, 0, 0, 0.35);
}

[data-testid="stMetricLabel"] {
    color: #9ca3af !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #fef3c7 !important;
    font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)

# 7. 유틸리티: 해시, 프로필 생성, JSON 파일 영구 저장
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_fresh_profile(is_challenge=False):
    blessing = random.choice(BLESSINGS)
    msg = (
        f"🏆 [도전 모드] 오늘의 운세 [{blessing['name']}] 적용! 최소 행동으로 +15를 완성하세요!"
        if is_challenge else
        f"✨ 오늘의 운세 [{blessing['name']}] 적용! 돌을 채굴해 강화를 시작하세요!"
    )
    return {
        "gold": 50,
        "shards": 0,
        "level": 0,
        "max_level": 0,
        "fever": 0.0,
        "unlocked": [0],
        "blessing": blessing,
        "last_msg": ["info", msg],
        "logs": [],
        "upg": {u["id"]: 0 for u in UPGRADES},
        "shields": 0,
        "scrolls": 0,
        "use_shield": False,
        "use_scroll": False,
        "mine_actions": 0,
        "enh_actions": 0,
        "destroy_count": 0,
        "spent_gold": 0,
        "cleared": False,
    }

def create_new_user_record(password: str):
    return {
        "pw_hash": hash_pw(password),
        "profiles": {
            "free": create_fresh_profile(False),
            "challenge": create_fresh_profile(True),
        },
    }

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "users" in data and "hall_of_fame" in data:
                    return data
        except Exception:
            pass
    default_db = {
        "users": {
            "guest": create_new_user_record("1234"),
        },
        "hall_of_fame": [],
    }
    save_db(default_db)
    return default_db

def save_db(db_data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

@st.cache_resource
def get_shared_storage():
    return load_db()

DB = get_shared_storage()

if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "started" not in st.session_state:
    st.session_state.started = False
if "mode" not in st.session_state:
    st.session_state.mode = "free"

# ==========================================
# [화면 0] 로그인 & 회원가입 화면
# ==========================================
if st.session_state.current_user is None:
    st.markdown("""
    <div style="background: radial-gradient(circle at top, #271c19 0%, #12151e 80%); border: 1.5px solid rgba(245, 158, 11, 0.45); border-radius: 24px; padding: 30px 24px; text-align: center; margin-top: 10px; box-shadow: 0 14px 40px rgba(0,0,0,0.6), inset 0 0 28px rgba(245, 158, 11, 0.08);">
        <div style="font-size: 56px; margin-bottom: 6px;">⚒️🔐💎</div>
        <div style="font-size: 31px; font-weight: 900; color: #fef3c7; letter-spacing: 0.5px;">돌 강화하기</div>
        <div style="font-size: 13px; color: #d6b88c; margin-top: 5px; font-weight: 600;">DARK FORGE ENHANCER · 계정별 영구 저장 & 랭킹 대전</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(" ")

    auth_tab1, auth_tab2 = st.tabs(["🔑 로그인", "📝 회원가입"])

    with auth_tab1:
        with st.form("login_form"):
            login_id = st.text_input("아이디", placeholder="아이디를 입력하세요 (체험용: guest)")
            login_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요 (체험용: 1234)")
            submitted = st.form_submit_button("로그인하기", type="primary", use_container_width=True)

            if submitted:
                uid = login_id.strip()
                if not uid or not login_pw:
                    st.error("아이디와 비밀번호를 모두 입력해 주세요.")
                elif uid not in DB["users"]:
                    st.error("존재하지 않는 아이디입니다. 회원가입 탭에서 새 계정을 만들어보세요.")
                elif DB["users"][uid]["pw_hash"] != hash_pw(login_pw):
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.session_state.current_user = uid
                    st.session_state.started = False
                    st.toast(f"환영합니다, {uid}님!")
                    st.rerun()

        st.caption("💡 바로 테스트해보려면 아이디 **`guest`**, 비밀번호 **`1234`**로 로그인하세요. (`save_data.json` 영구 저장 지원)")

    with auth_tab2:
        with st.form("signup_form"):
            new_id = st.text_input("새 아이디 (2~12자)", max_chars=12, placeholder="랭킹에 표시될 닉네임 겸 아이디")
            new_pw = st.text_input("비밀번호 (4자 이상)", type="password", placeholder="비밀번호 입력")
            new_pw_confirm = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호 다시 입력")
            reg_submitted = st.form_submit_button("회원가입 및 자동 로그인", type="primary", use_container_width=True)

            if reg_submitted:
                uid = new_id.strip()
                if len(uid) < 2:
                    st.error("아이디는 최소 2글자 이상이어야 합니다.")
                elif uid in DB["users"]:
                    st.error("이미 사용 중인 아이디입니다. 다른 아이디를 입력해 주세요.")
                elif len(new_pw) < 4:
                    st.error("비밀번호는 4자 이상으로 설정해 주세요.")
                elif new_pw != new_pw_confirm:
                    st.error("비밀번호 확인이 일치하지 않습니다.")
                else:
                    DB["users"][uid] = create_new_user_record(new_pw)
                    save_db(DB)
                    st.session_state.current_user = uid
                    st.session_state.started = False
                    st.toast(f"🎉 {uid}님, 회원가입이 완료되었습니다!")
                    st.rerun()

    if DB["hall_of_fame"]:
        st.markdown("---")
        st.markdown("##### 🏅 실시간 +15 도전 명예의 전당 (TOP 5)")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for idx, rec in enumerate(DB["hall_of_fame"][:5]):
            st.markdown(
                f"{medals[idx]} **{rec['name']}** — `[RANK {rec['grade']}]` **총 {rec['total']}회 행동** "
                f"<small style='color:#94a3b8'>(채굴 {rec['mine']} / 강화 {rec['enh']} / 파괴 {rec['destroy']})</small>",
                unsafe_allow_html=True
            )

    st.stop()

# 현재 로그인된 유저 데이터 참조
USER_ID = st.session_state.current_user
USER_DATA = DB["users"][USER_ID]

# ==========================================
# [화면 1] 타이틀 & 모드 선택 화면
# ==========================================
if not st.session_state.started:
    top_bar1, top_bar2 = st.columns([3, 1])
    with top_bar1:
        st.markdown(f"👤 **{USER_ID}** 님으로 로그인됨 · 💾 자동 저장 활성")
    with top_bar2:
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.current_user = None
            st.session_state.started = False
            st.rerun()

    st.markdown("""
    <div style="background: radial-gradient(circle at top, #291c18 0%, #12151e 85%); border: 1.5px solid rgba(245, 158, 11, 0.45); border-radius: 24px; padding: 30px 24px; text-align: center; margin-top: 6px; box-shadow: 0 14px 40px rgba(0,0,0,0.6), inset 0 0 28px rgba(245, 158, 11, 0.08);">
        <div style="font-size: 60px; margin-bottom: 6px;">⚒️✨💎</div>
        <div style="font-size: 32px; font-weight: 900; color: #fef3c7; letter-spacing: -0.5px;">돌 강화하기</div>
        <div style="font-size: 14px; color: #d6b88c; margin-top: 6px; font-weight: 600;">DARK FORGE ENHANCER · 확률과 도파민의 극한 제련 시뮬레이터</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(" ")

    c_intro1, c_intro2, c_intro3 = st.columns(3)
    with c_intro1:
        st.markdown("""
        <div style="background:rgba(20, 24, 34, 0.92); border:1px solid rgba(251, 191, 36, 0.22); border-radius:14px; padding:15px 10px; text-align:center; height:100%;">
            <div style="font-size:26px;">🔨</div>
            <div style="font-weight:800; font-size:14px; margin:6px 0 4px 0; color:#fef3c7;">+20 극한 강화</div>
            <div style="font-size:12px; color:#9ca3af; line-height:1.4;">길가의 조약돌에서<br>태초의 절대석까지 진화</div>
        </div>
        """, unsafe_allow_html=True)
    with c_intro2:
        st.markdown("""
        <div style="background:rgba(20, 24, 34, 0.92); border:1px solid rgba(251, 191, 36, 0.22); border-radius:14px; padding:15px 10px; text-align:center; height:100%;">
            <div style="font-size:26px;">🔥</div>
            <div style="font-weight:800; font-size:14px; margin:6px 0 4px 0; color:#fbbf24;">피버 확정 천장</div>
            <div style="font-size:12px; color:#9ca3af; line-height:1.4;">실패할수록 차오르는<br>100% 확정 강화 찬스</div>
        </div>
        """, unsafe_allow_html=True)
    with c_intro3:
        st.markdown("""
        <div style="background:rgba(20, 24, 34, 0.92); border:1px solid rgba(251, 191, 36, 0.22); border-radius:14px; padding:15px 10px; text-align:center; height:100%;">
            <div style="font-size:26px;">🔮</div>
            <div style="font-weight:800; font-size:14px; margin:6px 0 4px 0; color:#e879f9;">파편 & 익절 정산</div>
            <div style="font-size:12px; color:#9ca3af; line-height:1.4;">돌을 팔거나 파편을 모아<br>영구 능력치 업그레이드</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown("##### 🎯 플레이할 모드를 선택하세요")

    free_p = USER_DATA["profiles"]["free"]
    chal_p = USER_DATA["profiles"]["challenge"]
    free_lv = free_p["level"]
    chal_lv = chal_p["level"]

    mode_c1, mode_c2 = st.columns(2)
    with mode_c1:
        st.info(
            f"**🎮 자유 모드 (+20 목표)**\n\n"
            f"내 진행도: **+{free_lv} {LEVELS[free_lv]['name']}** (최고 +{free_p['max_level']})\n\n"
            f"적용 운세: **{free_p['blessing']['name']}**"
        )
        if st.button("🎮 자유 모드 입장하기", type="primary", use_container_width=True):
            st.session_state.mode = "free"
            st.session_state.started = True
            st.rerun()

    with mode_c2:
        if DB["hall_of_fame"]:
            top1 = DB["hall_of_fame"][0]
            best_str = f"전체 1위: **{top1['name']} ({top1['total']}회)**"
        else:
            best_str = "아직 명예의 전당 기록 없음"

        st.warning(
            f"**🏆 +15 최소 행동 도전**\n\n"
            f"내 진행도: **+{chal_lv}** · {best_str}\n\n"
            f"적용 운세: **{chal_p['blessing']['name']}**"
        )
        if st.button("🏆 +15 도전 모드 입장하기", type="primary", use_container_width=True):
            st.session_state.mode = "challenge"
            st.session_state.started = True
            st.rerun()

    st.stop()

# ==========================================
# [화면 2] 메인 인게임 화면
# ==========================================
P = USER_DATA["profiles"][st.session_state.mode]
is_challenge_mode = (st.session_state.mode == "challenge")
blessing = P.get("blessing", BLESSINGS[0])

# 8. 계산 유틸리티 함수 (오늘의 돌 운세 버프 반영)
def get_click_gold():
    base_by_lv = 10 * (1.42 ** P["level"])
    mult = 1.0 + (P["upg"]["goldClick"] * 0.20)
    if blessing["id"] == "gold_rush":
        mult *= 1.50
    return int(base_by_lv * mult)

def get_bonus_gold():
    if P["upg"]["autoGold"] == 0:
        return 0
    return int(get_click_gold() * (P["upg"]["autoGold"] * 0.10))

def get_enhance_cost(lv=None):
    if lv is None:
        lv = P["level"]
    if lv >= 20:
        return 0
    base = LEVELS[lv]["cost"]
    discount = P["upg"]["discount"] * 0.02
    if blessing["id"] == "cheap_enh":
        discount += 0.10
    return max(1, int(base * max(0.1, 1.0 - discount)))

def get_probabilities(apply_scroll=False, lv=None):
    if lv is None:
        lv = P["level"]
    if lv >= 20:
        return 0.0, 0.0, 0.0, 0.0
    if P["fever"] >= 100.0:
        return 100.0, 0.0, 0.0, 0.0

    base = LEVELS[lv]
    scroll_bonus = 10.0 if apply_scroll else 0.0
    blessing_bonus = 3.0 if blessing["id"] == "lucky_star" else 0.0

    succ = min(100.0, base["succ"] + P["upg"]["addSucc"] * 0.5 + scroll_bonus + blessing_bonus)
    dest = max(0.0, base["dest"] - P["upg"]["lessDest"] * 1.0) if base["dest"] > 0 else 0.0
    down = max(0.0, base["down"] - P["upg"]["lessDown"] * 1.0) if base["down"] > 0 else 0.0

    keep = 100.0 - (succ + down + dest)
    if keep < 0:
        down = max(0.0, down + keep)
        keep = 0.0
        if succ + down + dest > 100.0:
            dest = max(0.0, 100.0 - succ - down)

    return round(succ, 1), round(keep, 1), round(down, 1), round(dest, 1)

def get_sell_rewards(lv=None):
    if lv is None:
        lv = P["level"]
    if lv < 5:
        return 0, 0
    sell_gold = int(LEVELS[lv]["cost"] * 1.8)
    sell_shards = max(1, int(LEVELS[lv]["shard"] * 0.7))
    return sell_gold, sell_shards

def get_upg_cost(u):
    return int(u["base"] * (u["mult"] ** P["upg"][u["id"]]))

def add_log(entry: str):
    P["logs"].insert(0, entry)
    if len(P["logs"]) > 12:
        P["logs"] = P["logs"][:12]

def get_rank_grade(total_actions):
    if total_actions <= 45:
        return "S+", "신들린 운빨과 완벽한 자원 관리! 전설의 대장장이", "#f43f5e"
    elif total_actions <= 65:
        return "S", "군더더기 없는 깔끔한 최상위권 클리어!", "#eab308"
    elif total_actions <= 90:
        return "A", "안정적인 확률 계산이 돋보이는 우수 기록!", "#3b82f6"
    elif total_actions <= 125:
        return "B", "무난하게 목표를 완수한 준수한 성적입니다.", "#10b981"
    else:
        return "C", "수많은 시련과 파괴를 이겨낸 불굴의 의지!", "#94a3b8"

def check_challenge_clear():
    if is_challenge_mode and P["level"] >= CHALLENGE_GOAL and not P["cleared"]:
        P["cleared"] = True
        total_act = P["mine_actions"] + P["enh_actions"]
        grade, _, _ = get_rank_grade(total_act)

        DB["hall_of_fame"].append({
            "name": USER_ID,
            "total": total_act,
            "mine": P["mine_actions"],
            "enh": P["enh_actions"],
            "destroy": P["destroy_count"],
            "gold": P["spent_gold"],
            "grade": grade,
        })
        DB["hall_of_fame"].sort(key=lambda r: (r["total"], r["destroy"], r["gold"]))
        st.balloons()

# 단일 강화 처리 함수
def execute_single_enhance(want_shield, want_scroll):
    lv = P["level"]
    cost = get_enhance_cost(lv)
    if lv >= 20 or P["gold"] < cost:
        return "no_gold", 0

    P["gold"] -= cost
    P["spent_gold"] += cost
    P["enh_actions"] += 1

    is_fever = P["fever"] >= 100.0
    base_dest = LEVELS[lv]["dest"]

    used_shield = False
    if want_shield and P["shields"] > 0 and base_dest > 0 and not is_fever:
        P["shields"] -= 1
        used_shield = True

    used_scroll = False
    if want_scroll and P["scrolls"] > 0 and not is_fever:
        P["scrolls"] -= 1
        used_scroll = True

    succ_p, keep_p, down_p, _ = get_probabilities(apply_scroll=used_scroll, lv=lv)
    roll = random.uniform(0, 100)
    fever_mult = 1.0 + (P["upg"]["feverBoost"] * 0.05)
    if blessing["id"] == "rage_fire":
        fever_mult *= 1.25

    if is_fever or roll < succ_p:
        if is_fever:
            P["fever"] = 0.0
        P["level"] += 1
        P["max_level"] = max(P["max_level"], P["level"])
        if P["level"] not in P["unlocked"]:
            P["unlocked"].append(P["level"])
        add_log(f"🟢 +{lv} → +{P['level']} 강화 성공! {'(🔥피버)' if is_fever else ''}")
        check_challenge_clear()
        return "success", cost

    elif roll < succ_p + keep_p:
        P["fever"] = min(100.0, P["fever"] + 10.0 * fever_mult)
        add_log(f"⚪ +{lv} → +{lv} 등급 유지")
        return "keep", cost

    elif roll < succ_p + keep_p + down_p:
        P["fever"] = min(100.0, P["fever"] + 20.0 * fever_mult)
        P["level"] = max(0, P["level"] - 1)
        add_log(f"🟠 +{lv} → +{P['level']} 등급 하락")
        return "down", cost

    else:
        if used_shield:
            P["fever"] = min(100.0, P["fever"] + 20.0 * fever_mult)
            add_log(f"🛡️ +{lv} 파괴 방어 성공! (방지권 소모)")
            return "shielded", cost
        else:
            gained_shards = LEVELS[lv]["shard"]
            P["shards"] += gained_shards
            P["fever"] = min(100.0, P["fever"] + 40.0 * fever_mult)
            P["level"] = 0
            P["destroy_count"] += 1
            add_log(f"💥 +{lv} 돌 파괴! (파편 +{gained_shards:,}개 획득)")
            return "destroy", gained_shards

# 9. 상단 유저 상태 바 & 모드 전환 바
u_bar1, u_bar2 = st.columns([3, 1])
with u_bar1:
    st.caption(f"👤 **{USER_ID}** · ✨ **{blessing['name']}** ({blessing['desc']})")
with u_bar2:
    if st.button("🚪 로그아웃", key="ingame_logout", use_container_width=True):
        save_db(DB)
        st.session_state.current_user = None
        st.session_state.started = False
        st.rerun()

m_col0, m_col1, m_col2 = st.columns([0.75, 1.35, 1.6])
with m_col0:
    if st.button("🏠 타이틀", use_container_width=True):
        st.session_state.started = False
        st.rerun()

with m_col1:
    if st.button(
        "🎮 자유 모드 (+20)",
        type="primary" if not is_challenge_mode else "secondary",
        use_container_width=True
    ):
        st.session_state.mode = "free"
        st.rerun()

with m_col2:
    best_tag = f" (1위: {DB['hall_of_fame'][0]['total']}회)" if DB["hall_of_fame"] else ""
    if st.button(
        f"🏆 +15 도전{best_tag}",
        type="primary" if is_challenge_mode else "secondary",
        use_container_width=True
    ):
        st.session_state.mode = "challenge"
        st.rerun()

# 10. 도전 모드 전용 현황판 & 클리어 성적표
if is_challenge_mode:
    total_actions = P["mine_actions"] + P["enh_actions"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚡ 총 행동 수", f"{total_actions} 회")
    c2.metric("⛏️ 채굴 횟수", f"{P['mine_actions']} 회")
    c3.metric("🔨 강화 횟수", f"{P['enh_actions']} 회")
    c4.metric("💥 파괴 횟수", f"{P['destroy_count']} 회")

    if P["cleared"]:
        grade, comment, g_color = get_rank_grade(total_actions)
        my_rank = next(
            (i + 1 for i, r in enumerate(DB["hall_of_fame"])
             if r["name"] == USER_ID and r["total"] == total_actions and r["gold"] == P["spent_gold"]),
            1
        )
        rank_badge = f"현재 전체 {my_rank}위!" if my_rank <= 5 else f"전체 {my_rank}위"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #241914, #0f131c); border: 2px solid {g_color}; border-radius: 18px; padding: 20px; margin: 12px 0; text-align: center; box-shadow: 0 0 28px {g_color}33;">
            <div style="font-size: 13px; color: #d6b88c; font-weight: 700;">🏆 [{USER_ID}] +15 도전 클리어 성적표 · {rank_badge}</div>
            <div style="font-size: 52px; font-weight: 900; color: {g_color}; line-height: 1.2; margin: 6px 0;">RANK {grade}</div>
            <div style="font-size: 18px; font-weight: 800; color: #fef3c7;">최종 기록: 총 {total_actions}회 행동</div>
            <div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">{comment}</div>
            <hr style="border-color: #334155; margin: 12px 0;">
            <div style="font-size: 12px; color: #94a3b8;">
                채굴 {P['mine_actions']}회 · 강화 {P['enh_actions']}회 · 파괴 {P['destroy_count']}회 · 누적 소모 {P['spent_gold']:,} G
            </div>
        </div>
        """, unsafe_allow_html=True)

        sc_col1, sc_col2 = st.columns([1.6, 1.4])
        with sc_col1:
            st.code(f"[{USER_ID}] 돌 강화 +15 도전 | RANK {grade} | 총 {total_actions}회", language=None)
        with sc_col2:
            if st.button("🔁 새 운세로 기록 경신 재도전", type="primary", use_container_width=True):
                USER_DATA["profiles"]["challenge"] = create_fresh_profile(True)
                save_db(DB)
                st.rerun()

# 11. 다크 판타지 대장간 돌 카드 & 등급별 발광/부유 애니메이션 CSS
cur_stone = LEVELS[P["level"]]
lv_now = P["level"]

if lv_now >= 15:
    tier_badge = "🔥 MYTHIC FORGE · 초월 등급"
    glow_spread = 36 + (lv_now - 15) * 4
    anim_duration = "2.1s"
    icon_size = "74px"
    border_w = "2.5px"
elif lv_now >= 10:
    tier_badge = "🔮 ARCANE FORGE · 마력 등급"
    glow_spread = 24 + (lv_now - 10) * 2.5
    anim_duration = "2.6s"
    icon_size = "70px"
    border_w = "2px"
elif lv_now >= 5:
    tier_badge = "💎 JEWEL FORGE · 보석 등급"
    glow_spread = 16 + (lv_now - 5) * 2
    anim_duration = "3.2s"
    icon_size = "66px"
    border_w = "2px"
else:
    tier_badge = "⚒️ IRON FORGE · 원석 등급"
    glow_spread = 10 + lv_now * 1.5
    anim_duration = "3.8s"
    icon_size = "62px"
    border_w = "1.5px"

st.markdown(f"""
<style>
@keyframes forgeFloat {{
    0%, 100% {{
        transform: translateY(0px) scale(1);
    }}
    50% {{
        transform: translateY(-7px) scale(1.04);
    }}
}}

@keyframes forgePulse {{
    0%, 100% {{
        box-shadow:
            0 0 {glow_spread}px {cur_stone['color']}44,
            inset 0 0 22px {cur_stone['color']}22,
            0 12px 28px rgba(0, 0, 0, 0.55);
    }}
    50% {{
        box-shadow:
            0 0 {int(glow_spread * 1.35)}px {cur_stone['color']}77,
            inset 0 0 34px {cur_stone['color']}38,
            0 14px 34px rgba(0, 0, 0, 0.65);
    }}
}}

.forge-stone-card {{
    position: relative;
    background:
        radial-gradient(circle at 50% 35%, {cur_stone['color']}36 0%, rgba(24, 20, 26, 0.92) 58%, rgba(11, 13, 19, 0.98) 100%);
    border: {border_w} solid {cur_stone['color']};
    border-radius: 22px;
    padding: 22px 18px 24px 18px;
    text-align: center;
    margin: 8px 0 14px 0;
    animation: forgePulse {anim_duration} ease-in-out infinite;
    overflow: hidden;
}}

.forge-tier-pill {{
    display: inline-block;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #fef3c7;
    background: rgba(15, 18, 27, 0.78);
    border: 1px solid {cur_stone['color']}88;
    border-radius: 999px;
    padding: 3px 12px;
    margin-bottom: 10px;
}}

.forge-stone-icon {{
    font-size: {icon_size};
    line-height: 1.15;
    margin: 4px 0 8px 0;
    display: inline-block;
    filter: drop-shadow(0 0 {max(8, int(glow_spread * 0.45))}px {cur_stone['color']}99);
    animation: forgeFloat {anim_duration} ease-in-out infinite;
}}

.forge-stone-title {{
    font-size: 22px;
    font-weight: 900;
    color: {cur_stone['color']};
    text-shadow: 0 2px 12px {cur_stone['color']}55;
    margin-top: 2px;
}}

.forge-stone-sub {{
    font-size: 12px;
    color: #cbd5e1;
    margin-top: 4px;
    opacity: 0.88;
}}
</style>
""", unsafe_allow_html=True)

# 12. 상단 재화 대시보드
col1, col2, col3 = st.columns(3)
col1.metric("💰 보유 골드", f"{P['gold']:,} G")
col2.metric("🔮 돌 파편", f"{P['shards']:,} 개")
goal_label = f"+{P['max_level']} / +{CHALLENGE_GOAL}" if is_challenge_mode else f"+{P['max_level']}"
col3.metric("🎯 달성 현황", goal_label)

# 13. 메인 돌 스테이지 (다크 판타지 대장간 카드)
st.markdown(f"""
<div class="forge-stone-card">
    <div class="forge-tier-pill">{tier_badge}</div><br>
    <div class="forge-stone-icon">{cur_stone['icon']}</div>
    <div class="forge-stone-title">+{lv_now} {cur_stone['name']}</div>
    <div class="forge-stone-sub">최고 도달: +{P['max_level']} · 누적 파괴: {P['destroy_count']}회</div>
</div>
""", unsafe_allow_html=True)

# 최근 결과 알림 배너
msg_type, msg_text = P["last_msg"]
if msg_type == "success":
    st.success(msg_text)
elif msg_type == "warning":
    st.warning(msg_text)
elif msg_type == "error":
    st.error(msg_text)
else:
    st.info(msg_text)

# 보조 아이템 사용 체크박스 UI
is_fever = P["fever"] >= 100.0
base_dest_now = LEVELS[P["level"]]["dest"] if P["level"] < 20 else 0.0
locked_by_clear = is_challenge_mode and P["cleared"]

if P["shields"] == 0:
    P["use_shield"] = False
if P["scrolls"] == 0 or P["level"] >= 20:
    P["use_scroll"] = False

item_col1, item_col2 = st.columns(2)
with item_col1:
    P["use_shield"] = st.checkbox(
        f"🛡️ 파괴 방지권 사용 (보유: {P['shields']}개)",
        value=P["use_shield"],
        disabled=(P["shields"] == 0 or P["level"] >= 20 or locked_by_clear),
        help="체크해 두면 +10 이상 구간 강화 시 파괴를 자동으로 방어합니다."
    )
with item_col2:
    P["use_scroll"] = st.checkbox(
        f"🍀 행운의 주문서 사용 (보유: {P['scrolls']}개)",
        value=P["use_scroll"],
        disabled=(P["scrolls"] == 0 or P["level"] >= 20 or locked_by_clear),
        help="체크해 두면 강화 시도마다 성공 확률을 +10% 올려줍니다. (피버 시 미소모)"
    )

# 확률 정보 표시
apply_scroll_preview = P["use_scroll"] and not is_fever
apply_shield_preview = P["use_shield"] and base_dest_now > 0 and not is_fever

succ_p, keep_p, down_p, dest_p = get_probabilities(apply_scroll=apply_scroll_preview)
if P["level"] < 20:
    p1, p2, p3, p4 = st.columns(4)
    succ_bonus_tag = " (+10%)" if apply_scroll_preview else ""
    dest_display = f"~~{dest_p}%~~ **0%**" if apply_shield_preview else f"{dest_p}%"

    p1.markdown(f"**🟢 성공{succ_bonus_tag}**\n#### {succ_p}%")
    p2.markdown(f"**⚪ 유지**\n#### {keep_p}%")
    p3.markdown(f"**🟠 하락**\n#### {down_p}%")
    p4.markdown(f"**🔴 파괴**\n#### {dest_display}")
else:
    st.success("🌌 최종 등급 +20 태초의 절대석에 도달했습니다!")

# 피버 게이지
fever_val = min(100, int(P["fever"]))
st.caption(f"🔥 **피버 게이지: {fever_val}%** (100% 도달 시 다음 강화 무조건 성공!)")
st.progress(fever_val / 100.0)

# 14. 수동 액션 버튼 (1회 채굴 / 10연속 채굴 / 1회 강화)
btn_col1, btn_col2, btn_col3 = st.columns([1.05, 1.15, 1.3])
click_gain = get_click_gold() + get_bonus_gold()
bulk_gain = click_gain * 10
enh_cost = get_enhance_cost()

with btn_col1:
    if st.button(f"⛏️ 1회 채굴\n(+{click_gain:,} G)", disabled=locked_by_clear, use_container_width=True):
        P["gold"] += click_gain
        P["mine_actions"] += 1
        P["last_msg"] = ["info", f"채굴 완료! +{click_gain:,} G를 획득했습니다."]
        save_db(DB)
        st.rerun()

with btn_col2:
    if st.button(f"⚒️ 10연속 채굴\n(+{bulk_gain:,} G)", disabled=locked_by_clear, use_container_width=True):
        P["gold"] += bulk_gain
        P["mine_actions"] += 10
        P["last_msg"] = ["info", f"⚡ 10연속 대량 채굴 완료! +{bulk_gain:,} G를 한 번에 획득했습니다."]
        save_db(DB)
        st.rerun()

with btn_col3:
    btn_label = f"🔥 [확정] 강화\n({enh_cost:,} G)" if is_fever else f"🔨 1회 강화\n({enh_cost:,} G)"
    can_enhance = (P["level"] < 20) and (P["gold"] >= enh_cost) and (not locked_by_clear)

    if st.button(btn_label, type="primary", disabled=not can_enhance, use_container_width=True):
        with st.spinner("모루 위에 망치를 내리치는 중..."):
            time.sleep(0.18)

        res, val = execute_single_enhance(P["use_shield"], P["use_scroll"])
        if res == "success":
            P["last_msg"] = ["success", f"✨ 강화 성공! +{P['level']} {LEVELS[P['level']]['name']} 달성!"]
            if P["level"] in (5, 10, 15, 20) and not P["cleared"]:
                st.balloons()
        elif res == "keep":
            P["last_msg"] = ["info", "💨 강화 실패... 다행히 등급이 유지되었습니다."]
        elif res == "down":
            P["last_msg"] = ["warning", f"⬇️ 강화 실패! 등급이 +{P['level']}로 하락했습니다."]
        elif res == "shielded":
            P["last_msg"] = ["warning", "🛡️ 파괴 방지권이 발동하여 돌이 깨지지 않고 등급이 유지되었습니다!"]
        elif res == "destroy":
            P["last_msg"] = ["error", f"💥 돌이 파괴되었습니다! 돌 파편 +{val:,}개를 획득했습니다."]

        save_db(DB)
        st.rerun()

# 15. 돌 팔기(익절 정산) & 목표 등급 자동 연속 강화 섹션
if not locked_by_clear:
    if P["level"] >= 5:
        s_gold, s_shards = get_sell_rewards()
        sell_c1, sell_c2 = st.columns([2, 1.3])
        with sell_c1:
            st.caption(f"💎 **돌 안전 익절 판매 (+5 이상 가능):** 현재 돌을 팔면 파괴 위험 없이 **+{s_gold:,} G**와 **파편 +{s_shards:,}개**를 정산받고 `+0`부터 다시 시작합니다.")
        with sell_c2:
            if st.button(f"💰 현재 돌 팔기 (+{s_gold:,}G / +{s_shards}🔮)", use_container_width=True):
                old_lv = P["level"]
                P["gold"] += s_gold
                P["shards"] += s_shards
                P["level"] = 0
                add_log(f"💰 +{old_lv} 돌 판매 정산 (+{s_gold:,} G, 파편 +{s_shards:,}개)")
                P["last_msg"] = ["success", f"💰 +{old_lv} 돌을 성공적으로 판매하여 {s_gold:,} G와 파편 {s_shards:,}개를 정산받았습니다!"]
                save_db(DB)
                st.rerun()

    max_target_lv = CHALLENGE_GOAL if is_challenge_mode else 20
    if P["level"] < max_target_lv:
        st.markdown("##### ⚡ 목표 등급 자동 연속 강화")
        auto_col1, auto_col2 = st.columns([1.2, 2])
        target_options = list(range(P["level"] + 1, max_target_lv + 1))
        default_idx = len(target_options) - 1 if is_challenge_mode else min(len(target_options) - 1, max(0, 9 - P["level"]))

        with auto_col1:
            target_lv = st.selectbox(
                "목표 등급",
                options=target_options,
                index=default_idx,
                format_func=lambda x: f"+{x} ({LEVELS[x]['name']})",
                label_visibility="collapsed"
            )

        with auto_col2:
            if st.button(f"⚡ +{target_lv} 도달까지 연속 강화 시작", disabled=not can_enhance, use_container_width=True):
                attempts = 0
                spent_gold_run = 0
                stop_reason = ""
                gained_shards_total = 0

                while attempts < 500:
                    if P["level"] >= target_lv:
                        stop_reason = "goal"
                        break

                    next_cost = get_enhance_cost()
                    if P["gold"] < next_cost:
                        stop_reason = "no_gold"
                        break

                    res, val = execute_single_enhance(P["use_shield"], P["use_scroll"])
                    attempts += 1

                    if res == "destroy":
                        gained_shards_total += val
                        stop_reason = "destroy"
                        break
                    else:
                        spent_gold_run += val

                if stop_reason == "goal":
                    P["last_msg"] = [
                        "success",
                        f"🎉 [자동 강화 완료] 총 {attempts}회 시도 끝에 목표 +{target_lv} 달성! (소모 골드: {spent_gold_run:,} G)"
                    ]
                    if target_lv in (5, 10, 15, 20) and not P["cleared"]:
                        st.balloons()
                elif stop_reason == "destroy":
                    P["last_msg"] = [
                        "error",
                        f"💥 [자동 강화 중단] {attempts}회째에 돌이 파괴되어 중단되었습니다! (획득 파편: +{gained_shards_total:,}개)"
                    ]
                elif stop_reason == "no_gold":
                    P["last_msg"] = [
                        "warning",
                        f"💸 [자동 강화 중단] 골드가 부족하여 +{P['level']}에서 멈췄습니다. (총 {attempts}회 시도 / {spent_gold_run:,} G 소모)"
                    ]
                else:
                    P["last_msg"] = [
                        "info",
                        f"⏸️ 500회 연속 시도 제한에 도달해 일시 정지했습니다. (현재 +{P['level']})"
                    ]

                save_db(DB)
                st.rerun()

# 실시간 강화 히스토리 로그 (최근 12건)
if P["logs"]:
    with st.expander(f"📜 실시간 강화 히스토리 로그 (최근 {len(P['logs'])}건)", expanded=False):
        for lg in P["logs"]:
            st.markdown(f"- {lg}")

st.divider()

# 16. 하단 탭 (골드 상점 / 파편 연구소 / 도감 / 통합 명예의 전당 / 게임 가이드)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🛒 골드 상점",
    "🔮 파편 연구소",
    f"📖 도감 ({len(P['unlocked'])}/21)",
    "🏅 명예의 전당",
    "📘 게임 가이드"
])

with tab1:
    s_col1, s_col2, s_col3 = st.columns([2.2, 1, 1.1])
    with s_col1:
        st.markdown(f"**🛡️ 파괴 방지권** `(보유: {P['shields']}개)`  \n<small>+10 이상 강화 실패로 돌이 파괴될 때 1회 방어합니다.</small>", unsafe_allow_html=True)
    with s_col2:
        if st.button(f"1개 구매\n({SHIELD_COST:,} G)", key="buy_shield_1", disabled=P["gold"] < SHIELD_COST or locked_by_clear, use_container_width=True):
            P["gold"] -= SHIELD_COST
            P["shields"] += 1
            save_db(DB)
            st.toast("🛡️ 파괴 방지권 1개를 구매했습니다!")
            st.rerun()
    with s_col3:
        shield_10_cost = SHIELD_COST * 10
        if st.button(f"10개 구매\n({shield_10_cost:,} G)", key="buy_shield_10", disabled=P["gold"] < shield_10_cost or locked_by_clear, use_container_width=True):
            P["gold"] -= shield_10_cost
            P["shields"] += 10
            save_db(DB)
            st.toast("🛡️ 파괴 방지권 10개를 한 번에 구매했습니다!")
            st.rerun()

    st.markdown("---")

    c_col1, c_col2, c_col3 = st.columns([2.2, 1, 1.1])
    with c_col1:
        st.markdown(f"**🍀 행운의 주문서** `(보유: {P['scrolls']}개)`  \n<small>강화 시도 시 1회성으로 성공 확률을 +10% 올려줍니다.</small>", unsafe_allow_html=True)
    with c_col2:
        if st.button(f"1개 구매\n({SCROLL_COST:,} G)", key="buy_scroll_1", disabled=P["gold"] < SCROLL_COST or locked_by_clear, use_container_width=True):
            P["gold"] -= SCROLL_COST
            P["scrolls"] += 1
            save_db(DB)
            st.toast("🍀 행운의 주문서 1개를 구매했습니다!")
            st.rerun()
    with c_col3:
        scroll_10_cost = SCROLL_COST * 10
        if st.button(f"10개 구매\n({scroll_10_cost:,} G)", key="buy_scroll_10", disabled=P["gold"] < scroll_10_cost or locked_by_clear, use_container_width=True):
            P["gold"] -= scroll_10_cost
            P["scrolls"] += 10
            save_db(DB)
            st.toast("🍀 행운의 주문서 10개를 한 번에 구매했습니다!")
            st.rerun()

with tab2:
    for u in UPGRADES:
        lv = P["upg"][u["id"]]
        is_max = lv >= u["max"]
        cost = get_upg_cost(u)

        u_col1, u_col2, u_col3 = st.columns([2.5, 1, 1])
        with u_col1:
            st.markdown(f"**{u['name']}** `Lv.{lv}/{u['max']}`  \n<small>{u['desc']}</small>", unsafe_allow_html=True)
        with u_col2:
            if st.button("MAX" if is_max else f"+1 Lv\n🔮 {cost:,}", key=f"btn1_{USER_ID}_{st.session_state.mode}_{u['id']}", disabled=is_max or P["shards"] < cost or locked_by_clear, use_container_width=True):
                P["shards"] -= cost
                P["upg"][u["id"]] += 1
                save_db(DB)
                st.toast(f"{u['name']} Lv.{lv + 1} 강화 완료!")
                st.rerun()
        with u_col3:
            if st.button("MAX" if is_max else "최대 +5Lv\n일괄 강화", key=f"btn5_{USER_ID}_{st.session_state.mode}_{u['id']}", disabled=is_max or P["shards"] < cost or locked_by_clear, use_container_width=True):
                upgraded_cnt = 0
                for _ in range(5):
                    if P["upg"][u["id"]] >= u["max"]:
                        break
                    c_now = get_upg_cost(u)
                    if P["shards"] < c_now:
                        break
                    P["shards"] -= c_now
                    P["upg"][u["id"]] += 1
                    upgraded_cnt += 1
                if upgraded_cnt > 0:
                    save_db(DB)
                    st.toast(f"⚡ {u['name']} +{upgraded_cnt}레벨 일괄 강화 완료!")
                    st.rerun()

    st.markdown("---")
    reset_label = "🔁 현재 도전 모드 초기화 (새 운세 뽑기)" if is_challenge_mode else "🔄 자유 모드 초기화 (새 운세 뽑기)"
    if st.button(reset_label, use_container_width=True):
        USER_DATA["profiles"][st.session_state.mode] = create_fresh_profile(is_challenge_mode)
        save_db(DB)
        st.rerun()

with tab3:
    cols = st.columns(3)
    for idx, item in enumerate(LEVELS):
        with cols[idx % 3]:
            if idx in P["unlocked"]:
                st.markdown(f"**+{idx}** {item['icon']}  \n{item['name']}")
            else:
                st.markdown(f"**+{idx}** ❓  \n<span style='color:#64748b'>미발견</span>", unsafe_allow_html=True)

with tab4:
    st.markdown("##### 🏆 [도전 모드] +15 최소 행동 TOP 5 순위표")
    if not DB["hall_of_fame"]:
        st.info("아직 도전 모드 클리어 기록이 없습니다. **[🏆 +15 도전]**을 클리어해 1위에 올라보세요!")
    else:
        medals = ["🥇 1위", "🥈 2위", "🥉 3위", "4위", "5위"]
        rank_rows = []
        for idx, rec in enumerate(DB["hall_of_fame"][:5]):
            rank_rows.append({
                "순위": medals[idx],
                "플레이어": rec["name"],
                "등급": f"RANK {rec['grade']}",
                "총 행동 수": f"{rec['total']}회",
                "채굴 / 강화": f"{rec['mine']} / {rec['enh']}",
                "파괴": f"{rec['destroy']}회",
            })
        st.table(rank_rows)

    st.markdown("---")
    st.markdown("##### 🎮 [자유 모드] 최고 등급 & 도감 TOP 5 순위표")
    free_rankings = []
    for u_name, u_rec in DB["users"].items():
        fp = u_rec["profiles"]["free"]
        free_rankings.append({
            "name": u_name,
            "max_lv": fp["max_level"],
            "cur_lv": fp["level"],
            "dex": len(fp["unlocked"]),
            "gold": fp["gold"],
        })
    free_rankings.sort(key=lambda x: (x["max_lv"], x["dex"], x["cur_lv"], x["gold"]), reverse=True)

    medals = ["🥇 1위", "🥈 2위", "🥉 3위", "4위", "5위"]
    free_rows = []
    for idx, fr in enumerate(free_rankings[:5]):
        free_rows.append({
            "순위": medals[idx],
            "플레이어": fr["name"],
            "최고 등급": f"+{fr['max_lv']} ({LEVELS[fr['max_lv']]['name']})",
            "현재 등급": f"+{fr['cur_lv']}",
            "도감": f"{fr['dex']}/21",
            "보유 골드": f"{fr['gold']:,} G",
        })
    st.table(free_rows)

with tab5:
    st.markdown("##### 📌 핵심 게임 규칙 요약")
    st.markdown("""
    - **영구 파일 저장 (`save_data.json`):** 로그인한 계정의 모든 진행도와 랭킹이 파일로 저장되어 재실행 후에도 유지됩니다.
    - **✨ 오늘의 돌 운세:** 게임을 새로 시작하거나 초기화할 때마다 4가지 랜덤 축복 버프 중 하나가 부여됩니다.
    - **💰 돌 안전 익절 판매:** `+5` 이상 강화된 돌은 상단에 나타나는 **[현재 돌 팔기]** 버튼을 눌러 골드와 파편으로 안전하게 정산할 수 있습니다.
    - **🔥 피버 게이지 (천장 시스템):** 강화 실패 시 게이지가 충전되며(**유지 +10% / 하락 +20% / 파괴 +40%**), **100%**에 도달하면 다음 강화 1회가 **무조건 성공**합니다.
    - **🏆 도전 모드 행동 계산:** `1회 채굴 = +1행동`, `10연속 채굴 = +10행동`, `강화 1회 = +1행동`으로 합산됩니다.
    """)

    st.markdown("##### 🏆 도전 모드 (+15 달성) 랭크 커트라인")
    rank_table = [
        {"랭크": "S+", "총 행동 수 기준": "45회 이하", "평가 코멘트": "신들린 운빨과 완벽한 자원 관리! 전설의 대장장이"},
        {"랭크": "S",  "총 행동 수 기준": "46 ~ 65회", "평가 코멘트": "군더더기 없는 깔끔한 최상위권 클리어!"},
        {"랭크": "A",  "총 행동 수 기준": "66 ~ 90회", "평가 코멘트": "안정적인 확률 계산이 돋보이는 우수 기록!"},
        {"랭크": "B",  "총 행동 수 기준": "91 ~ 125회", "평가 코멘트": "무난하게 목표를 완수한 준수한 성적"},
        {"랭크": "C",  "총 행동 수 기준": "126회 이상", "평가 코멘트": "수많은 시련과 파괴를 이겨낸 불굴의 의지"},
    ]
    st.table(rank_table)

    st.markdown("##### 📊 +0 ~ +20 전체 강화 확률 및 비용표 (기본 수치)")
    guide_rows = []
    for lv in range(20):
        d = LEVELS[lv]
        guide_rows.append({
            "구간": f"+{lv} → +{lv+1}",
            "돌 이름": f"{d['icon']} {d['name']}",
            "기본 비용": f"{d['cost']:,} G",
            "성공": f"{d['succ']:.0f}%",
            "유지": f"{d['keep']:.0f}%",
            "하락": f"{d['down']:.0f}%",
            "파괴": f"{d['dest']:.0f}%",
            "파괴/익절 파편": f"{d['shard']:,}개" if d["shard"] > 0 else "-"
        })
    st.dataframe(guide_rows, use_container_width=True, hide_index=True)