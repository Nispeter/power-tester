#!/bin/bash

executable=$1
input_size=$2  # The maximum input size

outfile=resultsEnergy$(date +"%Y-%m-%d-%H:%M:%S").csv
echo $outfile

cols=("Increment" "EnergyCores" "EnergyPkg" "EnergyRAM" "Instructions" "LLCLoads" "LLCLoadMisses" "LLCStores" "LLCStoresMisses" "L1DcacheLoads" "L1DcacheLoadMisses" "L1DcacheStores" "CacheMisses" "CacheReferences" "Branches" "Branch-Misses" "CpuCycles" "DurationTime")

numcols=$(echo ${cols[@]})
columns=$(echo ${numcols// /,})
echo $columns >> ${outfile}
INCREMENT=30
SAMPLES=30

# For each increment
for((i=1; i<=INCREMENT; i++))
do
    num_input=$((input_size * i / INCREMENT))  # Calculate current input size

    # Within each increment, run the measurement 30 times
    for((j=0; j<SAMPLES; j++))
    do
        perf stat -a -x';' -o ${outfile}.tmp -e \
            power/energy-cores/,power/energy-pkg/,power/energy-ram/,instructions,LLC-loads,LLC-load-misses,LLC-stores,LLC-stores-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,cache-misses,cache-references,branches,branch-misses,cpu-cycles,duration_time ./${executable} $num_input
        
        results=$(cut -d';' -f1 ${outfile}.tmp | sed '/#/d' | sed '/^$/d' | paste -s | sed 's/,/./g' | sed 's/\s\+/,/g')
        
        # Add the increment number to the start of the results line
        echo "$i,$results" >> ${outfile}
    done
done

find ${outfile} -type f -exec sed -i 's/<not,counted>/<not-counted>/g' {} \;
find ${outfile} -type f -exec sed -i 's/<not,supported>/<not-supported>/g' {} \;

rm ${outfile}.tmp
