from enums import Month

xx = 1
nn = "JAN"
month_name = Month(xx).name
month = Month[nn].value
print(month_name, month)
