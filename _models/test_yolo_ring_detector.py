from RingDetectorYOLO import RingDetector
from Brain import Brain

rd = RingDetector(file="weights/best.pt")
b = Brain()

while True:
    data = [0.0, 0.0, 0.0, 0.0, 0.0] + rd.inference(10)
    print(data)
    vel, ret = b.inference(data)
    print(vel, ret)
