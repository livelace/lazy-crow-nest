libraries {
    dependency_check
    dependency_track {
        project = "lazy-crow-nest"
        version = "master"
    }
    git {
        repo_url = "https://github.com/livelace/lazy-crow-nest.git"
    }
    harbor_replicate {
        policy = "lazy-crow-nest"
    }
    harbor_scan {
        artifact = "data/lazy-crow-nest:latest"
        severity = "medium"
    }
    k8s_build {
        volume = """
            build1-spark-storage-shared, data/spark, ro
        """
    }
    kaniko {
        destination = "data/lazy-crow-nest:latest"
    }
    mattermost
    nexus {
       source = "dist/lazy_crow_nest-1.0.0-py3.8.egg"
       destination = "dists-internal/lazy-crow-nest/lazy-crow-nest-1.0.0-py3.8.egg"
    }
    sonarqube
    python
}
