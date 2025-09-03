import time
import os
import platform

def bunyi():
    if platform.system() == "Windows":
        # Windows pakai beep
        import winsound
        winsound.Beep(1000, 500)  
    else:
        # Linux/Mac pakai bell character
        print("\a")

def pengingat_air(interval):
    print(f"Pengingat minum air dimulai! Setiap {interval} menit kamu akan diingatkan.\n")
    try:
        while True:
            time.sleep(interval * 60)  # konversi menit ke detik
            bunyi()
            print("💧 Saatnya minum air! Tetap sehat ya!\n")
    except KeyboardInterrupt:
        print("\nProgram dihentikan. Jangan lupa tetap minum air! 💙")

if __name__ == "__main__":
    try:
        menit = int(input("Mau diingatkan setiap berapa menit? "))
        pengingat_air(menit)
    except ValueError:
        print("Masukkan angka yang valid!")
