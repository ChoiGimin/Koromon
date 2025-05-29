import streamlit as st
import random
import math

PET_LIST = [
    (1, "놀놀", 25, 29, 18, 29, 19),
    (2, "골골", 21, 30, 13, 28, 20),
    (3, "벨가", 24, 28, 16, 25, 25),  # [초기,공,방,순,체]
    (4, "베룰", 23, 21, 30, 13, 28),
    (5, "오가", 25, 26, 29, 20, 28),
    (6, "모가", 27, 23, 37, 25, 20),
    (7, "올곤", 26, 28, 30, 22, 22),
    (8, "골롯", 28, 23, 35, 21, 25),
]
PET_DIC = {pet[1]: pet for pet in PET_LIST}
PET_NAME_LIST = [pet[1] for pet in PET_LIST]
FIRST_PET = "벨가"
S_GROWTH_B = 495
PET_IMAGE_NUM = {pet[1]: f"{pet[0]}.gif" for pet in PET_LIST}
PET_BONUS = {"놀놀": 2.5, "골롯": 5.0}
S_GROWTH_TABLE = [
    ("S+", 0.02, float('inf'), 5),
    ("S", -0.02, 0.02, 4),
    ("A+", -0.4, -0.02, 3),
    ("A", -0.6, -0.4, 2.5),
    ("B+", -0.8, -0.6, 2),
    ("B", -1.2, -0.8, 1.5),
    ("애정", float('-inf'), -1.2, 1)
]

def get_growth_grade(total_g, s_total_g):
    diff = total_g - s_total_g
    for grade, min_diff, max_diff, mult in S_GROWTH_TABLE:
        if min_diff < diff <= max_diff:
            return grade, mult
    return "애정", 1

def pet_level_price(level):
    lv_block = (level - 1) // 20 + 1
    return min(lv_block, 7)

def display_stats(hp, atk, df, spd):
    # (체,공,방,순) -> (표기체력, 공격력, 방어력, 순발력)
    disp_hp  = math.floor(hp*4 + atk + df + spd)
    disp_atk = math.floor(hp*0.1 + atk + df*0.1 + spd*0.05)
    disp_df  = math.floor(hp*0.1 + atk*0.1 + df + spd*0.05)
    disp_spd = math.floor(spd)
    return disp_hp, disp_atk, disp_df, disp_spd

def calc_s_init_stats(petinfo):
    # [초기,공,방,순,체]
    initc, atk, df, spd, hp = petinfo[2:]
    # 각 능력치별 S급 초기치
    s_atk = initc * atk / 100
    s_df  = initc * df  / 100
    s_spd = initc * spd / 100
    s_hp  = initc * hp  / 100
    return s_hp, s_atk, s_df, s_spd

def calc_s_growth(petinfo):
    _, atk, df, spd, hp = petinfo[2:]
    # 성장계수+2.5 × 495 / 10000
    return [
        (hp  + 2.5) * S_GROWTH_B / 10000,   # 체
        (atk + 2.5) * S_GROWTH_B / 10000,   # 공
        (df  + 2.5) * S_GROWTH_B / 10000,   # 방
        (spd + 2.5) * S_GROWTH_B / 10000,   # 순
    ]

def calc_s_stats(petinfo, level):
    # S급 누적 실능력치(실수), 표기능력치(내림정수)
    s_hp, s_atk, s_df, s_spd = calc_s_init_stats(petinfo)
    h_g, a_g, d_g, s_g = calc_s_growth(petinfo)
    if level > 1:
        s_hp  += h_g * (level-1)
        s_atk += a_g * (level-1)
        s_df  += d_g * (level-1)
        s_spd += s_g * (level-1)
    return display_stats(s_hp, s_atk, s_df, s_spd)

class Pet:
    def __init__(self, name):
        petinfo = PET_DIC[name]
        self.idx = petinfo[0]
        self.name = name
        self.initc = petinfo[2]
        self.atk_coef = petinfo[3]
        self.df_coef = petinfo[4]
        self.spd_coef = petinfo[5]
        self.hp_coef = petinfo[6]
        self.level = 1
        self.growth_init()
    def growth_init(self):
        self.atk_growth = self.atk_coef + random.randint(-2, 2)
        self.df_growth  = self.df_coef  + random.randint(-2, 2)
        self.spd_growth = self.spd_coef + random.randint(-2, 2)
        self.hp_growth  = self.hp_coef  + random.randint(-2, 2)
        base_stats = [self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth]
        bonus_points = [0, 0, 0, 0]
        for _ in range(10):
            idx = random.randint(0, 3)
            bonus_points[idx] += 1
        self.base_stats = [base_stats[i] + bonus_points[i] for i in range(4)]
        # 순서: 체,공,방,순
        self.current_stats = [
            self.base_stats[0] * self.initc / 100,  # 체
            self.base_stats[1] * self.initc / 100,  # 공
            self.base_stats[2] * self.initc / 100,  # 방
            self.base_stats[3] * self.initc / 100,  # 순
        ]
        self.last_display_stats = [0, 0, 0, 0]
    def is_perfect_s_or_above(self):
        stats = self.get_stats()
        s_stats_now = calc_s_stats(PET_DIC[self.name], self.level)
        return stats == s_stats_now and self.level == 1
    def get_stats(self):
        return display_stats(*self.current_stats)
    def s_grade_stat_at_level(self, lv):
        return calc_s_stats(PET_DIC[self.name], lv)
    def s_init_stats(self):
        # S급 표기능력치(1레벨)
        return calc_s_stats(PET_DIC[self.name], 1)
    def levelup(self, up_count=1):
        MAX_LEVEL = 140
        for _ in range(up_count):
            if self.level >= MAX_LEVEL:
                break
            before = self.get_stats()
            base_growth = [
                self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth
            ]
            a_bonus = [0, 0, 0, 0]
            for _ in range(10):
                idx = random.randint(0, 3)
                a_bonus[idx] += 1
            b = S_GROWTH_B
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
        cur = self.get_stats()
        lv = self.level
        s_stats_1 = self.s_grade_stat_at_level(1)
        s_stats_cur = self.s_grade_stat_at_level(lv)
        if lv > 1:
            atk_g = (cur[1] - s_stats_1[1]) / (lv - 1)
            df_g  = (cur[2] - s_stats_1[2]) / (lv - 1)
            spd_g = (cur[3] - s_stats_1[3]) / (lv - 1)
            hp_g  = (cur[0] - s_stats_1[0]) / (lv - 1)
            total_g = atk_g + df_g + spd_g
            s_atk_g = (s_stats_cur[1] - s_stats_1[1]) / (lv - 1)
            s_df_g  = (s_stats_cur[2] - s_stats_1[2]) / (lv - 1)
            s_spd_g = (s_stats_cur[3] - s_stats_1[3]) / (lv - 1)
            s_hp_g  = (s_stats_cur[0] - s_stats_1[0]) / (lv - 1)
            s_total_g = s_atk_g + s_df_g + s_spd_g
            return atk_g, df_g, spd_g, hp_g, total_g, s_atk_g, s_df_g, s_spd_g, s_hp_g, s_total_g
        else:
            return None

if "money" not in st.session_state:
    st.session_state.money = 0
if "pet" not in st.session_state:
    st.session_state.pet = Pet(FIRST_PET)

st.set_page_config(page_title="석기시대 공룡키우기", layout="centered")
st.markdown(
    "<div style='font-weight:bold;font-size:17px;text-align:center;margin-bottom:10px;'>석기시대 공룡키우기</div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='position:absolute;top:15px;right:24px;font-size:21px;font-weight:bold;color:gold;'>"
    f"💰 {st.session_state.money} G"
    f"</div>",
    unsafe_allow_html=True
)
pet = st.session_state.pet

# ---- 이미지 + 능력치 ----
col_img, col_stat = st.columns([1, 2])
with col_img:
    st.image(PET_IMAGE_NUM[pet.name], width=100)
with col_stat:
    cur_hp, cur_atk, cur_df, cur_spd = pet.get_stats()
    s_hp, s_atk, s_df, s_spd = pet.s_grade_stat_at_level(pet.level)
    def stat_color(val):
        if val == 0:
            return "cyan"
        elif val > 0:
            return "lime"
        else:
            return "red"
    stat_table = (
        f"<div style='overflow-x:auto;'>"
        f"<table style='width:100%; font-size:17px; table-layout:fixed;'>"
        f"<tr><th>능력</th><th>현재(Lv{pet.level})</th><th>S급(Lv{pet.level})</th></tr>"
        f"<tr><td>체력</td>"
        f"<td>{cur_hp} <span style='color:{stat_color(cur_hp-s_hp)}'>({cur_hp-s_hp:+d})</span></td>"
        f"<td>{s_hp}</td></tr>"
        f"<tr><td>공격력</td>"
        f"<td>{cur_atk} <span style='color:{stat_color(cur_atk-s_atk)}'>({cur_atk-s_atk:+d})</span></td>"
        f"<td>{s_atk}</td></tr>"
        f"<tr><td>방어력</td>"
        f"<td>{cur_df} <span style='color:{stat_color(cur_df-s_df)}'>({cur_df-s_df:+d})</span></td>"
        f"<td>{s_df}</td></tr>"
        f"<tr><td>순발력</td>"
        f"<td>{cur_spd} <span style='color:{stat_color(cur_spd-s_spd)}'>({cur_spd-s_spd:+d})</span></td>"
        f"<td>{s_spd}</td></tr>"
        f"</table>"
        f"</div>"
    )
    st.markdown(stat_table, unsafe_allow_html=True)
    # S급 초기치/성장률
    s_hp_, s_atk_, s_df_, s_spd_ = calc_s_init_stats(PET_DIC[pet.name])
    h_g, a_g, d_g, s_g = calc_s_growth(PET_DIC[pet.name])
    st.markdown(
        f"<div style='font-size:13px; color:#888;'>"
        f"S급 초기치: 체력 {math.floor(s_hp_)} / 공격력 {math.floor(s_atk_)} / 방어력 {math.floor(s_df_)} / 순발력 {math.floor(s_spd_)}<br>"
        f"S급 성장률: 체력 {h_g:.2f} / 공격력 {a_g:.2f} / 방어력 {d_g:.2f} / 순발력 {s_g:.2f}"
        f"</div>",
        unsafe_allow_html=True
    )

# ---- 버튼(가로 4개) ----
growth = pet.get_growth()
if pet.level > 1 and growth:
    atk_g, df_g, spd_g, hp_g, total_g, s_atk_g, s_df_g, s_spd_g, s_hp_g, s_total_g = growth
    growth_grade, mult = get_growth_grade(total_g, s_total_g)
    base_money = pet_level_price(pet.level)
    bonus = PET_BONUS.get(pet.name, 1)
    sell_money = int(base_money * mult * bonus)
else:
    sell_money = pet_level_price(pet.level)

c1, c2, c3, c4 = st.columns(4)
alert_msg = None
with c1:
    if st.button("레벨업"):
        pet.levelup()
        st.rerun()
with c2:
    if st.button("10레벨업"):
        pet.levelup(up_count=10)
        st.rerun()
with c3:
    if st.button(f"판매 (예상 {sell_money}G)"):
        if pet.level > 1 and growth:
            atk_g, df_g, spd_g, hp_g, total_g, s_atk_g, s_df_g, s_spd_g, s_hp_g, s_total_g = growth
            growth_grade, mult = get_growth_grade(total_g, s_total_g)
            base_money = pet_level_price(pet.level)
            bonus = PET_BONUS.get(pet.name, 1)
            sell_money = int(base_money * mult * bonus)
        else:
            sell_money = pet_level_price(pet.level)
        st.session_state.money += sell_money
        alert_msg = f"{sell_money}골드를 획득합니다."
        st.session_state.pet = Pet(FIRST_PET)
        st.rerun()
with c4:
    if st.button("랜덤뽑기 (100G)"):
        if st.session_state.money < 100:
            alert_msg = "💸 골드가 부족합니다!"
        else:
            st.session_state.money -= 100
            random_pet = random.choice([name for name in PET_NAME_LIST if name != FIRST_PET])
            st.session_state.pet = Pet(random_pet)
            st.rerun()

# ---- 성장률 ----
growth = pet.get_growth()
if growth:
    atk_g, df_g, spd_g, hp_g, total_g, s_atk_g, s_df_g, s_spd_g, s_hp_g, s_total_g = growth
    growth_table = (
        "<div style='overflow-x:auto;'>"
        "<table style='width:100%; font-size:15px; table-layout:fixed;'>"
        "<tr><th>능력</th><th>내 성장률</th><th>S급 성장률</th></tr>"
        f"<tr><td>체력</td><td>{hp_g:.2f}</td><td>{s_hp_g:.2f}</td></tr>"
        f"<tr><td>공격력</td><td>{atk_g:.2f}</td><td>{s_atk_g:.2f}</td></tr>"
        f"<tr><td>방어력</td><td>{df_g:.2f}</td><td>{s_df_g:.2f}</td></tr>"
        f"<tr><td>순발력</td><td>{spd_g:.2f}</td><td>{s_spd_g:.2f}</td></tr>"
        f"<tr><td><b>합계</b></td><td><b>{total_g:.2f}</b></td><td><b>{s_total_g:.2f}</b></td></tr>"
        "</table></div>"
    )
    st.markdown(growth_table, unsafe_allow_html=True)
else:
    st.markdown("<div style='font-size:14px;text-align:center;'>성장률: - (2레벨 이상부터 표시)</div>", unsafe_allow_html=True)

if pet.level > 1:
    l_hp, l_atk, l_df, l_spd = pet.last_display_stats
    st.markdown(
        f"<div style='font-size:15px; text-align:center; margin-top:12px;'>"
        f"<b>직전 레벨업 변화량:</b> "
        f"<span style='color:{stat_color(l_hp)}'>체력 {l_hp:+d}</span>  "
        f"<span style='color:{stat_color(l_atk)}'>공격력 {l_atk:+d}</span>  "
        f"<span style='color:{stat_color(l_df)}'>방어력 {l_df:+d}</span>  "
        f"<span style='color:{stat_color(l_spd)}'>순발력 {l_spd:+d}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

if pet.is_perfect_s_or_above():
    st.toast("정석이 출현했습니다!!!")
if alert_msg:
    st.success(alert_msg)
