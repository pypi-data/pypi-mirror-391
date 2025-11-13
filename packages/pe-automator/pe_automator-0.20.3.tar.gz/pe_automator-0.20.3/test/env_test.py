# from pe_automator.types.ssh import SimpleSSHClient
# from pe_automator.actions.allocation import get_allocation_info
# from pe_automator.actions.remote import run_command


# def main(allocation, hostname, user):
    

#     with SimpleSSHClient(name=allocation, hostname=hostname, username=user) as ssh_client:
#         ssh_client.connect()

#         run_command(f"bash env_test.sh", ssh_client=ssh_client)


# if __name__ == "__main__":
#     main('AECT-2025-2-0025', 'picasso.scbi.uma.es', 'resh000615')