import os
import glob
import filecmp
import json
import shutil

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest

import pkg_resources
from invoice2data.main import *
from invoice2data.extract.loader import read_templates


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.templates = read_templates()
        self.parser = create_parser()

    def _get_test_file_pdf_path(self):
        out_files = []
        for path, subdirs, files in os.walk(pkg_resources.resource_filename(__name__, 'compare')):
            for file in files:
                if file.endswith(".pdf"):
                    out_files.append(os.path.join(path, file))
        return out_files

    def _get_test_file_json_path(self):
        compare_files = []
        for path, subdirs, files in os.walk(pkg_resources.resource_filename(__name__, 'compare')):
            for file in files:
                if file.endswith(".json"):
                    compare_files.append(os.path.join(path, file))
        return compare_files

    def compare_json_content(self, test_file, json_file):
        with open(test_file) as json_test_file, open(json_file) as json_json_file:
            jdatatest = json.load(json_test_file)
            jdatajson = json.load(json_json_file)
        # logger.info(jdatajson)
        # logger.info(jdatatest)
        if jdatajson == jdatatest:
            logger.info("True")
            return True
        else:
            logger.info("False")
            return False

    def test_input(self):
        args = self.parser.parse_args(['--input-reader', 'pdftotext'] + self._get_test_file_pdf_path())
        main(args)

    def test_output_name(self):
        test_file = 'inv_test_8asd89f78a9df.csv'
        args = self.parser.parse_args(['--output-name', test_file, '--output-format', 'csv']
                                      + self._get_test_file_pdf_path())
        main(args)
        self.assertTrue(os.path.exists(test_file))
        os.remove(test_file)

    def test_debug(self):
        args = self.parser.parse_args(['--debug'] + self._get_test_file_pdf_path())
        main(args)

    # TODO: move result comparison to own test module.
    # TODO: parse output files instaed of comparing them byte-by-byte.

    def test_content_json(self):
        pdf_files = self._get_test_file_pdf_path()
        json_files = self._get_test_file_json_path()
        test_files = 'test_compare.json'
        for pfile in pdf_files:
            for jfile in json_files:
                if pfile[:-4] == jfile[:-5]:
                    args = self.parser.parse_args(
                        ['--output-name', test_files, '--output-format', 'json', pfile])
                    main(args)
                    compare_verified = self.compare_json_content(test_files, jfile)
                    print(compare_verified)
                    if not compare_verified:
                        self.assertTrue(False)
                    os.remove(test_files)
        self.assertTrue(True)

    def test_copy(self):
        # folder = pkg_resources.resource_filename(__name__, 'pdfs')
        directory = os.path.dirname("invoice2data/test/copy_test/pdf/")
        os.makedirs(directory)
        args = self.parser.parse_args(['--copy', 'invoice2data/test/copy_test/pdf'] + self._get_test_file_pdf_path())
        main(args)
        i = 0
        for path, subdirs, files in os.walk(pkg_resources.resource_filename(__name__, 'copy_test/pdf')):
            for file in files:
                if file.endswith(".pdf"):
                    i += 1

        shutil.rmtree('invoice2data/test/copy_test/', ignore_errors=True)
        self.assertEqual(i, len(self._get_test_file_json_path()))
        '''
        if i != len(self._get_test_file_json_path()):
            print(i)
            self.assertTrue(True)
        else:
            print(i)
            self.assertTrue(False, "Number of files not equal")
        '''


    # def test_template(self):
    #     parser = create_parser()
    #     folder = pkg_resources.resource_filename(__name__, 'pdfs')      
    #     args = parser.parse_args(['--template-folder', 'ACME-templates', self._get_test_file_path()])
    #     self.assertTrue(args.template_folder)

    # def test_exclude_template(self):
    #     parser = create_parser()
    #     folder = pkg_resources.resource_filename(__name__, 'pdfs')      
    #     args = parser.parse_args(['--exclude-built-in-templates', '--template-folder', 'ACME-templates', self._get_test_file_path()])
    #     self.assertTrue(args.exclude_built_in_templates)


if __name__ == '__main__':
    unittest.main()
