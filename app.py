import streamlit as st
import random
import math

def calc_display_stats(hp, atk, df, spd):
    display_hp = math.floor(hp * 4 + atk + df + spd)
    display_atk = math.floor(hp * 0.1 + atk + df * 0.1 + spd * 0.05)
    display_df = math.floor(hp * 0.1 + atk * 0.1 + df + spd * 0.05)
    display_spd = math.floor(spd)
    return (display_hp, display_atk, display_df, display_spd)

S_GRADE_STATS = {'공격력': 12, '방어력': 7, '순발력': 6, '체력': 52}
S_GROWTH_ATK = 2.41
S_GROWTH_DF  = 1.43
S_GROWTH_SPD = 1.21
S_GROWTH_HP  = 9.97
MAX_LEVEL = 140

def get_pet_rank_and_correction(hp_coef, atk_coef, df_coef, spd_coef):
    total = hp_coef + atk_coef + df_coef + spd_coef
    if total >= 100:
        correction = random.randint(450, 500)
    elif total >= 95:
        correction = random.randint(470, 520)
    elif total >= 90:
        correction = random.randint(490, 540)
    elif total >= 85:
        correction = random.randint(510, 560)
    elif total >= 80:
        correction = random.randint(530, 580)
    else:
        correction = random.randint(550, 600)
    return correction

class Pet:
    def __init__(self):
        self.level = 1
        self.hp_coef = 24
        self.atk_coef = 38
        self.df_coef = 16
        self.spd_coef = 20
        self.hp_growth = self.hp_coef + random.randint(-2, 2)
        self.atk_growth = self.atk_coef + random.randint(-2, 2)
        self.df_growth = self.df_coef + random.randint(-2, 2)
        self.spd_growth = self.spd_coef + random.randint(-2, 2)
        base_stats = [self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth]
        bonus_points = [0, 0, 0, 0]
        for _ in range(10):
            idx = random.randint(0, 3)
            bonus_points[idx] += 1
        self.base_stats = [base_stats[i] + bonus_points[i] for i in range(4)]
        self.init_coef = 26
        self.current_stats = [
            self.init_coef * self.base_stats[0] / 100,
            self.init_coef * self.base_stats[1] / 100,
            self.init_coef * self.base_stats[2] / 100,
            self.init_coef * self.base_stats[3] / 100,
        ]
        self.init_display_stats = list(calc_display_stats(*self.current_stats))
        self.last_display_stats = [0, 0, 0, 0]

    def s_grade_stat_at_level(self, lv):
        s_atk = math.floor(S_GRADE_STATS['공격력'] + S_GROWTH_ATK * (lv-1))
        s_df  = math.floor(S_GRADE_STATS['방어력'] + S_GROWTH_DF  * (lv-1))
        s_spd = math.floor(S_GRADE_STATS['순발력'] + S_GROWTH_SPD * (lv-1))
        s_hp  = math.floor(S_GRADE_STATS['체력'] + S_GROWTH_HP  * (lv-1))
        return s_hp, s_atk, s_df, s_spd

    def is_perfect_s_or_above(self):
        hp, atk, df, spd = calc_display_stats(*self.current_stats)
        return atk >= 12 and df >= 7 and spd >= 6 and hp >= 52 and self.level == 1

    def get_stats(self):
        return calc_display_stats(*self.current_stats)

    def levelup(self, up_count=1):
        for _ in range(up_count):
            if self.level >= MAX_LEVEL:
                break
            before = self.get_stats()
            base_growth = [self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth]
            a_bonus = [0, 0, 0, 0]
            for _ in range(10):
                idx = random.randint(0, 3)
                a_bonus[idx] += 1
            b = get_pet_rank_and_correction(self.hp_coef, self.atk_coef, self.df_coef, self.spd_coef)
            growth = [(base_growth[i] + a_bonus[i]) * b / 10000 for i in range(4)]
            self.current_stats = [self.current_stats[i] + growth[i] for i in range(4)]
            self.level += 1
            after = self.get_stats()
            self.last_display_stats = [
                after[0] - before[0],
                after[1] - before[1],
                after[2] - before[2],
                after[3] - before[3]
            ]

    def get_growth(self):
        hp, atk, df, spd = self.get_stats()
        hp0, atk0, df0, spd0 = self.init_display_stats
        lv = self.level
        if lv > 1:
            atk_g = (atk - atk0) / (lv-1)
            df_g  = (df  - df0 ) / (lv-1)
            spd_g = (spd - spd0) / (lv-1)
            hp_g  = (hp  - hp0 ) / (lv-1)
            total_g = atk_g + df_g + spd_g
            return atk_g, df_g, spd_g, hp_g, total_g
        else:
            return None

    def get_base_growths(self):
        return self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth

# ---- Streamlit UI ----
st.set_page_config(page_title="코로몬키우기", layout="centered")
st.markdown("<h2 style='text-align:center; margin-bottom:6px;'>코로몬키우기</h2>", unsafe_allow_html=True)

if "pet" not in st.session_state:
    st.session_state.pet = Pet()
pet = st.session_state.pet

# 상단 알림
if pet.is_perfect_s_or_above():
    st.markdown("<div style='color:#FF3333; text-align:center; font-weight:bold;'>*정석이 출현했습니다!!!*</div>", unsafe_allow_html=True)

# 모바일 최적화 1열
col1, = st.columns([1])
with col1:
    st.image("pet.png", width=120)

# 능력치 테이블로 한 번에!
cur_hp, cur_atk, cur_df, cur_spd = pet.get_stats()
s_hp, s_atk, s_df, s_spd = pet.s_grade_stat_at_level(pet.level)

def stat_color(val):
    if val == 0:
        return "cyan"
    elif val > 0:
        return "lime"
    else:
        return "red"
def stat_line(label, cur, s):
    diff = cur - s
    return f"<tr><td>{label}</td><td><b>{cur}</b></td><td><span style='color:{stat_color(diff)}'>({diff:+})</span></td></tr>"

stat_table = (
    "<table style='width:100%; font-size:17px;'>"
    "<tr><th>능력</th><th>현재</th><th>S급대비</th></tr>"
    f"{stat_line('공격력', cur_atk, s_atk)}"
    f"{stat_line('방어력', cur_df, s_df)}"
    f"{stat_line('순발력', cur_spd, s_spd)}"
    f"{stat_line('체력', cur_hp, s_hp)}"
    "</table>"
)
st.markdown(stat_table, unsafe_allow_html=True)

if pet.level > 1:
    l_hp, l_atk, l_df, l_spd = pet.last_display_stats
    st.markdown(
        f"<div style='font-size:15px; text-align:center;'>"
        f"<b>직전 레벨업 변화량:</b> "
        f"<span style='color:{stat_color(l_atk)}'>공격력 {l_atk:+}</span>  "
        f"<span style='color:{stat_color(l_df)}'>방어력 {l_df:+}</span>  "
        f"<span style='color:{stat_color(l_spd)}'>순발력 {l_spd:+}</span>  "
        f"<span style='color:{stat_color(l_hp)}'>체력 {l_hp:+}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

growth = pet.get_growth()
if growth:
    atk_g, df_g, spd_g, hp_g, total_g = growth
    def srate_color(val, s):
        if val > s + 0.05:
            return "lime"
        elif abs(val - s) <= 0.05:
            return "orange"
        else:
            return "red"
    # 표로 요약!
    growth_table = (
        "<table style='width:100%; font-size:15px;'>"
        "<tr><th>능력</th><th>성장률</th><th>S급</th></tr>"
        f"<tr><td>공격력</td><td><span style='color:{srate_color(atk_g,S_GROWTH_ATK)}'>{atk_g:.2f}</span></td><td>{S_GROWTH_ATK:.2f}</td></tr>"
        f"<tr><td>방어력</td><td><span style='color:{srate_color(df_g,S_GROWTH_DF)}'>{df_g:.2f}</span></td><td>{S_GROWTH_DF:.2f}</td></tr>"
        f"<tr><td>순발력</td><td><span style='color:{srate_color(spd_g,S_GROWTH_SPD)}'>{spd_g:.2f}</span></td><td>{S_GROWTH_SPD:.2f}</td></tr>"
        f"<tr><td>체력</td><td><span style='color:{srate_color(hp_g,S_GROWTH_HP)}'>{hp_g:.2f}</span></td><td>{S_GROWTH_HP:.2f}</td></tr>"
        f"<tr><td><b>합계</b></td><td><span style='color:{srate_color(total_g,5.05)}'><b>{total_g:.2f}</b></span></td><td><b>5.05</b></td></tr>"
        "</table>"
    )
    st.markdown(growth_table, unsafe_allow_html=True)
else:
    st.markdown("<div style='font-size:14px;text-align:center;'>성장률: - (2레벨 이상부터 표시)</div>", unsafe_allow_html=True)

if pet.level == MAX_LEVEL:
    h, a, d, s = pet.get_base_growths()
    st.markdown(
        f"<div style='font-size:14px; text-align:center;'><b>초기 성장계수</b> (체력: {h}, 공격력: {a}, 방어력: {d}, 순발력: {s})</div>",
        unsafe_allow_html=True
    )

# 버튼을 2줄로 배치!
c1, c2 = st.columns(2)
with c1:
    if st.button("레벨업"):
        pet.levelup()
        st.rerun()
    if st.button("새로뽑기"):
        st.session_state.pet = Pet()
        st.rerun()
with c2:
    if st.button("10레벨업"):
        pet.levelup(up_count=10)
        st.rerun()
    if st.button("종료"):
        st.stop()
