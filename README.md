# lazy-crow-nest


***lazy-crow-nest*** ("lazy" + "[crow's nest](https://en.wikipedia.org/wiki/Crow%27s_nest)") is a [Dash](https://github.com/plotly/dash) app for a quick overview
of job market in Russia.

### Features:

* 24/7 new data fetching.
* Regular [Spark](https://spark.apache.org/) task for clean, extract, enrich data etc. Weekly [Docker](https://hub.docker.com/r/livelace/lazy-crow-nest) image.
* Different metrics: city, title, company, salary etc.
* Filtering by different parameters.

### Dash:
![overview](assets/overview.png)


### Quick start:

```shell script
# start daemon and navigate to web ui.
user@localhost / $ docker run -ti --rm ghcr.io/livelace/lazy-crow-nest
Dash is running on http://0.0.0.0:8050/

 * Serving Flask app "lcn.__main__" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8050/ (Press CTRL+C to quit)
```