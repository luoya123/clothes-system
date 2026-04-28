import streamlit as st
import requests
import json
import os
from PIL import Image

# 必须第一行
st.set_page_config(page_title="智能穿搭系统", layout="wide")

# ===================== 基础配置 =====================
IMG_FOLDER = "clothes_img"
WARDROBE_FILE = "wardrobe.json"
OUTFIT_FILE = "outfit.json"
CITY_FILE = "city_list.json"

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

# 温度分类
TEMP_TYPE_LIST = [
    ("hot", "高温夏季 ≥25℃"),
    ("warm", "春秋舒适 15~25℃"),
    ("cool", "微凉外套 5~15℃"),
    ("cold", "寒冬保暖 ＜5℃")
]
TEMP_DICT = dict(TEMP_TYPE_LIST)

# 关键：从Streamlit环境变量读取密钥（不写在代码里）
AMAP_WEB_KEY = st.secrets.get("AMAP_WEB_KEY", "")

# ===================== 核心CSS =====================
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
}
@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 calc(50% - 5px) !important;
        max-width: calc(50% - 5px) !important;
    }
}
@media (min-width: 641px) {
    div[data-testid="stHorizontalBlock"] > div {
        flex: 1 1 calc(33.33% - 8px) !important;
        max-width: calc(33.33% - 8px) !important;
    }
}
.stImage button[title="放大图片"] {
    opacity: 1 !important;
    transform: scale(1.5) !important;
    right: 5px !important;
    top: 5px !important;
    background: rgba(0,0,0,0.5) !important;
    border-radius: 50% !important;
}
</style>
""", unsafe_allow_html=True)

# ===================== 高德天气 =====================
def get_weather_by_amap(city_name, key):
    if not key:
        return {"success":False,"msg":"未配置密钥"}
    try:
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {"key": key,"city": city_name,"extensions": "base"}
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if data.get("status") == "1" and data.get("lives"):
            live = data["lives"][0]
            return {
                "success": True,
                "city": live["city"],
                "temp": int(float(live["temperature"])),
                "weather": live["weather"],
                "wind": live["winddirection"] + "风 " + live["windpower"]
            }
        else:
            return {"success": False, "msg": data.get("info", "查询失败")}
    except Exception as e:
        return {"success": False, "msg": str(e)}

def get_temp_type(temp):
    if temp >= 25:return "hot"
    elif temp >= 15:return "warm"
    elif temp >= 5:return "cool"
    else:return "cold"

def get_cloth_tips(temp_type):
    tips = {
        "hot":"气温偏高，建议轻薄短袖、短裤、短裙，透气清爽穿搭。",
        "warm":"温度舒适，长袖、卫衣、常规长裤、薄裙都很合适。",
        "cool":"气温偏凉，需要加外套、长袖长裤，注意防风保暖。",
        "cold":"天气寒冷，厚外套、羽绒服、加绒下装，全套保暖穿搭。"
    }
    return tips.get(temp_type, "正常穿搭即可")

# ===================== 数据读写 =====================
def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        with open(WARDROBE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "上衣":{"hot":[],"warm":[],"cool":[],"cold":[]},
        "下装":{"hot":[],"warm":[],"cool":[],"cold":[]},
        "裙子":{"hot":[],"warm":[],"cool":[],"cold":[]},
        "外套":{"hot":[],"warm":[],"cool":[],"cold":[]},
        "鞋子":{"hot":[],"warm":[],"cool":[],"cold":[]}
    }

def save_wardrobe(data):
    with open(WARDROBE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_outfits():
    if os.path.exists(OUTFIT_FILE):
        with open(OUTFIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_outfits(data):
    with open(OUTFIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cities():
    if os.path.exists(CITY_FILE):
        with open(CITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cities(lst):
    with open(CITY_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

# 会话状态
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = load_wardrobe()
if "outfits" not in st.session_state:
    st.session_state.outfits = load_outfits()
if "city_list" not in st.session_state:
    st.session_state.city_list = load_cities()

wardrobe = st.session_state.wardrobe
outfits = st.session_state.outfits
city_list = st.session_state.city_list

# 顶部菜单
menu = st.radio(
    "",
    ["👔 穿搭建议", "🧩 整套穿搭", "👕 单品穿搭"],
    horizontal=True,index=0
)

# ========== 穿搭建议页 ==========
if menu == "👔 穿搭建议":
    st.title("🌤️ 今日穿搭建议")

    # 只给部署者自己用，别人看不到输入框
    with st.expander("🔧 自定义天气密钥（仅自己使用）", expanded=False):
        user_key = st.text_input("高德Key", type="password", value=AMAP_WEB_KEY)
    use_key = user_key if user_key else AMAP_WEB_KEY

    st.subheader("📍 常用城市")
    new_city = st.text_input("添加城市")
    if st.button("添加") and new_city.strip():
        if new_city not in city_list:
            city_list.append(new_city.strip())
            save_cities(city_list)
            st.success(f"已添加：{new_city}")

    if city_list:
        for i, c in enumerate(city_list):
            col1, col2 = st.columns([6, 1])
            col1.write(c)
            if col2.button("删除", key=f"del_city_{i}"):
                city_list.pop(i)
                save_cities(city_list)
                st.rerun()

    default_city = city_list[0] if city_list else "武汉"
    search_city = st.text_input("查询城市", value=default_city)
    st.divider()

    temp = 20
    weather = get_weather_by_amap(search_city, use_key)
    if weather["success"]:
        temp = weather["temp"]
        st.success(f"🌍 城市：{weather['city']}")
        st.info(f"🌡 温度：{temp}℃ ｜ 天气：{weather['weather']} ｜ {weather['wind']}")
    else:
        st.info("暂无实时天气，使用默认20℃")

    curr_temp_key = get_temp_type(temp)
    st.subheader("💡 今日穿搭文字建议")
    st.write(get_cloth_tips(curr_temp_key))

    # 匹配穿搭、单品推荐不变
    st.divider()
    st.subheader("✨ 适合当前温度 · 整套穿搭")
    match_outfits = [o for o in outfits if o["temp_key"] == curr_temp_key]
    if match_outfits:
        for out in match_outfits:
            st.markdown(f"**{out['name']}**")
            st.text(f"上衣：{out['上衣']} | 下装：{out['下装']} | 裙子：{out['裙子']} | 外套：{out['外套']} | 鞋子：{out['鞋子']}")
            st.divider()
    else:
        st.warning("暂无匹配的整套穿搭")

    st.divider()
    st.subheader("👕 适合当前温度 · 单品推荐")
    cate_show = ["上衣","下装","外套","鞋子","裙子"]
    for cate in cate_show:
        item_list = wardrobe[cate][curr_temp_key]
        st.markdown(f"**▫️ {cate}**")
        if item_list:
            for i in range(0, len(item_list), 3):
                row = item_list[i:i+3]
                cols = st.columns(len(row))
                for j, item in enumerate(row):
                    with cols[j]:
                        st.text(item["name"])
                        st.image(item["img"], use_column_width=True)
        else:
            st.caption("暂无该温度单品")

# ========== 整套穿搭、单品页面完全不变 ==========
elif menu == "🧩 整套穿搭":
    st.title("🧩 整套穿搭管理")
    top_opt = ["无"] + [i["name"] for t in wardrobe["上衣"].values() for i in t]
    pants_opt = ["无"] + [i["name"] for t in wardrobe["下装"].values() for i in t]
    skirt_opt = ["无"] + [i["name"] for t in wardrobe["裙子"].values() for i in t]
    coat_opt = ["无"] + [i["name"] for t in wardrobe["外套"].values() for i in t]
    shoes_opt = ["无"] + [i["name"] for t in wardrobe["鞋子"].values() for i in t]

    suit_name = st.text_input("套装名称")
    suit_temp = st.selectbox("适用温度", [v for k, v in TEMP_TYPE_LIST])
    col1, col2, col3 = st.columns(3)
    with col1:
        top_sel = st.selectbox("上衣", top_opt)
        coat_sel = st.selectbox("外套", coat_opt)
    with col2:
        pants_sel = st.selectbox("下装", pants_opt)
        shoes_sel = st.selectbox("鞋子", shoes_opt)
    with col3:
        skirt_sel = st.selectbox("裙子", skirt_opt)

    if st.button("💾 保存套装") and suit_name:
        t_key = [k for k, v in TEMP_TYPE_LIST if v == suit_temp][0]
        outfits.append({
            "name": suit_name,"temp_key": t_key,
            "上衣": top_sel,"下装": pants_sel,"裙子": skirt_sel,
            "外套": coat_sel,"鞋子": shoes_sel
        })
        save_outfits(outfits)
        st.success("保存成功")
        st.rerun()

    st.divider()
    for idx, out in enumerate(outfits):
        st.markdown(f"**{out['name']} | {TEMP_DICT[out['temp_key']]}**")
        st.text(f"上衣：{out['上衣']} 下装：{out['下装']} 裙子：{out['裙子']}")
        st.text(f"外套：{out['外套']} 鞋子：{out['鞋子']}")
        if st.button("删除", key=f"del_outfit_{idx}"):
            outfits.pop(idx)
            save_outfits(outfits)
            st.rerun()
        st.divider()

elif menu == "👕 单品穿搭":
    st.title("👕 单品衣柜管理")
    cate_list = ["上衣", "下装", "裙子", "外套", "鞋子"]
    tabs = st.tabs(cate_list)

    for idx, cate in enumerate(cate_list):
        with tabs[idx]:
            name = st.text_input("衣物名称", key=f"name_{cate}")
            temp_sel = st.selectbox("适用温度", [v for k, v in TEMP_TYPE_LIST], key=f"temp_{cate}")
            img = st.file_uploader("上传图片", type=["jpg","png","jpeg"], key=f"img_{cate}")

            if st.button("保存单品", key=f"save_{cate}") and name and img:
                temp_key = [k for k, v in TEMP_TYPE_LIST if v == temp_sel][0]
                path = os.path.join(IMG_FOLDER, img.name)
                with open(path, "wb") as f:
                    f.write(img.read())
                wardrobe[cate][temp_key].append({"name": name, "img": path})
                save_wardrobe(wardrobe)
                st.success("添加成功")
                st.rerun()

            st.divider()
            for tkey, tname in TEMP_TYPE_LIST:
                items = wardrobe[cate][tkey]
                st.markdown(f"**【{tname}】**")
                if items:
                    for i in range(0, len(items), 3):
                        row = items[i:i+3]
                        cols = st.columns(len(row))
                        for j, item in enumerate(row):
                            with cols[j]:
                                st.text(item["name"])
                                st.image(item["img"], use_column_width=True)
                                if st.button("🗑️ 删除", key=f"del_{cate}_{tkey}_{i+j}"):
                                    if os.path.exists(item["img"]):
                                        os.remove(item["img"])
                                    wardrobe[cate][tkey].pop(i+j)
                                    save_wardrobe(wardrobe)
                                    st.rerun()
                else:
                    st.caption("暂无该温度单品")
                st.divider()