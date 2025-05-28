import streamlit as st
import random
import math

# ---- 펫 데이터 정의 ----
PET_LIST = [
    # (도감번호, 이름, 초기치계수, 체력계수, 공격계수, 방어계수, 순발계수)
    (1, "놀놀", 25, 19, 29, 18, 29),
    (2, "골골", 21, 20, 30, 13, 28),
    (3, "벨가", 24, 28, 16, 25, 25),
    (4, "베룰", 23, 21, 30, 13, 28),
    (5, "오가", 25, 26, 29, 28, 20),
    (6, "모가", 27, 23, 37, 20, 25),
    (7, "올곤", 26, 28, 30, 22, 22),
    (8, "골롯", 28, 23, 35, 25, 21),
]

PET_DIC = {pet[1]: pet for pet in PET_LIST}
PET_NAME_LIST = [pet[1] for pet in PET_LIST]
FIRST_PET = "벨가"
S_GROWTH_B = 495  # 평균 보정계수

# 이미지명 gif로 세팅
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

def calc_display_stats(hp, atk, df, spd):
    display_hp = math.floor(hp * 4 + atk + df + spd)
    display_atk = math.floor(hp * 0.1 + atk + df * 0.1 + spd * 0.05)
    display_df = math.floor(hp * 0.1 + atk * 0.1 + df + spd * 0.05)
    display_spd = math.floor(spd)
    return (display_hp, display_atk, display_df, display_spd)

def calc_s_init_stats(petinfo):
    # 초기치계수, 체력계수, 공격계수, 방어계수, 순발계수
    initc, h, a, d, s = petinfo[2:]
    s_hp = initc * h / 100
    s_atk = initc * a / 100
    s_df = initc * d / 100
    s_spd = initc * s / 100
    return [s_hp, s_atk, s_df, s_spd]

def calc_s_growth_stats(petinfo, level=140, B=495):
    # S급 초기치로 시작해서, 139번 평균분배로 성장 (A=2.5)
    initc, h, a, d, s = petinfo[2:]
    base = [h, a, d, s]
    s_stats = calc_s_init_stats(petinfo)
    cur = list(s_stats)
    for _ in range(1, level):
        for i in range(4):
            growth = (base[i] + 2.5) * B / 10000
            cur[i] += growth
    # 성장률 = (140레벨 능력치 - S급초기치) / (139)
    growths = [(cur[i] - s_stats[i]) / (level-1) for i in range(4)]
    total = sum(growths[1:4])  # 공+방+순
    return growths, total

class Pet:
    def __init__(self, name):
        petinfo = PET_DIC[name]
        self.idx = petinfo[0]
        self.name = name
        self.initc = petinfo[2]
        self.hp_coef = petinfo[3]
        self.atk_coef = petinfo[4]
        self.df_coef = petinfo[5]
        self.spd_coef = petinfo[6]
        self.s_init_stats = calc_s_init_stats(petinfo)
        self.s_growths, self.s_total_growth = calc_s_growth_stats(petinfo)
        self.level = 1
        self.growth_init()

    def growth_init(self):
        # 랜덤 생성
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
        self.current_stats = [
            self.initc * self.base_stats[0] / 100,
            self.initc * self.base_stats[1] / 100,
            self.initc * self.base_stats[2] / 100,
            self.initc * self.base_stats[3] / 100,
        ]
        self.init_display_stats = list(calc_display_stats(*self.current_stats))
        self.last_display_stats = [0, 0, 0, 0]

    def is_perfect_s_or_above(self):
        # 1레벨에서 S급 초기치와 동일
        stats = calc_display_stats(*self.current_stats)
        s_stats = calc_display_stats(*self.s_init_stats)
        return all(stats[i] == s_stats[i] for i in range(4)) and self.level == 1

    def get_stats(self):
        return calc_display_stats(*self.current_stats)

    def levelup(self, up_count=1):
        MAX_LEVEL = 140
        for _ in range(up_count):
            if self.level >= MAX_LEVEL:
                break
            before = self.get_stats()
            base_growth = [self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth]
            a_bonus = [0, 0, 0, 0]
            for _ in range(10):
                idx = random.randint(0, 3)
                a_bonus[idx] += 1
            b = S_GROWTH_B  # 평균 보정
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
        # S급 초기치 기준 성장률 (내림, 레벨 1은 -)
        cur = self.get_stats()
        s_init = calc_display_stats(*self.s_init_stats)
        lv = self.level
        if lv > 1:
            atk_g = math.floor((cur[1] - s_init[1]) / (lv-1))
            df_g  = math.floor((cur[2] - s_init[2]) / (lv-1))
            spd_g = math.floor((cur[3] - s_init[3]) / (lv-1))
            hp_g  = math.floor((cur[0] - s_init[0]) / (lv-1))
            total_g = atk_g + df_g + spd_g
            return atk_g, df_g, spd_g, hp_g, total_g
        else:
            return None

    def get_base_growths(self):
        return self.hp_growth, self.atk_growth, self.df_growth, self.spd_growth

# ---- 상태관리 ----
if "money" not in st.session_state:
    st.session_state.money = 0
if "pet" not in st.session_state:
    st.session_state.pet = Pet(FIRST_PET)

st.set_page_config(page_title="석기시대 공룡키우기", layout="centered")
st.markdown(
    "<h2 style='text-align:center; margin-bottom:6px;'>석기시대 공룡키우기</h2>",
    unsafe_allow_html=True
)

# ---- 우상단 골드 ----
st.markdown(
    f"<div style='position:absolute;top:15px;right:24px;font-size:21px;font-weight:bold;color:gold;'>"
    f"💰 {st.session_state.money} G"
    f"</div>",
    unsafe_allow_html=True
)

pet = st.session_state.pet

# ---- 이미지 + 능력치 ----
col_img, col_stat = st.columns([1,2])
with col_img:
    st.image(PET_IMAGE_NUM[pet.name], width=100)
with col_stat:
    cur_hp, cur_atk, cur_df, cur_spd = pet.get_stats()
    s_hp, s_atk, s_df, s_spd = calc_display_stats(*pet.s_init_stats)
    def stat_color(val):
        if val == 0:
            return "cyan"
        elif val > 0:
            return "lime"
        else:
            return "red"
    stat_table = (
        f"<table style='width:100%; font-size:17px;'>"
        f"<tr><th>능력</th><th>현재(Lv{pet.level})</th><th>S급 초기치</th><th>차이</th></tr>"
        f"<tr><td>공격력</td><td>{cur_atk}</td><td>{s_atk}</td><td><span style='color:{stat_color(cur_atk-s_atk)}'>{cur_atk-s_atk:+}</span></td></tr>"
        f"<tr><td>방어력</td><td>{cur_df}</td><td>{s_df}</td><td><span style='color:{stat_color(cur_df-s_df)}'>{cur_df-s_df:+}</span></td></tr>"
        f"<tr><td>순발력</td><td>{cur_spd}</td><td>{s_spd}</td><td><span style='color:{stat_color(cur_spd-s_spd)}'>{cur_spd-s_spd:+}</span></td></tr>"
        f"<tr><td>체력</td><td>{cur_hp}</td><td>{s_hp}</td><td><span style='color:{stat_color(cur_hp-s_hp)}'>{cur_hp-s_hp:+}</span></td></tr>"
        f"</table>"
    )
    st.markdown(stat_table, unsafe_allow_html=True)

# ---- 버튼 ----
btn1, btn2, btn3, btn4, btn5 = st.columns(5)
alert_msg = None

with btn1:
    if st.button("레벨업"):
        pet.levelup()
        st.rerun()
with btn2:
    if st.button("10레벨업"):
        pet.levelup(up_count=10)
        st.rerun()
with btn3:
    if st.button("새로뽑기"):
        st.session_state.pet = Pet(FIRST_PET)
        st.rerun()
with btn4:
    if st.button("판매"):
        lv_price = pet_level_price(pet.level)
        growth = pet.get_growth()
        s_total_growth = math.floor(pet.s_total_growth)
        growth_grade, mult = get_growth_grade(growth[-1] if growth else 0, s_total_growth)
        base_money = lv_price
        bonus = PET_BONUS.get(pet.name, 1)
        sell_money = int(base_money * mult * bonus)
        st.session_state.money += sell_money
        alert_msg = f"{sell_money}골드를 획득합니다."
        st.session_state.pet = Pet(FIRST_PET)
        st.rerun()
with btn5:
    if st.button("랜덤뽑기"):
        if st.session_state.money < 100:
            alert_msg = "💸 골드가 부족합니다!"
        else:
            st.session_state.money -= 100
            random_pet = random.choice([name for name in PET_NAME_LIST if name != FIRST_PET])
            st.session_state.pet = Pet(random_pet)
            st.rerun()

# ---- 성장률 ----
growth = pet.get_growth()
s_growth = pet.s_growths
s_total_growth = math.floor(pet.s_total_growth)

if growth:
    atk_g, df_g, spd_g, hp_g, total_g = growth
    s_atk_g, s_df_g, s_spd_g, s_hp_g = [math.floor(x) for x in s_growth]
    growth_table = (
        "<table style='width:100%; font-size:15px;'>"
        "<tr><th>능력</th><th>내 성장률</th><th>S급 성장률</th></tr>"
        f"<tr><td>공격력</td><td>{atk_g}</td><td>{s_atk_g}</td></tr>"
        f"<tr><td>방어력</td><td>{df_g}</td><td>{s_df_g}</td></tr>"
        f"<tr><td>순발력</td><td>{spd_g}</td><td>{s_spd_g}</td></tr>"
        f"<tr><td>체력</td><td>{hp_g}</td><td>{s_hp_g}</td></tr>"
        f"<tr><td><b>합계</b></td><td><b>{total_g}</b></td><td><b>{s_total_growth}</b></td></tr>"
        "</table>"
    )
    st.markdown(growth_table, unsafe_allow_html=True)
else:
    st.markdown("<div style='font-size:14px;text-align:center;'>성장률: - (2레벨 이상부터 표시)</div>", unsafe_allow_html=True)

if pet.level > 1:
    l_hp, l_atk, l_df, l_spd = pet.last_display_stats
    st.markdown(
        f"<div style='font-size:15px; text-align:center; margin-top:12px;'>"
        f"<b>직전 레벨업 변화량:</b> "
        f"<span style='color:{stat_color(l_atk)}'>공격력 {l_atk:+}</span>  "
        f"<span style='color:{stat_color(l_df)}'>방어력 {l_df:+}</span>  "
        f"<span style='color:{stat_color(l_spd)}'>순발력 {l_spd:+}</span>  "
        f"<span style='color:{stat_color(l_hp)}'>체력 {l_hp:+}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

# ---- 알럿 ----
if pet.is_perfect_s_or_above():
    st.markdown(
        """
        <script>
        alert("정석이 출현했습니다!!!");
        </script>
        """, unsafe_allow_html=True
    )
if alert_msg:
    st.markdown(
        f"""
        <script>
        alert("{alert_msg}");
        </script>
        """, unsafe_allow_html=True
    )
