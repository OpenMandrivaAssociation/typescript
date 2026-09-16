# Go binaries have no usable debugsource (DWARF line form unsupported).
%undefine _debugsource_packages

Name:		typescript
Version:	7.0.2
Release:	1
Summary:	A language for application-scale JavaScript
License:	Apache-2.0
Group:		Development/Languages
URL:		https://www.typescriptlang.org
# TypeScript 7 is the Go-native compiler (formerly typescript-go).
Source0:	https://github.com/microsoft/typescript-go/archive/refs/tags/typescript/v%{version}.tar.gz#/typescript-go-%{version}.tar.gz
Source1:	vendor.tar.xz
BuildRequires:	golang >= 1.26

%description
TypeScript is a language for application-scale JavaScript. TypeScript adds
optional types to JavaScript that support tools for large-scale JavaScript
applications for any browser, for any host, on any OS. TypeScript compiles to
readable, standards-based JavaScript.

Version 7 is a native Go port of the compiler (typically 8-12x faster than
the JavaScript-based 5.x/6.x toolchain). The command remains tsc. The
programmatic Node.js API is not ready until 7.1; this package ships the
compiler and LSP server only.

%prep
%autosetup -n typescript-go-typescript-v%{version} -a 1

%build
export GO111MODULE=on
export GOFLAGS="-mod=vendor -buildmode=pie -trimpath"
export GOPROXY=off
export GOSUMDB=off
go build -ldflags="-X github.com/microsoft/typescript-go/internal/core.version=%{version}" \
	-o tsc ./cmd/tsgo

%install
install -D -m 755 tsc %{buildroot}%{_bindir}/tsc
ln -s tsc %{buildroot}%{_bindir}/tsgo
# Language service: same binary, --lsp mode.
cat > %{buildroot}%{_bindir}/tsserver << 'EOF'
#!/bin/sh
exec %{_bindir}/tsc --lsp "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/tsserver

%check
./tsc --version | grep -q '%{version}'

%files
%license LICENSE
%doc README.md CHANGES.md
%{_bindir}/tsc
%{_bindir}/tsgo
%{_bindir}/tsserver
