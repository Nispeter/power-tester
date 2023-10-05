#!/bin/bash

executable=$1
input_file=$2
window_size=$3

outfile=resultsEnergy$(date +"%Y-%m-%d-%H:%M:%S").csv
echo $outfile

cols=("Increment" "EnergyCores" "EnergyPkg" "EnergyRAM" "Instructions" "LLCLoads" "LLCLoadMisses" "LLCStores" "LLCStoresMisses" "L1DcacheLoads" "L1DcacheLoadMisses" "L1DcacheStores" "CacheMisses" "CacheReferences" "Branches" "Branch-Misses" "CpuCycles" "DurationTime" "Q1" "Median" "Q3" "IQR" "Min" "Max" "StdDev")

numcols=$(echo ${cols[@]})
columns=$(echo ${numcols// /,})
echo $columns >> ${outfile}

SAMPLES=30

increment_results=()

# Iterating over the input increments
for ((i=1; i<=SAMPLES; i++))
do
    echo "Processing increment $i..."
    
    num_input=$((window_size * i))
    current_input=$(head -n $num_input $input_file)

    # Temporary storage for this increment's results
    tmp_increment_results=()

    for((j=0; j<SAMPLES; j++))
    do
        echo "$current_input" | perf stat -a -x';' -o ${outfile}.tmp -e \
        power/energy-cores/,power/energy-pkg/,power/energy-ram/,instructions,LLC-loads,LLC-load-misses,LLC-stores,LLC-stores-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,cache-misses,cache-references,branches,branch-misses,cpu-cycles,duration_time ./${executable} >> ${outfile}
        
        energy_cores_value=$(cut -d';' -f1 ${outfile}.tmp | sed '/#/d' | sed '/^$/d' | sed 's/,/./g')
        tmp_increment_results+=($energy_cores_value)
    done
    
    # Compute statistics for this increment's results
    sorted_results=$(printf "%s\n" "${tmp_increment_results[@]}" | sort -n)
    min=$(echo "$sorted_results" | head -n 1)
    max=$(echo "$sorted_results" | tail -n 1)
    q1=$(echo "$sorted_results" | awk 'NR==int(NR*0.25)')
    median=$(echo "$sorted_results" | awk 'NR==int(NR*0.5)')
    q3=$(echo "$sorted_results" | awk 'NR==int(NR*0.75)')
    iqr=$(echo "$q3 - $q1" | bc)
    std_dev=$(echo "$sorted_results" | awk '{sum+=$1; sumsq+=$1*$1} END {print sqrt(sumsq/NR - (sum/NR)^2)}')
    
    # Append statistics for this increment to the results file
    echo "$i;$min;$q1;$median;$q3;$max;$iqr;$std_dev" >> ${outfile}
done

find ${outfile} -type f -exec sed -i 's/<not,counted>/<not-counted>/g' {} \;
find ${outfile} -type f -exec sed -i 's/<not,supported>/<not-supported>/g' {} \;

rm ${outfile}.tmp
