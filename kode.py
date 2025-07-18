import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# Konfigurasi halaman
st.set_page_config(page_title="Simulasi Lab Kimia", page_icon="🧪", layout="wide")

# Inisialisasi state (penyimpanan data sementara)
if 'campuran' not in st.session_state:
    st.session_state.campuran = []
if 'reaksi' not in st.session_state:
    st.session_state.reaksi = ""
if 'warna' not in st.session_state:
    st.session_state.warna = "#FFFFFF"
if 'suhu' not in st.session_state:
    st.session_state.suhu = 25
if 'gambar_reaksi' not in st.session_state:
    st.session_state.gambar_reaksi = None

# Database zat kimia (warna & reaksi)
ZAT_KIMIA = {
    "Asam Klorida (HCl)": {"warna": "#FFFFFF", "reaksi_asam": None, "reaksi_basa": "Netralisasi"},
    "Natrium Hidroksida (NaOH)": {"warna": "#FFFFFF", "reaksi_asam": "Netralisasi", "reaksi_basa": None},
    "Tembaga Sulfat (CuSO4)": {"warna": "#00B4D8", "reaksi_asam": "Larut", "reaksi_basa": "Endapan Biru"},
    "Besi (Fe)": {"warna": "#B5651D", "reaksi_asam": "Gas Hidrogen", "reaksi_basa": "Korosi"},
    "Fenolftalein": {"warna": "#FFFFFF", "reaksi_asam": "Tak Berwarna", "reaksi_basa": "Merah Muda"},
    "Air (H2O)": {"warna": "#ADD8E6", "reaksi_asam": None, "reaksi_basa": None}
}

# Fungsi untuk mencampur warna
def campur_warna(warna1, warna2):
    def hex_to_rgb(hex):
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x' % rgb
    
    rgb1 = hex_to_rgb(warna1)
    rgb2 = hex_to_rgb(warna2)
    campuran = [(c1 + c2) // 2 for c1, c2 in zip(rgb1, rgb2)]
    return rgb_to_hex(tuple(campuran))

# Fungsi untuk cek reaksi kimia
def cek_reaksi(zat1, zat2):
    sifat1 = ZAT_KIMIA[zat1]
    sifat2 = ZAT_KIMIA[zat2]
    
    if "asam" in zat1.lower() and sifat2["reaksi_asam"]:
        return f"{zat1} + {zat2} → {sifat2['reaksi_asam']}"
    elif "basa" in zat1.lower() and sifat2["reaksi_basa"]:
        return f"{zat1} + {zat2} → {sifat2['reaksi_basa']}"
    else:
        return f"{zat1} + {zat2} → Tidak ada reaksi"

# Fungsi buat gambar reaksi
def buat_gambar_reaksi(warna, teks):
    img = Image.new('RGB', (300, 200), color=warna)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    draw.text((10, 10), teks, fill="black", font=font)
    return img

# Tampilan Aplikasi
st.title("🧪 Simulasi Laboratorium Kimia")
st.markdown("Campurkan zat kimia dan lihat reaksinya!")

# Sidebar untuk input zat
with st.sidebar:
    st.header("Tambah Zat ke Labu")
    zat = st.selectbox("Pilih Zat Kimia", list(ZAT_KIMIA.keys()))
    volume = st.slider("Volume (mL)", 1, 100, 10)
    
    if st.button("Tambahkan ke Labu"):
        st.session_state.campuran.append({
            "zat": zat,
            "volume": volume,
            "warna": ZAT_KIMIA[zat]["warna"]
        })
        st.success(f"{volume} mL {zat} ditambahkan!")
    
    if st.button("Bersihkan Labu"):
        st.session_state.campuran = []
        st.session_state.reaksi = ""
        st.session_state.warna = "#FFFFFF"
        st.session_state.gambar_reaksi = None
        st.success("Labu dibersihkan!")

# Tampilan Labu dan Hasil Reaksi
col1, col2 = st.columns(2)

with col1:
    st.subheader("Labu Percobaan")
    if st.session_state.campuran:
        # Hitung warna campuran
        warna_campuran = st.session_state.campuran[0]["warna"]
        for zat in st.session_state.campuran[1:]:
            warna_campuran = campur_warna(warna_campuran, zat["warna"])
        st.session_state.warna = warna_campuran
        
        # Gambar labu
        st.markdown(f"""
        <div style="
            width: 200px;
            height: 300px;
            background-color: {warna_campuran};
            border-radius: 50% 50% 10% 10% / 60% 60% 10% 10%;
            margin: auto;
            border: 3px solid #333;
        "></div>
        """, unsafe_allow_html=True)
        
        # Daftar zat dalam labu
        st.write("*Zat dalam labu:*")
        df = pd.DataFrame(st.session_state.campuran)
        st.dataframe(df[["zat", "volume"]], hide_index=True)
        
        # Tombol mulai reaksi
        if len(st.session_state.campuran) >= 2 and st.button("Mulai Reaksi"):
            zat1 = st.session_state.campuran[0]["zat"]
            zat2 = st.session_state.campuran[1]["zat"]
            st.session_state.reaksi = cek_reaksi(zat1, zat2)
            st.session_state.gambar_reaksi = buat_gambar_reaksi(warna_campuran, st.session_state.reaksi)
    else:
        st.info("Labu kosong. Tambahkan zat dari sidebar.")

with col2:
    st.subheader("Hasil Reaksi")
    if st.session_state.reaksi:
        st.write("*Reaksi:*")
        st.code(st.session_state.reaksi)
        
        st.write("*Warna Campuran:*")
        st.color_picker("Hasil", st.session_state.warna, disabled=True)
        
        st.write("*Gambar Reaksi:*")
        img_bytes = io.BytesIO()
        st.session_state.gambar_reaksi.save(img_bytes, format="PNG")
        st.image(img_bytes, use_column_width=True)
    else:
        st.info("Belum ada reaksi. Tambahkan minimal 2 zat dan klik 'Mulai Reaksi'.")

# Tabel informasi zat kimia
st.subheader("Daftar Zat Kimia")
st.dataframe(pd.DataFrame.from_dict(ZAT_KIMIA, orient="index"))
