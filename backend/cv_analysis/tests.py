from django.test import SimpleTestCase

from cv_analysis.views import CVAnalysisView


class CVAnalysisViewImportTests(SimpleTestCase):
    def test_view_module_imports_successfully(self):
        self.assertIsNotNone(CVAnalysisView)
