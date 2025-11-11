#! /bin/bash

doc_dir=$PWD

function run_cmd {
    output_file=$1
    shift

    newpath='\/home\/olwi'
    tmp='run_cmd.tmp'

    echo \$ $@ &> ${output_file}
    eval $@ &> $tmp
    status=$?
    eval cat $tmp | sed s#$doc_dir#$newpath# >> $output_file
    if [ $status -eq 0 ]
    then
        echo "OK      : $@"
    else
        echo "FAILURE : $@"
        cat $tmp
    fi
}

#---------------------------------------------------

#-- Clean demo run directory and copy fresh files

cd $doc_dir/demo
rm -rf * .psm

cd $doc_dir/../demo
cp -r modelTemplates variants_caselist rosen*.in $doc_dir/demo

cd $doc_dir/demo

#--

#-- Create project
echo '$ mkdir ~/my_proj
$ cd ~/my_proj' > mkdir_psm_init
run_cmd psm_init psm init myProject
cat psm_init >> mkdir_psm_init

#-- Create case
run_cmd psm_case_ref psm case --template box ref
run_cmd psm_case_define psm case --template box --define height=20,density=1200 bigBox
run_cmd psm_run_case psm run bigBox calc.py

#-- Create study
run_cmd psm_study psm study --template box --description \"Variants in series A and B\" --name \"variants\" variants_caselist
run_cmd psm_run_study psm run variants calc.py
run_cmd psm_collect psm collect variants

#-- Object info and logs
run_cmd psm_info_bigBox psm info bigBox
run_cmd psm_log_bigBox psm log bigBox





#---------------------------------------------------
cd $doc_dir
