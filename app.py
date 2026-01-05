import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# --- 1. 核心数据库 ---
# 教区数据 (ZLA) - 包含大致中心经纬度以便展示地图
PARISH_DATA = {
    "17": {"name": "East Baton Rouge", "lat": 30.5383, "lon": -91.0964, "office": "312"},
    "36": {"name": "Orleans", "lat": 29.9511, "lon": -90.0715, "office": "360"},
    "09": {"name": "Caddo", "lat": 32.5801, "lon": -93.8824, "office": "090"},
    "28": {"name": "Lafayette", "lat": 30.2079, "lon": -92.0620, "office": "280"},
    "10": {"name": "Calcasieu", "lat": 30.2312, "lon": -93.3601, "office": "100"},
    "26": {"name": "Jefferson", "lat": 29.8512, "lon": -90.1340, "office": "260"},
    "37": {"name": "Ouachita", "lat": 32.4851, "lon": -92.0526, "office": "370"},
    "40": {"name": "Rapides", "lat": 31.2842, "lon": -92.5317, "office": "400"},
    "55": {"name": "Terrebonne", "lat": 29.3400, "lon": -90.8500, "office": "550"},
    "52": {"name": "St. Tammany", "lat": 30.4500, "lon": -90.0400, "office": "520"},
    # ... (其他教区可在此补全，此处为主要城市示例)
}

# 补充所有 64 个教区的基本列表 (用于下拉展示)
ALL_PARISHES = {
    "01": "Acadia", "02": "Allen", "03": "Ascension", "04": "Assumption", "05": "Avoyelles",
    "06": "Beauregard", "07": "Bienville", "08": "Bossier", "09": "Caddo", "10": "Calcasieu",
    "11": "Caldwell", "12": "Cameron", "13": "Catahoula", "14": "Claiborne", "15": "Concordia",
    "16": "DeSoto", "17": "East Baton Rouge", "18": "East Carroll", "19": "East Feliciana", "20": "Evangeline",
    "21": "Franklin", "22": "Grant", "23": "Iberia", "24": "Iberville", "25": "Jackson",
    "26": "Jefferson", "27": "Jefferson Davis", "28": "Lafayette", "29": "Lafourche", "30": "LaSalle",
    "31": "Lincoln", "32": "Livingston", "33": "Madison", "34": "Morehouse", "35": "Natchitoches",
    "36": "Orleans", "37": "Ouachita", "38": "Plaquemines", "39": "Pointe Coupee", "40": "Rapides",
    "41": "Red River", "42": "Richland", "43": "Sabine", "44": "St. Bernard", "45": "St. Charles",
    "46": "St. Helena", "47": "St. James", "48": "St. John Baptist", "49": "St. Landry", "50": "St. Martin",
    "51": "St. Mary", "52": "St. Tammany", "53": "Tangipahoa", "54": "Tensas", "55": "Terrebonne",
    "56": "Union", "57": "Vermilion", "58": "Vernon", "59": "Washington", "60": "Webster",
    "61": "West Baton Rouge", "62": "West Carroll", "63": "West Feliciana", "64": "Winn"
}

# 办公室代码对照 (ZLI)
OFFICE_MAP = {
    "312": "Baton Rouge Hub", "360": "New Orleans Main", "090": "Shreveport Hub",
    "280": "Lafayette Hub", "100": "Lake Charles Hub", "260": "Harvey Office",
    "370": "Monroe Office", "400": "Alexandria Office", "550": "Houma Office",
    "520": "Covington Office"
}

# --- 2. 界面布局 ---
st.set_page_config(page_title="LA OMV Matcher with Map", layout="wide")
st.markdown("<h1 style='text-align: center;'>路易斯安那州 OMV 自动匹配系统</h1>", unsafe_allow_html=True)

# 侧边栏：搜索城市
with st.sidebar:
    st.header("🔍 城市搜索")
    city_name = st.text_input("输入城市名称 (如 New Orleans):", "Baton Rouge").upper()
    st.write("---")
    st.subheader("📋 教区列表参考")
    st.dataframe(pd.DataFrame(list(ALL_PARISHES.items()), columns=["Code", "Parish"]), height=400)

# 主页面布局
col_map, col_res = st.columns([3, 2])

# 初始化地图中心
m = folium.Map(location=[30.9843, -91.9623], zoom_start=7, tiles="cartodbpositron")

# 在地图上添加标记点
for code, info in PARISH_DATA.items():
    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=f"Parish: {info['name']} (Code: {code})",
        tooltip=info["name"],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

with col_map:
    st.subheader("🗺️ 交互式分布图")
    # 显示地图并捕捉点击事件
    map_data = st_folium(m, width=700, height=500)

# --- 3. 匹配逻辑 ---
selected_code = "17" # 默认值
if city_name in ["NEW ORLEANS", "NO"]: selected_code = "36"
elif city_name in ["SHREVEPORT"]: selected_code = "09"
elif city_name in ["LAFAYETTE"]: selected_code = "28"

# 结果展示
with col_res:
    st.subheader("📍 匹配结果")
    
    # 模拟“最近的3个”
    p_keys = list(ALL_PARISHES.keys())
    idx = p_keys.index(selected_code)
    neighbors = [p_keys[idx], p_keys[(idx+1)%64], p_keys[(idx-1)%64]]
    
    st.success(f"**当前主教区:** {ALL_PARISHES[selected_code]} (Code: {selected_code})")
    
    st.info("🏛️ 推荐教区 (Parish Codes)")
    for p in neighbors:
        st.write(f"- **{p}**: {ALL_PARISHES[p]} Parish")

    st.warning("🏢 推荐办公室 (Office Codes)")
    offices = [PARISH_DATA.get(p, {"office": "312"})["office"] for p in neighbors]
    for o in offices:
        st.write(f"- **{o}**: {OFFICE_MAP.get(o, 'Regional Office')}")

    # --- 4. Zint 转义输出 ---
    st.write("---")
    st.markdown("**📋 AAMVA ZL 子文件转义文本**")
    st.caption("解决 Error 234，自动换行且无滚动条。")
    
    zl_text = f"ZL\\nZLA{selected_code}\\nZLB0\\nZLC0\\nZLD88888888\\nZLE0\\nZLF0\\nZLG\\nZLH\\nZLI{offices[0]}\\r"
    
    # CSS 调整 textarea 样式以取消滚动条
    st.text_area(label="复制到 Zint:", value=zl_text, height=100)
