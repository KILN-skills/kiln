---
name: website-visual-inspector
description: Lihat tampilan sebuah website (screenshot desktop & mobile) dan bedah background-nya — warna, gradient, gambar, video, canvas, pseudo-element ::before/::after, overlay, dan palet warna. Gunakan saat user minta "lihat website ini", "cek tampilan", "background website apa", "tiru/clone desain", "ambil warna/gradient dari situs", atau memberi URL dan bertanya soal visualnya.
allowed-tools: Bash, Read, Write
---

# Website Visual Inspector

Skill ini membuat Claude bisa **melihat** sebuah website seperti manusia (lewat screenshot) dan **membaca** background-nya secara presisi (lewat computed CSS), lalu menggabungkan keduanya.

## Persiapan (sekali saja)

```bash
pip install playwright        # tambahkan --break-system-packages jika perlu
python -m playwright install chromium
```

## Alur kerja

1. **Jalankan inspeksi**
   ```bash
   python3 scripts/inspect_site.py <URL> --out site-inspect
   ```
   Opsi: `--dark` (render mode gelap), `--no-mobile`, `--no-download`, `--wait 3000` (situs dengan animasi berat).
   URL bisa juga file lokal (`./index.html`) atau dev server (`http://localhost:3000`).

2. **Lihat tampilannya** — buka screenshot dengan Read (Read bisa menampilkan gambar):
   - `site-inspect/viewport_desktop.png` → kesan pertama / hero section
   - `site-inspect/screenshot_desktop.png` → seluruh halaman
   - `site-inspect/screenshot_mobile.png` → versi mobile
   Screenshot full-page yang sangat tinggi bisa terlihat kecil; jika perlu detail, potong dulu:
   `python3 -c "from PIL import Image; im=Image.open('site-inspect/screenshot_desktop.png'); im.crop((0,0,1440,1800)).save('site-inspect/crop_1.png')"`

3. **Baca data background** — mulai dari `site-inspect/report.md` (ringkas). Buka `backgrounds.json` hanya untuk detail elemen tertentu.

4. **Gabungkan** apa yang terlihat di screenshot dengan data CSS. Contoh: hero terlihat ungu-biru → cocokkan dengan gradient di report, sebutkan selector dan nilai persisnya.

## Yang terdeteksi

| Jenis | Sumber |
|---|---|
| Warna solid | `background-color` semua elemen + `html`/`body` |
| Gradient | `linear/radial/conic-gradient` termasuk yang bertumpuk |
| Gambar | `url(...)` di `background-image` (diunduh ke `backgrounds/`) |
| Pseudo-element | `::before` / `::after` (sering dipakai untuk overlay gelap / noise) |
| Video background | `<video>` autoplay/loop/muted + poster |
| Canvas | `<canvas>` besar (animasi WebGL / particles — hanya bisa dilihat di screenshot) |
| Img sebagai background | `<img>` dengan `object-fit: cover` + `position: absolute/fixed` |
| Efek | `background-attachment: fixed` (parallax), `blend-mode`, `filter`, `backdrop-filter` (glassmorphism) |
| Design tokens | CSS variables warna di `:root` |
| Palet | Warna background diurutkan berdasarkan luas area (`palette.json`) |

## Saat menjawab user

- Tunjukkan screenshot yang relevan (kirim filenya jika user tidak bisa melihat folder kerja).
- Sebutkan background utama: warna/gradient persis (hex & CSS), gambar dan file hasil unduhan, lapisan overlay.
- Jika user ingin **meniru** desainnya, tuliskan CSS siap pakai yang mereproduksi background tersebut. Gambar/logo milik situs lain adalah hak cipta pemiliknya — sarankan diganti dengan aset sendiri untuk dipakai publik.
- Jika ada `canvas` atau video, jelaskan bahwa itu animasi dan deskripsikan dari screenshot.

## Kendala umum

- **Halaman kosong / diblokir bot** → coba `--wait 5000`; beberapa situs (Cloudflare challenge) memang tidak bisa diinspeksi otomatis. Jangan mencoba melewati CAPTCHA.
- **Konten muncul saat scroll** → skrip sudah auto-scroll; tambah `--wait` jika masih kosong.
- **Gambar gagal diunduh** → URL tetap tercatat di report; hotlink protection bisa menolak unduhan.
- **Stylesheet cross-origin** → CSS variables dari file CDN mungkin tidak terbaca, tapi computed style tetap akurat.
