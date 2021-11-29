import subprocess as s

agg = s.Popen(["bash", "measurescript.sh", "tmr"], universal_newlines=True)

try:
    agg.wait(timeout=15)
except s.TimeoutExpired:
    agg.kill()

# print(agg.stdout)
