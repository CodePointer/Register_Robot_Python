import itchat
import csv
import time

globals_para = {
	'confirmed': False,
	'running': False,
	'self_id': '',
	'register_num': 0,
	'group_id': ''}
csv_table = []
student_name = {}
student_id = {}


def import_student_information():
	"""Get student information from group information"""

	# Find group room
	group_room_list = itchat.search_chatrooms(name='测试群')
	group_room = itchat.update_chatroom(group_room_list[0]['UserName'], detailedMember=True)
	globals_para['self_id'] = group_room['self']['UserName']
	globals_para['group_id'] = group_room['UserName']

	# Import student information
	member_list = group_room['MemberList']
	for student in member_list:
		if student['UserName'] == globals_para['self_id']:
			continue
		information = student['DisplayName'].strip().split()
		if len(information) == 2:
			student_name[student['UserName']] = information[0]
			student_id[student['UserName']] = information[1]

	# Open file
	try:
		file = open('input.csv', 'r')
	except IOError:
		print('Open file error')
		return False

	# Read person information
	csv_reader = csv.reader(file)
	csv_table.clear()
	for line in csv_reader:
		line.append(-1)
		csv_table.append(line)
	file.close()

	# Write Initial file
	write_list()

	# Output information
	print('group_user_name: %s' % globals_para['group_id'])
	print('self_user_name: %s' % globals_para['self_id'])
	print('total student information import: %d' % len(student_name))
	print('Wait for next process')
	return True


def add_list(user_name, seat_num):
	"""Add information in student_list"""

	# Get student name and id by user_name
	if user_name not in student_name.keys():
		return '🐔: 无法识别的群名片。请稍后私信助教解决。'
	stu_name = student_name[user_name]
	stu_id = student_id[user_name]

	# Find student
	for line in csv_table:
		if (stu_name == line[0]) and (stu_id == line[1]):
			line[-1] = seat_num
			globals_para['register_num'] += 1
			write_list()
			return '🐔: %s_%s 成功签到，座位号：%s' % (line[0], line[2], line[-1])

	return '🐔: 无法找到%s_%s，签到名单中查无此人。请稍后私信助教解决。' % (stu_name, stu_id)


def write_list():
	"""Write list into a file"""

	# open file
	file_name = time.strftime('%Y_%m_%d.csv', time.localtime())
	try:
		file = open(file_name, 'w', newline='')
	except IOError:
		print('Write file error')
		return False

	# Write person information
	csv_writer = csv.writer(file)
	csv_writer.writerows(csv_table)
	file.close()

	return True


# @itchat.msg_register(['Text'])
# def process_text(msg):
# 	"""Process text received"""
#
# 	# Process information: only process my self
# 	if msg['FromUserName'] == msg['ToUserName']:
# 		if msg['Content'] == 'confirm':
#
# 			# Set self user id and running status
# 			globals_para['confirmed'] = True
# 			globals_para['self_id'] = msg['FromUserName']
# 			status = itchat.send_msg(
# 				'Robot: User id confirmed: %s' % globals_para['self_id'],
# 				toUserName='filehelper')
# 			print(status)
#
# 			# Read person information
# 			status = initialize_list()
# 			if status:
# 				message = 'Robot: Read csv file success. Information import: %d' % len(student_information)
# 			else:
# 				message = 'Robot: Read csv file failed.'
# 			status = itchat.send_msg(
# 				message,
# 				toUserName='filehelper')
# 			print(status)
#
# 		elif msg['Content'] == 'stop':
#
# 			# Set running status
# 			globals_para['running'] = False
#
# 			# reply
# 			itchat.send_msg(
# 				'Robot: Program stopped. Information collected: %d' % globals_para['sign_num'],
# 				toUserName='filehelper')
#
# 	return


@itchat.msg_register(['Text'], isGroupChat=True)
def process_group_text(msg):
	"""Process text in group"""

	# not running, wait for 'start' cmd
	if not globals_para['running']:
		if (msg['Content'] == 'start') and (msg['FromUserName'] == globals_para['self_id']):
			globals_para['running'] = True
			globals_para['group_id'] = msg['ToUserName']
			status = itchat.send_msg('🐔: 签到开始。请在群中回复: 签到[空格][座位号]', toUserName=globals_para['group_id'])

	# running, wait for '签到' cmd
	else:
		command = msg['Content'].strip().split()
		if (len(command) == 2) and (command[0] == '签到'):
			user_name = msg['ActualUserName']
			seat_num = command[1]
			response = add_list(user_name=user_name, seat_num=seat_num)
			status = itchat.send_msg(
				response,
				toUserName=globals_para['group_id'])
			print(status)
		elif (len(command) == 1) and (command[0] == 'stop') and (msg['FromUserName'] == globals_para['self_id']):
			globals_para['running'] = False
			status = itchat.send_msg(
				'🐔: 签到结束。共计%d人到场。具体文件如下。' % globals_para['register_num'],
				toUserName=globals_para['group_id'])
			print(status)
			file_name = time.strftime('%Y_%m_%d.csv', time.localtime())
			status = itchat.send_file(
				file_name,
				toUserName=globals_para['group_id'])
			print(status)
	return


itchat.auto_login()
import_student_information()
itchat.run()
