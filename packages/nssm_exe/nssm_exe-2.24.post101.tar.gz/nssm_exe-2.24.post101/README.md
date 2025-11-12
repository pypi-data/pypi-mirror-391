nssm_exe
=======

This package bundles nssm.exe (Non-Sucking Service Manager) for Windows and exposes it as a simple, portable executable that is installed into the Python "Scripts" directory when the package wheel is installed.

Purpose
-------

- Provide an easy way to include nssm.exe with Python projects and installers.
- Ensure the nssm.exe binary is placed in the environment's Scripts folder (e.g., venv or system Python), so it is available on PATH.

Usage
-----

After installing the package (e.g., pip install nssm_exe-<version>.whl), the nssm executable will be available as `nssm.exe` in the environment's Scripts folder. Use it as you would the upstream nssm tool:

- nssm install MyService C:\\path\\to\\executable.exe
- nssm start MyService
- nssm stop MyService

Notes
-----

- This package only wraps and redistributes the `nssm.exe` binary. It does not modify or extend the original project.
- Verify licensing and redistribution terms for nssm before publishing.

Files
-----

- `nssm_exe/nssm.exe` - the bundled executable included in the wheel.
- `pyproject.toml` - package metadata and build instructions.
