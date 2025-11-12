# -*- coding: utf-8 -*-
# vim: ts=4:sts=4:sw=4

import idf_converter


class TestPackage_Metadata(object):
    def test_has_version(self):
        assert hasattr(idf_converter, '__version__')

    def test_has_description(self):
        assert hasattr(idf_converter, '__description__')

    def test_has_author(self):
        assert hasattr(idf_converter, '__author__')

    def test_has_author_email(self):
        assert hasattr(idf_converter, '__author_email__')

    def test_has_url(self):
        assert hasattr(idf_converter, '__url__')

    def test_has_keywords(self):
        assert hasattr(idf_converter, '__keywords__')

    def test_has_classifiers(self):
        assert hasattr(idf_converter, '__classifiers__')
