#! /usr/bin/env python

import subprocess
import os
import shutil
import glob

doc_dir = os.getcwd()

def run_cmd(outfile, cmd, prolog=None, epilog=None):
    if os.name == 'nt':
        newpath = r'C:\home\olwi'
    else:
        newpath = '/home/olwi'

    with open(outfile, 'w') as fout:
        if prolog:
            fout.write(prolog)
        fout.write('$ %s\n' % cmd)
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            output = output.decode()
        except subprocess.CalledProcessError as e:
            print(e.output)
            output = e.output.decode(errors='ignore')
            print('FAILURE: %s' % cmd)
            print(output)
        else:
            print('OK: %s' % cmd)
        output.replace(doc_dir, newpath)
        # Get rid of extra windows-style line endings, when running on Windows
        oo = output.splitlines()
        fout.write('\n'.join(oo))
        if epilog:
            fout.write(epilog)

def prepare_run_dir():
    run_dir = os.path.join(doc_dir, 'demo')
    demo_dir = os.path.join(doc_dir, '../demo')

    # Clean demo run directory and copy fresh files
    shutil.rmtree(os.path.join(run_dir, '.psm'), ignore_errors=True)
    remove_list = glob.glob(os.path.join(run_dir, '*'))
    for f in remove_list:
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

    # Copy files from demo directory to run directory
    file_list = [os.path.join(demo_dir, 'variants_caselist')]
    file_list.extend(glob.glob(os.path.join(demo_dir, '*.in')))
    file_list.extend(glob.glob(os.path.join(demo_dir, '*.par')))
    for f in file_list:
        shutil.copy(f, run_dir)
    shutil.copytree(os.path.join(demo_dir, 'modelTemplates'), os.path.join(run_dir, 'modelTemplates'))

    # go to doc-demo run directory
    os.chdir(run_dir)

if __name__ == "__main__":
    prepare_run_dir()

    # Create project
    prolog = '$ mkdir ~/my_proj\n$ cd ~/my_proj\n'
    run_cmd('mkdir_psm_init', 'psm init myProject', prolog=prolog)

    # Create case
    run_cmd('psm_case_ref', 'psm case --template box ref')
    run_cmd('psm_case_define', 'psm case --template box --define height=20,density=1200 bigBox')
    run_cmd('psm_run_case', 'psm run bigBox calc.py')

    # Create study
    run_cmd('psm_study', 'psm study --template box --description \"Variants in series A and B\" --name \"variants\" variants_caselist')
    run_cmd('psm_run_study', 'psm run variants calc.py')
    run_cmd('psm_collect', 'psm collect variants')

    # Object info and logs
    run_cmd('psm_info_bigBox', 'psm info bigBox')
    run_cmd('psm_log_bigBox', 'psm log bigBox')
    run_cmd('psm_environ_bigBox', 'psm run bigBox print_env.py')

    # DOE, ff2n
    run_cmd('psm_doe_h_pb', 'psm doe -h pb')
    run_cmd('psm_doe_h_ff2n', 'psm doe -h ff2n')
    run_cmd('psm_doe_ff2n', 'psm doe -t box --name box_ff2n box_uniform.par ff2n beta=0.999')
    run_cmd('psm_run_doe', 'psm run box_ff2n calc.py')
    run_cmd('psm_collect_doe', 'psm collect box_ff2n')

    # DOE, ff2n_A: Extra output with missing values
    run_cmd('psm_doe_ff2n_A', 'psm doe -t box --name box_ff2n_A box_uniform.par ff2n beta=0.999')
    run_cmd('psm_run_doe_A', 'psm run box_ff2n_A calc.py')
    run_cmd('psm_collect_doe_A', 'psm collect box_ff2n_A')
    run_cmd('psm_run_doe2_A', 'psm run box_ff2n_A calc_extra.py')
    run_cmd('psm_collect_doe2_A', 'psm collect --input extra.json box_ff2n_A')

    # fullfact
    run_cmd('psm_doe_fullfact', 'psm doe -t box --name box_fullfact box_uniform.par fullfact beta=0.999 levels=3,3,2,2')
    run_cmd('psm_run_doe_fullfact', 'psm run box_fullfact calc.py')
    run_cmd('psm_collect_doe_fullfact', 'psm collect box_fullfact')

    # gsd
    run_cmd('psm_doe_gsd', 'psm doe -t box --name box_gsd box_uniform.par gsd beta=0.999 levels=3,3,2,2 reduction=2')
    run_cmd('psm_run_doe_gsd', 'psm run box_gsd calc.py')
    run_cmd('psm_collect_doe_gsd', 'psm collect box_gsd')

    # ccdesign
    run_cmd('psm_doe_ccd', 'psm doe -t box --name box_ccd box_uniform.par ccdesign face=ccc alpha=r')
    run_cmd('psm_run_doe_ccd', 'psm run box_ccd calc.py')
    run_cmd('psm_collect_doe_ccd', 'psm collect box_ccd')

    # fracfact
    run_cmd('psm_doe_fracfact', 'psm doe -t box --name box_fracfact box_uniform.par fracfact gen=\"a,b,c,ab\" fold=all')
    run_cmd('psm_run_doe_fracfact', 'psm run box_fracfact calc.py')
    run_cmd('psm_collect_doe_fracfact', 'psm collect box_fracfact')

    # fracfact by resolution
    run_cmd('psm_doe_fracfact_res', 'psm doe -t box --name box_fracfact_res box_uniform.par fracfact res=3 fold=all')

    # ---------------------------------------
    os.chdir(doc_dir)
