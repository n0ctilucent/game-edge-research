import time
import numpy as np
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate

model_path = "mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite"

print("Initializing Edge TPU...")
try:
    interpreter = Interpreter(model_path, experimental_delegates=[load_delegate('libedgetpu.so.1')])
    interpreter.allocate_tensors()
    print("✅ Hardware Delegate Active.")
                    
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]['index'], np.zeros(input_details[0]['shape'], dtype=np.uint8))
                                
    interpreter.invoke() # Warm up
                                      
    start = time.perf_counter()
    interpreter.invoke()
    end = time.perf_counter()
                                                       
    print(f"Inference speed: {(end - start) * 1000:.2f}ms")
except Exception as e:
        print(f"❌ Error: {e}")
