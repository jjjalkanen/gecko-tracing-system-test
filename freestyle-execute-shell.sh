if [! -d "/opt/bin" ]; then
  mkdir -p /opt/bin
fi
. /opt/m/.cargo/env
export PATH="/opt/m/.mozbuild/sccache:$PATH"
mkdir -p /opt/m/sccachedir/
export MOZBUILD_STATE_PATH=/opt/m/.mozbuild
cat << EOF > /opt/m/mozconfig
mk_add_options MOZ_OBJDIR=../obj-ff-dbg
# sccache starts yielding os error 11 with a larger number of threads
mk_add_options MOZ_PARALLEL_BUILD=20
ac_add_options --enable-application=browser
ac_add_options --enable-debug
ac_add_options --enable-warnings-as-errors
ac_add_options --with-ccache=sccache
export SCCACHE_DIR=/opt/m/sccachedir/
EOF
cat /opt/m/mozconfig
export MOZCONFIG=/opt/m/mozconfig
cd /opt/m/mozilla-unified
HOME=/opt/m ./mach build
HOME=/opt/m ./mach package
rm -fr /opt/bin/*
cp -Rf /opt/m/obj-ff-dbg/dist/firefox-*.en-US.linux-x86_64.tar.bz2 /opt/bin/

