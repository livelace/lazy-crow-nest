def APP_NAME = "lazy-crow-nest"
def APP_REPO = "https://github.com/livelace/lazy-crow-nest.git"
def APP_VERSION = env.VERSION + '-${GIT_COMMIT_SHORT}'
def IMAGE_TAG = env.VERSION == "master" ? "latest" : env.VERSION

libraries {
//     dependency_check
//     dependency_track {
//         project = "${APP_NAME}"
//         version = "env.VERSION"
//     }
    git {
        repo_url = "${APP_REPO}"
        repo_branch = env.VERSION
    }
    //harbor_replicate {
    //    policy = "${APP_NAME}"
    //}
    k8s_build {
        image = "registry.livelace.ru/dev/lazy-crow-nest:latest"

        volume = """
            worker-1-s3-lazy-crow-nest, data/lazy-crow-nest, ro
        """
    }
    kaniko {
        destination = "infra/${APP_NAME}:${IMAGE_TAG}"
    }
    nexus {
       source = "dist/lazy_crow_nest-1.0.0-py3.10.egg"
       destination = "raw/${APP_NAME}/${APP_NAME}-${APP_VERSION}.egg"
    }
    python {
        test = false
    }
    //sonarqube
}
