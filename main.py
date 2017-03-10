import itchat
import csv
import time

globals_para = {
	'confirmed': False,
	'running': False,
	'self_id': '',
	'sign_num': 0,
	'group_id': ''}
student_information = []
student_user_id = {}


def add_list(user_id, name, stu_id, seat_num):
	"""Add information in student_list"""

	# If in the user id list
	if user_id in student_user_id.values():
		return 'Robot: %s,%s failed for same user_id.' % (name, stu_id)

	# Find student
	for student in student_information:
		if (name == student[0]) and (stu_id == student[1]):
			student[-1] = seat_num
			globals_para['sign_num'] += 1
			student_user_id[student[0]] = user_id
			write_list()
			return '%s_%s success.' % (student[0], student[2])

	return 'Robot: Error in finding %s,%s, invalid information.' % (name, stu_id)


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
	csv_writer.writerows(student_information)
	file.close()

	return True


def initialize_list():
	"""Read student information from file"""

	status = True

	# open file
	try:
		file = open('原始名单.csv', 'r')
	except IOError:
		print('Open file error')
		return False

	# Read person information
	csv_reader = csv.reader(file)
	student_information.clear()
	student_user_id.clear()
	for line in csv_reader:
		line.append(-1)
		student_information.append(line)
	print(student_information)
	file.close()

	return status


@itchat.msg_register(['Text'])
def process_text(msg):
	"""Process text received"""

	# Process information: only process my self
	if msg['FromUserName'] == msg['ToUserName']:
		if msg['Content'] == 'confirm':

			# Set self user id and running status
			globals_para['confirmed'] = True
			globals_para['self_id'] = msg['FromUserName']
			status = itchat.send_msg(
				'Robot: User id confirmed: %s' % globals_para['self_id'],
				toUserName='filehelper')
			print(status)

			# Read person information
			status = initialize_list()
			if status:
				message = 'Robot: Read csv file success. Information import: %d' % len(student_information)
			else:
				message = 'Robot: Read csv file failed.'
			status = itchat.send_msg(
				message,
				toUserName='filehelper')
			print(status)

		elif msg['Content'] == 'stop':

			# Set running status
			globals_para['running'] = False

			# reply
			itchat.send_msg(
				'Robot: Program stopped. Information collected: %d' % globals_para['sign_num'],
				toUserName='filehelper')

	return


@itchat.msg_register(['Text'], isGroupChat=True)
def process_group_text(msg):
	"""Process text in group"""

	# Check status
	if globals_para['confirmed']:

		# not running, wait for 'start' cmd
		if not globals_para['running']:
			if (msg['Content'] == 'start') and (msg['FromUserName'] == globals_para['self_id']):
				globals_para['running'] = True
				globals_para['group_id'] = msg['ToUserName']
				status = itchat.send_msg('Robot: Program starts.', toUserName=globals_para['group_id'])
				print(status)

		# running, wait for '签到' cmd
		else:
			command = msg['Content'].strip().split()
			if (len(command) == 2) and (command[0] == '签到'):
				from_card = msg['ActualNickName'].strip().split()
				name = from_card[0]
				stu_id = from_card[1]
				user_id = msg['ActualUserName']
				seat_num = command[1]
				response = add_list(user_id, name, stu_id, seat_num)
				status = itchat.send_msg(
					response,
					toUserName=globals_para['group_id'])
				print(status)
			elif (len(command) == 1) and (command[0] == 'stop') and (msg['FromUserName'] == globals_para['self_id']):
				globals_para['running'] = False
				student_information.clear()
				student_user_id.clear()
				status = itchat.send_msg(
					'Robot: Finished, %d information received.' % globals_para['sign_num'],
					toUserName=globals_para['group_id'])
				print(status)

	return


itchat.auto_login(hotReload=True)
friends = itchat.get_friends()
itchat.run()
