# NOTICE

This software package includes and redistributes components from third-party projects.
Please review the licenses below.

---

## 1. srcML

**Website:** https://www.srcml.org/  
**Source code:** https://github.com/srcML/srcml  
**License:** GNU General Public License v3.0 (GPLv3)
**Copyright:** © 2008–2020 Kent State University

srcML is a toolkit for the syntactic analysis and manipulation of C/C++/Java code, primarily for converting source code to XML and back.

This AppImage redistributes the official `srcml` binary and supporting libraries in an isolated, portable format.

---

## 2. AppImage Wrapper and Packaging

The AppImage wrapper, packaging, and build process for `srcml` were created by:

**Author:** Hernani Samuel Diniz  
**License:** GNU General Public License v3.0 (GPLv3)
**Description:**  
- Bundles `srcml` and its dependencies (e.g., `libssl1.0.0`, `libcrypto.so.1.0.0`)  
- Provides a self-contained AppImage that can be used without requiring FUSE  
- Designed for integration into Python-based tooling (e.g., via `subprocess`)

---

## 3. Project License

This project, including the `cclearly` frontend and AppImage wrapper scripts, is licensed under:

**GNU General Public License v3.0 (GPLv3)**  
You may copy, modify, and distribute this software under the terms of that license.  
See `LICENSE` for full terms.

---

## Notes

- The `srcml` binary and libraries remain under their original GPLv2 license.
- This package does not alter the functionality or code of `srcml`, only wraps it for simplified distribution.

