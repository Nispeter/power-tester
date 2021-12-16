import subprocess as s

agg = s.run(["bash", "example.sh"], universal_newlines=True, timeout=1, capture_output=True)
stngaux = agg.stdout
stngaux = stngaux.strip()
print(5)
print(stngaux)
print(agg.stdout)


# try:
#     agg.wait()
# except s.TimeoutExpired:
#     agg.kill()

# print(agg.stdout)
