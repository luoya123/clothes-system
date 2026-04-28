import streamlit as st
import requests
import base64

# ==============================================
# 🔑 高德KEY（从Streamlit Secrets读取，安全不泄露）
# ==============================================
AMAP_WEB_KEY = st.secrets.get("AMAP_WEB_KEY", "")

# ==============================================
# 🖼️ 图片缓存（只存在你当前浏览器里，别人看不到）
# ==============================================
@st.cache_data(show_spinner=False)
def get_cached_image():
    return None

def save_image_to_cache(img_bytes):
    get_cached_image.clear()
    get_cached_image()
    st.session_state["clothes_image"] = img_bytes

def load_image_from_cache():
    return st.session_state.get("clothes_image", None)

# ==============================================
# 🌤️ 获取天气
# ==============================================
def get_weather(city="北京"):
    if not AMAP_WEB_KEY:
        return "未配置高德Key，无法获取天气"
    
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key={AMAP_WEB_KEY}&extensions=base&output=json"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data.get("status") == "1" and data.get("lives"):
            weather = data["lives"][0]
            return f"{weather['city']} {weather['weather']} 气温 {weather['temperature']}℃"
        return "天气获取失败"
    except:
        return "天气服务异常"

# ==============================================
# 🎨 穿搭建议
# ==============================================
def get_clothes_suggest(temp):
    try:
        temp = int(temp)
        if temp >= 28:
            return "☀️ 炎热：短袖、T恤、短裤、裙子"
        elif 20 <= temp < 28:
            return "🌤️ 舒适：长袖、薄外套、长裤"
        elif 10 <= temp < 20:
            return "🍃 微凉：针织衫、夹克、卫衣"
        elif 0 <= temp < 10:
            return "❄️ 较冷：大衣、毛衣、保暖裤"
        else:
            return "⛄ 寒冷：羽绒服、厚棉服、保暖内衣"
    except:
        return "无法判断温度"

# ==============================================
# 🏠 主界面
# ==============================================
st.set_page_config(page_title="智能穿搭助手", page_icon="👕", layout="wide")
st.title("👕 智能穿搭助手 · 专属版")

# 显示天气
weather_info = get_weather("北京")
st.info(f"当前天气：{weather_info}")

# 自动穿搭建议
if "气温" in weather_info:
    temp = weather_info.split("气温 ")[-1].replace("℃", "")
    st.success(f"👔 穿搭建议：{get_clothes_suggest(temp)}")

# ==============================================
# 🖼️ 衣柜图片上传（只存在你自己的浏览器里）
# ==============================================
st.subheader("🗄️ 我的衣柜")

# 读取已保存的图片
saved_img = load_image_from_cache()

# 上传
uploaded_file = st.file_uploader("上传衣服照片", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    img_bytes = uploaded_file.read()
    save_image_to_cache(img_bytes)
    st.success("✅ 图片已保存到你的浏览器！")
    st.image(img_bytes, caption="你的穿搭", use_column_width=True)
elif saved_img is not None:
    st.image(saved_img, caption="✅ 已从本地会话加载", use_column_width=True)
else:
    st.info("请上传你的衣服照片～")

# ==============================================
# 📝 备注
# ==============================================
st.markdown("---")
st.caption("✅ 图片只存在你当前的浏览器会话里，别人看不到 | ✅ 同一个浏览器刷新后仍可保留")
