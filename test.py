servers = [{"ip_address": "10.100.1.171", "label": "Server Lingga 1"}, {"ip_address": "10.100.1.172", "label": "Server Lingga 1"}, {"ip_address": "10.100.1.173", "label": "Server Lingga 1"}]

values = ",".join(f"(\'{server['ip_address']}\', \'{server['label']}\')" for server in servers)

print(values)