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
Release: 22
Summary: Java XML parser

Group: Development/Java
#Vendor: %{?_vendorinfo:%{_vendorinfo}}%{!?_vendorinfo:%{_vendor}}
#Distribution: %{?_distribution:%{_distribution}}%{!?_distribution:%{_vendor}}
License: Apache Software License
URL: http://xml.apache.org/%{name}
Source0: http://xml.apache.org/dist/%{name}/%{name}-%{version}-src.tar.gz
Patch0: %{name}-noapis.patch
Patch1: %{name}-javac6-build.patch
Patch2: %{name}-javac-target-15.patch
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
BuildRequires: java-1.6.0-openjdk-devel

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
%patch1 -p0
%patch2 -p0

# -----------------------------------------------------------------------------

%build
export OPT_JAR_LIST=:
export CLASSPATH=$(build-classpath xml-commons-apis)
%{ant} jar javadoc

# -----------------------------------------------------------------------------

%install
# jars
%__mkdir_p %{buildroot}%{_javadir}
cp -p build/%{name}.jar \
    %{buildroot}%{_javadir}/%{name}-%{version}.jar
(
    cd %{buildroot}%{_javadir}
    for jar in *-%{version}*; do 
        %{__ln_s} -f ${jar} `echo $jar | sed "s|-%{version}||g"`
    done
)

# javadoc
%__mkdir_p %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr build/docs/api/* \
    %{buildroot}%{_javadocdir}/%{name}-%{version}
%__ln_s %{name}-%{version} \
    %{buildroot}%{_javadocdir}/%{name} # ghost symlink

# demo
%__mkdir_p %{buildroot}%{_datadir}/%{name}
cp -pr examples %{buildroot}%{_datadir}/%{name}

# jaxp_parser_impl ghost symlink
%__ln_s %{_sysconfdir}/alternatives \
    %{buildroot}%{_javadir}/jaxp_parser_impl.jar

%if %{gcj_support}
    %{_bindir}/aot-compile-rpm
%endif

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



%changelog
* Thu May 10 2012 Andrew Lukoshko <andrew.lukoshko@rosalab.ru> 0:1.1.3-18
- patched to build with JDK6

* Sat Dec 29 2007 David Walluck <walluck@mandriva.org> 0:1.1.3-17.0.1mdv2008.1
+ Revision: 139080
- import crimson

* Wed May 30 2007 Jason Corley <jason.corley@gmail.com> - 0:1.1.3-17jpp
- syntactic cleanup
- rebuild in mock

* Fri May 11 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.1.3-16jpp
- Make Vendor, Distribution based on macro

* Fri Feb 09 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.1.3-15jpp
- Add gcj_support option
- Fix and reactivate javadoc

* Wed Jan 04 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.1.3-14jpp
- First JPP 1.7 build

* Fri Aug 20 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.1.3-13jpp
- Build with ant-1.6.2

* Wed Jun  4 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.1.3-12jpp
- Own (ghost) %%{_javadir}/jaxp_parser_impl.jar.
- Remove alternatives in preun instead of postun.

* Thu Apr 10 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.1.3-11jpp
- Rebuild for JPackage 1.5.
- Change alternative to point to non-versioned jar, don't remove it on upgrade.
- Don't include JAXP API classes in crimson.jar.
- Drop javadoc package (contained only JAXP APIs).

* Thu Aug 22 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-10jpp
- corrected case for Group tag
- no macro for Url tag

* Mon Jul 01 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-9jpp
- use sed instead of bash 2.x extension in link area to make spec compatible with distro using bash 1.1x
- provides jaxp_parser_impl
- priority lowered to 20

* Tue May 07 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-8jpp
- vendor, distribution, group tags

* Sun Mar 10 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-7jpp
- provides jaxp_parser2 virtual resource

* Sat Jan 19 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-6jpp
- no need of stylebook, yet another cut'n'past sequel
- section macro

* Fri Jan 11 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-5jpp
- fixed demo requires
- javadoc in %%{_datadir}/javadoc again

* Thu Dec 20 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-4jpp
- javadoc back to /usr/share/doc
- doc and javadoc requires nothing
- demo requires exact version and release
- requires /usr/sbin/update-alternatives

* Wed Dec 5 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-3jpp
- javadoc into javadoc package

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 1.1.3-2jpp
- removed packager tag
- new jpp extension

* Sat Oct 6 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.3-1jpp
- 1.1.3
- used original tarball

* Sun Sep 30 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.2-0.beta2.2jpp
- first unified release
- s/jPackage/JPackage

* Fri Sep 07 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.2-0.beta2.1mdk
- 1.1.2beta2
- used source distribution
- no more wrapper as one jar only
- example subpackage is now demo subpackage
- moved demo files in %%{_datadir}/%%{name}

* Sat Sep 01 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.1-4mdk
- used cvs instead of mixed release
- moved examples %%{javadir}/%%{name}

* Tue Jul 31 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.1-3mdk
- jaxp_parser symlink is now jaxp_parser.jar

* Tue Jul 24 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.1-2mdk
- changed priority to 30

* Mon Jul 23 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.1.1-1mdk
- first Mandrake release, using a build script stolen from Henry Gomez <gomez@slib.fr>
