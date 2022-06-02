Contributing to PyDBISAM
========================

Thanks for taking the time to contribute! 🎉👍

Open an Issue for feature and bugs. Please consider attaching an example database that would assist in addressing the issue. You know Python? Fork and open a Pull Request!

Release Procedure
-----------------

0. [Verify CI](https://github.com/linville/pydbisam/actions) is passing.
1. Bump version numbers in:
   - `setup.md`
   - `CHANGELOG.md`
2. On main branch, commit new version strings and push it up
   - `git checkout main`
   - `git commit -m "Releasing vX.Y.Z"`
   - `git push`
2. Tag commit
   - Optionally, tag with `git tag test-vX.Y.Z` for uploading to test instance of PyPi.
   - `git tag vX.Y.Z`
3. Push tag (this will trigger packing and uploading to PyPi)
   - `git push --tags`
4. [Check PyPi](https://pypi.org/project/pydbisam/).
5. [Create new GitHub Release](https://github.com/linville/pydbisam/releases)