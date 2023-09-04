#!/usr/bin/python3

# Because the endpoint functions in genres.views are all implemented as
# closures returned by define_*_closure() higher-order functions from
# moundmusic.viewutils, no testing is needed here.
#
# All of those higher-order functions were developed in albums.views and
# all are used there. The existing test suite in albums.tests tests all
# of the endpoints in albums.views, and thereby indirectly tests every
# higher-order function in moundmusic.viewutils. Testing them again here
# would only duplicate that work.
