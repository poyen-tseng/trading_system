import boto3
from pprint import pprint
import time
import os
import pyperclip as pc

while 1:
    try:
        availible_region = ["ap-east-1", "ap-northeast-1", "us-east-1"]
        for key, value in enumerate(availible_region):
            print(key, value)

        chosen_region = int(input("選擇地區:"))
        print("you choose", availible_region[chosen_region], "\n")

        session = boto3.Session(
            aws_access_key_id="GITHUB重要資訊隱藏",
            aws_secret_access_key="GITHUB重要資訊隱藏",
            region_name=availible_region[chosen_region],
        )
        ec2 = session.resource("ec2")
        availible_instance = []
        for i, instance in enumerate(ec2.instances.all()):
            availible_instance.append(instance.id)
            print(
                f"{i} | ID: {instance.id} | Type: {instance.instance_type} | Name: {next((tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'), None)} \t\t| State: {instance.state['Name']} | Private IP: {instance.private_ip_address} | Public IP: {instance.public_ip_address} "
            )
        chosen_instance = int(input("\nChoose instance:"))
        instance_to_operate = ec2.Instance(availible_instance[chosen_instance])
        print("you choose:", availible_instance[chosen_instance])
        chosen_ONOFF = int(
            input("\nturn 0-OFF or 1-ON or 2-ON-VNC or 3-SCP-上傳 4-SCP-下載 : ")
        )

        if chosen_ONOFF in (1, 2):
            response = instance_to_operate.start()

            print(
                f'正在turn ON {availible_instance[chosen_instance]}  {next((tag["Value"] for tag in instance_to_operate.tags if tag["Key"] == "Name"),None)} {instance_to_operate.private_ip_address}'
                # f'正在turn ON {availible_instance[chosen_instance]}  {next((tag["Value"] for tag in instance.tags if tag["Key"] == "Name"),None)} {instance_to_operate.private_ip_address}'
            )
            for i in range(30):
                print(i)
                time.sleep(1)
                # print("常常none的publicIP=", instance_to_operate.public_ip_address)
                # print("他的type=", type(instance_to_operate.public_ip_address))
                instance_to_operate = ec2.Instance(availible_instance[chosen_instance])
                if (
                    instance_to_operate.state["Name"] != "running"
                    or instance_to_operate.public_ip_address == None
                ):

                    # print(response)
                    # 表示還沒開機
                    continue
                else:
                    print("開機完成再等3秒")
                    break
            time.sleep(3)
            public_ip_address_dash = str(instance_to_operate.public_ip_address).replace(
                ".", "-"
            )
            ssh_command = f'ssh -i "{instance_to_operate.key_name}.pem" ec2-user@ec2-{public_ip_address_dash}.{availible_region[chosen_region]}.compute.amazonaws.com\n'
            print("\nSSH指令:\n", ssh_command)
            pc.copy(ssh_command)

            if chosen_ONOFF == 2:
                ssh_vnc_command = f'ssh -L 5901:localhost:5901 -Y -i "{instance_to_operate.key_name}.pem" ec2-user@ec2-{public_ip_address_dash}.{availible_region[chosen_region]}.compute.amazonaws.com\n'
                print("\nVNC指令:\n", ssh_vnc_command)
                os.startfile("D:\\source\\TigerVNC\\vncviewer.exe")
                # os.startfile("C:\\Program Files\\TigerVNC\\vncviewer.exe")
                os.startfile("D:\\_TradingSystem\\_InTrade\\_auto\\SSH入口_棕白_67.cmd")
                os.startfile("D:\\source\\eleader\\bin\\VUp.exe")
                pc.copy(ssh_vnc_command)

        elif chosen_ONOFF == 3:
            scp_command = f'scp -i "{instance_to_operate.key_name}.pem" -r "D:\_TradingSystem\_InTrade\_auto\@SCP通道" ec2-user@ec2-{public_ip_address_dash}.{availible_region[chosen_region]}.compute.amazonaws.com:poyen_file/@SCP通道\n\n'
            print("\nSCP指令:\n", scp_command)
            pc.copy(scp_command)

        elif chosen_ONOFF == 4:
            public_ip_address_dash = str(instance_to_operate.public_ip_address).replace(
                ".", "-"
            )
            scp_command = f'scp -i "{instance_to_operate.key_name}.pem" -r ec2-user@ec2-{public_ip_address_dash}.{availible_region[chosen_region]}.compute.amazonaws.com:poyen_file/@SCP通道 "D:\_TradingSystem\_InTrade\_auto\@SCP通道"\n\n'
            print("\nSCP指令:\n", scp_command)
            pc.copy(scp_command)
        else:
            instance_to_operate = ec2.Instance(availible_instance[chosen_instance])
            response = instance_to_operate.stop()
            print("turn OFF", availible_instance[chosen_instance])
            print(response)
        time.sleep(1)
        print("\n----本循環結束----\n")
        time.sleep(1)
    except Exception as e:
        print(e)
        print("\n----本循環結束----\n")
        pass

    # 所有可用指令
    # https://boto3.amazonaws.com/v1/documentation/api/1.26.82/reference/services/ec2/instance/index.html
    # print(instance.public_ip_address)  # 15.220.83.129
    # print(instance.private_ip_address)  #
    # print(instance.launch_time)       # 2024-09-22 18:56:56+00:00
    # print(instance.usage_operation)   # RunInstances
    # print(instance.platform)          # None
    # print(instance.platform_details)  #Linux/UNIX
    # print(instance.cpu_options)       # {'CoreCount': 1, 'ThreadsPerCore': 2}
    # print(instance.boot_mode)         # uefi-preferred
    # print(instance.architecture)      # x86_64
    # print(instance.key_name)  #poyen-taipei-1
    # print(instance.root_device_name)  #/dev/xvda
    # print(instance.root_device_type)  #ebs
    # print(instance.tags)  # [{'Key': 'Name', 'Value': 'taipei_PY'}]
    # print(instance.usage_operation_update_time)  # 2024-09-18 15:24:47+00:00
