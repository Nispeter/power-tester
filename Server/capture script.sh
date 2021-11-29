#sleep 30


executable=("MSI")

length=(10500000)

outfile=resultsEnergy$(date +"%Y-%m-%d-%H:%M:%S").data

cols=("ExpNumber" "NumElements"
      "TimeSec" "EnergyCores" "EnergyPkg" "EnergyRAM" "Instructions" "LLCLoads"
      "LLCLoadMisses" "LLCStores" "LLCStoresMisses" "L1DcacheLoads"
      "L1DcacheLoadMisses" "L1DcacheStores" "CacheMisses"
      "CacheReferences" "Branches" "Branch-Misses" "CpuCycles")

numcols=$(echo ${cols[@]})
columns=$(echo ${numcols// /;})
echo $columns >> ${outfile}

numalgos=${#executable[@]} # @ todos los elemtnos # cantidad de operaciones
num_len=${#length[@]}

countexps=1
iterations=1

## Plain
for((j=0; j<31; j++))
do
	for (( i=0; i<${iterations}; i++))
	do
    	echo ""
    	echo "Iteration ${i}"    
    	for (( r=0; r<${num_len}; r++))
    	do
	    	for (( l=0; l<${numalgos}; l++))
	    	do
			echo -n -e "\rExperiment ${countexps}"
		
			echo -n $countexps";" >> ${outfile}
			
			perf stat -a -x';' -o ${outfile}.tmp -e \
		    	     power/energy-cores/,power/energy-pkg/,power/energy-ram/,instructions,LLC-loads,LLC-load-misses,LLC-stores,LLC-stores-misses,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,cache-misses,cache-references,branches,branch-misses,cpu-cycles ./${executable[l]} ${length[r]} >> ${outfile}
			cut -d';' -f1 ${outfile}.tmp | sed '/#/d' | sed '/^$/d' | paste -s | sed 's/\s\+/;/g' >> ${outfile}
				
			countexps=`expr $countexps + 1`
			
		    done
    	done
	done
done
# -a capta todo de los rpocesadores
# imprimir todo por ;

find ${outfile} -type f -exec sed -i 's/<not;counted>/<not-counted>/g' {} \;
find ${outfile} -type f -exec sed -i 's/<not;supported>/<not-supported>/g' {} \;

# not counter indica que no alcanzo a medir
#bash run_exps.sh
#screen -r
#hacer inputs grandes
rm ${outfile}.tmp
