from Brain import Brain

brain = Brain("weights/04-27-2022.onnx")

for _ in range(19): 
    b = brain.inference([0.45]+[1] * 24)
    print(str(b[0]), b[1], type(str(b[0])), type(b[1]))
