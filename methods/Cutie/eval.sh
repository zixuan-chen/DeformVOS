#!/bin/bash
source activate zixuan
module load compilers/cuda/11.6

dataset="roves"
week_num=6

if [ "$dataset" == "roves" ]; then
    python cutie/eval_vos.py dataset=roves-val size=480 \
            weights=output/cutie-base-mega.pth model=base \
            exp_id=roves_week${week_num} gpu=0 roves_week=${week_num}
elif [ "$dataset" == "vost" ]; then
    python cutie/eval_vos.py dataset=vost-val size=-1 \
            weights=output/cutie-base-mega.pth model=base \
            exp_id=vost gpu=0 
else
    echo "data is neither 'roves' nor 'vost'"
fi


