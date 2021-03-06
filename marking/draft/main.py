import configparser
import os, shutil, csv, time
import xml.etree.ElementTree as ET


cf = configparser.ConfigParser()
cf.read("../config.properties")

junit_prj_base = cf.get("file_path", "junit_prj_base")
asgs_base = cf.get("file_path", "asgs_base")
file_name = cf.get("file_path", "file_name")
package_path = cf.get("file_path", "package_path")
surefire_report_path = cf.get("file_path", "surefire_report_path")
surefire_report_file = cf.get("file_path", "surefire_report_file")
final_report_path = cf.get("file_path", "final_report_path")

def copy_file_and_test(src_file, stu_number):
    junit_prj_file_path = os.path.join(junit_prj_base, package_path)
    if not os.path.isfile(src_file):
        print("File not exists under path " + stu_number)
        return False
    prj_file = junit_prj_file_path + file_name
    if os.path.exists(prj_file):
        os.remove(prj_file)
    shutil.copy(src_file, junit_prj_file_path)
    return True
    
def execute_maven():
    os.chdir(junit_prj_base)
    mvn_cmd = "mvn clean test"
    return_result = os.popen(mvn_cmd)
    return_str = return_result.read()
    return_result.close()
    return return_str
    
def analyze_mvn_output(mvn_output, stu_number, stat_file, report_path):
    success_str = "[INFO] BUILD SUCCESS"
    failure_str = "[INFO] BUILD FAILURE"
    compilation_error = "[ERROR] COMPILATION ERROR"
    if success_str in mvn_output:
        process_report(stu_number, stat_file, report_path)
    elif compilation_error in mvn_output:
        print("Failed when running test for student: " + stu_number)
    else:
        process_report(stu_number, stat_file, report_path)
        
def process_report(stu_number, stat_file, report_path):
    surefire_report_file_full_path = os.path.join(junit_prj_base, surefire_report_path, surefire_report_file)
    if not os.path.isfile(surefire_report_file_full_path):
        return
    shutil.copy(surefire_report_file_full_path, report_path)
    stu_report_file_name = stu_number + ".xml"
    stu_report_file_full_path = os.path.join(report_path, stu_report_file_name)
    os.rename(os.path.join(report_path, surefire_report_file), stu_report_file_full_path)
    parse_report(stu_number, stu_report_file_full_path, stat_file)
    
def parse_report(stu_number, stu_file_name, stat_file):
    if not os.path.exists(stu_file_name) or not os.path.isfile(stu_file_name):
        return
    tree = ET.parse(stu_file_name)
    root = tree.getroot()
    attrs = root.attrib
    write_to_csv(stu_number, attrs, stat_file)
    
def write_to_csv(stu_number, attrs, stat_file):
    if not os.path.exists(stat_file) or not os.path.isfile(stat_file):
        return
    with open(stat_file, 'a', newline='') as csvfile:
        f_csv = csv.writer(csvfile)
        f_csv.writerow([stu_number, attrs['tests'], attrs['failures'], attrs['errors'], attrs['skipped']])
    
def start_marking():
    asg_list = os.listdir(asgs_base)
    time_folder = time.strftime("%Y-%m-%d %H_%M_%S", time.localtime())
    report_folder = os.path.join(final_report_path, time_folder)
    os.makedirs(report_folder)
    csv_file = os.path.join(report_folder, "result.csv")
    with open(csv_file, 'w', newline='') as csvfile:
        f_csv = csv.writer(csvfile)
        f_csv.writerow(['Student No.', 'All Tests', 'Failures', 'Errors', 'Skipped'])
        
    for i in asg_list:
        print("Start processing " + i)
        stu_number = i
        stu_file_path = os.path.join(asgs_base, i, file_name)
        succ = copy_file_and_test(stu_file_path, stu_number)
        if not succ:
            continue
        return_str = execute_maven()
        analyze_mvn_output(return_str, stu_number, csv_file, report_folder)
        
if __name__ == '__main__':
    start_marking()
    
