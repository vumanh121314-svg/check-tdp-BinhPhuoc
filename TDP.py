import base64
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tra cứu trạm gần nhất",
    page_icon="📍",
    layout="wide"
)

# ==================== HÀM CÀI ĐẶT BACKGROUND ====================
def set_background(image_url_or_base64=None, is_url=True):
    """
    Hàm phủ hình nền toàn trang có lớp gradient tối (Dark Overlay)
    giúp nền tối om, làm nổi bật chữ và bảng dữ liệu.
    """
    if is_url:
        bg_css = f'url("{image_url_or_base64}")'
    else:
        bg_css = f'url("data:image/png;base64,{image_url_or_base64}")'

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(10, 14, 23, 0.88), rgba(10, 14, 23, 0.92)), {bg_css};
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* Làm cho các khung chữ/tiêu đề hiển thị rõ ràng trên nền */
        h1, h2, h3, p, span, label {{
            color: #f1f5f9 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Sidebar: Cho phép chọn hình nền mặc định hoặc tải ảnh từ máy
with st.sidebar:
    st.header("⚙️ Cài đặt giao diện")
    bg_option = st.radio(
        "Chọn nguồn hình nền:",
        ["Nền công nghệ tối mặc định", "Tải ảnh từ máy", "Dán Link ảnh (URL)"]
    )

    if bg_option == "Nền công nghệ tối mặc định":
        # Ảnh trạm phát sóng / viễn thông phong cách Dark mode
        default_url = "https://images.unsplash.com/photo-1516849841032-87cbac4d88f7?auto=format&fit=crop&w=1920&q=80"
        set_background(default_url, is_url=True)

    elif bg_option == "Tải ảnh từ máy":
        uploaded_bg = st.file_uploader("Tải lên ảnh nền (PNG, JPG):", type=["png", "jpg", "jpeg"])
        if uploaded_bg is not None:
            encoded_img = base64.b64encode(uploaded_bg.read()).decode()
            set_background(encoded_img, is_url=False)
        else:
            # Nếu chưa tải thì dùng nền tối mặc định
            default_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1920&q=80"
            set_background(default_url, is_url=True)

    else:
        custom_url = st.text_input("Dán link ảnh URL:", value="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1920&q=80")
        set_background(custom_url, is_url=True)

# ==================== NỘI DUNG CHÍNH ====================
st.title("📍 Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu Data nền từ file Excel
@st.cache_data
def load_data(file_source):
    df = pd.read_excel(file_source, sheet_name="Data", skiprows=1)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    data_file = "DATA Trạm.xlsx"
    df_raw = load_data(data_file)
    df_clean = df_raw.copy()

    # Hàm tìm cột linh hoạt theo tên hoặc vị trí dự phòng
    def get_col_name(df, possible_names, fallback_index):
        for name in possible_names:
            for col in df.columns:
                if name.lower() == str(col).lower():
                    return col
        if fallback_index < len(df.columns):
            return df.columns[fallback_index]
        return None

    # Xác định tên các cột dữ liệu
    col_phan_loai = get_col_name(df_clean, ['Phân loại', 'Phan loai'], 1)        # Cột B
    col_ten_tram = get_col_name(df_clean, ['Tên trạm', 'Ten tram'], 6)           # Cột G
    col_ma_tram = get_col_name(df_clean, ['Mã trạm theo SU', 'Mã trạm'], 5)     # Cột F
    col_trang_thai = get_col_name(df_clean, ['Trạng thái', 'Trang thai'], 14)    # Cột O
    col_tinh = get_col_name(df_clean, ['Tỉnh', 'Tinh'], 17)                      # Cột R
    col_mien_dia_ly = get_col_name(df_clean, ['Miền địa lý', 'Mien dia ly'], 18) # Cột S
    col_lat = get_col_name(df_clean, ['Lat', 'LAT', 'Latitude'], 19)             # Cột T
    col_long = get_col_name(df_clean, ['Long', 'LONG', 'Longitude'], 20)         # Cột U

    # Chuyển đổi Lat và Long sang số
    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors='coerce')
    df_clean[col_long] = pd.to_numeric(df_clean[col_long], errors='coerce')

    # Loại bỏ các hàng có tọa độ trống
    df_clean = df_clean.dropna(subset=[col_lat, col_long])

    # Trích xuất Loại Trạm
    def extract_loai_tram(row):
        return str(row[col_phan_loai]).strip() if col_phan_loai in row and pd.notna(row[col_phan_loai]) else ""

    df_clean['Loại Trạm Temp'] = df_clean.apply(extract_loai_tram, axis=1)

    # 2. Giao diện nhập liệu
    col_input1, col_input2 = st.columns([3, 1])
    with col_input1:
        raw_coord = st.text_input(
            "Dán tọa độ LATITUDE, LONGITUDE vào đây:",
            value="10.734728, 106.663666",
            placeholder="Ví dụ: 10.734728, 106.663666"
        )
    with col_input2:
        threshold_m = st.number_input(
            "Ngưỡng đạt khoảng cách (m):",
            min_value=1.0,
            value=500.0,
            step=50.0,
            help="Khoảng cách nhỏ hơn hoặc bằng giá trị này sẽ được tính là ĐẠT"
        )

    if st.button("Tính khoảng cách", type="primary"):
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
                    # Chuyển đổi Radians
                    lat1 = np.radians(input_lat)
                    lon1 = np.radians(input_lng)

                    lat2 = np.radians(df_clean[col_lat].values.astype(float))
                    lon2 = np.radians(df_clean[col_long].values.astype(float))

                    # Công thức Haversine
                    dlat = lat2 - lat1
                    dlon = lon2 - lon1
                    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
                    c = 2 * np.arcsin(np.sqrt(a))
                    r = 6371000  # Bán kính Trái Đất (m)

                    df_clean['Khoảng cách (m)'] = c * r

                    # Sắp xếp theo khoảng cách
                    df_sorted = df_clean.sort_values(by='Khoảng cách (m)').copy()

                    # Gom nhóm dữ liệu trùng
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

                    # Đánh giá Đạt / Không đạt
                    top5['Kết quả'] = top5['Khoảng cách (m)'].apply(
                        lambda d: "Đạt" if d <= threshold_m else "Không đạt"
                    )

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")

                    # HTML & CSS Table trong suốt đồng bộ nền
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
                            background-color: rgba(30, 41, 59, 0.95);
                            color: #38bdf8;
                            text-align: left;
                            padding: 12px 14px;
                            border: 1px solid rgba(71, 85, 105, 0.6);
                            white-space: nowrap;
                        }
                        .custom-table td {
                            padding: 10px 12px;
                            border: 1px solid rgba(71, 85, 105, 0.4);
                            background-color: rgba(15, 23, 42, 0.85);
                            vertical-align: middle;
                        }
                        .custom-table tr:hover td {
                            background-color: rgba(30, 41, 59, 0.9);
                        }
                        .copy-btn {
                            background-color: #0284c7;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-weight: 600;
                            font-size: 13px;
                            white-space: nowrap;
                            transition: 0.2s;
                        }
                        .copy-btn:hover {
                            background-color: #0369a1;
                        }
                        .badge-pass {
                            background-color: #16a34a;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            display: inline-block;
                        }
                        .badge-fail {
                            background-color: #dc2626;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            display: inline-block;
                        }
                    </style>

                    <script>
                    function fallbackCopyTextToClipboard(text, btn) {
                        var textArea = document.createElement("textarea");
                        textArea.value = text;
                        document.body.appendChild(textArea);
                        textArea.focus();
                        textArea.select();
                        try {
                            document.execCommand('copy');
                            showCopied(btn);
                        } catch (err) {
                            console.error('Lỗi copy', err);
                        }
                        document.body.removeChild(textArea);
                    }

                    function showCopied(btn) {
                        var originalText = btn.innerHTML;
                        btn.innerHTML = "✅ Đã Copy!";
                        btn.style.backgroundColor = "#16a34a";
                        setTimeout(function() {
                            btn.innerHTML = originalText;
                            btn.style.backgroundColor = "#0284c7";
                        }, 1500);
                    }

                    function copyToClipboard(text, btn) {
                        if (navigator.clipboard && window.isSecureContext) {
                            navigator.clipboard.writeText(text).then(function() {
                                showCopied(btn);
                            }).catch(function() {
                                fallbackCopyTextToClipboard(text, btn);
                            });
                        } else {
                            fallbackCopyTextToClipboard(text, btn);
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
                                    <th>Tên Trạm</th>
                                    <th>Mã Trạm</th>
                                    <th>Trạng Thái</th>
                                    <th>Loại Trạm</th>
                                    <th>Tỉnh</th>
                                    <th>Miền Địa Lý</th>
                                    <th>Lat</th>
                                    <th>Long</th>
                                    <th style="text-align: center;">Tọa độ Copy</th>
                                </tr>
                            </thead>
                            <tbody>
                    """

                    for idx, (_, row) in enumerate(top5.iterrows()):
                        lat_val = str(row[col_lat])
                        long_val = str(row[col_long])
                        coord_str = f"{lat_val}, {long_val}"
                        loai_tram_val = str(row['Loại Trạm Temp']) if row['Loại Trạm Temp'] != "" else "-"

                        badge_html = '<span class="badge-pass">✔ Đạt</span>' if row['Kết quả'] == "Đạt" else '<span class="badge-fail">✖ Không đạt</span>'

                        html_code += f"""
                                <tr>
                                    <td style="text-align: center; color: #94a3b8; font-weight: bold;">{idx + 1}</td>
                                    <td style="text-align: center;">{badge_html}</td>
                                    <td><b>{row['Khoảng cách (m)']}</b></td>
                                    <td>{row[col_ten_tram]}</td>
                                    <td>{row[col_ma_tram]}</td>
                                    <td>{row[col_trang_thai]}</td>
                                    <td>{loai_tram_val}</td>
                                    <td>{row[col_tinh]}</td>
                                    <td>{row[col_mien_dia_ly]}</td>
                                    <td>{lat_val}</td>
                                    <td>{long_val}</td>
                                    <td style="text-align: center;">
                                        <button class="copy-btn" onclick="copyToClipboard('{coord_str}', this)">📋 Copy</button>
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
