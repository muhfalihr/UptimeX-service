# import time
# from app.check import CRExec
# from typing import Any, List

# def main(ip_addresses: List[str]):
#     CR = CRExec()
#     if isinstance(ip_addresses, list):
#         for ip_address in ip_addresses:
#             CR.setup_executor_file(ip_address)
#             while True:
#                 result = CR.execute_tools_remote("ceker.py", action="detail")
#                 print(type(result))
#                 print(result)
#                 time.sleep(0.5)

#     else:
#         pass

# if __name__ == "__main__":
#     output = main(["10.12.1.175"])
    # print(output)

# from app.library.serverstatus import ServerStatusChecker

# checker = ServerStatusChecker(
#     hostname="10.12.1.103",  # Ganti dengan alamat IP atau hostname server
#     ssh_port=22,
#     ssh_username="root",  # Ganti dengan username SSH
#     ssh_password="123bdEsk@$ec"   # Ganti dengan password SSH
# )

# output = checker.get_server_status()
# print(output)

from app.check import CRExec as crexec

import asyncio

# Misal kamu memiliki instance dari class yang memiliki all_servers_status
# misal instance tersebut adalah `my_instance`

def update_list(list1, list2):
    for i in range(len(list2)):
        try:
            if list1[i]["status"] != list2[i]["status"]:
                list1[i] = list2[i]
        except IndexError:
            list1[i] = list2[i]
    return list1

async def get_all_server_status():
    all_servers_status1 = []
    all_servers_status2 = []
    all_servers_status = update_list(all_servers_status1, all_servers_status2)
    async for batch_result in exec.all_servers_status():
        all_servers_status = update_list(all_servers_status1, batch_result)
        print(batch_result if not all_servers_status else all_servers_status)
        all_servers_status.extend(batch_result)

# Jalankan fungsi asinkron ini
if __name__ == "__main__":
    exec = crexec()  # Ganti dengan instansiasi class yang benar
    while True:
        asyncio.run(get_all_server_status())
