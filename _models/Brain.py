import sys
import os
import onnxruntime as ort
import numpy as np

class Brain:
    def __init__(self, file="./weights/04-27-2022.onnx"):
        self.file = file
        self.model = self.load_model()
        self.recurrent_dummy = np.array([[[0] * 256]], dtype=np.float32)
        self.obs = []
        self.obs_filled = False
        
    def load_model(self):
        return ort.InferenceSession(self.file)

    def inference(self, inputs):

        outputs = self.model.run(None, {'obs_0': np.array([inputs], dtype=np.float32)})

        return outputs[4][0] # deterministic continuous actions
        #return outputs[2][0] # continuous actions

