from scapy.all import ARP, Ether, srp
import socket
def get_hostname(ip):
    try:
        hostname=socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return "bilinmiyor"

target_ip = input("Lütfen kontrol etmek istediğiniz IP aralığını yazınız: ") 

#Bu fonksiyon, OSI modelinin 2. katmanı olan Veri Bağı (Data Link) katmanında bir çerçeve (frame) oluşturur.
#  Cihazların birbirini IP ile değil, MAC adresleri ile tanıdığı yer burasıdır.
#dst="ff:ff:ff:ff:ff:ff": Bu bir "Broadcast" (Yayın) adresidir. Paketi ağdaki herkese gönder demektir.
#Kullanım Amacı: Paketin fiziksel ağda yolunu bulmasını sağlar.
#ARP() ip adreslerini mac adresleri ile eşleştirmek için kullanılır
packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip)

try:
    print(f" {target_ip} Tarama başlatılıyor, lütfen bekleyin...\n")
    result = srp(packet, timeout=3, verbose=False, inter=0.1)[0]
    print("IP Adresi\t\tMAC Adresi\t\tCİHAZ ADI")
    print("------------------------------------------------------------------")
    
    for sent, received in result:
        #sent: bizim gönderdiğimiz paket
        #received: bize gönderiken paket
        #received.psrc: Cevabı gönderen cihazın IP adresi
        #received.hwsrc: Cevabı gönderen cihazın MAC adresi
        name = get_hostname(received.psrc)
        print(f"{received.psrc:<20} {received.hwsrc}            {name}")

except Exception as e:
    print(f"Bir hata oluştu: {e}")