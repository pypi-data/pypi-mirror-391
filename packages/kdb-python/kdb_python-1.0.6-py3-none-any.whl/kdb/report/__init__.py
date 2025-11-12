import datetime
import logging
import os
import socket
import xml.etree.ElementTree as ET

from kdb.common.constants import TestStatus
from kdb.common.utils import TimeUtil
from kdb.report.test_case_log import TestCaseLog


def add_comment(comment):
    TestCaseLog.add_comment(str(comment))
    logging.info(str(comment))


def get_table_status_class(test_status):
    # TestStatus.SKIP
    table_status_class = "table-secondary"
    if test_status == TestStatus.PASSED:
        table_status_class = "table-success"
    elif test_status == TestStatus.FAILED or test_status == 'trace':
        table_status_class = "table-danger"
    elif test_status == TestStatus.WARN:
        table_status_class = "table-warning"
    return table_status_class


def create_tc_table_header_element():
    """
    Create table header of test case html report
    """
    thead_element = ET.Element('thead', attrib={"class": "thead"})
    tr = ET.SubElement(thead_element, 'tr')
    ET.SubElement(tr, 'th', attrib={"id": "th-id", "scope": "col"}).text = "#"
    ET.SubElement(tr, 'th', id="th-action", scope="col").text = "Action"
    ET.SubElement(tr, 'th', id="th-message", scope="col").text = "Parameters/Message"
    ET.SubElement(tr, 'th', id="th-duration", scope="col").text = "Duration (ms)"
    ET.SubElement(tr, 'th', id="th-status", scope="col").text = "Status"
    return thead_element


num_of_command = 0


def create_tc_table_row_element(index, action, params, message, duration, status):
    """
    Create a table's row of test case html report corresponding a test step
    """
    global num_of_command
    # remove first and last char of params
    params = str(params)[1:len(params) - 1]
    # reset the num_of_command when create new html report
    if index == 1:
        num_of_command = 0
    else:
        index = int(index) - num_of_command
    tr_class = get_table_status_class(status)

    tr = ET.Element('tr', attrib={"class": tr_class})

    if TestStatus.SKIP == status:
        num_of_command += 1
        ET.SubElement(tr, 'td', attrib={"scope": "row", "colspan": "5"}).text = str(message)
    elif 'trace' != status:
        ET.SubElement(tr, 'th', scope="row").text = str(index)
        ET.SubElement(tr, 'td').text = action

        td_message = ET.SubElement(tr, 'td')
        # if test is failed add  message, image, current url error to report
        if TestStatus.FAILED == status:
            ET.SubElement(td_message, 'div', attrib={"class": "params"}).text = str(params)
            div_tag = ET.SubElement(td_message, 'div', attrib={"class": "message"})
            ET.SubElement(div_tag, 'div', attrib={"class": ""}).text = message['message']
            if message['image_url'] is not None and message['url_error'] is not None:
                image_url = os.path.join(os.path.split(os.path.dirname(message['image_url']))[1],
                                         os.path.split(message['image_url'])[1])
                tag_a = ET.SubElement(div_tag, 'a', attrib={"class": "fancybox", 'href': image_url})
                ET.SubElement(tag_a, 'img', attrib={"class": "image-display margin-message", 'src': image_url})

                div_a = ET.SubElement(div_tag, 'div', attrib={"class": "margin-message"})
                ET.SubElement(div_a, 'span', attrib={"class": ""}).text = "URL error: "
                ET.SubElement(div_a, 'a', attrib={"class": "", 'href': message['url_error']}).text = message[
                    'url_error']

        # if screen shot add image to report
        elif 'screen_shot' in action:
            ET.SubElement(td_message, 'div', attrib={"class": "params"}).text = str(params)
            div_tag = ET.SubElement(td_message, 'div', attrib={"class": "message"})
            image_url = os.path.join(os.path.split(os.path.dirname(message['image_url']))[1],
                                     os.path.split(message['image_url'])[1])
            tag_a = ET.SubElement(div_tag, 'a', attrib={"class": "fancybox", 'href': image_url})
            ET.SubElement(tag_a, 'img', attrib={"class": "image-display margin-message", 'src': image_url})

        else:
            td_message.text = str(params)

        ET.SubElement(tr, 'td', attrib={"class": "right"}).text = str(duration)
        ET.SubElement(tr, 'td', attrib={"class": "status"}).text = status
    else:
        # if 'trace' == status
        num_of_command += 1
        td_trace = ET.SubElement(tr, 'td', attrib={"scope": "row", "colspan": "5"})
        ET.SubElement(td_trace, 'div', attrib={"class": "params"}).text = "Error tracking"
        ET.SubElement(td_trace, 'div', attrib={"class": "message hide"}).text = str(message)

    return tr


def create_index_table_header_element():
    """
    Create table header of index html report
    """
    thead_element = ET.Element('thead', attrib={"class": "thead"})
    tr = ET.SubElement(thead_element, 'tr')
    ET.SubElement(tr, 'th', attrib={"id": "th-id", "scope": "col"}).text = "#"
    ET.SubElement(tr, 'th', id="th-action", scope="col").text = "Test Script/Test Case"
    ET.SubElement(tr, 'th', id="th-duration", scope="col").text = "Duration"
    ET.SubElement(tr, 'th', id="th-status", scope="col").text = "Status"
    return thead_element


def create_index_table_row_element(index, test_name, test_file, duration, status):
    """
    Create a table's row of index html report corresponding a test case
    """
    tr_class = get_table_status_class(status)
    tr_class += " testcase"

    tr = ET.Element('tr', attrib={"class": tr_class, "onclick": "document.location = '" + test_name + ".html';"})
    ET.SubElement(tr, 'th', scope="row").text = str(index)
    ET.SubElement(tr, 'td').text = test_name + os.linesep + "(" + test_file + ")"
    ET.SubElement(tr, 'td', attrib={"class": "center"}).text = str(TimeUtil.strftime_from_ms("%H:%M:%S", duration))
    ET.SubElement(tr, 'td', attrib={"class": "status"}).text = status
    return tr


def create_summary_table_element(failure, skip, error, total, duration):
    """
    Create summary table report
    """
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)

    table = ET.Element('table', attrib={"class": "table table-bordered table-hover table-primary summary-table"})
    thead = ET.SubElement(table, 'thead', attrib={"class": "s-title"})

    tr_title = ET.SubElement(thead, 'tr')
    ET.SubElement(tr_title, 'th', attrib={"scope": "col", "colspan": "8"}).text = "SUMMARY"

    tr_head = ET.SubElement(thead, 'tr', attrib={"class": "s-head"})
    ET.SubElement(tr_head, 'th', scope="col").text = "Host/IP"
    ET.SubElement(tr_head, 'th', scope="col").text = "Start Time (YYYY-MM-DD)"
    ET.SubElement(tr_head, 'th', scope="col").text = "Passed"
    ET.SubElement(tr_head, 'th', scope="col").text = "Failures"
    ET.SubElement(tr_head, 'th', scope="col").text = "Skipped"
    ET.SubElement(tr_head, 'th', scope="col").text = "Errors"
    ET.SubElement(tr_head, 'th', scope="col").text = "Total Test"
    ET.SubElement(tr_head, 'th', scope="col").text = "Total Time (hh:mm:ss)"

    tr_data = ET.SubElement(thead, 'tr', attrib={"class": "s-head"})
    ET.SubElement(tr_data, 'th', scope="col").text = hostname + " / " + IP
    ET.SubElement(tr_data, 'th', scope="col").text = str(datetime.date.today().strftime("%Y-%m-%d"))
    ET.SubElement(tr_data, 'th', scope="col").text = str(total - failure - skip - error)
    ET.SubElement(tr_data, 'th', scope="col").text = str(failure)
    ET.SubElement(tr_data, 'th', scope="col").text = str(skip)
    ET.SubElement(tr_data, 'th', scope="col").text = str(error)
    ET.SubElement(tr_data, 'th', scope="col").text = str(total)
    ET.SubElement(tr_data, 'th', scope="col").text = str(TimeUtil.strftime_from_ms("%H:%M:%S", duration))

    return table


def create_index_table_report(testsuite):
    """
    Create table in index page
    :param testsuite: content of xml file that created by pytest
    :return:
    """
    test_result = TestStatus.FAILED
    if int(testsuite.attrib["failures"]) == 0:
        test_result = TestStatus.PASSED

    # create content table tag
    table = ET.Element('table', attrib={"class": "table table-bordered table-hover " + test_result})
    # append table header to table
    table.append(create_index_table_header_element())
    # create tbody tag
    tbody = ET.SubElement(table, 'tbody')

    # add all test step to tbody
    for index in range(len(testsuite)):
        test_case = testsuite[index]
        # test case duration
        tc_duration = int(float(test_case.attrib["time"]) * 1000)
        # test case status
        tc_status = test_case.attrib["status"]
        # add a tr to tbody
        tbody.append(create_index_table_row_element(index + 1, test_case.attrib["name"], test_case.attrib["classname"],
                                                    tc_duration, tc_status))

    return table
