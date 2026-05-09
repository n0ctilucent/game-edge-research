import cv2
import time
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

# Paths to the payload files in your models directory
MODEL = "../models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
LABELS = "../models/coco_labels.txt"

def main():
    print("Initializing Skynet Tier 2 Edge Node...")
    
    # Load the Edge TPU interpreter
    interpreter = make_interpreter(MODEL)
    interpreter.allocate_tensors()
    labels = read_label_file(LABELS)
    
    # Connect to the Logitech Webcam (/dev/video1)
    # If it fails, you can change this to 0 to test the other node
    cap = cv2.VideoCapture(1)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam. Check /dev/video* permissions.")
        return

    print("✅ Camera linked. Press 'Ctrl+C' to stop scanning.\n")
    print("--- [ LIVE DETECTIONS ] ---")

    try:
        while cap.isOpened():
            start_time = time.perf_counter()
            
            # Read a frame from the webcam
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert color from BGR (OpenCV default) to RGB
            cv2_im = frame
            cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
            
            # Resize the frame to match the model's required input size
            _, scale = common.set_resized_input(
                interpreter, cv2_im.shape[:2], lambda size: cv2.resize(cv2_im_rgb, size))
            
            # Run inference on the Edge TPU
            interpreter.invoke()
            
            # Extract detections with > 50% confidence
            objs = detect.get_objects(interpreter, score_threshold=0.5, image_scale=scale)
            
            inference_time = (time.perf_counter() - start_time) * 1000
            fps = 1000.0 / inference_time

            # Format the output for the CLI
            if objs:
                output_str = f"[FPS: {fps:.1f} | {inference_time:.1f}ms] "
                for obj in objs:
                    class_name = labels.get(obj.id, obj.id)
                    score = int(obj.score * 100)
                    output_str += f"| {class_name}: {score}% "
                # Use \r to overwrite the same line in the terminal for a cleaner look
                print(f"{output_str:<80}", end='\r', flush=True)
            else:
                print(f"[FPS: {fps:.1f} | {inference_time:.1f}ms] Scanning...{' '*40}", end='\r', flush=True)

    except KeyboardInterrupt:
        print("\n\n🛑 Scanning halted by user.")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
