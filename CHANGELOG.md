# Change History of intercom_test

## v2.0.1

* Fixed a typo relating to safe loading of YAML in augmentation data update files.
* Introduced semi-automated update of the package's `__version__`, adding a PEP 440-compliant _local version identifier_ indicating local changes; the main benefit to this is an inability to publish an improperly tagged/versioned revision (as PyPI doesn't accept packages with local version identifiers).

---

## v2.0.0

### Breaking Changes

* Default-unsafe loading of YAML has been disabled (see `safe_loading` in the docs), which could be a breaking change.

### New Features

v2.0.0 features CLI support for use by systems written in other languages.  When installed with the `[cli]` _extra_, it installs a command line script named `icy-test` (and it's additional dependencies) that can enumerate the test cases and commit updates to the compact files.  Please use the `icy-test --help` for more info.  Equivalent functionality can be accessed through `python -mintercom_test.foreign` if the appropriate dependencies are installed.

---

## v1.0.1

Although this patch-level release removes the auto-magic "body-type" JSON parsing functionality, it was broken (through a typo, fixed in commit b68317b) so it wasn't available anyway.  This way, it is opt-in and working.
