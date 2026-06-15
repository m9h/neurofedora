# mcp-slicer — a Model Context Protocol (MCP) server that lets an LLM agent
# (Claude Desktop / Cline / Claude Code) drive 3D Slicer: inspect the MRML scene,
# run Python in Slicer, and capture view screenshots. It talks to a running
# Slicer over the built-in Web Server module (ship 3dslicer, activate "Web
# Server"), so the whole agentic loop is: agent -> mcp-slicer -> HTTP -> Slicer.

%global pypi_name mcp_slicer

Name:           python-mcp-slicer
Version:        0.2.1
Release:        1%{?dist}
Summary:        MCP server for driving 3D Slicer from LLM agents

License:        MIT
URL:            https://github.com/zhaoyouj/mcp-slicer
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
mcp-slicer is a Model Context Protocol (MCP) server that connects 3D Slicer to
LLM clients such as Claude Desktop, Cline, or Claude Code, enabling an agent to
inspect the MRML scene (list_nodes), run arbitrary Python in the Slicer
environment (execute_python_code), and capture slice/3D view screenshots
(capture_screenshot) for a visual REACT loop. It drives Slicer over the
application's built-in Web Server interface; no custom Slicer module is needed.

Security note: execute_python_code is arbitrary code execution against the
running Slicer. Keep Slicer's Web Server bound to localhost (its default).}

%description %_description

%package -n python3-mcp-slicer
Summary:        %{summary}
Requires:       python3-mcp
Requires:       python3-requests
# The MCP client (Slicer side) is 3D Slicer with its Web Server module active.
Recommends:     3dslicer

%description -n python3-mcp-slicer %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# Upstream ships no LICENSE file and declares no PEP 639 License-File metadata,
# so use -L (skip license-file handling) rather than -l.
%pyproject_save_files -L mcp_slicer

%check
%pyproject_check_import

%files -n python3-mcp-slicer -f %{pyproject_files}
%doc README.md
%{_bindir}/mcp-slicer

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.1-1
- Initial package. mcp-slicer 0.2.1: MCP server for agentic control of 3D
  Slicer (list_nodes / execute_python_code / capture_screenshot) over the
  Slicer Web Server interface. Enables Claude Code / Claude Desktop to drive
  the Fedora 3dslicer package.
