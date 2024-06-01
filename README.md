# github-lfs-usage-api

Get GitHub LFS Usage for the organization.

## Limitations

Since there are no known public API for the LFS statistics, this library works by scraping the billing Web UI, and thus there are several limitations:

* GitHub.com session cookie (not an access token) is required.
* For SAML-protected organizations the SSO session must be active.
* Only top 5 repositories are listed.
