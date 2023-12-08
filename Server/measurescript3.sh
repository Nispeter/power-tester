#!/bin/bash

executable=$1
input_file=$2
input_size=$3

outfile=resultsEnergy$(date +"%Y-%m-%d-%H:%M:%S").csv
echo $outfile

cols=("Increment" "EnergyCores" "EnergyPkg" "EnergyRAM" "Instructions" "LLCLoads" "LLCLoadMisses" "LLCStores" "LLCStoresMisses" "L1DcacheLoads" "L1DcacheLoadMisses" "L1DcacheStores" "CacheMisses" "CacheReferences" "Branches" "Branch-Misses" "CpuCycles" "DurationTime")

numcols=$(echo ${cols[@]})
columns=$(echo ${numcols// /,})

WARMUP_ROUNDS=3
for((i=0; i<WARMUP_ROUNDS; i++))
do
    ./${executable} > /dev/null 2>&1
done

echo $columns >> ${outfile}
SAMPLES=30

# Determine total numbers in the file
# total_numbers=$(wc -w < $input_file)
total_numbers=$(head -n $input_size $input_file | wc -w)

# Calculate step size based on 30 increments
step_size=$((total_numbers / 30))
if [[ $step_size -eq 0 ]]; then
    step_size=1
fi

INCREMENT=30  # Number of increments.
# For each increment
current_size=$step_size

WARMUP_ROUNDS=3
for((i=0; i<WARMUP_ROUNDS; i++))
do
    warmup_input=$(head -n $((input_size / INCREMENT)) $input_file | tr '\n' ' ')
    ./${executable} $warmup_input> /dev/null 2>&1
done

for((i=1; i<=INCREMENT; i++))
do
    current_input=$(head -n $current_size $input_file | tr '\n' ' ')
    
    # Within each increment, run the measurement 30 times
    for((j=0; j<SAMPLES; j++))
    do
        perf stat -a -x';' -o ${outfile}.tmp -e \
            power/energy-cores/,power/energy-pkg/,power/energy-ram/,instructions,LLC-loads,LLC-load-misses,LLC-stores,LLC-stores-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,cache-misses,cache-references,branches,branch-misses,cpu-cycles,duration_time ./${executable} $current_input
        
        results=$(cut -d';' -f1 ${outfile}.tmp | sed '/#/d' | sed '/^$/d' | paste -s | sed 's/,/./g' | sed 's/\s\+/,/g')
        
        # Add the increment number to the start of the results line
        # echo "INC$i,SAM$j"
        echo "$i,$results" >> ${outfile}
    done
    
    # Increase the current_size for the next iteration
    current_size=$((current_size + step_size))
    if [[ $current_size -gt $total_numbers ]]; then
        current_size=$total_numbers
    fi
done

find ${outfile} -type f -exec sed -i 's/<not,counted>/<not-counted>/g' {} \;
find ${outfile} -type f -exec sed -i 's/<not,supported>/<not-supported>/g' {} \;

rm ${outfile}.tmp
