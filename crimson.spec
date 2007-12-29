# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# build with native support:
%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section free

Name: crimson
Epoch: 0
Version: 1.1.3
Release: %mkrel 17.0.1
Summary: Java XML parser

Group: Development/Java
#Vendor: %{?_vendorinfo:%{_vendorinfo}}%{!?_vendorinfo:%{_vendor}}
#Distribution: %{?_distribution:%{_distribution}}%{!?_distribution:%{_vendor}}
License: Apache Software License
URL: http://xml.apache.org/%{name}
Source0: http://xml.apache.org/dist/%{name}/%{name}-%{version}-src.tar.gz
Patch0: %{name}-noapis.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Provides: jaxp_parser_impl
%if ! %{gcj_support}
BuildArch: noarch
%endif

BuildRequires: ant
BuildRequires: java-rpmbuild >= 0:1.6
BuildRequires: xml-commons-apis
Requires: xml-commons-apis
Requires(post): update-alternatives
Requires(preun): update-alternatives
Requires: jpackage-utils >= 0:1.6
%if %{gcj_support}
BuildRequires: java-gcj-compat-devel
%endif

%description
Crimson is a Java XML parser which supports XML 1.0 via the following
APIs:
- Java API for XML Processing (JAXP) 1.1 minus the javax.xml.transform
package. JAXP is a pluggable API that allows applications to access XML
documents in a parser-independent manner. It endorses the industry
standard SAX and DOM APIs and also adds a few classes under the
javax.xml.parsers package to implement pluggability and utility methods
Note: the javax.xml.transform package hierarchy of JAXP is not
implemented by Crimson. One implementation of javax.xml.transform can be
found at Xalan Java 2.
- SAX 2.0
- SAX2 Extensions version 1.0
- DOM Level 2 Core Recommendation

%package manual
Summary: Manual for %{name}
Group: Development/Java

%description manual
Documentation for %{name}.

%package javadoc
Summary: Javadoc for %{name}
Group: Development/Java

%description javadoc
Javadoc for %{name}.

%package demo
Summary: Demo for %{name}
Group: Development/Java
Requires: %{name} = %{epoch}:%{version}-%{release}

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -q
%patch0 -p0

# -----------------------------------------------------------------------------

%build
export OPT_JAR_LIST=:
export CLASSPATH=$(build-classpath xml-commons-apis)
%{ant} jar javadoc

# -----------------------------------------------------------------------------

%install
%{__rm} -rf $RPM_BUILD_ROOT

# jars
%{__mkdir} -p ${RPM_BUILD_ROOT}%{_javadir}
%{__cp} -p build/%{name}.jar \
    ${RPM_BUILD_ROOT}%{_javadir}/%{name}-%{version}.jar
(
    cd $RPM_BUILD_ROOT%{_javadir}
    for jar in *-%{version}*; do 
        %{__ln_s} -f ${jar} `echo $jar | sed "s|-%{version}||g"`
    done
)

# javadoc
%{__mkdir} -p ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-%{version}
%{__cp} -pr build/docs/api/* \
    ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-%{version}
%{__ln_s} %{name}-%{version} \
    ${RPM_BUILD_ROOT}%{_javadocdir}/%{name} # ghost symlink

# demo
%{__mkdir} -p ${RPM_BUILD_ROOT}%{_datadir}/%{name}
%{__cp} -pr examples ${RPM_BUILD_ROOT}%{_datadir}/%{name}

# jaxp_parser_impl ghost symlink
%{__ln_s} %{_sysconfdir}/alternatives \
    ${RPM_BUILD_ROOT}%{_javadir}/jaxp_parser_impl.jar

%if %{gcj_support}
    %{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

# -----------------------------------------------------------------------------

%post
update-alternatives --install %{_javadir}/jaxp_parser_impl.jar \
    jaxp_parser_impl %{_javadir}/%{name}.jar 20
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]; then
    %{_bindir}/rebuild-gcj-db
fi
%endif

%preun
if [ "$1" -eq 0 ]; then
    update-alternatives --remove jaxp_parser_impl %{_javadir}/%{name}.jar
fi

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]; then
    %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc ChangeLog README.txt
%{_javadir}/%{name}*.jar
%ghost %{_javadir}/jaxp_parser_impl.jar
%if %{gcj_support}
%attr(-,root,root) %dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif

%files manual
%defattr(0644,root,root,0755)
%doc docs/*

%files javadoc
%defattr(0644,root,root,0755)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files demo
%defattr(0644,root,root,0755)
%{_datadir}/%{name}

