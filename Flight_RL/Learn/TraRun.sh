#!/usr/bin/env bash
echo $'------ CNN Learning for Each Domain ------\n\n\n'
DIR='/home/sirius/Sample/'
#DIR='/Users/jiahen/Data/US_flights/Sample'
for EXP_DATA in `ls ${DIR}`
do
    python -u CNN.py 1500 100 2 ${DIR} ${EXP_DATA}
    echo $'\n\n'
done
for EXP_DATA1 in `ls ${DIR}`
do
    for EXP_DATA2 in `ls ${DIR}`
    do
        python -u TraEva.py 1500 100 2 ${DIR} ${EXP_DATA1} ${EXP_DATA2} $'H'
        python -u TraEva.py 1500 100 2 ${DIR} ${EXP_DATA1} ${EXP_DATA2} $'S'
        echo $'\n\n'
    done
done
