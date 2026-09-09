import base64
import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tra cứu tủ đổi pin V-Green",
    page_icon="🔋",
    layout="wide"
)

# ==================== CÀI ĐẶT HÌNH NỀN TỦ V-GREEN ====================
def set_vgreen_background():
    local_img_candidates = ["background_vgreen.jpg", "background_vgreen.png", "vgreen.jpg", "vgreen.png"]
    local_img_path = next((p for p in local_img_candidates if os.path.exists(p)), None)

    if local_img_path:
        with open(local_img_path, "rb") as img_file:
            encoded_img = base64.b64encode(img_file.read()).decode()
            bg_css = f'url("data:image/png;base64,{encoded_img}")'
    else:
        online_url = "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?auto=format&fit=crop&w=1920&q=80"
        bg_css = f'url("{online_url}")'

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(10, 18, 26, 0.88), rgba(10, 18, 26, 0.90)), {bg_css};
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        h1, h2, h3, p, span, label {{
            color: #f8fafc !important;
        }}

        /* 1. TRIỆT TIÊU ICON CON MẮT TRONG Ô PASSWORD CỦA STREAMLIT */
        button[aria-label="Show password"], 
        button[aria-label="Hide password"],
        div[data-testid="stTextInput"] button {{
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }}

        /* 2. TRIỆT TIÊU NÚT REVEAL PASSWORD CỦA TRÌNH DUYỆT (EDGE / CHROME / SAFARI) */
        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_vgreen_background()

# ==================== BẢO MẬT & ĐĂNG NHẬP ====================
APP_PASSWORD = "123456"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False

# Xử lý khi chưa đăng nhập
if not st.session_state.authenticated:
    col_l, col_center, col_r = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.88); padding: 26px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 8px 32px rgba(0,0,0,0.6); text-align: center; margin-bottom: 20px;">
                <h2 style="color: #00e599; margin-bottom: 8px;">🔒 XÁC THỰC TRUY CẬP</h2>
                <p style="color: #cbd5e1; font-size: 14px; margin: 0;">Vui lòng nhập mật khẩu chính xác để vào hệ thống tra cứu</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Hiển thị thông báo nếu lần trước nhập sai
        if st.session_state.login_error:
            st.error("❌ Mật khẩu không chính xác! Vui lòng nhập lại.")

        # Dùng st.form để khi bấm Đăng nhập hoặc Enter nếu sai sẽ tự làm mới (reset) ô nhập
        with st.form("login_form", clear_on_submit=True):
            entered_password = st.text_input(
                "Mật khẩu truy cập:",
                type="password",
                placeholder="Nhập mật khẩu...",
                help="Mật khẩu được mã hóa ẩn tuyệt đối"
            )
            submit_btn = st.form_submit_button("🔓 Mở khóa", type="primary", use_container_width=True)

            if submit_btn:
                if entered_password == APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.login_error = False
                    st.rerun()
                else:
                    st.session_state.authenticated = False
                    st.session_state.login_error = True
                    st.rerun()  # Load lại trang, ô mật khẩu tự động bị xóa trắng bắt nhập lại

    st.stop()  # Ngăn chặn toàn bộ code ứng dụng bên dưới thực thi nếu chưa nhập đúng mật khẩu

# ==================== GIAO DIỆN CHÍNH (KHI ĐÃ ĐĂNG NHẬP ĐÚNG) ====================
header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    st.title("🔋 Tra cứu khoảng cách tủ đổi pin V-Green gần nhất")
with header_col2:
    st.write("")
    if st.button("🔒 Đăng xuất", type="secondary"):
        st.session_state.authenticated = False
        st.session_state.login_error = False
        st.rerun()

# ==================== KHU VỰC BẢN ĐỒ & ĐỊNH VỊ GPS ====================
st.markdown("### 🗺️ Bản đồ & Định vị vị trí đang đứng")
st.caption("Bấm nút **'Lấy vị trí hiện tại của tôi (GPS)'** để thiết bị tự định vị tọa độ bạn đang đứng, hoặc click trực tiếp lên bản đồ.")

map_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; background: transparent; font-family: sans-serif; }
        #map { height: 350px; width: 100%; border-radius: 8px; border: 1px solid #334155; }
        .control-panel {
            margin-top: 8px;
            padding: 10px 14px;
            background: #0f172a;
            color: #38bdf8;
            border-radius: 6px;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            border: 1px solid #1e293b;
        }
        .btn-gps {
            background: #2563eb;
            color: white;
            border: none;
            padding: 7px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: 0.2s;
        }
        .btn-gps:hover { background: #1d4ed8; }
        .btn-copy {
            background: #059669;
            color: white;
            border: none;
            padding: 7px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            transition: 0.2s;
        }
        .btn-copy:hover { background: #047857; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="control-panel">
        <div>
            <span>📍 Tọa độ xác định: <strong id="coord-text" style="color: #4ade80;">10.734728, 106.663666</strong></span>
            <div id="status-msg" style="font-size: 12px; color: #94a3b8; margin-top: 3px;">(Chưa lấy GPS hoặc đang dùng vị trí mặc định)</div>
        </div>
        <div style="display: flex; gap: 8px;">
            <button class="btn-gps" onclick="locateMe()">🎯 Lấy vị trí hiện tại của tôi (GPS)</button>
            <button class="btn-copy" onclick="copyPickedCoord()">📋 Copy tọa độ</button>
        </div>
    </div>

    <script>
        var initLat = 10.734728;
        var initLng = 106.663666;

        var map = L.map('map').setView([initLat, initLng], 14);

        L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            maxZoom: 20,
            attribution: '© Google Maps'
        }).addTo(map);

        var marker = L.marker([initLat, initLng], {draggable: true}).addTo(map);
        var accuracyCircle = null;

        function updateCoordUI(lat, lng, accuracyMeters) {
            var latFormatted = lat.toFixed(6);
            var lngFormatted = lng.toFixed(6);
            var coordStr = latFormatted + ", " + lngFormatted;
            document.getElementById('coord-text').innerText = coordStr;

            var statusEl = document.getElementById('status-msg');
            if (accuracyMeters !== undefined) {
                statusEl.innerText = "✅ Đã xác định GPS chính xác (sai số ~" + Math.round(accuracyMeters) + "m)";
                statusEl.style.color = "#4ade80";
            } else {
                statusEl.innerText = "👉 Đã chọn điểm thủ công trên bản đồ";
                statusEl.style.color = "#38bdf8";
            }
        }

        function locateMe() {
            var statusEl = document.getElementById('status-msg');
            statusEl.innerText = "⏳ Đang tìm tín hiệu GPS vệ tinh...";
            statusEl.style.color = "#facc15";

            if (!navigator.geolocation) {
                alert("Trình duyệt không hỗ trợ Geolocation/GPS.");
                return;
            }

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    var curLat = position.coords.latitude;
                    var curLng = position.coords.longitude;
                    var acc = position.coords.accuracy;

                    map.setView([curLat, curLng], 16);
                    marker.setLatLng([curLat, curLng]);

                    if (accuracyCircle) {
                        map.removeLayer(accuracyCircle);
                    }
                    accuracyCircle = L.circle([curLat, curLng], {
                        radius: acc,
                        color: '#2563eb',
                        fillColor: '#3b82f6',
                        fillOpacity: 0.18
                    }).addTo(map);

                    updateCoordUI(curLat, curLng, acc);

                    var coordStr = curLat.toFixed(6) + ", " + curLng.toFixed(6);
                    navigator.clipboard.writeText(coordStr);
                    alert("📍 Đã xác định vị trí:\\n" + coordStr + "\\n(Đã tự động Copy)");
                },
                function(error) {
                    var msg = "Lỗi khi lấy vị trí: ";
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            msg += "Bạn đã từ chối cấp quyền vị trí. Vui lòng bật lại quyền vị trí trên trình duyệt.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            msg += "Không có tín hiệu GPS.";
                            break;
                        case error.TIMEOUT:
                            msg += "Quá thời gian phản hồi GPS.";
                            break;
                        default:
                            msg += error.message;
                    }
                    statusEl.innerText = "❌ " + msg;
                    statusEl.style.color = "#f87171";
                    alert(msg);
                },
                { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
            );
        }

        map.on('click', function(e) {
            marker.setLatLng(e.latlng);
            if (accuracyCircle) { map.removeLayer(accuracyCircle); }
            updateCoordUI(e.latlng.lat, e.latlng.lng);
        });

        marker.on('dragend', function(e) {
            var pos = marker.getLatLng();
            if (accuracyCircle) { map.removeLayer(accuracyCircle); }
            updateCoordUI(pos.lat, pos.lng);
        });

        function copyPickedCoord() {
            var coordStr = document.getElementById('coord-text').innerText;
            navigator.clipboard.writeText(coordStr).then(function() {
                alert("Đã copy tọa độ: " + coordStr);
            });
        }
    </script>
</body>
</html>
"""

st.components.v1.html(map_html, height=430, scrolling=False)

# ==================== ĐỌC DỮ LIỆU EXCEL ====================
@st.cache_data
def load_data(file_source):
    df = pd.read_excel(file_source, sheet_name="Data", skiprows=1)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    data_file = "DATA Trạm.xlsx"
    df_raw = load_data(data_file)
    df_clean = df_raw.copy()

    def get_col_name(df, possible_names, fallback_index):
        for name in possible_names:
            for col in df.columns:
                if name.lower() == str(col).lower():
                    return col
        if fallback_index < len(df.columns):
            return df.columns[fallback_index]
        return None

    col_phan_loai = get_col_name(df_clean, ['Phân loại', 'Phan loai'], 1)
    col_ten_tram = get_col_name(df_clean, ['Tên trạm', 'Ten tram'], 6)
    col_ma_tram = get_col_name(df_clean, ['Mã trạm theo SU', 'Mã trạm'], 5)
    col_trang_thai = get_col_name(df_clean, ['Trạng thái', 'Trang thai'], 14)
    col_tinh = get_col_name(df_clean, ['Tỉnh', 'Tinh'], 17)
    col_mien_dia_ly = get_col_name(df_clean, ['Miền địa lý', 'Mien dia ly'], 18)
    col_lat = get_col_name(df_clean, ['Lat', 'LAT', 'Latitude'], 19)
    col_long = get_col_name(df_clean, ['Long', 'LONG', 'Longitude'], 20)

    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors='coerce')
    df_clean[col_long] = pd.to_numeric(df_clean[col_long], errors='coerce')
    df_clean = df_clean.dropna(subset=[col_lat, col_long])

    def extract_loai_tram(row):
        return str(row[col_phan_loai]).strip() if col_phan_loai in row and pd.notna(row[col_phan_loai]) else ""

    df_clean['Loại Trạm Temp'] = df_clean.apply(extract_loai_tram, axis=1)

    # ==================== NHẬP LIỆU & TÍNH TOÁN ====================
    st.markdown("### 📍 Nhập hoặc Dán Tọa độ cần tra cứu")
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        raw_coord = st.text_input(
            "Tọa độ LATITUDE, LONGITUDE:",
            value="10.734728, 106.663666",
            placeholder="Ví dụ: 10.734728, 106.663666"
        )
    with col_input2:
        threshold_m = st.number_input(
            "Ngưỡng đạt khoảng cách (m):",
            min_value=1.0,
            value=500.0,
            step=50.0,
            help="Khoảng cách <= giá trị này sẽ tính là ĐẠT"
        )

    if st.button("🚀 Tính khoảng cách", type="primary"):
        clean_input = raw_coord.strip().replace('\t', ',')

        if ',' in clean_input:
            parts = [p.strip() for p in clean_input.split(',')]
        else:
            parts = clean_input.split()

        if len(parts) >= 2:
            try:
                input_lat = float(parts[0])
                input_lng = float(parts[1])

                with st.spinner('Đang tính toán khoảng cách...'):
                    lat1 = np.radians(input_lat)
                    lon1 = np.radians(input_lng)
                    lat2 = np.radians(df_clean[col_lat].values.astype(float))
                    lon2 = np.radians(df_clean[col_long].values.astype(float))

                    # Haversine
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
                    c = 2 * np.arcsin(np.sqrt(a))
                    r = 6371000

                    df_clean['Khoảng cách (m)'] = c * r
                    df_sorted = df_clean.sort_values(by='Khoảng cách (m)').copy()

                    def combine_unique(series):
                        vals = [str(v).strip() for v in series if pd.notna(v) and str(v).strip() not in ['', '-']]
                        seen = set()
                        unique_vals = []
                        for v in vals:
                            if v not in seen:
                                seen.add(v)
                                unique_vals.append(v)
                        return " & ".join(unique_vals) if unique_vals else "-"

                    group_cols = [col_ma_tram, col_lat, col_long]
                    existing_group_cols = [c for c in group_cols if c in df_sorted.columns]

                    grouped = df_sorted.groupby(existing_group_cols, as_index=False, sort=False).agg({
                        'Khoảng cách (m)': 'first',
                        col_ten_tram: 'first',
                        col_trang_thai: combine_unique,
                        'Loại Trạm Temp': combine_unique,
                        col_tinh: 'first',
                        col_mien_dia_ly: 'first',
                    })

                    top5 = grouped.head(5).copy()
                    top5['Khoảng cách (m)'] = top5['Khoảng cách (m)'].round(2)
                    top5['Kết quả'] = top5['Khoảng cách (m)'].apply(
                        lambda d: "Đạt" if d <= threshold_m else "Không đạt"
                    )

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")

                    # Cột Tên Trạm nằm ngay sau Mã Trạm
                    html_code = """
                    <style>
                        .table-container {
                            width: 100%;
                            overflow-x: auto;
                            margin: 10px 0;
                            border-radius: 8px;
                            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
                        }
                        .custom-table {
                            width: 100%;
                            border-collapse: collapse;
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                            font-size: 14px;
                            color: #f1f5f9;
                        }
                        .custom-table th {
                            background-color: rgba(22, 33, 49, 0.95);
                            color: #00e599;
                            text-align: left;
                            padding: 12px 14px;
                            border: 1px solid rgba(71, 85, 105, 0.6);
                            white-space: nowrap;
                        }
                        .custom-table td {
                            padding: 10px 12px;
                            border: 1px solid rgba(71, 85, 105, 0.4);
                            background-color: rgba(13, 22, 33, 0.85);
                            vertical-align: middle;
                        }
                        .custom-table tr:hover td {
                            background-color: rgba(22, 33, 49, 0.9);
                        }
                        .copy-btn {
                            background-color: #059669;
                            color: white;
                            border: none;
                            padding: 6px 10px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-weight: 600;
                            font-size: 12px;
                            white-space: nowrap;
                        }
                        .map-link-btn {
                            background-color: #0284c7;
                            color: white !important;
                            text-decoration: none;
                            padding: 6px 10px;
                            border-radius: 4px;
                            font-weight: 600;
                            font-size: 12px;
                            display: inline-block;
                            white-space: nowrap;
                        }
                        .map-link-btn:hover { background-color: #0369a1; }
                        .badge-pass {
                            background-color: #10b981;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            display: inline-block;
                        }
                        .badge-fail {
                            background-color: #ef4444;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            display: inline-block;
                        }
                    </style>

                    <script>
                    function fallbackCopy(text, btn) {
                        var textArea = document.createElement("textarea");
                        textArea.value = text;
                        document.body.appendChild(textArea);
                        textArea.focus();
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        showCopied(btn);
                    }

                    function showCopied(btn) {
                        var originalText = btn.innerHTML;
                        btn.innerHTML = "✅ Đã Copy!";
                        btn.style.backgroundColor = "#10b981";
                        setTimeout(function() {
                            btn.innerHTML = originalText;
                            btn.style.backgroundColor = "#059669";
                        }, 1500);
                    }

                    function copyToClipboard(text, btn) {
                        if (navigator.clipboard && window.isSecureContext) {
                            navigator.clipboard.writeText(text).then(function() {
                                showCopied(btn);
                            }).catch(function() {
                                fallbackCopy(text, btn);
                            });
                        } else {
                            fallbackCopy(text, btn);
                        }
                    }
                    </script>

                    <div class="table-container">
                        <table class="custom-table">
                            <thead>
                                <tr>
                                    <th style="width: 40px; text-align: center;">STT</th>
                                    <th>Kết quả</th>
                                    <th>Khoảng cách (m)</th>
                                    <th>Mã Trạm</th>
                                    <th>Tên Trạm</th>
                                    <th>Trạng Thái</th>
                                    <th>Loại Trạm</th>
                                    <th>Tỉnh</th>
                                    <th>Miền</th>
                                    <th>Lat</th>
                                    <th>Long</th>
                                    <th style="text-align: center;">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody>
                    """

                    for idx, (_, row) in enumerate(top5.iterrows()):
                        lat_val = str(row[col_lat])
                        long_val = str(row[col_long])
                        coord_str = f"{lat_val}, {long_val}"
                        loai_tram_val = str(row['Loại Trạm Temp']) if row['Loại Trạm Temp'] != "" else "-"
                        gmaps_link = f"https://www.google.com/maps?q={lat_val},{long_val}"

                        badge_html = '<span class="badge-pass">✔ Đạt</span>' if row['Kết quả'] == "Đạt" else '<span class="badge-fail">✖ Không đạt</span>'

                        html_code += f"""
                                <tr>
                                    <td style="text-align: center; color: #94a3b8; font-weight: bold;">{idx + 1}</td>
                                    <td style="text-align: center;">{badge_html}</td>
                                    <td><b>{row['Khoảng cách (m)']}</b></td>
                                    <td>{row[col_ma_tram]}</td>
                                    <td>{row[col_ten_tram]}</td>
                                    <td>{row[col_trang_thai]}</td>
                                    <td>{loai_tram_val}</td>
                                    <td>{row[col_tinh]}</td>
                                    <td>{row[col_mien_dia_ly]}</td>
                                    <td>{lat_val}</td>
                                    <td>{long_val}</td>
                                    <td style="text-align: center; white-space: nowrap;">
                                        <button class="copy-btn" onclick="copyToClipboard('{coord_str}', this)">📋 Copy</button>
                                        <a class="map-link-btn" href="{gmaps_link}" target="_blank">🗺️ Mở Maps</a>
                                    </td>
                                </tr>
                        """

                    html_code += """
                            </tbody>
                        </table>
                    </div>
                    """

                    st.components.v1.html(html_code, height=450, scrolling=True)

            except ValueError:
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng kiểm tra lại số liệu.")
        else:
            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ.")

except FileNotFoundError:
    st.error("⚠️ Không tìm thấy file 'DATA Trạm.xlsx'. Hãy đảm bảo file này nằm cùng thư mục.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi: {e}")
