# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project will (likely) adhere to [Semantic Versioning](http://semver.org/).



## [Unreleased]

### Added
-   Added a non-admin-specific login page for users. (STILL TODO as of Sept. 7)

### Changed
-   Implemented more accurate semantic versioning.
-   Modified URL structure for dataset creating/editing/detail pages:
    *    `/datasets/create/` now enables users to create a new dataset.
    *    `/datasets/FOO/` now shows the dataset's detail page.
    *    `/datasets/FOO/change-dataset/` now enables users to edit a dataset's metadata.
    *    `/datasets/FOO/change-dictionary/` now enables users to edit a dataset's data dictionary.
-   Restricted upload and editing views to authenticated users.
-   Improved handling of unauthenticated uses in sitewide title bar.



## 0.1.6 - 2016-09-07

### Changed
-   Storage class no longer refers to boto (or django-storages) directly. Users can create such a storage class on their own implementations if desired.
-   As a result of this change, Datafreezer now uses only one optional storage-related setting, `DATAFREEZER_CUSTOM_STORAGE_CLASS`. In the previous version there were four optional storage-related settings to decide between.



## 0.1.5 - 2016-09-06

### Added
-   First version of this changelog.

-   Custom storages setting (with multiple fallbacks) for all FileFields in app:
    *   Datafreezer will first look for custom S3 settings, applying a django-storages `S3BotoStorage` subclass if S3 credentials are available.
    *   If no custom S3 settings are provided, Datafreezer will look for and apply a custom storage class, as defined in `settings.py`.
    *   Failing both these options, Datafreezer will default to the project-wide file storage class.



## 0.1.4 - 2016-09-02

### Added
-   Files for favicon and touch icon.
-   HTML for favicon.



## 0.1.3 - 2016-09-02

### Changed
-   Removed unnecessary dependencies from `requirements.in` (and `requirements.txt`).



## 0.1.2 - 2016-09-02

### Changed
-   `setup.py` file will now read in dependencies rendered to `requirements.txt` and install them accordingly.



## 0.1.1 - 2016-09-02

### Removed
-   All deployment-specific (read: non-Datafreezer-critical) files.

### Changed
-   Start following [SemVer](http://semver.org) properly.
-   **NOTE:** This release was originally targeted to v0.1.0, but was amended to v0.1.1 after a hiccup in the release process. v0.1.0 doesn't fully exist.



## 0.0.1 - 2016-09-01

### Added
-   Initial release on PyPI.
-   Initial versions of all packaging files, along with Datafreezer app and core app files (models, views, etc.).

