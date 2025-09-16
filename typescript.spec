Name:           typescript
Version:        5.9.2
Release:        1
Summary:        A language for application-scale JavaScript
License:        Apache-2.0
URL:            https://www.typescriptlang.org
#Source:         https://registry.npmjs.org/typescript/-/typescript-%{version}.tgz
Source0:        https://github.com/microsoft/TypeScript/releases/download/v%{version}/%{name}-%{version}.tgz
BuildArch:      noarch
BuildRequires:  nodejs
BuildRequires:	nodejs-packaging

%description
TypeScript is a language for application-scale JavaScript. TypeScript adds
optional types to JavaScript that support tools for large-scale JavaScript
applications for any browser, for any host, on any OS. TypeScript compiles to
readable, standards-based JavaScript.

%prep
%autosetup -n package
# adjust the shebang lines to get a runtime dependency matching the
# node_modules_* directory where the code is actually installed to
#sed -e '/#!/ s/node/node-%{_nodejs_major_version}/' -i bin/tsc bin/tsserver

%install
%nodejs_install

# Fix shebang lines
for file in %{buildroot}%{_bindir}/ts* ; do
    sed -i -e "s|#!%{_bindir}/env node|#!%{_bindir}/node|" $(readlink -f $file)
done



%check
%{__nodejs} -e 'require("./")'


%files
%license LICENSE.txt
%{nodejs_sitelib}/typescript
%{_bindir}/tsc
%{_bindir}/tsserver
