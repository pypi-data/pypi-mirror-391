import os
import random
import requests
import shutil
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel

console = Console()
gr = '\033[1;32;41m'
k = '\033[33m'
w = '\033[1;37m'
g = '\033[1;32m'
r = '\033[1;31m'
b = '\033[1;34m'
p = '\033[1;35m'
c = '\033[1;36m'
y = '\033[1;33m'
oren = '\033[38;5;214m'
pan = f"{g} ╰─>{w} "
reset = '\033[0m'
y2 = "[bold yellow]"      # kuning
w2 = "[bold white]"       # putih
g2 = "[bold green]"       # hijau
r2 = "[bold red]"         # merah
b2 = "[bold blue]"        # biru
p2 = "[bold magenta]"     # ungu / pink
c2 = "[bold cyan]"        # biru muda / toska
reset2 = "[/]"       # reset warna ke default
def warna(nama):
    warna_dict = {
        "kuning": "bold yellow",
        "merah": "red",
        "hijau": "bold green",
        "biru": "blue",
        "ungu": "bold magenta",
        "cyan": "cyan",
        "putih": "white",
    }
    return warna_dict.get(nama.lower(), "white")

def panelku(label, isi, lebar=None, tinggi=None, werno="cyan"):
    # Ambil lebar terminal otomatis
    if lebar is None:
        try:
            lebar_terminal = shutil.get_terminal_size().columns
        except:
            lebar_terminal = 80  # default kalau gagal
        # Kurangi sedikit agar tidak terlalu mepet pinggir
        lebar = lebar_terminal - 4

    panel = Panel(
        isi,
        title=label,
        title_align="center",
        border_style=warna(werno),
        width=lebar,
        height=tinggi
    )
    console.print(panel)

def st(kata):
    return f"{w2}{r2}● {y2}● {g2}●{w2} {kata} {g2}● {y2}● {r2}●"
tanda = f"{g} |─>{w}"
#tanda2 = f'{warna_warni2}[{w2}+{warna_warni2}]{w2}'
def userku():
    try:
        with open('user.txt', 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            print('File kosong atau tidak ada User-Agent.')
            return None

        return random.choice(lines)

    except Exception as e:
        print('Gagal membaca file:', e)
        return None

def generate_user_agents(alias=None,cik='10'):
    BASE_URL = "https://whatmyuseragent.com"

    # Daftar brand dan aliasnya
    BRAND_MAP = {
        "motorola": "mr/motorola",
        "advan": "a9/advan",
        "huawei": "hu/huawei",
        "vivo": "vv/vivo",
        "realme": "re/realme",
        "samsung": "sa/samsung",
        "xiaomi": "xi/xiaomi",
        "oppo": "op/oppo",
        "infinix": "if/infinix",
        "tecno": "tb/tecno-mobile"
    }

    user_agents_list = []
    piro = int(cik)
    hitung=0
    try:
        with requests.Session() as session:
            # Loop 5x untuk buat UA
            for _ in range(piro):
                # Tentukan brand (kalau alias kosong → random tiap kali)
                if alias:
                    brand_key = alias.strip().lower()
                    if brand_key not in BRAND_MAP:
                        brand_text = ""
                        for i, name in enumerate(BRAND_MAP.keys()):
                            brand_text += f"{g}{name}{w}"
                            if i != len(BRAND_MAP) - 1:
                                brand_text += ", "  # koma tetap putih

                        print(f"{tanda} '{alias}' tidak ada")
                        print(f"{tanda} Gunakan salah satu dari: {brand_text}")
                        return
                    brand_path = BRAND_MAP[brand_key]
                else:
                    brand_key = random.choice(list(BRAND_MAP.keys()))
                    brand_path = BRAND_MAP[brand_key]
                    #print(f"→ Memilih brand random: {brand_key.capitalize()}")

                # Ambil halaman brand
                brand_url = f"{BASE_URL}/brand/{brand_path}"
                res_brand = session.get(brand_url)
                res_brand.raise_for_status()

                soup = BeautifulSoup(res_brand.text, "html.parser")

                # Ambil semua link device
                device_links = [
                    link.get("href")
                    for link in soup.find_all("a")
                    if "/device/" in link.get("href", "")
                ]

                if not device_links:
                    print(f"{tanda} Tidak ditemukan device untuk brand {brand_key}")
                    continue

                # Pilih device random
                device_url = BASE_URL + random.choice(device_links)
                res_dev = session.get(device_url)
                res_dev.raise_for_status()

                soup_dev = BeautifulSoup(res_dev.text, "html.parser")
                uas = [td.get_text(strip=True) for td in soup_dev.find_all("td", class_="useragent")]

                if uas:
                    hitung+=1
                    ua = random.choice(uas)
                    panelku(f"{st(f'USER AGENT {hitung}')}", f"{p2}{ua}",None ,None ,werno="hijau")
                    user_agents_list.append(ua)
                else:
                    hitung+=1
                    panelku(f"{st(f'USER AGENT {hitung}')}", f"{p2}{fallback}",None ,None ,werno="hijau")
                    user_agents_list.append(fallback)

        # Simpan hasil ke file
        with open("user.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(user_agents_list))

    except requests.RequestException as e:
        print("Gagal memuat halaman:", e)

