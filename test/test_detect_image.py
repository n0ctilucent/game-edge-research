import os
from PIL import Image, ImageDraw
from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter

# Updated paths to point to the new models directory
MODEL = "../models/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
LABELS = "../models/coco_labels.txt"
IMAGE = "../models/grace_hopper.bmp"

def main():
    print("Loading Edge TPU Object Detector...")
    
    # Initialize the LiteRT/TFLite interpreter with the Edge TPU delegate
    interpreter = make_interpreter(MODEL)
    interpreter.allocate_tensors()
    
    # Load labels
    labels = read_label_file(LABELS)
    
    # Open the image and resize it to match the model's expected input tensor
    image = Image.open(IMAGE)
    _, scale = common.set_resized_input(
        interpreter, image.size, lambda size: image.resize(size, Image.LANCZOS))

    print("Running Inference...")
    interpreter.invoke()
    
    # Extract the bounding boxes and classes
    # threshold=0.4 means we only want results with >40% confidence
    objs = detect.get_objects(interpreter, score_threshold=0.4, image_scale=scale)

    # Draw the results on the image
    print("Detected Objects:")
    if not objs:
        print("No objects detected.")
    
    draw = ImageDraw.Draw(image)
    for obj in objs:
        bbox = obj.bbox
        class_name = labels.get(obj.id, obj.id)
        score = round(obj.score * 100, 2)
        print(f" - {class_name} ({score}% confidence)")
        
        # Draw a red bounding box
        draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)], outline="red", width=3)
        draw.text((bbox.xmin, bbox.ymin), f"{class_name} {score}%", fill="red")

    # Save the output image into the test directory
    output_filename = "grace_hopper_detected.bmp"
    image.save(output_filename)
    print(f"✅ Output saved to: {output_filename}")

if __name__ == "__main__":
    main()
