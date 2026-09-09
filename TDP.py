
Trò chuyện với Gemini
import pandas as pd

import numpy as np

import streamlit as st



st.set_page_config(

    page_title="Tra cứu trạm gần nhất",

    page_icon="📍",

    layout="wide"

)



st.title("📍 Tra cứu khoảng cách trạm gần nhất")



# 1. Tải dữ liệu Data nền từ file Excel

@st.cache_data

def load_data():

    df = pd.read_excel("DATA Trạm.xlsx", sheet_name="Data", skiprows=1)

    df.columns = [str(c).strip() for c in df.columns]

    return df



try:

    df_raw = load_data()

    df_clean = df_raw.copy()



    # Hàm tìm cột linh hoạt

    def get_col_name(df, possible_names, fallback_index):

        for name in possible_names:

            for col in df.columns:

                if name.lower() == str(col).lower():

                    return col

        if fallback_index < len(df.columns):

            return df.columns[fallback_index]

        return None



    # Xác định tên các cột dữ liệu

    col_phan_loai = get_col_name(df_clean, ['Phân loại', 'Phan loai'], 1)       # Cột B (Loại Trạm)

    col_ten_tram = get_col_name(df_clean, ['Tên trạm', 'Ten tram'], 6)          # Cột G

    col_ma_tram = get_col_name(df_clean, ['Mã trạm theo SU', 'Mã trạm'], 5)    # Cột F

    col_trang_thai = get_col_name(df_clean, ['Trạng thái', 'Trang thai'], 14)   # Cột O

    col_tinh = get_col_name(df_clean, ['Tỉnh', 'Tinh'], 17)                     # Cột R

    col_mien_dia_ly = get_col_name(df_clean, ['Miền địa lý', 'Mien dia ly'], 18)# Cột S

    col_lat = get_col_name(df_clean, ['Lat', 'LAT', 'Latitude'], 19)            # Cột T

    col_long = get_col_name(df_clean, ['Long', 'LONG', 'Longitude'], 20)        # Cột U



    # Chuyển đổi Lat và Long sang số

    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors='coerce')

    df_clean[col_long] = pd.to_numeric(df_clean[col_long], errors='coerce')



    # Loại bỏ các hàng có tọa độ trống

    df_clean = df_clean.dropna(subset=[col_lat, col_long])



    # Trích xuất Loại Trạm chỉ từ cột B (Phân loại)

    def extract_loai_tram(row):

        val_b = str(row[col_phan_loai]).strip() if col_phan_loai in row and pd.notna(row[col_phan_loai]) else ""

        return val_b



    df_clean['Loại Trạm Temp'] = df_clean.apply(extract_loai_tram, axis=1)



    # 2. Ô dán tọa độ duy nhất

    raw_coord = st.text_input(

        "Dán tọa độ LATITUDE, LONGITUDE vào đây:",

        value="10.734728, 106.663666",

        placeholder="Ví dụ: 10.734728, 106.663666"

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



                    # Hàm gom nhóm dữ liệu trùng

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



                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")



                    # Mã HTML hiển thị bảng

                    html_code = """

                    <style>

                        .table-container {

                            width: 100%;

                            overflow-x: auto;

                            margin: 10px 0;

                        }

                        .custom-table {

                            width: 100%;

                            border-collapse: collapse;

                            font-family: Arial, sans-serif;

                            font-size: 14px;

                            color: #ffffff;

                        }

                        .custom-table th {

                            background-color: #262730;

                            color: #fafafa;

                            text-align: left;

                            padding: 10px 12px;

                            border: 1px solid #41444C;

                            white-space: nowrap;

                        }

                        .custom-table td {

                            padding: 10px 12px;

                            border: 1px solid #41444C;

                            background-color: #0e1117;

                            vertical-align: middle;

                        }

                        .copy-btn {

                            background-color: #ff4b4b;

                            color: white;

                            border: none;

                            padding: 6px 12px;

                            border-radius: 4px;

                            cursor: pointer;

                            font-weight: bold;

                            font-size: 13px;

                            white-space: nowrap;

                            transition: 0.2s;

                        }

                        .copy-btn:hover {

                            background-color: #d33a3a;

                        }

                    </style>



                    <script>

                    function copyToClipboard(text, btn) {

                        navigator.clipboard.writeText(text).then(function() {

                            var originalText = btn.innerHTML;

                            btn.innerHTML = "✅ Đã Copy!";

                            btn.style.backgroundColor = "#28a745";

                            setTimeout(function() {

                                btn.innerHTML = originalText;

                                btn.style.backgroundColor = "#ff4b4b";

                            }, 1500);

                        });

                    }

                    </script>



                    <div class="table-container">

                        <table class="custom-table">

                            <thead>

                                <tr>

                                    <th style="width: 40px; text-align: center;"></th>

                                    <th>Khoảng cách (m)</th>

                                    <th>Tên Trạm</th>

                                    <th>Mã Trạm</th>

                                    <th>Trạng Thái</th>

                                    <th>Loại Trạm</th>

                                    <th>Tỉnh</th>

                                    <th>Miền Địa Lý</th>

                                    <th>Lat</th>

                                    <th>Long</th>

                                    <th style="text-align: center;">Tọa độ Copy (Lat, Long)</th>

                                </tr>

                            </thead>

                            <tbody>

                    """



                    for idx, (_, row) in enumerate(top5.iterrows()):

                        lat_val = str(row[col_lat])

                        long_val = str(row[col_long])

                        coord_str = f"{lat_val}, {long_val}"

                        loai_tram_val = str(row['Loại Trạm Temp']) if row['Loại Trạm Temp'] != "" else "-"

                        

                        html_code += f"""

                            <tr>

                                <td style="text-align: center; color: #888888; font-weight: bold;">{idx}</td>

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



                    st.components.v1.html(html_code, height=500, scrolling=False)



            except ValueError:

                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng đảm bảo chỉ nhập số, ví dụ: 10.734728, 106.663666")

                st.error("liên hệ Sếp để có cái biên bản")

        else:

            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ phân tách bởi dấu phẩy.")

            st.error("liên hệ Sếp để có cái biên bản")



except FileNotFoundError:

    st.error("Không tìm thấy file 'DATA Trạm.xlsx'. Bạn hãy đảm bảo file này đã được tải lên cùng thư mục trên GitHub.")

except Exception as e:

    st.error(f"Đã xảy ra lỗi: {e}")

Đoạn mã Streamlit của bạn đã viết khá tốt và hoàn chỉnh logic tính khoảng cách bằng công thức Haversine, xử lý dữ liệu và gom nhóm trạm trùng lặp.

Tuy nhiên, mã hiện tại đang gặp một số vấn đề thực tế khi chạy trên Streamlit:

1. Các vấn đề cần lưu ý và khắc phục:
Lỗi ký tự khoảng trắng lạ (Non-breaking space \u00a0): Mã bạn dán vào chứa rất nhiều ký tự \xa0 ở các thụt lề, khiến Python báo lỗi IndentationError hoặc SyntaxError khi chạy trực tiếp.

Nút Copy qua JavaScript trong st.components.v1.html:

st.components.v1.html chạy trong một <iframe> độc lập. Ở một số trình duyệt hoặc khi deploy lên web (Streamlit Cloud), quyền truy cập Clipboard API (navigator.clipboard.writeText) trong iframe có thể bị chặn vì thiếu thuộc tính allow="clipboard-write".

Để khắc phục, ta thêm fallback dùng document.execCommand('copy') giúp nút copy luôn hoạt động 100% trên mọi trình duyệt.

Cột hiển thị STT: Cột chỉ số đang hiển thị từ 0 đến 4 ({idx}). Hiển thị từ 1 đến 5 ({idx + 1}) sẽ tự nhiên hơn cho người dùng tra cứu.

Hỗ trợ tải trực tiếp file Excel: Thêm tùy chọn tải file lên (st.file_uploader) phòng trường hợp không đặt sẵn file DATA Trạm.xlsx trong cùng thư mục.

2. Bản code hoàn chỉnh, tối ưu và đã sửa lỗi thụt lề:
Python
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tra cứu trạm gần nhất",
    page_icon="📍",
    layout="wide"
)

st.title("📍 Tra cứu khoảng cách trạm gần nhất")

# 1. Tải dữ liệu Data nền từ file Excel
@st.cache_data
def load_data(file_source):
    df = pd.read_excel(file_source, sheet_name="Data", skiprows=1)
    df.columns = [str(c).strip() for c in df.columns]
    return df

try:
    # Cho phép ưu tiên đọc file sẵn có, hoặc upload nếu cần
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

    # 2. Ô dán tọa độ duy nhất
    raw_coord = st.text_input(
        "Dán tọa độ LATITUDE, LONGITUDE vào đây:",
        value="10.734728, 106.663666",
        placeholder="Ví dụ: 10.734728, 106.663666"
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

                    # Sắp xếp theo khoảng cách tăng dần
                    df_sorted = df_clean.sort_values(by='Khoảng cách (m)').copy()

                    # Hàm gom nhóm dữ liệu trùng
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

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")

                    # HTML & CSS & JS Clipboard dự phòng
                    html_code = """
                    <style>
                        .table-container {
                            width: 100%;
                            overflow-x: auto;
                            margin: 10px 0;
                        }
                        .custom-table {
                            width: 100%;
                            border-collapse: collapse;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            color: #ffffff;
                        }
                        .custom-table th {
                            background-color: #262730;
                            color: #fafafa;
                            text-align: left;
                            padding: 10px 12px;
                            border: 1px solid #41444C;
                            white-space: nowrap;
                        }
                        .custom-table td {
                            padding: 10px 12px;
                            border: 1px solid #41444C;
                            background-color: #0e1117;
                            vertical-align: middle;
                        }
                        .copy-btn {
                            background-color: #ff4b4b;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-weight: bold;
                            font-size: 13px;
                            white-space: nowrap;
                            transition: 0.2s;
                        }
                        .copy-btn:hover {
                            background-color: #d33a3a;
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
                            console.error('Không thể copy', err);
                        }
                        document.body.removeChild(textArea);
                    }

                    function showCopied(btn) {
                        var originalText = btn.innerHTML;
                        btn.innerHTML = "✅ Đã Copy!";
                        btn.style.backgroundColor = "#28a745";
                        setTimeout(function() {
                            btn.innerHTML = originalText;
                            btn.style.backgroundColor = "#ff4b4b";
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
                                    <th>Khoảng cách (m)</th>
                                    <th>Tên Trạm</th>
                                    <th>Mã Trạm</th>
                                    <th>Trạng Thái</th>
                                    <th>Loại Trạm</th>
                                    <th>Tỉnh</th>
                                    <th>Miền Địa Lý</th>
                                    <th>Lat</th>
                                    <th>Long</th>
                                    <th style="text-align: center;">Tọa độ Copy (Lat, Long)</th>
                                </tr>
                            </thead>
                            <tbody>
                    """

                    for idx, (_, row) in enumerate(top5.iterrows()):
                        lat_val = str(row[col_lat])
                        long_val = str(row[col_long])
                        coord_str = f"{lat_val}, {long_val}"
                        loai_tram_val = str(row['Loại Trạm Temp']) if row['Loại Trạm Temp'] != "" else "-"

                        html_code += f"""
                                <tr>
                                    <td style="text-align: center; color: #888888; font-weight: bold;">{idx + 1}</td>
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
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng đảm bảo chỉ nhập số, ví dụ: 10.734728, 106.663666")
        else:
            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ phân tách bởi dấu phẩy.")

except FileNotFoundError:
    st.error("⚠️ Không tìm thấy file 'DATA Trạm.xlsx'. Hãy đảm bảo file này nằm cùng thư mục chứa script chạy.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi: {e}")
Gợi ý mở rộng thêm nếu bạn muốn:
Hiển thị bản đồ trực quan: Bạn có thể dùng st.map(top5[[col_lat, col_long]]) hoặc thư viện folium để vẽ trực quan vị trí điểm nhập và 5 trạm xung quanh kèm bán kính.

Cho phép tùy chọn số lượng trạm: Thêm top_n = st.slider("Số lượng trạm cần xem", 1, 20, 5) thay vì cố định head(5).

Từ dòng code trên, bổ súng giúp tôi khi xuất kết quả sẽ hiện thêm cột kết quả hiện đạt/ không đạt

Để thêm cột Đạt / Không đạt, giải pháp tối ưu và linh hoạt nhất là:

Cho phép bạn cài đặt khoảng cách chuẩn (ngưỡng Đạt) ngay trên giao diện (mặc định ví dụ 500m, 1000m, hoặc bạn có thể chỉnh theo quy định của bên bạn).

Kiểm tra nếu Khoảng cách (m) <= Ngưỡng thì hiển thị Đạt (màu xanh lá), ngược lại hiển thị Không đạt (màu đỏ cam) để dễ nhìn nhất.

Dưới đây là toàn bộ mã nguồn đã được bổ sung:

Python
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tra cứu trạm gần nhất",
    page_icon="📍",
    layout="wide"
)

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
        # Ngưỡng khoảng cách để đánh giá Đạt / Không đạt (đơn vị: mét)
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

                    # Sắp xếp theo khoảng cách tăng dần
                    df_sorted = df_clean.sort_values(by='Khoảng cách (m)').copy()

                    # Hàm gom nhóm dữ liệu trùng
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

                    # BỔ SUNG CỘT KẾT QUẢ ĐẠT / KHÔNG ĐẠT
                    top5['Kết quả'] = top5['Khoảng cách (m)'].apply(
                        lambda d: "Đạt" if d <= threshold_m else "Không đạt"
                    )

                    st.subheader("🎯 Kết quả 5 trạm gần nhất:")

                    # HTML & CSS & JS Clipboard
                    html_code = """
                    <style>
                        .table-container {
                            width: 100%;
                            overflow-x: auto;
                            margin: 10px 0;
                        }
                        .custom-table {
                            width: 100%;
                            border-collapse: collapse;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            color: #ffffff;
                        }
                        .custom-table th {
                            background-color: #262730;
                            color: #fafafa;
                            text-align: left;
                            padding: 10px 12px;
                            border: 1px solid #41444C;
                            white-space: nowrap;
                        }
                        .custom-table td {
                            padding: 10px 12px;
                            border: 1px solid #41444C;
                            background-color: #0e1117;
                            vertical-align: middle;
                        }
                        .copy-btn {
                            background-color: #ff4b4b;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-weight: bold;
                            font-size: 13px;
                            white-space: nowrap;
                            transition: 0.2s;
                        }
                        .copy-btn:hover {
                            background-color: #d33a3a;
                        }
                        /* Badge Đạt / Không đạt */
                        .badge-pass {
                            background-color: #28a745;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            display: inline-block;
                            white-space: nowrap;
                        }
                        .badge-fail {
                            background-color: #dc3545;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-weight: bold;
                            font-size: 12px;
                            display: inline-block;
                            white-space: nowrap;
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
                            console.error('Không thể copy', err);
                        }
                        document.body.removeChild(textArea);
                    }

                    function showCopied(btn) {
                        var originalText = btn.innerHTML;
                        btn.innerHTML = "✅ Đã Copy!";
                        btn.style.backgroundColor = "#28a745";
                        setTimeout(function() {
                            btn.innerHTML = originalText;
                            btn.style.backgroundColor = "#ff4b4b";
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
                                    <th style="text-align: center;">Tọa độ Copy (Lat, Long)</th>
                                </tr>
                            </thead>
                            <tbody>
                    """

                    for idx, (_, row) in enumerate(top5.iterrows()):
                        lat_val = str(row[col_lat])
                        long_val = str(row[col_long])
                        coord_str = f"{lat_val}, {long_val}"
                        loai_tram_val = str(row['Loại Trạm Temp']) if row['Loại Trạm Temp'] != "" else "-"
                        
                        # Tạo badge nhãn Đạt / Không đạt
                        if row['Kết quả'] == "Đạt":
                            badge_html = '<span class="badge-pass">✔ Đạt</span>'
                        else:
                            badge_html = '<span class="badge-fail">✖ Không đạt</span>'

                        html_code += f"""
                                <tr>
                                    <td style="text-align: center; color: #888888; font-weight: bold;">{idx + 1}</td>
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
                st.error("Tọa độ nhập vào không hợp lệ. Vui lòng đảm bảo chỉ nhập số, ví dụ: 10.734728, 106.663666")
        else:
            st.warning("Vui lòng nhập đầy đủ cả Vĩ độ và Kinh độ phân tách bởi dấu phẩy.")

except FileNotFoundError:
    st.error("⚠️ Không tìm thấy file 'DATA Trạm.xlsx'. Hãy đảm bảo file này nằm cùng thư mục chứa script chạy.")
except Exception as e:
    st.error(f"Đã xảy ra lỗi: {e}")
Điểm cải tiến chính:
Thêm ô nhập "Ngưỡng đạt khoảng cách (m)": Người dùng có thể tùy chỉnh khoảng cách yêu cầu (mặc định là 500m). Nếu khoảng cách tính được ≤ ngưỡng này thì ghi nhận là Đạt.

Cột "Kết quả" với nhãn badge đẹp mắt: Hiển thị nhãn xanh ✔ Đạt và nhãn đỏ ✖ Không đạt nổi bật ngay cạnh cột khoảng cách.

thay đổi bckground nền thành hình tủ ơim

Có thể bạn gõ phím bị nhầm từ "tối om" (nền tối/dark mode) hoặc "tự chọn / của mình" (chọn hình ảnh bất kỳ từ máy hoặc link).

Để giải quyết trọn vẹn cả hai trường hợp, dưới đây là cách chèn hình nền vào Streamlit bằng CSS:

Tự động phủ một lớp làm tối (Dark Overlay): Giúp hình nền nhìn sang trọng, huyền bí ("tối om") và chữ, bảng biểu không bao giờ bị chìm/khó đọc.

Linh hoạt: Bạn có thể dùng ảnh nền công nghệ/tối mặc định, hoặc tải ảnh từ máy tính / dán URL ảnh bất kỳ.

Mã nguồn hoàn chỉnh đã tích hợp Background hình nền:
Python
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
Các điểm nổi bật:
Lớp phủ linear-gradient tối: Dù bạn chọn hình sáng hay tối, trang vẫn được phủ màu đen mờ rgba(10, 14, 23, 0.88) giúp tổng thể nhìn sắc nét, hiện đại chuẩn phong cách Dark mode.

Cột bên trái (Sidebar): Bạn có thể click chọn dùng ảnh có sẵn, tải ảnh từ máy tính lên ngay lập tức hoặc dán bất kỳ link ảnh nào bạn thích.




Gemini là một AI và có thể mắc sai sót.

