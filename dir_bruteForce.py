import requests
import time
import random
import argparse
from concurrent.futures import ThreadPoolExecutor
 
# ---------------------------------------------------------
# Renkli terminal ciktisi icin (harici kutuphane gerekmez)
# ---------------------------------------------------------
class Renk:
    YESIL = '\033[92m'
    SARI = '\033[93m'
    KIRMIZI = '\033[91m'
    MAVI = '\033[94m'
    GRI = '\033[90m'
    BOLD = '\033[1m'
    SIFIRLA = '\033[0m'
 
 
def istek_atma(hedef_url, headers, cookies, timeout, min_bekleme, max_bekleme):
    """Tek bir URL'e istek atar, sonucu (mesaj, status_code, url) olarak dondurur."""
    try:
        response = requests.get(hedef_url, headers=headers, cookies=cookies,
                                 timeout=timeout, allow_redirects=False)
        kod = response.status_code
 
        if min_bekleme > 0 or max_bekleme > 0:
            time.sleep(random.uniform(min_bekleme, max_bekleme))
 
        if kod == 200:
            return (f"{Renk.YESIL}[+] BULUNDU (200){Renk.SIFIRLA} {hedef_url}", kod, hedef_url)
        elif kod == 403:
            return (f"{Renk.SARI}[!] YASAKLI (403){Renk.SIFIRLA} {hedef_url}", kod, hedef_url)
        elif kod in (301, 302):
            konum = response.headers.get("Location", "?")
            return (f"{Renk.MAVI}[>] YONLENDIRME ({kod}){Renk.SIFIRLA} {hedef_url} -> {konum}", kod, hedef_url)
        else:
            return None  # 404 ve digerleri: sessiz gec
 
    except requests.exceptions.ConnectionError:
        return (f"{Renk.KIRMIZI}[x] Baglanti hatasi{Renk.SIFIRLA} {hedef_url}", None, hedef_url)
    except requests.exceptions.Timeout:
        return (f"{Renk.KIRMIZI}[x] Zaman asimi{Renk.SIFIRLA} {hedef_url}", None, hedef_url)
    except requests.exceptions.RequestException as e:
        return (f"{Renk.KIRMIZI}[x] Beklenmedik hata: {e}{Renk.SIFIRLA}", None, hedef_url)
 
 
def tara(base_url, derinlik, kelimeler, uzantilar, ayarlar, bulunan_toplam):
    """Recursive directory/file brute-force tarama fonksiyonu."""
    if derinlik >= ayarlar["maks_derinlik"]:
        return
 
    print(f"\n{Renk.BOLD}{Renk.MAVI}==> Taraniyor: {base_url} (derinlik {derinlik}){Renk.SIFIRLA}")
 
    topurl = []
    for kelime in kelimeler:
        topurl.append(base_url + kelime)               # uzantisiz (dizin adayi)
        for uzanti in uzantilar:
            topurl.append(base_url + kelime + "." + uzanti)  # uzantili (dosya adayi)
 
    uzantisiz_bulunan = []
 
    with ThreadPoolExecutor(max_workers=ayarlar["thread_sayisi"]) as executor:
        futures = [
            executor.submit(
                istek_atma, hedef_url,
                ayarlar["headers"], ayarlar["cookies"], ayarlar["timeout"],
                ayarlar["min_bekleme"], ayarlar["max_bekleme"]
            )
            for hedef_url in topurl
        ]
 
        for future in futures:
            sonuc = future.result()
            if sonuc is None:
                continue
 
            mesaj, kod, hedef_url = sonuc
            print(mesaj)
 
            if kod in (200, 301, 302):
                bulunan_toplam.append(hedef_url)
                # sadece uzantisiz (nokta icermeyen) sonuclar dizin adayi sayilir
                son_parca = hedef_url.rstrip("/").split("/")[-1]
                if "." not in son_parca:
                    uzantisiz_bulunan.append(hedef_url)
 
    # bulunan her dizin adayi icin bir sonraki seviyeye recursive gec
    for dizin_url in uzantisiz_bulunan:
        yeni_base = dizin_url.rstrip("/") + "/"
        tara(yeni_base, derinlik + 1, kelimeler, uzantilar, ayarlar, bulunan_toplam)
 
 
def kelimeleri_oku(dosya_yolu):
    """Wordlist dosyasini bir kere okuyup listeye alir (her recursive cagrida tekrar okumamak icin)."""
    kelimeler = []
    with open(dosya_yolu, "r", encoding="utf-8", errors="ignore") as f:
        for satir in f:
            temiz = satir.strip()
            if temiz and not temiz.startswith("#"):
                kelimeler.append(temiz)
    return kelimeler
 
 
def main():
    parser = argparse.ArgumentParser(description="Recursive Directory & Extension Brute-Forcer")
    parser.add_argument("-u", "--url", required=True, help="Hedef URL (ornek: http://127.0.0.1:8000/)")
    parser.add_argument("-w", "--wordlist", required=True, help="Wordlist dosyasinin yolu")
    parser.add_argument("-x", "--extensions", default="php,html,bak,zip,txt,tar.gz,sql,tar,gz,rar,7z,old,config,env",
                         help="Virgulle ayrilmis uzanti listesi (varsayilan: yaygin uzantilar)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Es zamanli thread sayisi (varsayilan: 10)")
    parser.add_argument("--timeout", type=float, default=10, help="Istek zaman asimi (saniye, varsayilan: 10)")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Maksimum recursive derinlik (varsayilan: 2)")
    parser.add_argument("--min-delay", type=float, default=0.0, help="Istekler arasi min bekleme (saniye)")
    parser.add_argument("--max-delay", type=float, default=0.0, help="Istekler arasi max bekleme (saniye)")
    parser.add_argument("--cookie", action="append", default=[],
                         help="Cookie ekle, format: isim=deger (birden fazla kez kullanilabilir)")
 
    args = parser.parse_args()
 
    base_url = args.url if args.url.endswith("/") else args.url + "/"
    uzantilar = [u.strip() for u in args.extensions.split(",") if u.strip()]
    kelimeler = kelimeleri_oku(args.wordlist)
 
    cookies = {}
    for c in args.cookie:
        if "=" in c:
            isim, deger = c.split("=", 1)
            cookies[isim.strip()] = deger.strip()
 
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }
 
    ayarlar = {
        "thread_sayisi": args.threads,
        "timeout": args.timeout,
        "maks_derinlik": args.depth,
        "min_bekleme": args.min_delay,
        "max_bekleme": args.max_delay,
        "headers": headers,
        "cookies": cookies,
    }
 
    print(f"{Renk.BOLD}Hedef:{Renk.SIFIRLA} {base_url}")
    print(f"{Renk.BOLD}Kelime sayisi:{Renk.SIFIRLA} {len(kelimeler)}")
    print(f"{Renk.BOLD}Uzanti sayisi:{Renk.SIFIRLA} {len(uzantilar)}")
    print(f"{Renk.BOLD}Maks derinlik:{Renk.SIFIRLA} {args.depth}")
    print(f"{Renk.BOLD}Thread sayisi:{Renk.SIFIRLA} {args.threads}")
 
    baslangic = time.time()
    bulunan_toplam = []
 
    tara(base_url, 0, kelimeler, uzantilar, ayarlar, bulunan_toplam)
 
    sure = time.time() - baslangic
    print(f"\n{Renk.BOLD}{Renk.GRI}===== TARAMA TAMAMLANDI ====={Renk.SIFIRLA}")
    print(f"Toplam bulunan: {len(bulunan_toplam)}")
    print(f"Gecen sure: {sure:.2f} saniye")
    for u in bulunan_toplam:
        print(f"  - {u}")
 
 
if __name__ == "__main__":
    main()
 