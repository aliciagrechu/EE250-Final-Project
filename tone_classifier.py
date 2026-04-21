
#tone_classifier.py: classifies song as chill, warm, dark, or dance using features extracted by audio_features.py

#defining different tones for LED changes
TONE_COLORS = {
    "chill": (0,   180, 200),   
    "warm":  (255, 160,  40),  
    "dark":  (80,   0,  160),   
    "dance": (220,  50,  50),   
}

#function to predict tone, gets features and returns tone string with score breakdown
def predict_tone(features: dict) -> tuple[str, dict]:
    #extract features
    tempo    = features["tempo"]
    energy   = features["energy"]
    centroid = features["spectral_centroid"]
    zcr      = features["zero_crossing_rate"]

    scores = {"chill": 0, "warm": 0, "dark": 0, "dance": 0} #keep track of scores for each tone group

    # tempo: we found during testing that tempo was least trusted features as librosa and often returns half or double real BPM, so we gave it lower weight
    if tempo < 90:
        scores["chill"] += 1
        scores["dark"]  += 1
    elif tempo < 110:
        scores["warm"]  += 1
        scores["chill"] += 1
    elif tempo < 125: #ambiguous zone so other features will break tie
        scores["dark"]  += 1
        scores["warm"]  += 1
        scores["dance"] += 1
    else:
        scores["dance"] += 2

    # energy: how busy the signal is on average. Through testing, we found it was the most stable feature librosa gave us, so we gave it highest weight.
    if energy < 0.08:
        scores["chill"] += 3 #very quiet, usually means chill
    elif energy < 0.13:
        scores["warm"]  += 2
        scores["chill"] += 1
    elif energy < 0.18:
        scores["dark"]  += 1
        scores["dance"] += 2
    else:
        scores["dance"] += 4   # very high energy is almost certainly dance

    # spectral centroid (Hz): center of mass of the frequency spectrum. Low means bass-heavy which is usually dark or warm. High means bright which is usually dance or chill.
    if centroid < 1800:
        scores["dark"]  += 3
    elif centroid < 2200:
        scores["warm"]  += 2
        scores["dark"]  += 1
    elif centroid < 2800:
        scores["dance"] += 1
        scores["chill"] += 1
    else:
        scores["dance"] += 2

    # zero crossing rate: how often waveform flips sign per second. A high ZCR means lots of percussion, which is usually dance. A low ZCR means smooth, sustained notes which is usually warm or chill.
    if zcr < 0.07:
        scores["warm"]  += 2
        scores["chill"] += 1
    elif zcr < 0.09:
        scores["warm"]  += 1
        scores["dark"]  += 1
    elif zcr < 0.11:
        scores["dark"]  += 1
    else:
        scores["dance"] += 3   

    # combination rules: during testing, we found certain combinations of features a guaranteed a certain category.

    # high energy and high zero crossing rate almost always dance
    if energy > 0.13 and zcr > 0.10:
        scores["dance"] += 3

    # a low energy and low zero crossing rate is certainly not dance, yet we were getting some songs with these combinations appearing as dance. Therefore, we subtracted scores from dance and added score to chill.
    if energy < 0.14 and zcr < 0.09:
        scores["dance"] = max(0, scores["dance"] - 3)
        scores["chill"] += 1

    # a very low centroid is almost always dark, yet during testing we had a few songs show up as dance, so we subtracted from dance catergory.
    if centroid < 1800:
        scores["dark"]  += 2
        scores["dance"] = max(0, scores["dance"] - 2)

    tone = max(scores, key=scores.get)
    return tone, scores

#test cases to verify classifier accuracy, can run directly to check with python tone_classfiier.py
if __name__ == "__main__":
    test_cases = [
        {
            "name": "In My Life — The Beatles",
            "expected": "warm",
            "features": {"tempo": 103.36, "energy": 0.1183,
                "spectral_centroid": 2088.44, "spectral_rolloff": 4371.82,
                "zero_crossing_rate": 0.090, "mfcc_1": -154.39,
                "mfcc_2": 101.76, "mfcc_3": 16.63, "mfcc_4": 38.77, "mfcc_5": 8.45}
        },
        {
            "name": "Gimme Shelter — Rolling Stones",
            "expected": "dark",
            "features": {"tempo": 117.45, "energy": 0.1510,
                "spectral_centroid": 1706.78, "spectral_rolloff": 3445.20,
                "zero_crossing_rate": 0.078, "mfcc_1": -125.00,
                "mfcc_2": 123.33, "mfcc_3": -18.85, "mfcc_4": 25.34, "mfcc_5": 1.32}
        },
        {
            "name": "Good Vibrations — Beach Boys",
            "expected": "dance",
            "features": {"tempo": 151.99, "energy": 0.1702,
                "spectral_centroid": 2527.04, "spectral_rolloff": 4991.20,
                "zero_crossing_rate": 0.124, "mfcc_1": -73.39,
                "mfcc_2": 75.09, "mfcc_3": -26.26, "mfcc_4": 34.67, "mfcc_5": 1.64}
        },
        {
            "name": "Twist and Shout — The Beatles",
            "expected": "dance",
            "features": {"tempo": 129.20, "energy": 0.1415,
                "spectral_centroid": 2425.23, "spectral_rolloff": 4720.81,
                "zero_crossing_rate": 0.135, "mfcc_1": -51.11,
                "mfcc_2": 88.71, "mfcc_3": -27.07, "mfcc_4": 27.26, "mfcc_5": -0.91}
        },
        {
            "name": "Respect — Aretha Franklin",
            "expected": "dance",
            "features": {"tempo": 112.35, "energy": 0.1839,
                "spectral_centroid": 2148.58, "spectral_rolloff": 4562.36,
                "zero_crossing_rate": 0.092, "mfcc_1": -71.62,
                "mfcc_2": 99.10, "mfcc_3": -6.58, "mfcc_4": 25.11, "mfcc_5": 5.63}
        },
        {
            "name": "Here Comes the Sun — The Beatles",
            "expected": "chill",
            "features": {"tempo": 129.20, "energy": 0.1283,
                "spectral_centroid": 2263.12, "spectral_rolloff": 5056.33,
                "zero_crossing_rate": 0.082, "mfcc_1": -165.88,
                "mfcc_2": 86.02, "mfcc_3": 17.32, "mfcc_4": 27.39, "mfcc_5": 5.52}
        },
        {
            "name": "Paint It Black — Rolling Stones",
            "expected": "dark",
            "features": {"tempo": 161.50, "energy": 0.1094,
                "spectral_centroid": 2396.50, "spectral_rolloff": 4771.81,
                "zero_crossing_rate": 0.121, "mfcc_1": -106.20,
                "mfcc_2": 86.54, "mfcc_3": -16.18, "mfcc_4": 37.05, "mfcc_5": 0.88}
        },
        {
            "name": "Johnny B Goode — Chuck Berry",
            "expected": "dance",
            "features": {"tempo": 86.13, "energy": 0.1981,
                "spectral_centroid": 2199.20, "spectral_rolloff": 4506.70,
                "zero_crossing_rate": 0.104, "mfcc_1": -50.70,
                "mfcc_2": 98.41, "mfcc_3": -17.42, "mfcc_4": 4.29, "mfcc_5": -13.09}
        },
    ]

    print("Testing rule-based classifier:\n")
    correct = 0
    for case in test_cases:
        tone, scores = predict_tone(case["features"])
        expected = case["expected"]
        ok = "OK" if tone == expected else "WRONG"
        print(f"  [{ok}] {case['name']}")
        print(f"        predicted={tone.upper():6s}  expected={expected.upper()}")
        print(f"        scores={scores}\n")
        if tone == expected:
            correct += 1

    print(f"Result: {correct}/{len(test_cases)} correct")