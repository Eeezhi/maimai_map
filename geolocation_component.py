import streamlit as st
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "geolocation",
        url="http://localhost:3000",
    )
else:
    parent_dir = __file__.split('\\')
    build_dir = parent_dir[:-1]
    build_dir = '\\'.join(build_dir) + "\\geolocation_build"
    _component_func = components.declare_component(
        "geolocation",
        path=build_dir
    )

def geolocation_component(key=None):
    """
    获取用户的地理位置
    返回: {'latitude': float, 'longitude': float, 'accuracy': float} 或 None
    """
    component_value = _component_func(key=key)
    return component_value

def get_user_location():
    """
    简化版：直接获取用户位置并存储到 session_state
    """
    html_component = """
    <html>
    <body>
    <button id="get-location-btn" style="
        background-color: #FF6B6B;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
    ">🎯 获取我的位置</button>
    
    <div id="location-info" style="margin-top: 10px; font-size: 14px; line-height: 1.8;">
        准备就绪...
    </div>
    
    <script>
    function getLocation() {
        const btn = document.getElementById('get-location-btn');
        const info = document.getElementById('location-info');
        
        btn.disabled = true;
        btn.innerHTML = '🔄 获取中...';
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    
                    // 保存到 localStorage
                    localStorage.setItem('user_lat', lat);
                    localStorage.setItem('user_lon', lon);
                    localStorage.setItem('user_accuracy', accuracy);
                    localStorage.setItem('location_timestamp', new Date().getTime());
                    
                    info.innerHTML = 
                        '✅ 已获取位置<br/>' +
                        '纬度: ' + lat.toFixed(6) + '<br/>' +
                        '经度: ' + lon.toFixed(6) + '<br/>' +
                        '精度: ±' + accuracy.toFixed(0) + '米<br/><br/>' +
                        '<span style="color: #4CAF50; font-weight: bold;">页面正在自动加载...</span>';
                    
                    btn.innerHTML = '✅ 位置已获取';
                    btn.style.backgroundColor = '#4CAF50';
                    
                    // 延迟刷新页面
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                },
                function(error) {
                    let msg = '❌ 获取位置失败';
                    if (error.code === 1) msg += '：用户拒绝权限';
                    else if (error.code === 2) msg += '：无法获取位置';
                    else if (error.code === 3) msg += '：请求超时';
                    
                    info.innerHTML = msg;
                    btn.disabled = false;
                    btn.innerHTML = '🎯 获取我的位置';
                }
            );
        } else {
            info.innerHTML = '❌ 浏览器不支持地理定位';
            btn.disabled = false;
            btn.innerHTML = '🎯 获取我的位置';
        }
    }
    
    // 检查是否已有位置
    const savedLat = localStorage.getItem('user_lat');
    const savedLon = localStorage.getItem('user_lon');
    if (savedLat && savedLon) {
        document.getElementById('get-location-btn').style.display = 'none';
        document.getElementById('location-info').innerHTML = 
            '✅ 已获取位置<br/>' +
            '纬度: ' + parseFloat(savedLat).toFixed(6) + '<br/>' +
            '经度: ' + parseFloat(savedLon).toFixed(6) + '<br/><br/>' +
            '<span style="color: green;">位置已自动加载</span>';
    }
    
    document.getElementById('get-location-btn').addEventListener('click', getLocation);
    </script>
    </body>
    </html>
    """
    
    return components.html(html_component, height=180)
