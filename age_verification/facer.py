from deepface import DeepFace

def analyze():
    input("Tensorflow loaded, waiting for you to start the process.")
    # Analyze the image (ensure you provide a valid path)
    try:
        path = input("path: ") or "WIN_20260204_20_03_26_Pro.jpg"
        analysis = DeepFace.analyze(img_path = path, actions = ['age'])
        
        # DeepFace returns a list of dicts (one for each face found)
        estimated_age = analysis[0]['age']
        
        print(f"Estimated Age: {estimated_age}")
        
        if estimated_age >= 18:
            print("User appears to be an adult.")
        else:
            print("User appears to be a minor.")
            
    except Exception as e:
        print(f"Error: {e}")

while True:
    analyze()