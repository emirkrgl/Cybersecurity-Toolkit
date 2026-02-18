import socket
import threading #port taraması hızlandırmak için fonks.
#socket.socket bir fonk. çağrısıdır. işletim sistemindbe yeni bir socket nesnesi oluşturmasını sağlar.
#socket.AF_INET hangi adres tipini tutacağını belirtir.INET6 olsaydı ipv6 olurdu bu hali ile ipv4
#socket.SOCK_STREAM Bu,verinin nasıl gönderileceğini belirler.Bu, verinin nasıl gönderileceğini belirler.TCP protokolünü temsil eder

# 1. ANALİZ FONKSİYONU: Gelen karmaşık metni temizler
def banner_ayikla(ham_veri):
    if not ham_veri:
        return "Cevap yok (Sessiz Servis)"
    
    try:
        metin = ham_veri.decode(errors='ignore').strip()
        
        # Eğer HTTP cevabıysa sadece Sunucu ismini ayıkla
        if "HTTP" in metin:
            for satir in metin.split('\r\n'):
                if "Server:" in satir:
                    return satir.replace("Server:", "").strip()
            return "Web Sunucusu (Detay yok)"
            
        # SSH, FTP gibi servisler için ilk satırı al
        return metin.replace('\n', ' ').replace('\r', '')[:50]
    
    except:
        return "Veri okunamadı"

# 2. TARAMA FONKSİYONU
def port_tara(target, port, target_ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)  
        result = s.connect_ex((target, port)) #portla bağlantı kuran fonksiyon
        
        if result == 0:
            # ---PAYLOAD SEÇİMİ ---
            if port in [80, 8080, 443]:
                payload = b"HEAD / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n"
            
            elif port == 3306:
                payload = b"\x00\x00\x00\x01\x00"
            
            elif port in [21, 22]:
                payload = None # Bunlar zaten kendisi konuşur, bir şey gönderme
            
            else:
                payload = b"\r\n" # Diğerlerine bir 'tık' yap

            try:
                port_servis = socket.getservbyport(port) #portun ne olduğunu söyleyen fonksiyon
            
            except:
                port_servis = "bilinmeyen"

            ceviri_cevap = "Cevap yok"
            
            try:
                s.settimeout(1.5)
                
                # Eğer payload varsa gönder, yoksa doğrudan dinlemeye geç (FTP/SSH için)
                if payload:
                    s.send(payload)
                
                gelen = s.recv(1024)
                ceviri_cevap = banner_ayikla(gelen)
            except:
                pass

            print(f"[+] Port {port:5}: AÇIK {port_servis:15} CEVAP-> {ceviri_cevap}\n")

        s.close()
    except:
        pass

# --- ANA PROGRAM ---
try:
    target = input("Taramak istediğiniz hedef (IP veya Domain): ")
    
    target_ip = socket.gethostbyname(target) # verilen domain adresini ip adrwsine çeviren fonksiyon
    
    print(f"Hedef IP belirlendi: {target_ip}")
    
    start_port = int(input("Başlangıç portu: "))
    
    end_port = int(input("Bitiş portu: "))
    
    print(f"\n--- {target} taranıyor... ---\n")
    
    thread_listesi = []
    
    for current_port in range(start_port, end_port + 1):
        t = threading.Thread(target=port_tara, args=(target, current_port, target_ip))
        thread_listesi.append(t)
        t.start()
        
    for t in thread_listesi:
        t.join()

    print("\n--- Tarama tamamlandı. ---")

except socket.gaierror:
    print("Hata: Geçersiz adres!")

except ValueError:
    print("Hata: Portlar sayı olmalıdır!")

except KeyboardInterrupt:
    print("\nDurduruldu.")