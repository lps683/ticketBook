#!/bin/bash
my_array=("130****3887" "****"\
        "187****4631" "****")
#待操作用户个数
len=${#my_array[@]}
len=`expr $len / 2`
i=0
while (($i < $len))
do 
    echo "第($i)个用户为: ${my_array[2*i]}"
    logname="/Users/lps/work/program/ticketReservation/log/${my_array[2*i]}.log"
    nohup /Users/lps/anaconda/bin/python /Users/lps/work/program/ticketReservation/book.py ${my_array[2*i]} ${my_array[2*i+1]} > ${logname} 2>&1 &
    i=`expr $i + 1`
done

