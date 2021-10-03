import yfinance as yf
import json, datetime, calendar, math
import holidays

us_holidays = holidays.UnitedStates()

SPY = yf.Ticker("SPY")

data = SPY.history(start="2017-01-01", end="2021-09-22")
data = data.to_json(orient="records")
data = json.loads(data)

current = datetime.datetime(2016, 12, 31)
result = []

for row in data:
	current += datetime.timedelta(days=1)
	weekday = current.strftime("%A")
	if weekday == "Saturday":
		current += datetime.timedelta(days=2)
	elif weekday == "Sunday" or us_holidays.get(current.strftime("%Y-%m-%d")) != None:
		current += datetime.timedelta(days=1)
	weekday = current.strftime("%A")
	row["date"] = current.strftime("%Y-%m-%d")
	row['weekday'] = weekday
	result.append(row)


print(json.dumps(result, indent=4), file=open("raw.json", "w"))


fridayClose = None
mondayClose = None
friday = None
monday = None

change = []

for row in result:
	dateObj = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
	year = dateObj.year
	month = dateObj.month
	day_to_count = calendar.FRIDAY
	c = calendar.monthcalendar(year,month)
	num_days = sum(1 for x in c if x[day_to_count] != 0)
	friday_index = math.floor(num_days/2)

	first_day_of_month = datetime.datetime(year, month, 1)
	first_friday = first_day_of_month + datetime.timedelta(days=((4-calendar.monthrange(year, month)[0])+7)%7)
	friday = first_friday + datetime.timedelta(days=friday_index*2)
	friday = datetime.datetime(friday.year, friday.month, friday.day)

	monday = friday + datetime.timedelta(days=10)
	monday = datetime.datetime(monday.year, monday.month, monday.day)

	if dateObj == friday:
		fridayClose = row['Close']
	elif dateObj == monday:
		mondayClose = row['Close']

	if fridayClose and mondayClose and dateObj == monday:
		percentChange = mondayClose/fridayClose*100-100
		change.append({
			"friday": friday.strftime("%m/%d/%Y"),
			"monday": monday.strftime("%m/%d/%Y"),
			"percentChange": percentChange
		})


print(json.dumps(change, indent=4), file=open("datadump.json", "w"))

total = 18

for set in change:
	total += set['percentChange']

print(str(total) + "%")