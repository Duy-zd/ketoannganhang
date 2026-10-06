import streamlit as st
from datetime import date
import calendar

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="centered"
)

st.title("💰 ỨNG DỤNG TÍNH LÃI TIỀN GỬI TIẾT KIỆM")
st.write("Tính toán tiền lãi theo số ngày thực tế gửi tiền (1 năm = 365 ngày).")

st.divider()

# ============================================================
# HÀM ĐỊNH DẠNG TIỀN
# ============================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


def format_percent(value):
    return f"{value:.2f}%"


# ============================================================
# HÀM TÍNH SỐ NGÀY GỬI
# ============================================================

def tinh_so_ngay(ngay_gui, ngay_rut):
    """
    Tính số ngày từ ngày gửi đến trước ngày rút.
    
    Ví dụ:
    Ngày gửi: 01/01
    Ngày rút: 02/01
    => Số ngày tính lãi = 1 ngày
    """

    return (ngay_rut - ngay_gui).days


# ============================================================
# HÀM TÍNH LÃI ĐƠN
# ============================================================

def tinh_lai_don(tien_goc, lai_suat_nam, so_ngay):
    """
    Lãi đơn:
    Tiền lãi = Tiền gốc × lãi suất năm × số ngày / 365
    """

    return tien_goc * lai_suat_nam / 100 * so_ngay / 365


# ============================================================
# HÀM TÍNH LÃI KÉP
# ============================================================

def tinh_lai_kep(tien_goc, lai_suat_nam, so_ngay):
    """
    Lãi kép theo ngày:
    
    Số tiền cuối kỳ =
    Tiền gốc × (1 + lãi suất ngày)^số ngày
    
    Trong đó:
    lãi suất ngày = lãi suất năm / 365
    """

    lai_suat_ngay = lai_suat_nam / 100 / 365

    tong_tien = tien_goc * ((1 + lai_suat_ngay) ** so_ngay)

    tien_lai = tong_tien - tien_goc

    return tien_lai, tong_tien


# ============================================================
# HÀM TÍNH LÃI HÀNG THÁNG
# ============================================================

def tinh_lai_theo_thang(
    tien_goc,
    lai_suat_nam,
    ngay_gui,
    ngay_rut,
    kieu_lai
):
    """
    Chia khoảng thời gian gửi thành từng tháng.

    Tiền lãi mỗi tháng được tính theo số ngày thực tế
    của từng khoảng tháng, với quy ước 365 ngày/năm.
    """

    lai_suat_ngay = lai_suat_nam / 100 / 365

    danh_sach = []

    ngay_bat_dau = ngay_gui

    while ngay_bat_dau < ngay_rut:

        # Tìm ngày cuối tháng
        last_day = calendar.monthrange(
            ngay_bat_dau.year,
            ngay_bat_dau.month
        )[1]

        ngay_cuoi_thang = date(
            ngay_bat_dau.year,
            ngay_bat_dau.month,
            last_day
        )

        # Khoảng tính lãi kết thúc tại ngày cuối tháng
        # hoặc ngày trước ngày rút nếu rút trước cuối tháng
        ngay_ket_thuc = min(
            ngay_cuoi_thang,
            ngay_rut - __import__("datetime").timedelta(days=1)
        )

        so_ngay = (ngay_ket_thuc - ngay_bat_dau).days + 1

        if so_ngay <= 0:
            break

        # ====================================================
        # LÃI ĐƠN
        # ====================================================

        if kieu_lai == "Lãi đơn":

            tien_lai = (
                tien_goc
                * lai_suat_ngay
                * so_ngay
            )

            tien_cuoi_ky = tien_goc

        # ====================================================
        # LÃI KÉP
        # ====================================================

        else:

            tien_cuoi_ky = (
                tien_goc
                * ((1 + lai_suat_ngay) ** so_ngay)
            )

            tien_lai = tien_cuoi_ky - tien_goc

            # Lãi kép:
            # tiền lãi được nhập vào gốc
            tien_goc = tien_cuoi_ky

        danh_sach.append({
            "thang": f"{ngay_bat_dau.strftime('%d/%m/%Y')} - "
                     f"{ngay_ket_thuc.strftime('%d/%m/%Y')}",
            "so_ngay": so_ngay,
            "tien_lai": tien_lai,
            "tien_cuoi_ky": tien_cuoi_ky
        })

        ngay_bat_dau = ngay_ket_thuc + __import__("datetime").timedelta(days=1)

    return danh_sach


# ============================================================
# NHẬP THÔNG TIN KHÁCH HÀNG
# ============================================================

st.subheader("📋 Thông tin tiền gửi")

tien_gui = st.number_input(
    "💵 Số tiền gửi (VNĐ)",
    min_value=0.0,
    value=100_000_000.0,
    step=1_000_000.0,
    format="%.0f"
)

lai_suat = st.number_input(
    "📈 Lãi suất theo năm (%)",
    min_value=0.0,
    value=6.0,
    step=0.01,
    format="%.2f"
)

ky_han = st.number_input(
    "📅 Kỳ hạn gửi (tháng)",
    min_value=1,
    max_value=120,
    value=12,
    step=1
)

hinh_thuc_nhan_lai = st.selectbox(
    "💰 Hình thức nhận lãi",
    [
        "Cuối kỳ",
        "Hàng tháng",
        "Đầu kỳ"
    ]
)

kieu_lai = st.radio(
    "📊 Phương pháp tính lãi",
    [
        "Lãi đơn",
        "Lãi kép"
    ],
    horizontal=True
)

# ============================================================
# NGÀY GỬI / NGÀY RÚT
# ============================================================

st.subheader("📆 Thời gian gửi tiền")

ngay_gui = st.date_input(
    "Ngày khách hàng gửi tiền",
    value=date.today()
)

ngay_rut = st.date_input(
    "Ngày khách hàng rút tiền",
    value=date.today()
)

st.info(
    "📌 Quy ước: Ngày gửi được tính lãi. "
    "Ngày rút không tính lãi."
)

# ============================================================
# KIỂM TRA LÃI KÉP
# ============================================================

if kieu_lai == "Lãi kép" and hinh_thuc_nhan_lai != "Cuối kỳ":

    st.warning(
        "⚠️ Lãi kép chỉ được áp dụng khi khách hàng chọn "
        "hình thức nhận lãi Cuối kỳ."
    )

    cho_phep_tinh = False

else:
    cho_phep_tinh = True


# ============================================================
# NÚT TÍNH TOÁN
# ============================================================

if st.button(
    "🧮 TÍNH TOÁN",
    type="primary",
    use_container_width=True
):

    # --------------------------------------------------------
    # KIỂM TRA DỮ LIỆU
    # --------------------------------------------------------

    if tien_gui <= 0:

        st.error("❌ Số tiền gửi phải lớn hơn 0.")

    elif ngay_rut <= ngay_gui:

        st.error(
            "❌ Ngày rút phải sau ngày gửi."
        )

    elif not cho_phep_tinh:

        st.error(
            "❌ Lãi kép chỉ áp dụng cho hình thức nhận lãi cuối kỳ."
        )

    else:

        # ----------------------------------------------------
        # SỐ NGÀY GỬI
        # ----------------------------------------------------

        so_ngay_gui = tinh_so_ngay(
            ngay_gui,
            ngay_rut
        )

        # ----------------------------------------------------
        # TÍNH LÃI
        # ----------------------------------------------------

        if kieu_lai == "Lãi đơn":

            tong_lai = tinh_lai_don(
                tien_gui,
                lai_suat,
                so_ngay_gui
            )

            tong_tien = tien_gui + tong_lai

        else:

            tong_lai, tong_tien = tinh_lai_kep(
                tien_gui,
                lai_suat,
                so_ngay_gui
            )

        # ----------------------------------------------------
        # TÍNH LÃI HÀNG THÁNG
        # ----------------------------------------------------

        danh_sach_thang = tinh_lai_theo_thang(
            tien_gui,
            lai_suat,
            ngay_gui,
            ngay_rut,
            kieu_lai
        )

        # ====================================================
        # KẾT QUẢ
        # ====================================================

        st.divider()

        st.subheader("📊 KẾT QUẢ TÍNH LÃI")

        # ----------------------------------------------------
        # THÔNG TIN TỔNG QUAN
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "💵 Tiền gốc",
                format_money(tien_gui)
            )

            st.metric(
                "📅 Số ngày gửi",
                f"{so_ngay_gui} ngày"
            )

        with col2:

            st.metric(
                "📈 Lãi suất",
                format_percent(lai_suat)
            )

            st.metric(
                "💰 Tổng tiền lãi",
                format_money(tong_lai)
            )

        # ----------------------------------------------------
        # TỔNG TIỀN
        # ----------------------------------------------------

        st.success(
            f"### 💰 Tổng số tiền khách hàng nhận được\n\n"
            f"**{format_money(tong_tien)}**"
        )

        # ====================================================
        # LÃI HÀNG THÁNG
        # ====================================================

        st.subheader("📆 Chi tiết tiền lãi hàng tháng")

        if danh_sach_thang:

            import pandas as pd

            bang_lai = []

            for i, item in enumerate(danh_sach_thang, start=1):

                bang_lai.append({
                    "Kỳ": f"Kỳ {i}",
                    "Thời gian": item["thang"],
                    "Số ngày": item["so_ngay"],
                    "Tiền lãi": format_money(
                        item["tien_lai"]
                    )
                })

            df = pd.DataFrame(bang_lai)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        # ====================================================
        # THÔNG TIN HÌNH THỨC NHẬN LÃI
        # ====================================================

        st.subheader("💳 Hình thức nhận lãi")

        if hinh_thuc_nhan_lai == "Cuối kỳ":

            st.info(
                "Khách hàng nhận toàn bộ tiền gốc và tiền lãi "
                "vào ngày rút tiền."
            )

        elif hinh_thuc_nhan_lai == "Hàng tháng":

            st.info(
                "Tiền lãi được tính theo từng tháng và nhận "
                "theo từng kỳ tháng. Tiền gốc được nhận khi rút tiền."
            )

        elif hinh_thuc_nhan_lai == "Đầu kỳ":

            st.info(
                "Tiền lãi được xác định ngay từ đầu kỳ. "
                "Tiền gốc được nhận khi khách hàng rút tiền."
            )

        # ====================================================
        # TỔNG KẾT CUỐI CÙNG
        # ====================================================

        st.divider()

        st.subheader("🧾 Tổng kết")

        st.write(
            f"**Ngày gửi:** {ngay_gui.strftime('%d/%m/%Y')}"
        )

        st.write(
            f"**Ngày rút:** {ngay_rut.strftime('%d/%m/%Y')}"
        )

        st.write(
            f"**Số ngày tính lãi:** {so_ngay_gui} ngày"
        )

        st.write(
            f"**Phương pháp:** {kieu_lai}"
        )

        st.write(
            f"**Hình thức nhận lãi:** {hinh_thuc_nhan_lai}"
        )

        st.write(
            f"**Tổng tiền gốc:** {format_money(tien_gui)}"
        )

        st.write(
            f"**Tổng tiền lãi:** {format_money(tong_lai)}"
        )

        st.write(
            f"**TỔNG TIỀN KHÁCH HÀNG NHẬN:** "
            f"{format_money(tong_tien)}"
        )

        st.caption(
            "ℹ️ Công thức tính lãi sử dụng quy ước 1 năm = 365 ngày. "
            "Ngày gửi được tính lãi, ngày rút không tính lãi."
        )
