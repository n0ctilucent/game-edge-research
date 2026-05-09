import cv2
import time
import json
import paho.mqtt.client as mqtt
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

# --- CONFIGURATION ---
MODEL = "../models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
LABELS = "../models/coco_labels.txt"
MQTT_BROKER = "10.10.8.60" # Chonk's IP (Update if different)
MQTT_PORT = 1883
MQTT_TOPIC = "skynet/tier2/edge-t/vision"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Uplink established to Core Broker.")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def main():
    print("Initializing Skynet Edge Vision Service...")
    
    # Setup MQTT
    client = mqtt.Client(client_id="edge-t-vision")
    client.on_connect = on_connect
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"⚠️ Could not connect to MQTT broker: {e}")

    # Load TPU and Labels
    interpreter = make_interpreter(MODEL)
    interpreter.allocate_tensors()
    labels = read_label_file(LABELS)
    
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("❌ Cannot open webcam.")
        return

    print("👁️ Sensor online. Monitoring for targets...")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            _, scale = common.set_resized_input(
                interpreter, frame.shape[:2], lambda size: cv2.resize(cv2_im_rgb, size))
            
            interpreter.invoke()
            objs = detect.get_objects(interpreter, score_threshold=0.6, image_scale=scale)
            
            # If objects are detected, format and publish
            if objs:
                payload = {
                    "node": "edge-t",
                    "timestamp": time.time(),
                    "detections": []
                }
                
                for obj in objs:
                    class_name = labels.get(obj.id, obj.id)
                    score = round(obj.score * 100, 1)
                    payload["detections"].append({"class": class_name, "confidence": score})
                
                # Publish the JSON payload
                json_payload = json.dumps(payload)
                client.publish(MQTT_TOPIC, json_payload)
                
                # Simple standard output for systemctl logs
                print(f"Published alert: {json_payload}")
                
                # Prevent spamming the broker (max 2 alerts per second)
                time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nHalting vision service.")
    finally:
        cap.release()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
