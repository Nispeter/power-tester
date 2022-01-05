import pandas as pd
import matplotlib.pyplot as plt
# import subprocess as s

# agg = s.run(["bash", "example.sh"], universal_newlines=True, timeout=1, capture_output=True)
# stngaux = agg.stdout
# stngaux = stngaux.strip()
# print(5)
# print(stngaux)
# print(agg.stdout)


# try:
#     agg.wait()
# except s.TimeoutExpired:
#     agg.kill()

# print(agg.stdout)

df = pd.read_csv('resultsEnergy2021-12-05-23:39:10.csv')
print(df)
aux = df.plot(y=0,use_index=True,color='red', title="numero de" + df.columns[1], legend=None, xlabel='Iterations', ylabel=df.columns[0], style='--', marker='o')
#aux.set_ylabel("Branch-Misses")
#aux.set_xlabel("Iterations")
plt.minorticks_on()
plt.grid()
plt.show()
# plt.savefig("asdasd.svg", format='svg')