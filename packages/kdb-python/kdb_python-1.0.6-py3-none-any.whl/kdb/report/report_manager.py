import os
import xml.etree.ElementTree as ET

from kdb import FolderSettings
from kdb.common.constants import TestStatus
from kdb.common.utils import TimeUtil
from kdb.report import create_summary_table_element, create_index_table_report
from kdb.report import create_tc_table_header_element, create_tc_table_row_element
from kdb.report.test_case_log import TestCaseLog
from kdb.report.test_step_log import TestStepLog


class ReportManager:
    __dict_tc_result: dict = {}

    @staticmethod
    def create_test_case_report(test_case_name, is_passed, duration, file_name):
        # set status text
        test_result = TestStatus.FAILED
        if is_passed:
            test_result = TestStatus.PASSED

        # add result of tc to dict
        ReportManager.__dict_tc_result[test_case_name] = test_result

        # read html layout
        html = ET.parse(os.path.join(FolderSettings.REPORT_TEMPLATE_DIR, 'test_case_layout.html'))
        # set html report title
        # html.find('head').find('title').text = file_name
        title_tag = html.find('./head/title')
        title_tag.text = test_case_name + " - " + title_tag.text
        # get body tag
        body = html.find('body')

        # create table tag
        table = ET.Element('table', attrib={"class": "table table-bordered table-hover " + test_result})
        # append table header to table
        table.append(create_tc_table_header_element())
        # create tbody tag
        tbody = ET.SubElement(table, 'tbody')

        # get test steps list from TestCaseLog
        test_steps_list = TestCaseLog.get_test_steps_list()
        # add all test step to tbody
        for index in range(len(test_steps_list)):
            test_step: TestStepLog = test_steps_list[index]
            # add a tr to tbody
            tbody.append(create_tc_table_row_element(index + 1, test_step.action, test_step.params, test_step.message,
                                                     test_step.duration, test_step.status))

        # create tfoot tag
        tfoot = ET.SubElement(table, 'tfoot')
        tr_tf = ET.SubElement(tfoot, 'tr')
        ET.SubElement(tr_tf, 'th', attrib={"scope": "col"}).text = "End"
        ET.SubElement(tr_tf, 'th', attrib={"class": "right", "scope": "col", "colspan": "2"}).text = "Final Result:"
        ET.SubElement(tr_tf, 'th', attrib={"class": "right", "scope": "col"}).text = str(
            TimeUtil.strftime_from_ms("%H:%M:%S", duration))
        ET.SubElement(tr_tf, 'th', scope="col").text = test_result

        # create container element
        container = ET.Element('div', attrib={"class": "container"})
        table_wrapper = ET.Element('div', attrib={"class": "table-wrapper"})

        section_title = ET.Element('div', attrib={"class": "section-title"})
        ET.SubElement(section_title, 'h2', attrib={"class": "title center"}).text = test_case_name
        ET.SubElement(section_title, 'h4',
                      attrib={"class": "title center", "style": "margin-top: -16px;"}).text = file_name

        table_wrapper.append(table)
        container.append(section_title)
        container.append(table_wrapper)

        # append container element to body
        body.append(container)

        # write to html file
        html_file_path = os.path.join(FolderSettings.HTML_REPORT_DIR, test_case_name + ".html")
        html.write(file_or_filename=html_file_path, encoding="utf-8", method='html', short_empty_elements=False)
        # open html file in browser
        # webbrowser.open_new(html_file_path)
        return test_case_name + ".html"

    @staticmethod
    def create_index_report(xml_report_name=None):
        # read xml report file
        if xml_report_name is None:
            xml_report = ET.parse(os.path.join(FolderSettings.XML_REPORT_DIR, 'xml_report_main.xml'))
        else:
            xml_report = ET.parse(os.path.join(FolderSettings.XML_REPORT_DIR, xml_report_name))
        testsuite = xml_report.getroot().find("testsuite")
        if testsuite is None:
            testsuite = xml_report.getroot()
        num_of_tests = int(testsuite.attrib["tests"])
        if num_of_tests > 0:
            num_of_errors = int(testsuite.attrib["errors"])
            # num_of_failures = int(testsuite.attrib["failures"])
            num_of_skips = int(testsuite.attrib["skipped"])
            duration = int(float(testsuite.attrib["time"]) * 1000)

            # update the failures attr of testsuite
            num_of_failures = 0
            for result in ReportManager.__dict_tc_result.values():
                if result == TestStatus.FAILED:
                    num_of_failures += 1
            testsuite.set("failures", str(num_of_failures))

            # add the status attr for testcase element in testsuite
            for tc in testsuite.findall("testcase"):
                tc_name = tc.attrib["name"]
                tc_result = ReportManager.__dict_tc_result.get(tc_name)
                tc.set('status', tc_result)

            # read html layout
            html = ET.parse(os.path.join(FolderSettings.REPORT_TEMPLATE_DIR, 'index_layout.html'))
            # get body tag
            body = html.find('body')

            # append summary table to body
            body.append(
                create_summary_table_element(num_of_failures, num_of_skips, num_of_errors, num_of_tests, duration))

            # create container element
            container = ET.Element('div', attrib={"class": "container"})

            section_title = ET.Element('div', attrib={"class": "section-title"})
            ET.SubElement(section_title, 'h2', attrib={"class": "title center"}).text = str(testsuite.attrib["name"])

            container.append(section_title)
            container.append(create_index_table_report(testsuite))

            # append container element to body
            body.append(container)

            # write to html file
            html_file_path = os.path.join(FolderSettings.HTML_REPORT_DIR, "index.html")
            html.write(file_or_filename=html_file_path, encoding="utf-8", method='html', short_empty_elements=False)
            return html_file_path
