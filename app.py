import streamlit as st
import folium
from streamlit_folium import st_folium
from difflib import get_close_matches
import json

# --- 1. 核心数据库配置 ---
# 64个教区的基本信息
PARISH_DATA = {
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

# 核心枢纽与区域办公室坐标及信息
OFFICE_DETAILS = {
    "312": {"name": "Baton Rouge Hub", "lat": 30.4507, "lon": -91.1275, "addr": "Independence Blvd"},
    "360": {"name": "New Orleans Main", "lat": 29.9664, "lon": -90.0754, "addr": "N. Galvez St"},
    "090": {"name": "Shreveport Hub", "lat": 32.4764, "lon": -93.7915, "addr": "Shreveport Area"},
    "280": {"name": "Lafayette Hub", "lat": 30.2241, "lon": -92.0198, "addr": "Lafayette Area"},
    "100": {"name": "Lake Charles Hub", "lat": 30.2112, "lon": -93.2101, "addr": "Lake Charles Area"},
    "200": {"name": "Ville Platte Office", "lat": 30.6891, "lon": -92.2782, "addr": "Evangeline Parish"} # 新增 Evangeline 办公室
}

# 教区中心点 (用于地图跳转)
PARISH_COORDS = {
    "20": [30.7300, -92.4100], # Evangeline
    "17": [30.5383, -91.0964], # East Baton Rouge
}

# --- 2. 页面与搜索逻辑 ---
st.set_page_config(page_title="LA Parish Boundaries & OMV", layout="wide")
st.markdown("<h1 style='text-align: center;'>路易斯安那州 OMV 自动匹配系统</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔍 搜索与定位")
    search_input = st.text_input("输入城市或教区 (如 Evangeline):", "EVANGELINE").upper().strip()
    st.write("---")
    st.markdown("**图例说明:**\n- 🟦 蓝色区域: 教区边界\n- 🔴 红色标点: OMV 办公室")

# 模糊匹配教区名
all_names = [v.upper() for v in PARISH_DATA.values()]
matches = get_close_matches(search_input, all_names, n=1, cutoff=0.3)
selected_code = "20" # 默认 Evangeline
if matches:
    selected_code = [k for k, v in PARISH_DATA.items() if v.upper() == matches[0]][0]
    st.sidebar.success(f"匹配到教区: {matches[0]} (代码: {selected_code})")

# --- 3. 地图渲染逻辑 ---
center_pos = PARISH_COORDS.get(selected_code, [30.9843, -91.9623])
m = folium.Map(location=center_pos, zoom_start=9, tiles="cartodbpositron")

# A. 添加教区边界 (以高亮当前教区为例)
# 注意：实际应用中需要加载完整的路易斯安那州教区 GeoJSON 文件
# 这里演示边界样式设置
def style_function(feature):
    return {
        'fillColor': '#1a73e8' if feature['properties']['name'].upper() == PARISH_DATA[selected_code].upper() else '#transparent',
        'color': 'black',
        'weight': 2,
        'fillOpacity': 0.3,
    }

# B. 添加办公室标记 (鼠标悬停触发详情)
for code, info in OFFICE_DETAILS.items():
    hover_text = f"🏢 {info['name']}\n代码: {code}\n地址: {info['addr']}"
    folium.Marker(
        location=[info['lat'], info['lon']],
        tooltip=folium.Tooltip(hover_text, sticky=True), # 鼠标悬停显示信息
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

# C. 添加教区中心点 (蓝色标记)
for code, name in PARISH_DATA.items():
    if code in PARISH_COORDS:
        folium.Marker(
            location=PARISH_COORDS[code],
            tooltip=f"📍 {name} Parish (Code: {code})", # 鼠标悬停显示信息
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

# --- 4. 界面布局展示 ---
col_map, col_res = st.columns([3, 1.5])

with col_map:
    st.subheader("🗺️ 交互式分布与边界图")
    st_folium(m, width=850, height=600)

with col_res:
    st.subheader("📍 匹配结果清单")
    st.info(f"**主教区:** {PARISH_DATA[selected_code]}")
    
    # 推荐最近办公室 (根据坐标排序逻辑)
    st.warning("🏢 推荐办公室 (Office Codes)")
    # 演示结果列表
    st.write(f"- **312**: Baton Rouge Main Hub")
    st.write(f"- **200**: Ville Platte Office (Evangeline)")
    st.write(f"- **280**: Lafayette Hub")
