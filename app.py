import streamlit as st
import folium
from streamlit_folium import st_folium
from difflib import get_close_matches

# --- 1. 核心数据库配置 ---
# 所有的 64 个教区 (ZLA) 及其代表坐标
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

# 教区中心参考坐标 (用于地图渲染)
PARISH_COORDS = {
    "17": [30.5383, -91.0964], "36": [29.9511, -90.0715], "09": [32.5801, -93.8824],
    "28": [30.2079, -92.0620], "10": [30.2312, -93.3601], "37": [32.4851, -92.0526],
    "40": [31.2842, -92.5317], "52": [30.4500, -90.0400], "55": [29.3400, -90.8500],
    "32": [30.4355, -90.7384], "03": [30.2044, -90.9100], "01": [30.2677, -92.4110],
    "08": [32.5959, -93.6166], "26": [29.8512, -90.1340], "53": [30.5044, -90.4612]
}

# 您提供的所有 办公室代码 (ZLI) 及其精确位置
OFFICE_COORDS = {
    "312": {"name": "Baton Rouge (Indep. Blvd)", "lat": 30.4507, "lon": -91.1275, "type": "Hub"},
    "360": {"name": "New Orleans (N. Galvez St)", "lat": 29.9664, "lon": -90.0754, "type": "Hub"},
    "361": {"name": "New Orleans (Westbank)", "lat": 29.9142, "lon": -90.0412, "type": "Hub"},
    "090": {"name": "Shreveport", "lat": 32.4764, "lon": -93.7915, "type": "Hub"},
    "280": {"name": "Lafayette", "lat": 30.2241, "lon": -92.0198, "type": "Hub"},
    "100": {"name": "Lake Charles", "lat": 30.2112, "lon": -93.2101, "type": "Hub"},
    "010": {"name": "Crowley", "lat": 30.2140, "lon": -92.3740, "type": "Office"},
    "030": {"name": "Gonzales", "lat": 30.2274, "lon": -90.9237, "type": "Office"},
    "080": {"name": "Bossier City", "lat": 32.5159, "lon": -93.6876, "type": "Office"},
    "172": {"name": "Baton Rouge (Coursey Blvd)", "lat": 30.3980, "lon": -91.0255, "type": "Office"},
    "260": {"name": "Harvey", "lat": 29.8833, "lon": -90.0754, "type": "Office"},
    "261": {"name": "Kenner", "lat": 29.9946, "lon": -90.2417, "type": "Office"},
    "320": {"name": "Livingston", "lat": 30.5035, "lon": -90.7482, "type": "Office"},
    "370": {"name": "Monroe", "lat": 32.5093, "lon": -92.1193, "type": "Office"},
    "400": {"name": "Alexandria", "lat": 31.3113, "lon": -92.4451, "type": "Office"},
    "520": {"name": "Covington", "lat": 30.4755, "lon": -90.1009, "type": "Office"},
    "521": {"name": "Slidell", "lat": 30.2758, "lon": -89.7812, "type": "Office"},
    "530": {"name": "Hammond", "lat": 30.5044, "lon": -90.4612, "type": "Office"},
    "550": {"name": "Houma", "lat": 29.5958, "lon": -90.7195, "type": "Office"}
}

# --- 2. 界面初始化 ---
st.set_page_config(page_title="路易斯安那州 OMV 匹配系统", layout="wide")
st.markdown("<h1 style='text-align: center;'>路易斯安那州 OMV 自动匹配系统</h1>", unsafe_allow_html=True)

# 侧边栏搜索
with st.sidebar:
    st.header("🔍 地理匹配")
    search_input = st.text_input("输入城市或教区 (如 Baton Rouge):", "").upper().strip()
    st.write("---")
    st.markdown("**图例说明:**")
    st.markdown("🔵 **蓝色标记**: 教区中心 (ZLA)")
    st.markdown("🔴 **红色标记**: OMV 办公室 (ZLI)")

# --- 3. 搜索与定位逻辑 ---
current_target_code = "17" # 默认 EBR
if search_input:
    all_names = [name.upper() for name in PARISH_DATA.values()]
    matches = get_close_matches(search_input, all_names, n=1, cutoff=0.3)
    if matches:
        # 反查代码
        current_target_code = [k for k, v in PARISH_DATA.items() if v.upper() == matches[0]][0]
        st.sidebar.success(f"匹配到教区: {matches[0]}")

# 确定中心点
center_pos = PARISH_COORDS.get(current_target_code, [30.9843, -91.9623])

# --- 4. 地图渲染 ---
m = folium.Map(location=center_pos, zoom_start=8, tiles="cartodbpositron")

# 渲染所有教区中心 (蓝色)
for code, name in PARISH_DATA.items():
    if code in PARISH_COORDS:
        folium.Marker(
            location=PARISH_COORDS[code],
            popup=f"教区: {name} (Code: {code})",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

# 渲染所有办公室 (红色)
for code, info in OFFICE_COORDS.items():
    folium.Marker(
        location=[info["lat"], info["lon"]],
        popup=f"办公室: {info['name']} (Code: {code})",
        tooltip=info["name"],
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

# 布局显示
col_map, col_res = st.columns([3, 2])

with col_map:
    st.subheader("🗺️ 全量分布图")
    st_folium(m, width=800, height=600)

with col_res:
    st.subheader("📍 匹配结果详情")
    
    # 1. 推荐教区
    p_keys = list(PARISH_DATA.keys())
    idx = p_keys.index(current_target_code)
    neighbors = [p_keys[idx], p_keys[(idx+1)%64], p_keys[(idx-1)%64]]
    
    st.info("🏛️ 推荐教区 (Parish Codes)")
    for p in neighbors:
        st.write(f"- **{p}**: {PARISH_DATA[p]} Parish")

    # 2. 推荐办公室 (计算距离搜索点最近的 3 个)
    st.warning("🏢 推荐办公室 (Office Codes)")
    dist_list = []
    for o_code, o_info in OFFICE_COORDS.items():
        # 简单的欧式距离排序
        d = ((o_info['lat']-center_pos[0])**2 + (o_info['lon']-center_pos[1])**2)**0.5
        dist_list.append((o_code, o_info['name'], d))
    
    dist_list.sort(key=lambda x: x[2])
    for o in dist_list[:3]:
        st.write(f"- **{o[0]}**: {o[1]}")
