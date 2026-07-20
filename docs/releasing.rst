Release validation
==================

This project validates release archives without uploading them. The process
follows the `Python Packaging User Guide
<https://packaging.python.org/en/latest/tutorials/packaging-projects/>`_ and runs
automatically in the ``Distribution`` GitHub Actions job.

Local preflight
---------------

Install the release tools and build both standard distribution formats:

.. code-block:: console

   pip install -e ".[release]"
   python -m build
   python -m twine check --strict dist/*
   python scripts/check_distribution.py dist

The archive check verifies core metadata, project URLs, runtime dependencies,
the SPDX license expression, required source files, and separation between the
installable wheel and development-only content.

Clean-install smoke test
------------------------

The CI job creates a new virtual environment, installs the built wheel and its
declared dependencies, changes out of the repository, and runs
``scripts/release_smoke_test.py``. The smoke test confirms that:

* imports come from the installed wheel rather than the source checkout;
* installed and runtime versions agree;
* every modulation scheme completes a noiseless round trip; and
* a short reproducible BER simulation completes successfully.

Publishing boundary
--------------------

Passing these checks does not upload anything. Before the first release, the
maintainer must configure the repository and workflow as a PyPI Trusted
Publisher. PyPI recommends a dedicated GitHub environment with manual approval
for production publishing. See the official `Trusted Publishing guide
<https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>`_.

For the final ``0.1.0`` release:

#. Confirm every CI job passes on the release commit.
#. Replace ``Unreleased`` for version 0.1.0 in ``CHANGELOG.md`` with the release
   date.
#. Configure the ``pypi`` GitHub environment and its Trusted Publisher entry.
#. Create the ``v0.1.0`` tag and GitHub Release only from the validated commit.
#. Publish the exact validated artifacts; do not rebuild them after approval.
