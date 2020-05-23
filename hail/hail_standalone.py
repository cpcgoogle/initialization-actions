# All work courtsey of Hail Team @https://github.com/hail-is/hail, 
#!/opt/conda/default/bin/python3

import json
import os
import subprocess as sp
import sys
from subprocess import check_output

assert sys.version_info > (3, 0), sys.version_info

if sys.version_info >= (3, 7):
    def safe_call(*args, **kwargs):
        sp.run(args, capture_output=True, check=True, **kwargs)
else:
    def safe_call(*args, **kwargs):
        try:
            sp.check_output(args, stderr=sp.STDOUT, **kwargs)
        except sp.CalledProcessError as e:
            print(e.output).decode()
            raise e


def get_metadata(key):
    return check_output(['/usr/share/google/get_metadata_value', 'attributes/{}'.format(key)]).decode()


def mkdir_if_not_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise


# get role of machine (master or worker)
role = get_metadata('dataproc-role')

if role == 'Master':
    # additional packages to install
    pip_pkgs = [
        'https://github.com/hail-is/jgscm/archive/v0.1.12+hail.zip'
    ]

    # add user-requested packages
    try:
        user_pkgs = get_metadata('PKGS')
    except Exception:
        pass
    else:
        pip_pkgs.extend(user_pkgs.split('|'))

    print('pip packages are {}'.format(pip_pkgs))
    command = ['pip', 'install']
    command.extend(pip_pkgs)
    safe_call(*command)

    print('getting metadata')

    wheel_path = get_metadata('WHEEL')
    wheel_name = wheel_path.split('/')[-1]

    print('copying wheel')
    safe_call('gsutil', 'cp', wheel_path, f'/home/hail/{wheel_name}')

    safe_call('pip', 'install', '--no-dependencies', f'/home/hail/{wheel_name}')

    print('setting environment')

    spark_lib_base = '/usr/lib/spark/python/lib/'
    files_to_add = [os.path.join(spark_lib_base, x) for x in os.listdir(spark_lib_base) if x.endswith('.zip')]

    env_to_set = {
        'PYTHONHASHSEED': '0',
        'PYTHONPATH': ':'.join(files_to_add),
        'SPARK_HOME': '/usr/lib/spark/',
        'PYSPARK_PYTHON': '/opt/conda/default/bin/python',
        'PYSPARK_DRIVER_PYTHON': '/opt/conda/default/bin/python',
    }

    print('setting environment')

    for e, value in env_to_set.items():
        safe_call('/bin/sh', '-c',
                  'set -ex; echo "export {}={}" | tee -a /etc/environment /usr/lib/spark/conf/spark-env.sh'.format(e, value))

    hail_jar = sp.check_output([
        '/bin/sh', '-c',
        'set -ex; python3 -m pip show hail | grep Location | sed "s/Location: //"'
    ]).decode('ascii').strip() + '/hail/backend/hail-all-spark.jar'

    conf_to_set = [
        'spark.executorEnv.PYTHONHASHSEED=0',
        'spark.app.name=Hail',
        # the below are necessary to make 'submit' work
        'spark.jars={}'.format(hail_jar),
        'spark.driver.extraClassPath={}'.format(hail_jar),
        'spark.executor.extraClassPath=./hail-all-spark.jar',
    ]

    print('setting spark-defaults.conf')

    with open('/etc/spark/conf/spark-defaults.conf', 'a') as out:
        out.write('\n')
        for c in conf_to_set:
            out.write(c)
            out.write('\n')

    