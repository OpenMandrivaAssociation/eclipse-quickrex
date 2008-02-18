%define gcj_support         1
%define eclipse_base        %{_datadir}/eclipse
%define upstream_name       QuickREx
%define cvs_tag             QuickREx_3_5_0
%define oro_jar             jakarta-oro-2.0.8.jar
%define regexp_jar          jakarta-regexp-1.4.jar

Name:           eclipse-quickrex
Version:        3.5.0
Release:        %mkrel 0.5.2
Summary:        Regular-expression test Eclipse Plug-In

Group:          Development/Java
License:        Eclipse Public License
URL:            http://www.bastian-bergerhoff.com/eclipse/features/web/QuickREx/toc.html
# This tarball was made using the included script, like so:
#   sh ./fetch-quickrex.sh %{cvs_tag}
Source0:        quickrex-fetched-src-%{cvs_tag}.tar.bz2
Source1:        fetch-quickrex.sh
# build.properties and feature.xml was create to easily build this plugin with
# the awesome Fedora way, these files are licensed under the same license as
# the package.
Source2:        build.properties
Source3:        feature.xml
# This patch disables jregex support due to the fact that there isn't a Fedora
# package of it.
Patch0:         quickrex-disable-jregex-capability.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if %{gcj_support}
BuildRequires:    gcc-java
BuildRequires:    java-gcj-compat-devel
%else
BuildRequires:    java-devel >= 1.5.0
%endif
%if ! %{gcj_support}
BuildArch: noarch
%endif

BuildRequires: eclipse-pde >= 1:3.3.0
Requires: eclipse-platform >= 3.3.1 
BuildRequires: jakarta-oro
Requires: jakarta-oro
BuildRequires: regexp
Requires: regexp
Provides: eclipse-%{upstream_name} = %{version}-%{release}

%description
%{upstream_name} provides an Eclipse view in which you can enter
test-texts and try regular expressions.

# Note: This version of QuickREx disables jregex support due to
# the fact that there isn't a Fedora package of it.

%prep
%setup -q -n quickrex-fetched-src-%{cvs_tag}

mkdir quickrex-features
# create the feature plugin
cp -p %{SOURCE2} %{SOURCE3} quickrex-features

pushd Plug-In
%patch0 -p0
pushd lib
ln -s %{_javadir}/%{oro_jar}
ln -s %{_javadir}/regexp.jar %{regexp_jar}
popd
popd

# See comments in the script to understand this.
/bin/sh -x %{eclipse_base}/buildscripts/copy-platform SDK %{eclipse_base}
mkdir home

%build
SDK=$(cd SDK > /dev/null && pwd)

# Eclipse may try to write to the home directory.
homedir=$(cd home > /dev/null && pwd)

java -cp $SDK/startup.jar \
     -Dosgi.sharedConfiguration.area=%{_libdir}/eclipse/configuration \
     org.eclipse.core.launcher.Main \
     -application org.eclipse.ant.core.antRunner \
     -Dtype=feature \
     -Did=de.babe.eclipse.plugins.QuickREx \
     -DbaseLocation=$SDK \
     -DsourceDirectory=$(pwd) \
     -DbuildDirectory=$(pwd)/build \
     -Dbuilder=%{eclipse_base}/plugins/org.eclipse.pde.build/templates/package-build \
     -f %{eclipse_base}/plugins/org.eclipse.pde.build/scripts/build.xml \
     -vmargs -Duser.home=$homedir 

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{eclipse_base}
unzip -q -d %{buildroot}%{eclipse_base}/.. \
 build/rpmBuild/de.babe.eclipse.plugins.QuickREx.zip

# Re-symlink
pushd  %{buildroot}/%{eclipse_base}/plugins/de.babe.eclipse.plugins.QuickREx_%{version}/lib
rm %{oro_jar}
rm %{regexp_jar}
ln -s %{_javadir}/%{oro_jar}
ln -s %{_javadir}/regexp.jar %{regexp_jar}
popd

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf %{buildroot}

%if %{gcj_support}
%post
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi

%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(-,root,root,-)
%dir %{eclipse_base}/plugins/de.babe.eclipse.plugins.QuickREx_%{version}
%doc %{eclipse_base}/plugins/de.babe.eclipse.plugins.QuickREx_%{version}/html
%{eclipse_base}/features/de.babe.eclipse.plugins.QuickREx_%{version}
%{eclipse_base}/plugins/de.babe.eclipse.plugins.QuickREx_%{version}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%{_libdir}/gcj/%{name}/%{upstream_name}.*
%endif
