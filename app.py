import streamlit as st
import requests
from streamlit_javascript import st_javascript
import base64

# ==============================================
# 🔑 高德KEY（从Streamlit Secrets读取，安全不泄露）
# ==============================================
AMAP_WEB_KEY = st.secrets.get("AMAP_WEB_KEY", "")

# ==============================================
# 🖼️ 图片本地永久存储（手机/电脑都能永久保存）
# ==============================================
def save_image_to_local_storage(img_key, img_data):
    base64_data = base64.b64encode(img_data).decode()
    js_code = f"localStorage.setItem('{img_key}', '{base64_data}');"
    st_javascript(js_code)

def load_image_from_local_storage(img_key):
    js_code = f"localStorage.getItem('{img_key}');"
    result = st_javascript(js_code)
    if result and isinstance(result, str):
        return base64.b64decode(result)
    return None

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
st.title("👕 智能穿搭助手 · 永久存图版")

# 显示天气
weather_info = get_weather("北京")
st.info(f"当前天气：{weather_info}")

# 自动穿搭建议
if "气温" in weather_info:
    temp = weather_info.split("气温 ")[-1].replace("℃", "")
    st.success(f"👔 穿搭建议：{get_clothes_suggest(temp)}")

# ==============================================
# 🖼️ 衣柜图片上传（永久保存在你自己手机里！）
# ==============================================
st.subheader("🗄️ 我的衣柜 - 图片永久保存")
IMAGE_KEY = "my_clothes_image"

# 读取已保存的图片
saved_img = load_image_from_local_storage(IMAGE_KEY)

# 上传
uploaded_file = st.file_uploader("上传衣服照片", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    img_bytes = uploaded_file.read()
    save_image_to_local_storage(IMAGE_KEY, img_bytes)
    st.success("✅ 图片已永久保存到你的设备！")
    st.image(img_bytes, caption="你的穿搭", use_column_width=True)
elif saved_img is not None:
    st.image(saved_img, caption="✅ 已从本地加载（永久保存）", use_column_width=True)
else:
    st.info("请上传你的衣服照片～")

# ==============================================
# 📝 备注
# ==============================================
st.markdown("---")
st.caption("✅ 图片只存在你的手机/电脑里，别人看不到 | ✅ 刷新/关闭再打开都不会丢")
