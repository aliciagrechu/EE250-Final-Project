Emma Howard
Alicia Grechu

Laptop Installations:

Laptop requires Python 3.1 and Node.js (can download from  https://nodejs.org)

Install flask, spotipy, env environment for spotify client, paho-mqtt, librosa, numpy 

- pip install flask spotipy python-dotenv paho-mqtt librosa numpy

Install yt-dlp

- pip install yt-dlp

Raspberry Pi Installations:

- pip install paho-mqtt

Install Mosquitto MQTT broker:

- sudo apt-get install mosquitto mosquitto-clients
- sudo systemctl enable mosquitto
- sudo systemctl start mosquitto

Spotify API Setup:

1. Create an app on https://developer.spotify.com/dashboard
2. Set the Redirect URI in the app settings to http://127.0.0.1:5000/callback
3. Create a .env file in project folder with the following code:
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback

Configure MQTT:
In mqtt_publisher.py and replace RPI_IP with your RPi's IP address

- RPI_IP = "192.168.1.45"   # replace with your RPi's actual IP

To Run Project:



