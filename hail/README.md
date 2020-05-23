<img src="https://hail.is/hail-logo-cropped.png" alt="hail" width="500"/>

All work courtsey of Hail Team @https://github.com/hail-is/hail, modified for Dataproc Optional Components 

# Hail 0.2 Standalone 

This folder contains the initialization action `hail_standalone.py`
[Hail](https://hail.is/)  is an open-source, general-purpose, Python-based data analysis library with additional data types and methods for working with genomic data.

Hail is built to scale and has first-class support for multi-dimensional structured data, like the genomic data in a genome-wide association study (GWAS).

As of Hail version 0.2.15, pip installations of Hail come bundled with a command-line tool, hailctl which has a submodule called dataproc for working with Google Dataproc clusters configured for Hail, including a fully configured notebook enviroment that can be used simply by calling 
```bash
hailctl dataproc connect CLUSTER_NAME notebook
```

**This init action is designed for running Hail without a notebook or using the Juypter notebook configured through the Dataproc Optional Component.**

[Hail Source Code](https://github.com/hail-is/hail)

__Pre-requisites:__ This initialization action must be used with Dataproc version 1.4-debian9. 

## Using this initialization action

**:warning: NOTICE:** See [best practices](/README.md#how-initialization-actions-are-used) of using initialization actions in production.

You can use this initialization action to create a Dataproc cluster with Hail installed for use with the Dataproc optional component of JuypterLab and component gateway. This will allow Hail to be used over direct web access and enforce the Cloud IAM permissions of the user accessing the Hail link. This init action can also be used with clusters created by Dataproc Hub. 

1.  Use the `gcloud` command to create a new cluster with this initialization
    action.

    ```bash
    # gcloud command normally created with hailctl start dataproc
    # modified for use with the hail_standalone.py init action
    gcloud beta dataproc clusters create \
    hail \
    --image-version=1.4-debian9 \
    --properties=spark:spark.task.maxFailures=20,spark:spark.driver.extraJavaOptions=-Xss4M,spark:spark.executor.extraJavaOptions=-Xss4M,spark:spark.speculation=true,hdfs:dfs.replication=1,dataproc:dataproc.logging.stackdriver.enable=false,dataproc:dataproc.monitoring.stackdriver.enable=false,spark:spark.driver.memory=41g \
    --initialization-actions=gs://crosbie-dev/initcomponentgatewayhail.py  \
    --metadata=^*^WHEEL="gs://hail-common/hailctl/dataproc/0.2.41/hail-0.2.41-py3-none-any.whl"*PKGS="aiohttp>=3.6,<3.7|aiohttp_session>=2.7,<2.8|asyncinit>=0.2.4,<0.3|bokeh>1.1,<1.3|decorator<5|gcsfs==0.2.1|humanize==1.0.0|hurry.filesize==0.9|nest_asyncio|numpy<2|pandas>0.24,<0.26|parsimonious<0.9|PyJWT|python-json-logger==0.1.11|requests>=2.21.0,<2.21.1|scipy>1.2,<1.4|tabulate==0.8.3|tqdm==4.42.1" \
    --master-machine-type=n1-highmem-8 \
    --region=us-central1 \
    --initialization-action-timeout=20m \
    --enable-component-gateway \
    --optional-components=ANACONDA,JUPYTER
    ```

1.  To access to the Jupyter web interface, you can just use the Component
    Gateway on the GCP Dataproc cluster console. Alternatively, you can access
    following the instructions in
    [connecting to cluster web interfaces](https://cloud.google.com/dataproc/docs/concepts/cluster-web-interfaces).
1.  After opening the Jupyter notebook, make sure you select the `Hail` kernel
    