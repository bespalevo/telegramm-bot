



dict_a = [{"city": {"id": 3}}, {"city": {"id": 1}}]

print(sorted(dict_a, key=lambda i: i["city"]["id"]))
