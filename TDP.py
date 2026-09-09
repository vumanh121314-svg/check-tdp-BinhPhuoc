import base64
import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tra cứu trạm V-Green",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================== TỐI ƯU GIAO DIỆN & HÌNH NỀN ====================
def setup_ui_and_background():
    local_img_candidates = [
        "background_vgreen.jpg",
        "background_vgreen.png",
        "vgreen.jpg",
        "vgreen.png",
    ]
    local_img_path = next(
        (p for p in local_img_candidates if os.path.exists(p)), None
    )

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
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        h1, h2, h3, h4, h5, p, span, label {{
            color: #f8fafc !important;
        }}

        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}

        button[aria-label="Show password"], 
        button[aria-label="Hide password"],
        div[data-testid="stTextInput"] button {{
            display: none !important;
            visibility: hidden !important;
        }}

        input[type="password"]::-ms-reveal,
        input[type="password"]::-ms-clear {{
            display: none !important;
        }}

        button[kind="primary"], button[kind="secondary"] {{
            min-height: 44px !important;
            font-size: 15px !important;
            border-radius: 8px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


setup_ui_and_background()

# ==================== BẢO MẬT & ĐĂNG NHẬP ====================
APP_PASSWORD = "123456"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_error" not in st.session_state:
    st.session_state.login_error = False

if not st.session_state.authenticated:
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.92); padding: 24px; border-radius: 12px; border: 1px solid #334155; text-align: center; margin-bottom: 16px;">
                <h2 style="color: #00e599; font-size: 22px; margin-bottom: 8px;">🔒 XÁC THỰC TRUY CẬP</h2>
                <p style="color: #94a3b8; font-size: 13px; margin: 0;">Nhập mật khẩu để mở ứng dụng tra cứu trạm V-Green</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.login_error:
            st.error("❌ Mật khẩu không chính xác! Vui lòng thử lại.")

        with st.form("login_form", clear_on_submit=True):
            entered_password = st.text_input(
                "Mật khẩu:", type="password", placeholder="Nhập mật khẩu..."
            )
            submit_btn = st.form_submit_button(
                "🔓 Mở khóa", type="primary", use_container_width=True
            )

            if submit_btn:
                if entered_password == APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.login_error = False
                    st.rerun()
                else:
                    st.session_state.authenticated = False
                    st.session_state.login_error = True
                    st.rerun()

    st.stop()

# ==================== GIAO DIỆN CHÍNH ====================
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown(
        "<h2 style='margin: 0; color: #00e599;'>🔋 Tra cứu tủ đổi pin V-Green</h2>",
        unsafe_allow_html=True,
    )
with header_col2:
    if st.button("🔒 Đăng xuất", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.login_error = False
        st.rerun()

# ==================== BẢN ĐỒ & ĐỊNH VỊ GPS ====================
st.markdown("##### 🗺️ Bản đồ & Định vị vị trí")

map_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; background: transparent; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        #map { height: 320px; width: 100%; border-radius: 8px; border: 1px solid #334155; }
        .control-panel {
            margin-top: 8px;
            padding: 10px 12px;
            background: #0f172a;
            color: #38bdf8;
            border-radius: 6px;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            border: 1px solid #1e293b;
        }
        .btn-group { display: flex; gap: 6px; width: 100%; }
        @media (min-width: 600px) {
            .btn-group { width: auto; }
        }
        .btn-action {
            flex: 1;
            border: none;
            padding: 9px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 13px;
            text-align: center;
            transition: 0.2s;
        }
        .btn-gps { background: #2563eb; color: white; }
        .btn-gps:active { background: #1d4ed8; }
        .btn-copy { background: #059669; color: white; }
        .btn-copy:active { background: #047857; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="control-panel">
        <div style="flex: 1; min-width: 200px;">
            <div>📍 Tọa độ chọn: <strong id="coord-text" style="color: #4ade80;">10.734728, 106.663666</strong></div>
            <div id="status-msg" style="font-size: 11px; color: #94a3b8; margin-top: 2px;">(Kéo thả ghim hoặc bấm nút dưới để lấy GPS)</div>
        </div>
        <div class="btn-group">
            <button class="btn-action btn-gps" onclick="locateMe()">🎯 Vị trí của tôi</button>
            <button class="btn-action btn-copy" onclick="copyPickedCoord()">📋 Copy tọa độ</button>
        </div>
    </div>

    <script>
        var initLat = 10.734728;
        var initLng = 106.663666;

        var map = L.map('map', { tap: true }).setView([initLat, initLng], 14);

        L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            maxZoom: 20,
            attribution: '© Google Maps'
        }).addTo(map);

        var marker = L.marker([initLat, initLng], {draggable: true}).addTo(map);
        var accuracyCircle = null;

        function updateCoordUI(lat, lng, accuracyMeters) {
            var coordStr = lat.toFixed(6) + ", " + lng.toFixed(6);
            document.getElementById('coord-text').innerText = coordStr;
            var statusEl = document.getElementById('status-msg');
            if (accuracyMeters !== undefined) {
                statusEl.innerText = "✅ Đã lấy GPS (sai số ~" + Math.round(accuracyMeters) + "m)";
                statusEl.style.color = "#4ade80";
            } else {
                statusEl.innerText = "👉 Đã chọn điểm trên bản đồ";
                statusEl.style.color = "#38bdf8";
            }
        }

        function locateMe() {
            var statusEl = document.getElementById('status-msg');
            statusEl.innerText = "⏳ Đang kết nối GPS...";
            statusEl.style.color = "#facc15";

            if (!navigator.geolocation) {
                alert("Thiết bị không hỗ trợ Geolocation.");
                return;
            }

            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    var curLat = pos.coords.latitude;
                    var curLng = pos.coords.longitude;
                    var acc = pos.coords.accuracy;

                    map.setView([curLat, curLng], 16);
                    marker.setLatLng([curLat, curLng]);

                    if (accuracyCircle) { map.removeLayer(accuracyCircle); }
                    accuracyCircle = L.circle([curLat, curLng], {
                        radius: acc,
                        color: '#2563eb',
                        fillColor: '#3b82f6',
                        fillOpacity: 0.2
                    }).addTo(map);

                    updateCoordUI(curLat, curLng, acc);
                    var coordStr = curLat.toFixed(6) + ", " + curLng.toFixed(6);
                    navigator.clipboard.writeText(coordStr);
                    alert("📍 Đã lấy vị trí:\\n" + coordStr + "\\n(Đã copy vào bộ nhớ tạm)");
                },
                function(err) {
                    statusEl.innerText = "❌ Không lấy được GPS (Hãy bật vị trí trình duyệt)";
                    statusEl.style.color = "#f87171";
                    alert("Vui lòng cho phép quyền truy cập Vị trí (GPS) trên trình duyệt.");
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
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
                alert("Đã sao chép: " + coordStr);
            });
        }
    </script>
</body>
</html>
"""

st.components.v1.html(map_html, height=410, scrolling=False)


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

    def get_col_name(df, possible_names, fallback_index=None):
        for name in possible_names:
            for col in df.columns:
                if name.lower() == str(col).lower():
                    return col
        if fallback_index is not None and fallback_index < len(df.columns):
            return df.columns[fallback_index]
        return None

    col_phan_loai = get_col_name(df_clean, ["Phân loại", "Phan loai"], 1)
    col_ten_tram = get_col_name(df_clean, ["Tên trạm", "Ten tram"], 6)
    col_ma_tram = get_col_name(df_clean, ["Mã trạm theo SU", "Mã trạm"], 5)
    col_trang_thai = get_col_name(df_clean, ["Trạng thái", "Trang thai"], 14)
    col_tinh = get_col_name(df_clean, ["Tỉnh", "Tinh"], 17)
    col_mien_dia_ly = get_col_name(df_clean, ["Miền địa lý", "Mien dia ly"], 18)
    col_lat = get_col_name(df_clean, ["Lat", "LAT", "Latitude"], 19)
    col_long = get_col_name(df_clean, ["Long", "LONG", "Longitude"], 20)

    if not col_lat or not col_long:
        st.error("Không tìm thấy cột Tọa độ (Lat/Long) trong file dữ liệu.")
        st.stop()

    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors="coerce")
    df_clean[col_long] = pd.to_numeric(df_clean[col_long], errors="coerce")
    df_clean = df_clean.dropna(subset=[col_lat, col_long])

    def extract_loai_tram(row):
        return (
            str(row[col_phan_loai]).strip()
            if col_phan_loai and col_phan_loai in row and pd.notna(row[col_phan_loai])
            else ""
        )

    df_clean["Loại Trạm Temp"] = df_clean.apply(extract_loai_tram, axis=1)

    # ==================== NHẬP LIỆU & TÍNH TOÁN ====================
    st.markdown("##### 📍 Nhập tọa độ & Ngưỡng kiểm tra")
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        raw_coord = st.text_input(
            "Tọa độ (Lat, Long):",
            value="10.734728, 106.663666",
            placeholder="Ví dụ: 10.734728, 106.663666",
        )
    with col_input2:
        threshold_m = st.number_input(
            "Ngưỡng Đạt (m):", min_value=1.0, value=500.0, step=50.0
        )

    if st.button(
        "🚀 Tính khoảng cách", type="primary", use_container_width=True
    ):
        clean_input = raw_coord.strip().replace("\t", ",")
        parts = (
            [p.strip() for p in clean_input.split(",")]
            if "," in clean_input
            else clean_input.split()
        )

        if len(parts) >= 2:
            try:
                input_lat = float(parts[0])
                input_lng = float(parts[1])

                with st.spinner("Đang tính khoảng cách đến các trạm..."):
                    lat1 = np.radians(input_lat)
                    lon1 = np.radians(input_lng)
                    lat2 = np.radians(df_clean[col_lat].values.astype(float))
                    lon2 = np.radians(df_clean[col_long].values.astype(float))

                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = (
                        np.sin(dlat / 2) ** 2
                        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
                    )
                    c = 2 * np.arcsin(np.sqrt(a))
                    r = 6371000

                    df_clean["Khoảng cách (m)"] = c * r
                    df_sorted = df_clean.sort_values(
                        by="Khoảng cách (m)"
                    ).copy()

                    def combine_unique(series):
                        vals = [
                            str(v).strip()
                            for v in series
                            if pd.notna(v) and str(v).strip() not in ["", "-"]
                        ]
                        seen = set()
                        unique_vals = []
                        for v in vals:
                            if v not in seen:
                                seen.add(v)
                                unique_vals.append(v)
                        return (
                            " & ".join(unique_vals) if unique_vals else "-"
                        )

                    group_cols = [
                        c
                        for c in [col_ma_tram, col_lat, col_long]
                        if c and c in df_sorted.columns
                    ]

                    grouped = df_sorted.groupby(
                        group_cols, as_index=False, sort=False
                    ).agg(
                        {
                            "Khoảng cách (m)": "first",
                            col_ten_tram: "first",
                            col_trang_thai: combine_unique,
                            "Loại Trạm Temp": combine_unique,
                            col_tinh: "first",
                            col_mien_dia_ly: "first",
                        }
                    )

                    top5 = grouped.head(5).copy()
                    top5["Khoảng cách (m)"] = top5["Khoảng cách (m)"].round(1)
                    top5["Kết quả"] = top5["Khoảng cách (m)"].apply(
                        lambda d: "Đạt" if d <= threshold_m else "Không đạt"
                    )

                    st.markdown("### 🎯 Kết quả 5 trạm gần nhất")

                    # GIAO DIỆN HIỂN THỊ
                    html_code = """
                    <style>
                        * { box-sizing: border-box; }
                        .custom-table {
                            width: 100%;
                            border-collapse: collapse;
                            font-size: 13px;
                            color: #f1f5f9;
                        }
                        .custom-table th {
                            background-color: rgba(22, 33, 49, 0.95);
                            color: #00e599;
                            text-align: left;
                            padding: 10px 12px;
                            border: 1px solid rgba(71, 85, 105, 0.6);
                            white-space: nowrap;
                        }
                        .custom-table td {
                            padding: 10px 12px;
                            border: 1px solid rgba(71, 85, 105, 0.4);
                            background-color: rgba(13, 22, 33, 0.85);
                        }
                        .btn-s {
                            border: none;
                            padding: 6px 10px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: 600;
                            text-decoration: none;
                            cursor: pointer;
                            display: inline-block;
                        }
                        .btn-copy-s { background: #059669; color: white; }
                        .btn-map-s { background: #0284c7; color: white !important; margin-left: 4px; }
                        .badge-pass { background: #10b981; color: white; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
                        .badge-fail { background: #ef4444; color: white; padding: 3px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
                        .mobile-card {
                            display: none;
                            background: rgba(15, 23, 42, 0.9);
                            border: 1px solid #334155;
                            border-radius: 8px;
                            padding: 12px;
                            margin-bottom: 10px;
                        }
                        @media (max-width: 768px) {
                            .table-container { display: none; }
                            .mobile-card { display: block; }
                        }
                    </style>

                    <script>
                    function copyText(str, btn) {
                        navigator.clipboard.writeText(str).then(function() {
                            var old = btn.innerText;
                            btn.innerText = "✅ Đã chép";
                            setTimeout(function() { btn.innerText = old; }, 1200);
                        });
                    }
                    </script>

                    <div class="table-container" style="overflow-x: auto; border-radius: 8px;">
                        <table class="custom-table">
                            <thead>
                                <tr>
                                    <th>STT</th>
                                    <th>Kết quả</th>
                                    <th>Khoảng cách</th>
                                    <th>Mã Trạm</th>
                                    <th>Tên Trạm</th>
                                    <th>Trạng Thái</th>
                                    <th>Loại Trạm</th>
                                    <th>Tỉnh</th>
                                    <th>Miền</th>
                                    <th>Tọa độ</th>
                                    <th>Thao tác</th>
                                </tr>
                            </thead>
                            <tbody>
                    """

                    cards_html = "<div>"

                    for idx, (_, row) in enumerate(top5.iterrows()):
                        lat_val = str(row[col_lat])
                        long_val = str(row[col_long])
                        coord_str = f"{lat_val}, {long_val}"
                        loai_tram_val = (
                            str(row["Loại Trạm Temp"])
                            if row["Loại Trạm Temp"] != ""
                            else "-"
                        )
                        gmaps_link = (
                            f"https://www.google.com/maps?q={lat_val},{long_val}"
                        )

                        is_pass = row["Kết quả"] == "Đạt"
                        badge = (
                            '<span class="badge-pass">✔ Đạt</span>'
                            if is_pass
                            else '<span class="badge-fail">✖ Không đạt</span>'
                        )

                        html_code += f"""
                            <tr>
                                <td style="text-align: center; color: #94a3b8; font-weight: bold;">{idx + 1}</td>
                                <td>{badge}</td>
                                <td><b>{row['Khoảng cách (m)']} m</b></td>
                                <td>{row.get(col_ma_tram, '-')}</td>
                                <td>{row.get(col_ten_tram, '-')}</td>
                                <td>{row.get(col_trang_thai, '-')}</td>
                                <td>{loai_tram_val}</td>
                                <td>{row.get(col_tinh, '-')}</td>
                                <td>{row.get(col_mien_dia_ly, '-')}</td>
                                <td>{coord_str}</td>
                                <td style="white-space: nowrap;">
                                    <button class="btn-s btn-copy-s" onclick="copyText('{coord_str}', this)">📋 Copy</button>
                                    <a class="btn-s btn-map-s" href="{gmaps_link}" target="_blank">🗺️ Maps</a>
                                </td>
                            </tr>
                        """

                        cards_html += f"""
                        <div class="mobile-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <strong style="color: #38bdf8; font-size: 15px;">#{idx + 1}. {row.get(col_ten_tram, '-')}</strong>
                                {badge}
                            </div>
                            <div style="font-size: 13px; line-height: 1.6; color: #cbd5e1;">
                                <div>📏 Khoảng cách: <b style="color: #facc15;">{row['Khoảng cách (m)']} m</b></div>
                                <div>🏷️ Mã trạm: <b>{row.get(col_ma_tram, '-')}</b> | Loại: {loai_tram_val}</div>
                                <div>📍 Tỉnh/Miền: {row.get(col_tinh, '-')} ({row.get(col_mien_dia_ly, '-')})</div>
                                <div style="font-size: 12px; color: #94a3b8;">🌐 Tọa độ: {coord_str}</div>
                            </div>
                            <div style="margin-top: 8px; display: flex; gap: 8px;">
                                <button class="btn-s btn-copy-s" style="flex: 1; padding: 7px;" onclick="copyText('{coord_str}', this)">📋 Copy</button>
                                <a class="btn-s btn-map-s" style="flex: 1; padding: 7px; text-align: center;" href="{gmaps_link}" target="_blank">🗺️ Mở Maps</a>
                            </div>
                        </div>
                        """

                    html_code += "</tbody></table></div>"
                    cards_html += "</div>"

                    full_rendered_html = html_code + cards_html
                    st.components.v1.html(
                        full_rendered_html, height=520, scrolling=True
                    )

            except ValueError:
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng kiểm tra lại.")
        else:
            st.warning("Vui lòng nhập đầy đủ Vĩ độ và Kinh độ.")

except FileNotFoundError:
    st.error("⚠️ Không tìm thấy file 'DATA Trạm.xlsx' trong cùng thư mục chạy ứng dụng.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi khi đọc/xử lý dữ liệu: {e}")
