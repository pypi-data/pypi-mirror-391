# Development

Sections below cover testing, local k8s testing, and making releases.

## Testing Geneva

Geneva testing happens at a few different levels:

* CI tests (lint, unit tests, local cluster test, basic GCP/AWS integration)
* E2E tests (stress tests, and external API tests)

### CI Tests

The Geneva CI test suite does lint checks, runs unit tests, and integration tests on GCP and AWS.
They take ~15 minutes to run, and are run at precommit and after PRs are merged to `origin/main`.

* pyright and ruff are used to check formatting and types in the code base.
* unit tests may have mocks or spin up local ray clusters (`ray.init()`) to verify functionality.
* integration tests exercise kuberay provisioning paths, auto manifest packaging, and job lifecycles.

Unit tests can be run using `make test`.  There are also helper targets that split the workloads into stable or experimental tests which can be run in parallel.

Integration tests are run using `make test-integration-gcp` or `make test-integration-aws`.  These tests run against standing k8s deploys and require credentials with proper authorizations to run the workloads.  See these [docs](https://lancedb.com/docs/geneva/deployment/).

### E2E Test

The Geneva end-to-end (e2e) tests exercise UDFs that use real models or external apis against real datasets.

These are intended to run:
* via weekly Github Actions cron,
* as pre-GA release gates,
* manually triggered on demand.

Ideally they are pre GA-release gates and can take around an hour.   They jobs however can be configured to run at even larger scale and for longer periods of time.

Currently, we focus our testing on an oxford pets image dataset (3680 images) to perform embedding and captioning using various models.   Here we test models pulled from hugging face or other repos, and also exercise external APIs such as Google Gemini or OpenAI models.  We provide a matrix of udfs (some of which may have conflicting dependencies in separate manifests) that use the data to test the Geneva framework.

In the future, other datasets will be added exercising other realistic scenarios such as url download udfs and auto batch size selection.

All of these tests can be executed by using either `make test-e2e-gcp` or `make test-e2e-aws` with extra arguments flagging different udfs and scale parameters.  They can also be triggered in the github actions menu with various options for scale and coverage.

(TODO move prebaked Sentence Transformers tests to e2e tests).

There also are stress tests that exercise scaling limitations (e.g. # of connections, # of threads, memory usage, etc).  This can be individually triggered by `make test-stress-gcp`.  (TODO move from CI tests to here)

## Local kuberay testing infrastructure

> Note: this is experimental.

Distributed geneva can be tested locally.  This requires Python 3.10+, KinD, and Kuberay.  Kind (Kubernetes in Docker) provides a local k8s which kuberay can be deployed in.

### Setting up KinD
To install KinD please see [this page](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)

TL;DR

for Linux
```bash
# For AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-linux-amd64
# For ARM64
[ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

for Mac
```bash
# For Intel Macs
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-darwin-amd64
# For M1 / ARM Macs
[ $(uname -m) = arm64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.27.0/kind-darwin-arm64
chmod +x ./kind
mv ./kind /some-dir-in-your-PATH/kind
```

### Setting up Kuberay
To install Kuberay please see [this page](https://ray-project.github.io/kuberay/deploy/helm/)

TL;DR
```bash
helm repo add kuberay https://ray-project.github.io/kuberay-helm/

helm install kuberay-operator kuberay/kuberay-operator

# Check the KubeRay operator Pod in `default` namespace
kubectl get pods
# NAME                                READY   STATUS    RESTARTS   AGE
# ...
```

## How to Release

We use github actions to release bits to our pypi repos.

Go to https://github.com/lancedb/geneva/actions/workflows/publish.yml and choose "Run workflow".  Choose your branch and then the bump type.

You can use this command to see how bump types will change the version for release.

```
$ uv run bump-my-version
0.2.4-beta1 ── bump ─┬─ major ─ 1.0.0-beta0
                     ├─ minor ─ 0.3.0-beta0
                     ├─ patch ─ 0.2.5-beta0
                     ├─ pre_l ─ 0.2.4
                     ╰─ pre_n ─ 0.2.4-beta2
```

You can see that the diferent options yield different release numbers.

Any release without "beta" in the version will be publshed to official pypi (https://pypi.org/project/geneva/) while any release with "beta" will be published to the fury repo (https://pypi.fury.io/lancedb/geneva).
