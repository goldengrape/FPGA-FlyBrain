"""Checks for Lesson 16: simplified compute/memory model."""
from ._core import evaluate_group, report

def evaluate(transfer_profile, language: str = "zh"):
    zh=language.lower().startswith("zh")
    labels=(("Memory-bound case","检查 data volume、bandwidth 与 startup latency。"),("Compute-bound case","检查较慢算术能成为 bottleneck。"),("Balanced case","检查时间相等时返回 balanced。")) if zh else (("Memory-bound case","Check data volume, bandwidth, and startup latency."),("Compute-bound case","Check slower arithmetic can dominate."),("Balanced case","Check equal times return balanced."))
    def a():
        c,t,b=transfer_profile(100,8,2.0,2.0,20.0); return abs(c-200)<1e-9 and abs(t-420)<1e-9 and b=="memory"
    def b():
        c,t,x=transfer_profile(10,4,10.0,4.0,0.0); return abs(c-100)<1e-9 and abs(t-10)<1e-9 and x=="compute"
    def c():
        x,y,b=transfer_profile(10,4,2.0,2.0,0.0); return abs(x-20)<1e-9 and abs(y-20)<1e-9 and b=="balanced"
    return [evaluate_group(labels[0][0],a,labels[0][1]),evaluate_group(labels[1][0],b,labels[1][1]),evaluate_group(labels[2][0],c,labels[2][1])]

def check(transfer_profile, language: str = "zh") -> bool:
    return report("第 16 课检查" if language.lower().startswith("zh") else "Lesson 16 checks", evaluate(transfer_profile, language))
