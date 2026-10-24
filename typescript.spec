# Go binaries have no usable debugsource (DWARF line form unsupported).
%undefine _debugsource_packages

Name:		typescript
Version:	7.0.2
Release:	2
Summary:	A language for application-scale JavaScript
License:	Apache-2.0
Group:		Development/Languages
URL:		https://www.typescriptlang.org
# TypeScript 7 is the Go-native compiler (formerly typescript-go).
Source0:	https://github.com/microsoft/typescript-go/archive/refs/tags/typescript/v%{version}.tar.gz#/typescript-go-%{version}.tar.gz
Source1:	vendor.tar.xz
# Chromium WebUI assigns string|TrustedHTML to innerHTML and
# string|TrustedScriptURL to HTMLScriptElement.src. Upstream lib.dom.d.ts
# types those setters as string (microsoft/TypeScript#30024). These four
# edits match Chromium's typescript_native_preview.patch. go:embed compiles
# the file into tsc; a lib.dom.d.ts beside the binary does not override it.
Patch0:		typescript-7.0.2-trusted-types-dom.patch
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
%autosetup -n typescript-go-typescript-v%{version} -p1 -a 1

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
# The setter must accept TrustedHTML. Upstream lib.dom.d.ts rejects this
# assignment, which is the Helium 0.20.1 chrome ninja failure.
cat > trusted-types.ts << 'EOF'
interface TrustedHTML {}
interface TrustedScriptURL {}
interface Window {
  trustedTypes?: {
    emptyHTML: TrustedHTML;
    emptyScript: TrustedScriptURL;
  };
}
function emptyHTML(): string|TrustedHTML {
  return window.trustedTypes ? window.trustedTypes.emptyHTML : "";
}
const template = document.createElement("template");
template.innerHTML = emptyHTML();
const read: string = template.innerHTML;
const el = document.createElement("div");
el.hidden = false;
function scriptURL(): string|TrustedScriptURL {
  return window.trustedTypes ? window.trustedTypes.emptyScript : "";
}
const script = document.createElement("script");
script.src = scriptURL();
const srcRead: string = script.src;
const shadow = el.attachShadow({mode: "open"});
shadow.innerHTML = emptyHTML();
const shadowRead: string = shadow.innerHTML;
EOF
./tsc --strict --lib dom,esnext --target esnext --noEmit trusted-types.ts

%files
%license LICENSE
%doc README.md CHANGES.md
%{_bindir}/tsc
%{_bindir}/tsgo
%{_bindir}/tsserver
