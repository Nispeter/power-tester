#!/bin/bash
executable=$1  
input_file=$2  
window_size=$3

outfile=resultsEnergy$(date +"%Y-%m-%d-%H:%M:%S").csv
echo $outfile

cols=("EnergyCores" "EnergyPkg" "EnergyRAM"
      "Instructions" "LLCLoads" "LLCLoadMisses" "LLCStores" 
      "LLCStoresMisses" "L1DcacheLoads" "L1DcacheLoadMisses" 
      "L1DcacheStores" "CacheMisses" "CacheReferences" "Branches" 
      "Branch-Misses" "CpuCycles" "DurationTime")

numcols=$(echo ${cols[@]})
columns=$(echo ${numcols// /,})
echo $columns >> ${outfile}
SAMPLES=30

WARMUP_RUNS=3
for((w=0; w<WARMUP_RUNS; w++))
do
    warmup_input=$(head -n $window_size $input_file)
    echo $warmup_input | ./${executable} > /dev/null 2>&1
done

for((j=1; j<=SAMPLES; j++))
do
    num_input=$((window_size * j))
    current_input=$(head -n $num_input $input_file)
    #echo "loop ${j}"
    echo $current_input | perf stat -a -x';' -o ${outfile}.tmp -e \
		    	     power/energy-cores/,power/energy-pkg/,power/energy-ram/,instructions,LLC-loads,LLC-load-misses,LLC-stores,LLC-stores-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,cache-misses,cache-references,branches,branch-misses,cpu-cycles,duration_time ./${executable} >> ${outfile} #<- agregar soporte de argumentos
	cut -d';' -f1 ${outfile}.tmp | sed '/#/d' | sed '/^$/d' | paste -s | sed 's/,/./g' | sed 's/\s\+/,/g' >> ${outfile}
done

find ${outfile} -type f -exec sed -i 's/<not,counted>/<not-counted>/g' {} \;
find ${outfile} -type f -exec sed -i 's/<not,supported>/<not-supported>/g' {} \;

rm ${outfile}.tmp
