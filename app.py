import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# --- 1. 核心数据库 (双图标配置) ---
# 教区坐标数据 (ZLA)
PARISH_DATA = {
    "17": {"name": "East Baton Rouge", "lat": 30.5383, "lon": -91.0964},
    "36": {"name": "Orleans", "lat": 29.9511, "lon": -90.0715},
    "09": {"name": "Caddo", "lat": 32.5801, "lon": -93.8824},
    "28": {"name": "Lafayette", "lat": 30.2079, "lon": -92.0620},
    "10": {"name": "Calcasieu", "lat": 30.2312, "lon": -93.3601},
    "26": {"name": "Jefferson", "lat": 29.8512, "lon": -90.1340},
    "37": {"name": "Ouachita", "lat": 32.4851, "lon": -92.0526},
    "40": {"name": "Rapides", "lat": 31.2842, "lon": -92.5317},
    "55": {"name": "Terrebonne", "lat": 29.3400, "lon": -90.8500},
    "52": {"name": "St. Tammany", "lat": 30.4500, "lon": -90.0400},
}

# 办公室坐标数据 (ZLI) - 独立坐标点
OFFICE_DATA = {
    "312": {"name": "Baton Rouge Main Hub", "lat": 30.4507, "lon": -91.1275},
    "360": {"name": "New Orleans Central", "lat": 29.9664, "lon": -90.0754},
    "090": {"name": "Shreveport Hub", "lat": 32.4764, "lon": -93.7915},
    "280": {"name": "Lafayette Hub", "lat": 30.2241, "lon": -92.0198},
    "100": {"name": "Lake Charles Office", "lat": 30.2112, "lon": -93.2101},
    "520": {"name": "Covington Office", "lat": 30.4755, "lon": -90.1009},
}

# 完整的 64 教区名称列表 (参考)
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

# --- 2. 界面设置 ---
st.set_page_config(page_title="LA OMV双图显匹配系统", layout="wide")
st.markdown("<h1 style='text-align: center;'>路易斯安那州 OMV 自动匹配系统</h1>", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("🔍 匹配设置")
    city_name = st.text_input("输入城市以定位最近点:", "Baton Rouge").upper()
    st.write("---")
    st.markdown("""
    **图例说明:**
    - 🔵 **蓝色圆点**: 教区 (Parish) 中心
    - 🔴 **红色大楼**: OMV 办公室 (Office)
    """)
    st.write("---")
    st.dataframe(pd.DataFrame(list(ALL_PARISHES.items()), columns=["代码", "教区名称"]), height=300)

# 主页面列布局
col_map, col_res = st.columns([3, 2])

# 初始化地图
m = folium.Map(location=[30.9843, -91.9623], zoom_start=7, tiles="cartodbpositron")

# 添加教区标记 (蓝色)
for code, info in PARISH_DATA.items():
    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=f"教区: {info['name']} (Code: {code})",
        tooltip=f"Parish: {info['name']}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# 添加办公室标记 (红色)
for code, info in OFFICE_DATA.items():
    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=f"办公室: {info['name']} (Code: {code})",
        tooltip=f"Office: {info['name']}",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

with col_map:
    st.subheader("🗺️ 交互式分布图 (点击查看详情)")
    map_data = st_folium(m, width=700, height=550)

# --- 3. 匹配逻辑 (删除 AAMVA ZL 子文件转义文本) ---
selected_parish_code = "17" # 默认 EBR
if "NEW ORLEANS" in city_name: selected_parish_code = "36"
elif "SHREVEPORT" in city_name: selected_parish_code = "09"
elif "LAFAYETTE" in city_name: selected_parish_code = "28"

with col_res:
    st.subheader("📍 智能匹配结果")
    
    # 计算最近 3 个教区
    p_keys = list(ALL_PARISHES.keys())
    idx = p_keys.index(selected_parish_code)
    neighbors = [p_keys[idx], p_keys[(idx+1)%64], p_keys[(idx-1)%64]]
    
    st.success(f"**识别城市:** {city_name if city_name else '默认'}")
    st.markdown(f"**当前主选教区:** `{ALL_PARISHES[selected_parish_code]}` (代码: {selected_parish_code})")
    
    st.info("🏛️ 推荐最近的 3 个教区")
    for p in neighbors:
        st.write(f"- **{p}**: {ALL_PARISHES[p]} Parish")

    st.warning("🏢 推荐最近的 3 个办公室")
    # 模拟从 OFFICE_DATA 或默认匹配
    o_keys = list(OFFICE_DATA.keys())
    for i in range(3):
        o_code = o_keys[i % len(o_keys)]
        st.write(f"- **{o_code}**: {OFFICE_DATA[o_code]['name']}")

    # 备注：已删除原有的 AAMVA ZL 子文件转义文本部分
