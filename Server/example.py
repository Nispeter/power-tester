import pandas as pd
import matplotlib.pyplot as plt

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
rangeInt = 3
color = ['red', 'green', 'blue']
aux = []
fig, ax = plt.subplots()
for i in range(rangeInt):
    aux.append(pd.read_csv("12679365502" + "Results" + str(i) + ".csv"))

for i in range(rangeInt):
    df = aux[i]
    df.plot(y=0, use_index=True, color=color[i], title=df.columns[0],
                legend=True, xlabel='Iterations',
                ylabel="n. de " + df.columns[0], style='--', marker='.', label="12679365502"+"Results"+str(i)+".csv", ax=ax)
# plt.legend(['Maquina 1', 'Maquina 2', 'Maquina 3'])
plt.grid()
plt.show()
# df = pd.read_csv('resultsEnergy2021-12-05-23:39:10.csv')
# print(df)
# aux = df.plot(y=[0,2],use_index=True,color=['red','green'], title="numero de" + df.columns[1], xlabel='Iterations', ylabel=df.columns[0], style='--', marker='o')
# #aux.set_ylabel("Branch-Misses")
# #aux.set_xlabel("Iterations")
# plt.minorticks_on()
# plt.grid()
# plt.show()
# # plt.savefig("asdasd.svg", format='svg')