libraries {
    git {
        repo_url = "https://github.com/livelace/lazy-crow-nest.git"
    }
    k8s
    kaniko {
        destination = "data/lazy-crow-nest:latest"
    }
    mattermost
    nexus {
       source = "dist/lazy_crow_nest-1.0.0-py3.8.egg"
       destination = "dists-internal/lazy-crow-nest/lazy-crow-nest-1.0.0-py3.8.egg"
    }
    python
}
