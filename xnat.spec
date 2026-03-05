Name:           xnat
Version:        1.8.10
Release:        1%{?dist}
Summary:        Extensible Neuroimaging Archive Toolkit
License:        BSD-3-Clause
URL:            https://www.xnat.org
Source0:        https://github.com/nrg/xnat-web/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch
# Fedora 43 Legacy Java 8 via Temurin
BuildRequires:  temurin-8-jdk
BuildRequires:  maven-local-openjdk21
# We use bundled gradlew, so no 'gradle' BuildRequire needed
Requires:       temurin-8-jre
Requires:       tomcat
Requires:       postgresql-server

%description
XNAT is an open-source imaging informatics platform. 
Note: This package requires Java 8 (Temurin) to run correctly.

%prep
%setup -q -c
mv xnatdev-xnat-web-*/* . || :

# --- XNAT BUILD REPAIR STRATEGY: REPLACE, DON'T DELETE ---

# 1. Remove the Palantir plugin (This is the only line we strictly delete)
sed -i "/id ['\"]com.palantir.git-version['\"]/d" build.gradle

# 2. Inject the version variable after the plugins block
sed -i '/plugins {/,/^}/ s/^}/}\ndef vXnat = "1.8.10"/' build.gradle

# 3. Replace the function calls with static strings/objects
sed -i "s/gitVersion()/'1.8.10'/g" build.gradle
# Replace versionDetails() with an empty map so it doesn't crash if called
sed -i "s/versionDetails()/[:]/g" build.gradle

# 4. REPLACE MISSING GIT VARIABLES WITH "unknown"
# Instead of deleting the lines, we fill them with dummy data.
# This matches 'gitDetails.anything' or 'details.anything' and replaces it with "unknown"
sed -i 's/gitDetails\.[a-zA-Z0-9_]*/"unknown"/g' build.gradle
sed -i 's/details\.[a-zA-Z0-9_]*/"unknown"/g' build.gradle

# 5. Handle any "project.version" references inside strings if they exist
# (Sometimes used in the manifest, usually fine, but good to be safe)
sed -i "s/project.version/vXnat/g" build.gradle

# 6. Safety check: ensure no 'def vXnat' exists on line 1
sed -i '1{/^def vXnat/d}' build.gradle

%build
# Force Java 8 for the build process
export JAVA_HOME=/usr/lib/jvm/temurin-8-jdk

# Ensure the wrapper is executable
chmod +x ./gradlew

# INCREASED MEMORY: We add -Dorg.gradle.jvmargs to give it 4GB of RAM
# We also set MaxMetaspaceSize to ensure it handles the large number of classes.
./gradlew war -x test --no-daemon -Dorg.gradle.jvmargs="-Xmx4096m -XX:MaxMetaspaceSize=1024m"

# CORRECTED BUILD COMMAND:
# We removed the ":xnat-web" prefix because we are at the project root.
./gradlew war -x test --no-daemon

%install
# Create standard Fedora directory structure
install -d -m 0755 %{buildroot}%{_sysconfdir}/xnat
install -d -m 0755 %{buildroot}%{_sharedstatedir}/xnat/{archive,build,cache,ftp,pipeline,prearchive}
install -d -m 0755 %{buildroot}%{_var}/log/xnat
install -d -m 0755 %{buildroot}%{_var}/lib/tomcat/webapps

# CORRECTED CP COMMAND:
# Since we built from root, the WAR is in build/libs/
# We use a wildcard (*) for the source filename just in case Gradle named it slightly differently
cp build/libs/*.war %{buildroot}%{_var}/lib/tomcat/webapps/xnat.war

# Default configuration file
cat <<EOF > %{buildroot}%{_sysconfdir}/xnat/xnat-conf.properties
datasource.driver=org.postgresql.Driver
datasource.url=jdbc:postgresql://localhost/xnat
datasource.username=xnat
datasource.password=xnat
hibernate.dialect=org.hibernate.dialect.PostgreSQL9Dialect
EOF

%files
# The Tomcat webapp (WAR file)
%attr(0644, tomcat, tomcat) %{_var}/lib/tomcat/webapps/xnat.war

# Configuration directory and file
# We set the directory to 755 and the file to 640 (secure read)
%dir %attr(0755, tomcat, tomcat) %{_sysconfdir}/xnat
%config(noreplace) %attr(0640, tomcat, tomcat) %{_sysconfdir}/xnat/xnat-conf.properties

# Data directories (Must be writable by Tomcat)
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat/archive
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat/build
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat/cache
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat/ftp
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat/pipeline
%dir %attr(0755, tomcat, tomcat) %{_sharedstatedir}/xnat/prearchive

# Log directory
%dir %attr(0755, tomcat, tomcat) %{_var}/log/xnat

# Documentation
%license LICENSE.txt
%doc README.md

%changelog
* Tue Jan 06 2026 mhough <mhough@fedora-amd-nuc-lan> - 1.8.10-1
- Migrated to Temurin 8 JDK for Fedora 43 compatibility
- Explicitly set JAVA_HOME to Java 8 in build section
- Initial package for Fedora with gradlew wrapper
