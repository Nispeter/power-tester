#!/bin/bash
#sleep 30

executable=$1

outfile=resultsEnergy$(date +"%Y-%m-%d-%H:%M:%S").csv
echo $outfile

cols=("EnergyCores" "EnergyPkg" "EnergyRAM"
	"Instructions" "LLCLoads"
      "LLCLoadMisses" "LLCStores" "LLCStoresMisses" "L1DcacheLoads"
      "L1DcacheLoadMisses" "L1DcacheStores" "CacheMisses"
      "CacheReferences" "Branches" "Branch-Misses" "CpuCycles" "DurationTime")


numcols=$(echo ${cols[@]})
columns=$(echo ${numcols// /,})


WARMUP_ROUNDS=3
for((i=0; i<WARMUP_ROUNDS; i++))
do
    ./${executable} > /dev/null 2>&1
done

echo $columns >> ${outfile}
SAMPLES=30

for((j=0; j<SAMPLES; j++))
do
	#echo "loop ${j}"
	perf stat -a -x';' -o ${outfile}.tmp -e \
		    	     power/energy-cores/,power/energy-pkg/,power/energy-ram/,instructions,LLC-loads,LLC-load-misses,LLC-stores,LLC-stores-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,cache-misses,cache-references,branches,branch-misses,cpu-cycles,duration_time ./${executable} >> ${outfile} #<- agregar soporte de argumentos
	cut -d';' -f1 ${outfile}.tmp | sed '/#/d' | sed '/^$/d' | paste -s | sed 's/,/./g' | sed 's/\s\+/,/g' >> ${outfile}
done

find ${outfile} -type f -exec sed -i 's/<not,counted>/<not-counted>/g' {} \;
find ${outfile} -type f -exec sed -i 's/<not,supported>/<not-supported>/g' {} \;

rm ${outfile}.tmp