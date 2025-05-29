import streamlit as st
import random

# 펫 정보: (번호, 이름, 초기치계수, 공격, 방어, 순발, 체력)
PET_LIST = [
    (1, "놀놀", 25, 29, 18, 29, 19),
    (2, "골골", 21, 30, 13, 28, 20),
    (3, "벨가", 24, 28, 16, 25, 25),
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
MAX_LEVEL = 140

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

def pet_level_price(level):
    lv_block = (level - 1) // 20 + 1
    return min(lv_block, 7)

def stat_display_formula(hp, atk, df, spd):
    # 표기능력치 공식 (round, 실제 표기치)
    disp_atk = round(hp*0.1 + atk + df*0.1 + spd*0.05)
    disp_df  = round(hp*0.1 + atk*0.1 + df + spd*0.05)
    disp_spd = round(spd)
    disp_hp  = round(hp*4 + atk + df + spd)
    return disp_atk, disp_df, disp_spd, disp_hp  # 공,방,순,체

def s_grade_stat_array(petinfo):
    # S급 표기능력치(정수) 누적, 1~140까지 시뮬
    initc, atk, df, spd, hp = petinfo[2:]
    # S급 초기치 공식
    base_stats = [
        (hp  + 2.5) * initc / 100,
        (atk + 2.5) * initc / 100,
        (df  + 2.5) * initc / 100,
        (spd + 2.5) * initc / 100,
    ]  # 체,공,방,순
    # S급 성장 공식
    grow = [
        (hp  + 2.5) * S_GROWTH_B / 10000,
        (atk + 2.5) * S_GROWTH_B / 10000,
        (df  + 2.5) * S_GROWTH_B / 10000,
        (spd + 2.5) * S_GROWTH_B / 10000,
    ]  # 체,공,방,순
    s_arr = []
    for lv in range(1, MAX_LEVEL+1):
        stats = [base_stats[i] + grow[i]*(lv-1) for i in range(4)]
        # 표기 공식
        disp = stat_display_formula(stats[0], stats[1], stats[2], stats[3])  # 공,방,순,체
        s_arr.append(disp)  # (공,방,순,체)
    return s_arr

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
        # 랜덤 초기화
        self.atk_growth = self.atk_coef + random.randint(-2, 2)
        self.df_growth  = self.df_coef  + random.randint(-2, 2)
        self.spd_growth = self.spd_coef + random.randint(-2, 2)
        self.hp_growth  = self.hp_coef  + random.randint(-2, 2)
        base_stats = [
            self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth
        ]
        bonus_points = [0, 0, 0, 0]
        for _ in range(10):
            idx = random.randint(0, 3)
            bonus_points[idx] += 1
        stats = [base_stats[i] + bonus_points[i] for i in range(4)]
        self.stats_real = [
            stats[0] * self.initc / 100,  # hp
            stats[1] * self.initc / 100,  # atk
            stats[2] * self.initc / 100,  # df
            stats[3] * self.initc / 100,  # spd
        ]
        self.stats_history = [stat_display_formula(self.stats_real[0], self.stats_real[1], self.stats_real[2], self.stats_real[3])]
        self.last_display_stats = [0, 0, 0, 0]
    def get_stats_display(self):
        return self.stats_history[-1]
    def levelup(self, up_count=1):
        for _ in range(up_count):
            if self.level >= MAX_LEVEL:
                break
            before = self.stats_history[-1]
            base_growth = [
                self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth
            ]
            a_bonus = [0, 0, 0, 0]
            for _ in range(10):
                idx = random.randint(0, 3)
                a_bonus[idx] += 1
            b = S_GROWTH_B
            growth = [
                (base_growth[0] + a_bonus[0]) * b / 10000,  # hp
                (base_growth[1] + a_bonus[1]) * b / 10000,  # atk
                (base_growth[2] + a_bonus[2]) * b / 10000,  # df
                (base_growth[3] + a_bonus[3]) * b / 10000,  # spd
            ]
            for i in range(4):
                self.stats_real[i] += growth[i]
            after = stat_display_formula(self.stats_real[0], self.stats_real[1], self.stats_real[2], self.stats_real[3])
            self.stats_history.append(after)
            self.level += 1
            self.last_display_stats = [
                after[0] - before[0],
                after[1] - before[1],
                after[2] - before[2],
                after[3] - before[3]
            ]
    def get_growth(self, s_arr):
        lv = self.level
        my = self.stats_history[-1]
        if lv > 1:
            s_lv1 = s_arr[0]
            return tuple((my[i] - s_lv1[i]) / (lv - 1) for i in range(4))
        else:
            return (None, None, None, None)

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
st.markdown(
    f"<div style='position:absolute;top:55px;right:30px;font-size:13px;font-weight:bold;color:#aaa;'>"
    f"Lv.{st.session_state.pet.level}"
    f"</div>",
    unsafe_allow_html=True
)
pet = st.session_state.pet

# S급 표기능력치 배열(정수, 진짜 유저표와 완벽 일치)
s_arr = s_grade_stat_array(PET_DIC[pet.name])
s_lv1 = s_arr[0]
s_140 = s_arr[MAX_LEVEL-1]
s_growth = tuple((s_140[i] - s_lv1[i]) / (MAX_LEVEL-1) for i in range(4))

# ---- 이미지 + 능력치 ----
col_img, col_stat = st.columns([1, 2])
with col_img:
    st.image(PET_IMAGE_NUM[pet.name], width=100)
with col_stat:
    my_disp = pet.get_stats_display()
    s_disp = s_arr[pet.level-1]
    def stat_color(val):
        if val == 0:
            return "cyan"
        elif val > 0:
            return "lime"
        else:
            return "red"
    stat_table = (
        f"<div style='overflow-x:auto;'>"
        f"<table style='width:100%; font-size:13.2px; line-height:1.1; table-layout:fixed;'>"
        f"<tr style='height:22px;'><th style='font-size:12px;'>공격력</th>"
        f"<th style='font-size:12px;'>방어력</th>"
        f"<th style='font-size:12px;'>순발력</th>"
        f"<th style='font-size:12px;'>체력</th></tr>"
        f"<tr style='height:27px;'>"
        f"<td style='padding:2px'>{my_disp[0]} <span style='color:{stat_color(my_disp[0]-s_disp[0])}'>({my_disp[0]-s_disp[0]:+d})</span></td>"
        f"<td style='padding:2px'>{my_disp[1]} <span style='color:{stat_color(my_disp[1]-s_disp[1])}'>({my_disp[1]-s_disp[1]:+d})</span></td>"
        f"<td style='padding:2px'>{my_disp[2]} <span style='color:{stat_color(my_disp[2]-s_disp[2])}'>({my_disp[2]-s_disp[2]:+d})</span></td>"
        f"<td style='padding:2px'>{my_disp[3]} <span style='color:{stat_color(my_disp[3]-s_disp[3])}'>({my_disp[3]-s_disp[3]:+d})</span></td>"
        f"</tr>"
        f"<tr style='height:18px;'><td style='font-size:11.2px; color:#bbb; padding:1px'>{s_disp[0]}</td>"
        f"<td style='font-size:11.2px; color:#bbb; padding:1px'>{s_disp[1]}</td>"
        f"<td style='font-size:11.2px; color:#bbb; padding:1px'>{s_disp[2]}</td>"
        f"<td style='font-size:11.2px; color:#bbb; padding:1px'>{s_disp[3]}</td></tr>"
        f"</table>"
        f"</div>"
    )
    st.markdown(stat_table, unsafe_allow_html=True)

# ---- 버튼(가로 4개) ----
growth = pet.get_growth(s_arr)
if pet.level > 1 and growth:
    atk_g, df_g, spd_g, hp_g = growth
    s_atk_g, s_df_g, s_spd_g, s_hp_g = s_growth
    total_g = atk_g + df_g + spd_g
    s_total_g = s_atk_g + s_df_g + s_spd_g
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
            atk_g, df_g, spd_g, hp_g = growth
            s_atk_g, s_df_g, s_spd_g, s_hp_g = s_growth
            total_g = atk_g + df_g + spd_g
            s_total_g = s_atk_g + s_df_g + s_spd_g
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
if pet.level > 1 and growth:
    s_atk_g, s_df_g, s_spd_g, s_hp_g = s_growth
    atk_g, df_g, spd_g, hp_g = growth
    total_g = atk_g + df_g + spd_g
    s_total_g = s_atk_g + s_df_g + s_spd_g
    growth_table = (
        "<div style='overflow-x:auto;'>"
        "<table style='width:100%; font-size:13.4px; line-height:1.08; table-layout:fixed;'>"
        "<tr><th>능력</th><th>내 성장률</th><th>S급 성장률</th></tr>"
        f"<tr><td>공격력</td><td>{atk_g:.3f}</td><td>{s_atk_g:.3f}</td></tr>"
        f"<tr><td>방어력</td><td>{df_g:.3f}</td><td>{s_df_g:.3f}</td></tr>"
        f"<tr><td>순발력</td><td>{spd_g:.3f}</td><td>{s_spd_g:.3f}</td></tr>"
        f"<tr><td>체력</td><td>{hp_g:.3f}</td><td>{s_hp_g:.3f}</td></tr>"
        f"<tr><td><b>합계</b></td><td><b>{total_g:.3f}</b></td><td><b>{s_total_g:.3f}</b></td></tr>"
        "</table></div>"
    )
    st.markdown(growth_table, unsafe_allow_html=True)
else:
    st.markdown("<div style='font-size:14px;text-align:center;'>성장률: - (2레벨 이상부터 표시)</div>", unsafe_allow_html=True)

if pet.level > 1:
    l_atk, l_df, l_spd, l_hp = pet.last_display_stats
    st.markdown(
        f"<div style='font-size:12.7px; text-align:center; margin-top:7px;'>"
        f"<b>직전 레벨업 변화량:</b> "
        f"<span style='color:{stat_color(l_atk)}'>공격력 {l_atk:+d}</span>  "
        f"<span style='color:{stat_color(l_df)}'>방어력 {l_df:+d}</span>  "
        f"<span style='color:{stat_color(l_spd)}'>순발력 {l_spd:+d}</span>  "
        f"<span style='color:{stat_color(l_hp)}'>체력 {l_hp:+d}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

if alert_msg:
    st.success(alert_msg)
