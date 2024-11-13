# gecko-tracing-system-test

## Bill of materials:
Pre-configured Podman images
 - `localhost/end_to_end-ssh-agent-conf`
 - `localhost/end_to_end-jenkins-conf`

which are based on
 - `docker.io/jenkins/ssh-agent` (35c170948a5a)
 - `docker.io/jenkins/jenkins` (7a7add0bf3da)

The preconfigured image has Jenkins with nothing but the account and the credentials.
It will build the Firefox binaries directly on the node, and the configuration for
that is done on the first step below using BuilderFile, in order to make it quick to
perform build configuration changes, as necessary.

## Steps:
1. `podman build -t localhost/jenkins-build-ff -f BuilderFile`
1. `podman build -t localhost/test-server -f TesterFile`
1. `mkdir -p build_artifacts/ jenkins_home/`
1. Create Jenkins admin account with the secret from the console output
1. Log into Jenkins, do all the updates, and go to dashboard
1. Add new item, give it name `build-firefox`, choose `Freestyle project` as type
1. From Build Triggers, choose `Trigger builds remotely`, use a secret as `Authentication Token`
1. From Build Steps, add `Execute shell` and fill in the contents of `freestyle-execute-shell.sh`
1. Save and try building the job
1. Log into test container with `podman exec -it $(podman ps | grep test-server | cut -d ' ' -f 1) bash`
1. Check that the build artifacts are under /opt/bin/firefox
1. If necessary, unpack them with `tar -xvjf`
1. Check that we get the test site `emit_telemetry.html` from `curl http://brokensite.com/emit_telemetry.html`
1. Try if triggering the test works with `curl http://brokensite.com/testtrigger`

