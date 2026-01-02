import streamlit as st
import os
import pandas as pd
import pydeck as pdk
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import streamlit.components.v1 as components
import json
from urllib.parse import urlencode

def _get_api_key() -> str:
    """从 Streamlit secrets 获取 Google Maps API Key"""
    try:
        if hasattr(st, 'secrets'):
            map_apikey = st.secrets.get('map', {})
            key = map_apikey.get('apikey')
            if key:
                return key
    except Exception:
        pass
    return os.getenv('MAP_API_KEY') or ''

@st.cache_data
def load_store_data():
    """加载店铺数据"""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'store_data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # 检查是否已有地理位置数据
        if 'lat' in df.columns and 'lon' in df.columns:
            # 过滤掉没有坐标的行来判断是否需要重新获取
            has_coords = df['lat'].notna() & df['lon'].notna()
            if has_coords.any():
                return df, True  # 返回数据和是否已有坐标的标志
        return df, False
    return pd.DataFrame(columns=['Store Name', 'Address']), False

def save_store_data_with_coords(df):
    """保存带有坐标的店铺数据到原文件"""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'store_data.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    st.success(f"✅ 已更新 store_data.csv，添加了地理位置信息")

@st.cache_data
def geocode_addresses(df, api_key):
    """将地址转换为经纬度"""
    if api_key:
        geolocator = GoogleV3(api_key=api_key)
    else:
        st.warning("未配置 Google Maps API Key，使用 Nominatim 服务（速度较慢）")
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="maimai_map")
    
    # 复制数据框并添加坐标列
    result_df = df.copy()
    if 'lat' not in result_df.columns:
        result_df['lat'] = None
    if 'lon' not in result_df.columns:
        result_df['lon'] = None
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, row in result_df.iterrows():
        # 如果已有坐标则跳过
        if pd.notna(row.get('lat')) and pd.notna(row.get('lon')):
            continue
            
        try:
            status_text.text(f"正在获取位置 {idx + 1}/{len(result_df)}: {row['Store Name']}")
            location = geolocator.geocode(row['Address'], timeout=10)
            
            if location:
                result_df.at[idx, 'lat'] = location.latitude
                result_df.at[idx, 'lon'] = location.longitude
            else:
                st.warning(f"无法找到地址: {row['Address']}")
            
            # 避免请求过快
            time.sleep(0.5)
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            st.warning(f"地理编码错误: {row['Store Name']} - {str(e)}")
            time.sleep(1)
        
        progress_bar.progress((idx + 1) / len(result_df))
    
    progress_bar.empty()
    status_text.empty()
    
    return result_df

def main():
    st.set_page_config(page_title="Maimai 店铺地图", layout="wide")
    st.title("🎮 Maimai Deluxe 店铺地图")
    
    # 加载数据
    store_df, has_coords = load_store_data()
    
    if store_df.empty:
        st.error("未找到店铺数据！")
        return
    
    #st.success(f"已加载 {len(store_df)} 家店铺")
    
    # 检查URL查询参数中是否有浏览器位置，如果有自动加载
    query_params = st.query_params
    if 'browser_lat' in query_params and 'browser_lon' in query_params:
        try:
            lat = float(query_params['browser_lat'])
            lon = float(query_params['browser_lon'])
            st.session_state['user_location'] = {'lat': lat, 'lon': lon}
        except (ValueError, TypeError):
            pass
    
    # 获取 API Key
    api_key = _get_api_key()
    
    # 如果 localStorage 中有坐标但 session_state 中没有，显示提示和自动加载按钮
    
    # 如果已有坐标数据，显示地图
    if has_coords:
        coord_count = store_df['lat'].notna().sum()
        st.info(f"✅ 已有 {coord_count} 个店铺的位置信息")
        
        # if st.button("🔄 重新获取位置（更新所有坐标）"):
        #     # 清除缓存并重新获取
        #     load_store_data.clear()
        #     geocode_addresses.clear()
        #     with st.spinner("正在重新获取店铺地理位置..."):
        #         # 移除现有坐标
        #         store_df_clean = store_df[['Store Name', 'Address']].copy()
        #         geo_df = geocode_addresses(store_df_clean, api_key)
        #         save_store_data_with_coords(geo_df)
        #         st.rerun()
        
        # 显示地图
        geo_df = store_df[store_df['lat'].notna() & store_df['lon'].notna()].copy()
        if not geo_df.empty:
            st.subheader("📍 店铺位置地图")
            
            # 获取地理位置的按钮和JavaScript组件
            geolocation_js = """
                <script>
                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {
                            var lat = position.coords.latitude;
                            var lon = position.coords.longitude;
                            
                            // 修改 URL 参数并刷新页面
                            var url = new URL(window.location);
                            url.searchParams.set('browser_lat', lat);
                            url.searchParams.set('browser_lon', lon);
                            window.history.replaceState({}, '', url.toString());
                            
                            // 刷新页面以自动加载位置
                            location.reload();
                        }, function(error) {
                            console.error('地理定位失败:', error);
                        });
                    }
                }
                </script>
                
                <button id="get-loc-btn" onclick="getLocation()" style="
                    background-color: #FF6B6B;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                ">🎯 获取我的位置</button>
                """
            components.html(geolocation_js, height=80)
            
            # 添加手动输入功能
            with st.expander("✏️ 手动输入位置"):
                col1, col2 = st.columns(2)
                with col1:
                    user_lat = st.number_input(
                        "我的纬度", 
                        value=35.6762, 
                        format="%.6f", 
                        key="manual_lat"
                    )
                with col2:
                    user_lon = st.number_input(
                        "我的经度", 
                        value=139.6503, 
                        format="%.6f", 
                        key="manual_lon"
                    )
                
                if st.button("显示位置", key="use_manual_location"):
                    st.session_state['user_location'] = {'lat': user_lat, 'lon': user_lon}
                    st.rerun()
            
            # 删除位置按钮
            if 'user_location' in st.session_state:
                if st.button("❌ 删除我的位置", key="clear_location"):
                    del st.session_state['user_location']
                    st.rerun()
            
            layers = []
            
            # 店铺图层（红色）
            store_layer = pdk.Layer(
                'ScatterplotLayer',
                data=geo_df,
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 200]',
                get_radius=100,
                radius_scale=6,
                radius_min_pixels=5,
                radius_max_pixels=30,
                pickable=True,
                auto_highlight=True
            )
            layers.append(store_layer)
            
            # 用户位置图层（蓝色）
            tooltips = []
            if 'user_location' in st.session_state:
                user_loc = st.session_state['user_location']
                user_df = pd.DataFrame([{
                    'lat': user_loc['lat'],
                    'lon': user_loc['lon'],
                    'name': '我的位置'
                }])
                
                user_layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=user_df,
                    get_position='[lon, lat]',
                    get_color='[0, 100, 255, 255]',
                    get_radius=100,
                    radius_scale=8,
                    radius_min_pixels=8,
                    radius_max_pixels=40,
                    pickable=True
                )
                layers.append(user_layer)
                
                # 设置视图中心为用户位置
                center_lat = user_loc['lat']
                center_lon = user_loc['lon']
                zoom_level = 10
            else:
                center_lat = geo_df['lat'].mean()
                center_lon = geo_df['lon'].mean()
                zoom_level = 5
            
            # 使用 pydeck 创建可交互的地图
            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=zoom_level,
                pitch=0
            )
            
            # 设置工具提示，鼠标悬停时显示店铺信息
            tooltip = {
                "html": "<b>🏪 {Store Name}</b><br/>📍 {Address}<br/><b>{name}</b>",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white",
                    "fontSize": "14px",
                    "padding": "10px",
                    "borderRadius": "5px"
                }
            }
            
            deck = pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=tooltip
            )
            
            st.pydeck_chart(deck, height=800)
            
            # 图例说明
            legend_col1, legend_col2 = st.columns(2)
            with legend_col1:
                st.markdown("🔴 **红色圆点** = 店铺位置")
            with legend_col2:
                if 'user_location' in st.session_state:
                    st.markdown("🔵 **蓝色圆点** = 我的位置")
            
            st.info("💡 将鼠标悬停在圆点上查看详细信息")
    
    else:
        # 没有坐标数据，显示获取按钮
        if st.button("🗺️ 获取店铺位置"):
            with st.spinner("正在获取店铺地理位置..."):
                geo_df = geocode_addresses(store_df, api_key)
                if not geo_df.empty:
                    save_store_data_with_coords(geo_df)
                    load_store_data.clear()
                    st.rerun()
    

if __name__ == "__main__":
    main()
